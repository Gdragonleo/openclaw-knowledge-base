#!/usr/bin/env python3
"""
招标日报 - 评分 + 报告生成模块
从爬虫数据读取 → 硬筛选 → 7维度评分 → 生成 Markdown/HTML/JSON 报告
"""
import json
import re
import sys
import ssl
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any
from html import unescape
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# ============================================================
# 配置加载
# ============================================================

def load_config(config_dir: Path) -> dict:
    """加载所有配置文件"""
    configs = {}
    for name in ["settings", "keywords", "company_profile", "sites"]:
        fpath = config_dir / f"{name}.json"
        if fpath.exists():
            configs[name] = json.loads(fpath.read_text(encoding="utf-8"))
        else:
            configs[name] = {}
    return configs


# ============================================================
# 数据模型
# ============================================================

@dataclass
class CompanyProfile:
    preferred_types: list[str] = field(default_factory=lambda: ["勘察", "监测", "测绘"])
    preferred_regions: list[str] = field(default_factory=lambda: ["重庆市"])
    preferred_budget_range: list[int] = field(default_factory=lambda: [50, 500])
    excluded_keywords: list[str] = field(default_factory=list)
    long_term_customers: list[str] = field(default_factory=list)
    success_keywords: list[str] = field(default_factory=list)
    current_capacity: str = "high"
    special_focus: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> "CompanyProfile":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


# ============================================================
# 硬筛选
# ============================================================

def load_hard_exclude(configs: dict) -> list[str]:
    """从关键词配置加载硬排除词"""
    keywords = configs.get("keywords", {})
    return keywords.get("hard_exclude", [
        "监理", "施工", "EPC", "总承包", "采购",
        "比选公告", "竞争性比选", "园林", "绿化",
        "景观", "垃圾消纳", "铝镁锰屋面瓦"
    ])


def passes_hard_filter(item: dict, hard_exclude: list[str]) -> bool:
    """硬筛选：标题含排除词的项目直接过滤"""
    title_text = f"{item.get('title', '')} {item.get('type_name', '')}"
    return not any(kw.lower() in title_text.lower() for kw in hard_exclude)


# ============================================================
# 7维度评分
# ============================================================

class TenderScoringService:
    def __init__(self, profile: CompanyProfile, hard_exclude: list[str]):
        self.profile = profile
        self.hard_exclude = hard_exclude

    def score_project(self, raw: dict[str, Any]) -> dict[str, Any]:
        eligible = self._is_eligible(raw)
        dimensions = {
            "业务方向": self._score_business(raw),
            "地区匹配": self._score_region(raw),
            "金额匹配": self._score_budget(raw),
            "客户关系": self._score_customer(raw),
            "成功案例": self._score_case_match(raw),
            "时间安排": self._score_schedule(raw),
            "特殊需求": self._score_special(raw),
        }
        overall = round(sum(dimensions.values()) / len(dimensions)) if dimensions else 0
        win_probability = min(95, max(35, round(overall * 0.9)))
        quote_discount = self._suggest_discount(raw, overall)

        return {
            **raw,
            "eligible": eligible,
            "recommendation_score": overall,
            "win_probability": win_probability,
            "quote_strategy": {
                "mode": "积极跟进" if overall >= 85 else "谨慎报价" if overall < 70 else "标准跟进",
                "discount_rate": quote_discount,
                "suggestion": self._build_quote_suggestion(raw, quote_discount),
            },
            "scores": dimensions,
        }

    def _is_eligible(self, raw: dict) -> bool:
        text = f"{raw.get('type_name', '')} {raw['name']} {raw.get('keywords', '')}"
        return not any(kw in text for kw in self.hard_exclude)

    def _score_business(self, raw: dict) -> int:
        text = f"{raw.get('type_name', '')} {raw['name']} {raw.get('keywords', '')}"
        if not self._is_eligible(raw):
            return 0
        hits = sum(1 for item in self.profile.preferred_types if item in text)
        return 96 if hits >= 2 else (84 if hits == 1 else 60)

    def _score_region(self, raw: dict) -> int:
        return 95 if raw.get("region", "") in self.profile.preferred_regions else 68

    def _score_budget(self, raw: dict) -> int:
        minimum, maximum = self.profile.preferred_budget_range
        amount = raw.get("amount_wan", 0) or 0
        if minimum <= amount <= maximum:
            return 90
        if amount < minimum:
            return 74
        return 82 if amount <= maximum * 1.4 else 66

    def _score_customer(self, raw: dict) -> int:
        purchaser = raw.get("purchaser", "")
        return 94 if purchaser in self.profile.long_term_customers else 72

    def _score_case_match(self, raw: dict) -> int:
        text = f"{raw['name']} {raw.get('keywords', '')} {raw.get('summary', '')}"
        hits = sum(1 for item in self.profile.success_keywords if item in text)
        return 92 if hits >= 2 else (82 if hits == 1 else 65)

    def _score_schedule(self, raw: dict) -> int:
        try:
            deadline = datetime.fromisoformat(str(raw.get("deadline", ""))[:10])
            days_left = (deadline.date() - datetime.now().date()).days
            if days_left < 3:
                return 62
            if days_left <= 7:
                return 76
            return 90 if self.profile.current_capacity == "high" else 78
        except Exception:
            return 70

    def _score_special(self, raw: dict) -> int:
        text = f"{raw['name']} {raw.get('keywords', '')}"
        return 98 if any(item in text for item in self.profile.special_focus) else 70

    def _suggest_discount(self, raw: dict, overall: int) -> float:
        if overall >= 88:
            return 0.03
        if (raw.get("amount_wan", 0) or 0) > 500:
            return 0.05
        return 0.02

    def _build_quote_suggestion(self, raw: dict, discount: float) -> str:
        return f"建议以历史同类项目均价为基准，下浮 {discount * 100:.0f}% 左右，突出{raw.get('type_name', '相关领域')}经验与履约能力。"


# ============================================================
# 数据读取（兼容旧爬虫输出格式）
# ============================================================

PREFERRED_INCLUDE_KEYWORDS = [
    "勘察", "勘测", "测绘", "测量", "监测", "岩土", "地质",
    "水文地质", "物探", "检测", "治理", "河道", "供水",
    "管网", "水利", "边坡", "土壤修复"
]

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"


def infer_type_and_keywords(title: str) -> tuple[str, list[str]]:
    text = title or ""
    hits = [kw for kw in PREFERRED_INCLUDE_KEYWORDS if kw in text]
    checks = [
        ("勘察设计", "勘察" in text and "设计" in text),
        ("勘察", "勘察" in text or "勘测" in text),
        ("测绘", "测绘" in text or "测量" in text),
        ("监测", "监测" in text),
        ("地质类", any(k in text for k in ["岩土", "地质", "水文地质", "物探"])),
        ("市政/水利工程", any(k in text for k in ["河道", "治理", "水利", "供水", "管网"])),
    ]
    for type_name, condition in checks:
        if condition:
            return type_name, hits
    return "工程项目", hits


def fetch_text(url: str, timeout: int = 20) -> str:
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept-Language": "zh-CN,zh;q=0.9"})
    ctx = ssl._create_unverified_context()
    with urlopen(req, timeout=timeout, context=ctx) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read().decode(charset, errors="ignore")


def strip_html(text: str) -> str:
    text = re.sub(r"<script[\s\S]*?</script>", " ", text, flags=re.I)
    text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", unescape(text)).strip()


def clean_title(title: str) -> str:
    title = unescape(title or "")
    title = re.sub(r"重庆市公共资源交易网_重庆市公共资源交易中心", " ", title)
    title = re.sub(r"您当前的位置[:：]?.*?(招标公告\s*>?|工程招投标\s*>?)", " ", title)
    title = re.sub(r"首页\s*>?\s*信息汇总\s*>?\s*工程招投标\s*>?\s*招标公告\s*>?\s*", " ", title)
    title = re.sub(r"【\s*信息时间[:：]?\s*[^】]+】", " ", title)
    title = re.sub(r"\b20\d{2}-\d{2}-\d{2}】?", " ", title)
    title = re.sub(r"【\s*字号\s*大\s*中\s*小\s*】", " ", title)
    title = re.sub(r"我要报名", " ", title)
    title = re.sub(r"\b(招标公告|比选公告|竞争性比选公告)\b\s*$", "", title)
    title = re.sub(r"^[\s【】>*\-]+|[\s【】>*\-]+$", "", title)
    return re.sub(r"\s+", " ", title).strip(" 】>-")


def extract_detail_fields(detail_text: str, fallback_title: str) -> dict[str, Any]:
    title = clean_title(fallback_title)
    candidates = [
        re.search(r"([\u4e00-\u9fa5A-Za-z0-9（）()、，,\-—《》\[\]【】·\s]{8,}?)招标公告", detail_text),
        re.search(r"([\u4e00-\u9fa5A-Za-z0-9（）()、，,\-—《》\[\]【】·\s]{8,}?)竞争性比选\s*公告", detail_text),
        re.search(r"([\u4e00-\u9fa5A-Za-z0-9（）()、，,\-—《》\[\]【】·\s]{8,}?)\s*1\.招标条件", detail_text),
        re.search(r"项目名称[：:\s]*([\u4e00-\u9fa5A-Za-z0-9（）()、，,\-—《》\[\]【】·\s]{8,})", detail_text),
    ]
    valid_titles = []
    for m in candidates:
        if m:
            cand = clean_title(m.group(1))
            if cand and len(cand) >= 8:
                valid_titles.append(cand)
    if valid_titles:
        title = sorted(valid_titles, key=len, reverse=True)[0]

    # 金额提取
    amount = ""
    amount_patterns = [
        (r"本次招标项目合同估算金额[：:\s]*约?\s*([\d\s\.]+)\s*万元", "wan"),
        (r"合同估算金额[：:\s]*约?\s*([\d\s\.]+)\s*万元", "wan"),
        (r"预算金额[：:\s]*约?\s*([\d\s\.]+)\s*万元", "wan"),
        (r"投标最高限价[：:\s]*约?\s*([\d\s\.]+)\s*万元", "wan"),
        (r"招标控制价[：:\s]*约?\s*([\d\s\.]+)\s*万元", "wan"),
        (r"控制价[：:\s]*约?\s*([\d\s\.]+)\s*万元", "wan"),
        (r"本次招标项目合同估算金额[：:\s]*约?\s*([\d\s\.]+)\s*元", "yuan"),
        (r"预算金额[：:\s]*约?\s*([\d\s\.]+)\s*元", "yuan"),
        (r"投标最高限价[：:\s]*约?\s*([\d\s\.]+)\s*元", "yuan"),
        (r"([\d\s\.]+)\s*万元", "wan"),
    ]
    for pat, unit in amount_patterns:
        mm = re.search(pat, detail_text)
        if mm:
            raw_value = re.sub(r"\s+", "", mm.group(1))
            value = float(raw_value)
            if unit == "yuan":
                value = round(value / 10000, 4)
            amount = f"{value:g}万元"
            break

    # 招标人
    purchaser = ""
    for pat in [r"招标人\s*为\s*([^，。；\n]+)", r"招标人为\s*([^，。；\n]+)", r"项目业主为\s*([^，。；\n]+)"]:
        mm = re.search(pat, detail_text)
        if mm:
            purchaser = mm.group(1).strip()
            break

    # 截止时间
    deadline = ""
    for pat in [r"投标文件递交的截止时间[^\d]*(20\d{2}-\d{2}-\d{2}\s*\d{1,2}:\d{2})", r"截止时间[^\d]*(20\d{2}-\d{2}-\d{2}\s*\d{1,2}:\d{2})"]:
        mm = re.search(pat, detail_text)
        if mm:
            deadline = mm.group(1).strip()
            break

    # 发布时间
    published_at = ""
    mm = re.search(r"(20\d{2}年\d{2}月\d{2}日|20\d{2}-\d{2}-\d{2})", detail_text)
    if mm:
        published_at = mm.group(1).replace("年", "-").replace("月", "-").replace("日", "")

    return {
        "title": title,
        "amount": amount or "未披露",
        "purchaser": purchaser,
        "deadline": deadline or (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
        "date": published_at or datetime.now().strftime("%Y-%m-%d"),
        "content": detail_text[:1500],
        "summary": detail_text[:180],
    }


def load_scraper_data(scraper_dir: Path) -> tuple[list[dict], str]:
    """读取爬虫产物，返回(项目列表, 数据来源类型)"""
    search_dirs = [
        scraper_dir / "scripts" / "output" / "tenders",
        scraper_dir / "output" / "tenders",
    ]
    candidates = []
    for d in search_dirs:
        if d.exists():
            candidates.extend(d.glob("*_cqggzy.md"))
    candidates = sorted(candidates, key=lambda p: p.stat().st_mtime, reverse=True)

    for candidate in candidates[:3]:
        age_hours = (datetime.now().timestamp() - candidate.stat().st_mtime) / 3600
        if age_hours <= 12:
            projects = parse_scrape_markdown(candidate)
            if projects:
                print(f"✅ 使用详细爬虫数据: {candidate.name}")
                return projects, "detailed"

    # 降级：读 quick_report 产物
    qr_path = Path.home() / ".openclaw/workspace/知识库/招标监控/原始清单/重庆公共资源_近3个月_初步清单.md"
    if qr_path.exists():
        projects = parse_quick_report_markdown(qr_path)
        if projects:
            print(f"✅ 使用 quick_report 数据")
            return projects, "quick"

    print("⚠️ 未找到爬虫产物，返回空数据")
    return [], "none"


def parse_scrape_markdown(md_path: Path) -> list[dict]:
    text = md_path.read_text(encoding="utf-8")
    blocks = re.split(r"\n## \d+\. ", text)
    projects = []
    for block in blocks[1:]:
        lines = block.splitlines()
        title = lines[0].strip() if lines else "未知项目"
        bidder = re.search(r"\*\*招标单位\*\*: (.+)", block)
        amount = re.search(r"\*\*项目金额\*\*: (.+)", block)
        deadline = re.search(r"\*\*截止时间\*\*: (.+)", block)
        date = re.search(r"\*\*发布时间\*\*: (.+)", block)
        url = re.search(r"\*\*原文链接\*\*: \[查看详情\]\((.+)\)", block)
        detail = re.search(r"\*\*项目详情\*\*:\n```\n([\s\S]*?)\n```", block)
        projects.append({
            "title": title,
            "link": url.group(1) if url else "",
            "date": date.group(1) if date else datetime.now().strftime("%Y-%m-%d"),
            "amount": amount.group(1) if amount else "0万",
            "deadline": deadline.group(1) if deadline else (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "purchaser": bidder.group(1) if bidder else "",
            "content": detail.group(1)[:1000] if detail else "",
            "summary": detail.group(1)[:120] if detail else "",
            "source": "重庆市公共资源交易中心",
            "region": "重庆市",
            "type": "勘察类",
            "keywords": [],
        })
    return projects


def parse_quick_report_markdown(md_path: Path) -> list[dict]:
    text = md_path.read_text(encoding="utf-8")
    blocks = re.split(r"\n### \d+\. ", text)
    projects = []
    for block in blocks[1:]:
        lines = block.splitlines()
        title = lines[0].strip() if lines else "未知项目"
        date = re.search(r"\*\*发布时间\*\*: (.+)", block)
        url = re.search(r"\*\*原文链接\*\*: \[查看详情\]\((.+)\)", block)
        region_match = re.search(r"【([^】]+)】", title)
        region = f"重庆市{region_match.group(1)}" if region_match else "重庆市"
        inferred_type, inferred_keywords = infer_type_and_keywords(title)
        projects.append({
            "title": title,
            "link": url.group(1) if url else "",
            "date": date.group(1) if date else datetime.now().strftime("%Y-%m-%d"),
            "amount": "未披露",
            "deadline": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "purchaser": "",
            "content": "",
            "summary": title,
            "source": "重庆市公共资源交易中心",
            "region": region,
            "type": inferred_type,
            "keywords": inferred_keywords,
        })
    return projects


def enrich_project(item: dict) -> dict:
    """补充抓取详情页信息"""
    url = item.get("link")
    if not url:
        return item
    try:
        raw = fetch_text(url)
        detail_text = strip_html(raw)
        enriched = extract_detail_fields(detail_text, item.get("title", ""))
        out = dict(item)
        out.update(enriched)
        out["title"] = clean_title(out.get("title", item.get("title", "")))
        inferred_type, inferred_keywords = infer_type_and_keywords(out.get("title", ""))
        out["type"] = inferred_type
        out["keywords"] = list(sorted(set((out.get("keywords") or []) + inferred_keywords)))
        region_match = re.search(r"建设地点[：:\s]*([^\s，。]+)", detail_text)
        if region_match:
            out["region"] = region_match.group(1)
        return out
    except Exception:
        return item


# ============================================================
# 数据转换
# ============================================================

def convert_to_whale_format(scraper_data: list[dict]) -> list[dict]:
    whale_projects = []
    for idx, item in enumerate(scraper_data, 1):
        amount_text = item.get("amount", "未披露")
        amount_wan = 0
        if isinstance(amount_text, str):
            if "万" in amount_text:
                try:
                    amount_wan = float(amount_text.replace("万元", "").replace("万", "").strip())
                except ValueError:
                    pass
            elif "元" in amount_text:
                try:
                    amount_wan = float(amount_text.replace("元", "").strip()) / 10000
                except ValueError:
                    pass

        whale_projects.append({
            "id": f"{datetime.now().strftime('%Y%m%d')}-{idx:03d}",
            "name": item.get("title", "未知项目"),
            "notice_url": item.get("link", ""),
            "source_name": item.get("source", "重庆市公共资源交易中心"),
            "published_at": item.get("date", datetime.now().strftime("%Y-%m-%d")),
            "deadline": item.get("deadline", ""),
            "type_name": item.get("type", "勘察类"),
            "region": item.get("region", "重庆市"),
            "purchaser": item.get("purchaser", ""),
            "amount_wan": amount_wan,
            "amount_text": amount_text,
            "summary": item.get("summary", ""),
            "description": item.get("content", ""),
            "keywords": item.get("keywords", []),
        })
    return whale_projects


# ============================================================
# 报告生成
# ============================================================

def generate_markdown_report(scored_projects: list[dict], stats: dict, source_mode: str, date_str: str) -> str:
    source_label = "详细抓取 + whale智能评分" if source_mode == "detailed" else "初步清单 + whale智能评分"
    high_match = [p for p in scored_projects if p.get("recommendation_score", 0) >= 85]
    big = [p for p in scored_projects if (p.get("amount_wan", 0) or 0) > 500]
    mid = [p for p in scored_projects if 50 <= (p.get("amount_wan", 0) or 0) <= 500]
    small = [p for p in scored_projects if (p.get("amount_wan", 0) or 0) < 50]

    r = f"""# 招标日报 - {date_str}

**报告生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
**数据来源**: {source_label}
**项目总数**: {stats['total']}个
**高匹配项目**: {len(high_match)}个（推荐指数≥85）
**平均推荐指数**: {stats['avg_score']}分

---

## 📊 总体统计

- 💰 项目总金额：{stats['budget_sum']:,.0f}万元
- 🏢 大型项目（>500万）：{len(big)}个
- 💰 中型项目（50-500万）：{len(mid)}个
- 💰 小型项目（<50万）：{len(small)}个

---

## 🏆 重点推荐（TOP 10）

"""
    top = sorted(scored_projects, key=lambda x: x.get("recommendation_score", 0), reverse=True)[:10]
    for idx, p in enumerate(top, 1):
        score = p.get("recommendation_score", 0)
        stars = "⭐" * min(5, score // 20)
        r += f"""### {idx}. {p['name']} {stars}

**📋 基本信息**
- **推荐指数**: {score}分 | **中标概率**: {p.get('win_probability', 0)}%
- **预算金额**: {p.get('amount_text', '未知')}
- **招标单位**: {p.get('purchaser', '未知')}
- **所在地区**: {p.get('region', '未知')}
- **截止时间**: {p.get('deadline', '未知')}
- **原文链接**: [{p.get('source_name', '查看详情')}]({p.get('notice_url', '#')})

**📊 7维度评分**"""
        for dim, val in p.get("scores", {}).items():
            bar = "█" * (val // 10) + "░" * (10 - val // 10)
            r += f"\n  - {dim}: {val}分 {bar}"

        qs = p.get("quote_strategy", {})
        r += f"""

**🎯 投标建议**: {qs.get('mode', '标准跟进')} | 建议折扣: {qs.get('discount_rate', 0.02) * 100:.0f}%

---

"""

    other = scored_projects[10:]
    if other:
        r += "## 📌 其他项目\n\n"
        for p in other[:20]:
            r += f"- **{p['name']}** — {p.get('amount_text', '未知')} — 推荐: {p.get('recommendation_score', 0)}分\n"

    r += f"""

---

## 📝 分析说明

**评分维度**: 业务方向 / 地区匹配 / 金额匹配 / 客户关系 / 成功案例 / 时间安排 / 特殊需求
**推荐指数**: 7维度平均分
**中标概率**: 基于推荐指数计算

---

**报告生成**: 小八爪 🐙 | 抓取模式: {source_label}
"""
    return r


# ============================================================
# 主流程
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="招标日报 - 评分+报告生成")
    parser.add_argument("--config", required=True, help="配置目录")
    parser.add_argument("--output-dir", required=True, help="输出目录")
    parser.add_argument("--scraper-dir", required=True, help="爬虫目录")
    parser.add_argument("--date", default="", help="日期字符串 YYYY-MM-DD")
    args = parser.parse_args()

    config_dir = Path(args.config)
    output_dir = Path(args.output_dir)
    scraper_dir = Path(args.scraper_dir)
    date_str = args.date or datetime.now().strftime("%Y-%m-%d")

    # 1. 加载配置
    configs = load_config(config_dir)
    profile = CompanyProfile.from_dict(configs.get("company_profile", {}))
    hard_exclude = load_hard_exclude(configs)
    print(f"📋 公司画像加载完成，偏好类型: {profile.preferred_types}")

    # 2. 读取爬虫数据
    scraper_data, source_mode = load_scraper_data(scraper_dir)
    if not scraper_data:
        print("❌ 无可用数据，请先运行爬虫")
        sys.exit(1)

    # 3. 硬筛选
    before = len(scraper_data)
    scraper_data = [item for item in scraper_data if passes_hard_filter(item, hard_exclude)]
    filtered = before - len(scraper_data)
    print(f"🔍 硬筛选: {before} → {len(scraper_data)} (过滤{filtered}个)")

    # 4. 补充详情（对 quick_report 的项目）
    if source_mode == "quick":
        print("🌐 补充详情页信息...")
        scraper_data = [enrich_project(item) for item in scraper_data]

    # 5. 转换格式
    whale_projects = convert_to_whale_format(scraper_data)

    # 6. 7维度评分
    service = TenderScoringService(profile, hard_exclude)
    scored_projects = [service.score_project(p) for p in whale_projects]
    eligible = [p for p in scored_projects if p.get("eligible", False)]
    eligible.sort(key=lambda x: x.get("recommendation_score", 0), reverse=True)

    stats = {
        "total": len(eligible),
        "high_match": len([p for p in eligible if p.get("recommendation_score", 0) >= 85]),
        "avg_score": round(sum(p.get("recommendation_score", 0) for p in eligible) / len(eligible)) if eligible else 0,
        "budget_sum": sum(p.get("amount_wan", 0) or 0 for p in eligible),
    }
    print(f"📊 评分完成: {stats['total']}个 | 平均{stats['avg_score']}分 | 高匹配{stats['high_match']}个")

    # 7. 生成 Markdown 报告
    report = generate_markdown_report(eligible, stats, source_mode, date_str)
    report_path = output_dir / f"招标日报_{date_str}.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"📝 Markdown报告: {report_path}")

    # 8. 生成项目 JSON
    projects_json = output_dir / f"招标日报_{date_str}_projects.json"
    projects_json.write_text(json.dumps(eligible, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"📋 项目JSON: {projects_json}")

    # 9. 生成汇总 JSON
    summary = {
        "date": date_str,
        "generated_at": datetime.now().isoformat(),
        "source_mode": source_mode,
        "stats": stats,
        "top_recommendations": [
            {
                "name": p["name"],
                "score": p.get("recommendation_score", 0),
                "amount": p.get("amount_text", ""),
                "url": p.get("notice_url", ""),
            }
            for p in eligible[:5]
        ],
    }
    summary_json = output_dir / f"招标日报_{date_str}_summary.json"
    summary_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"📊 汇总JSON: {summary_json}")

    print(f"\n🎉 完成！共{stats['total']}个项目，报告已保存到 {output_dir}")


if __name__ == "__main__":
    main()
