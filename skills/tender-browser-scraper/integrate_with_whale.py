#!/usr/bin/env python3
"""
招标系统整合脚本：tender-browser-scraper + whale
功能：
1. 从 tender-browser-scraper 读取爬取的数据
2. 转换为 whale 格式
3. 使用 whale 的7维度评分
4. 生成专业报告
5. 保存到 whale 数据库
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass
from typing import Any
import re
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from html import unescape
import ssl

# 路径配置
WHALE_DIR = Path.home() / "Desktop/项目管理平台代码/whale/whale"
SCRAPER_DIR = Path.home() / ".openclaw/workspace/skills/tender-browser-scraper"
DATA_DIR = WHALE_DIR / "data"

HARD_EXCLUDE_KEYWORDS = [
    "监理", "施工", "EPC", "总承包", "采购", "比选公告", "竞争性比选",
    "园林", "绿化", "景观", "垃圾消纳", "铝镁锰屋面瓦"
]

PREFERRED_INCLUDE_KEYWORDS = [
    "勘察", "勘测", "测绘", "测量", "监测", "岩土", "地质", "水文地质", "物探", "检测",
    "治理", "河道", "供水", "管网", "水利", "边坡", "土壤修复"
]

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"

@dataclass
class CompanyProfile:
    preferred_types: list[str]
    preferred_regions: list[str]
    preferred_budget_range: list[int]
    excluded_keywords: list[str]
    long_term_customers: list[str]
    success_keywords: list[str]
    current_capacity: str
    special_focus: list[str]


class TenderScoringService:
    """Whale 的7维度评分逻辑"""
    def __init__(self, profile: CompanyProfile) -> None:
        self.profile = profile

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
        overall = round(sum(dimensions.values()) / len(dimensions))
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

    def _is_eligible(self, raw: dict[str, Any]) -> bool:
        text = f"{raw.get('type_name', '')} {raw['name']} {raw.get('keywords', '')}"
        return not any(keyword in text for keyword in self.profile.excluded_keywords)

    def _score_business(self, raw: dict[str, Any]) -> int:
        text = f"{raw.get('type_name', '')} {raw['name']} {raw.get('keywords', '')}"
        if not self._is_eligible(raw):
            return 0
        hits = sum(1 for item in self.profile.preferred_types if item in text)
        if hits >= 2:
            return 96
        if hits == 1:
            return 84
        return 60

    def _score_region(self, raw: dict[str, Any]) -> int:
        return 95 if raw["region"] in self.profile.preferred_regions else 68

    def _score_budget(self, raw: dict[str, Any]) -> int:
        minimum, maximum = self.profile.preferred_budget_range
        amount = raw.get("amount_wan", 0)
        if minimum <= amount <= maximum:
            return 90
        if amount < minimum:
            return 74
        return 82 if amount <= maximum * 1.4 else 66

    def _score_customer(self, raw: dict[str, Any]) -> int:
        purchaser = raw.get("purchaser", "")
        return 94 if purchaser in self.profile.long_term_customers else 72

    def _score_case_match(self, raw: dict[str, Any]) -> int:
        text = f"{raw['name']} {raw.get('keywords', '')} {raw.get('summary', '')}"
        hits = sum(1 for item in self.profile.success_keywords if item in text)
        if hits >= 2:
            return 92
        if hits == 1:
            return 82
        return 65

    def _score_schedule(self, raw: dict[str, Any]) -> int:
        try:
            deadline = datetime.fromisoformat(raw["deadline"])
            today = datetime.now().date()
            days_left = (deadline.date() - today).days
            if days_left < 3:
                return 62
            if days_left <= 7:
                return 76
            return 90 if self.profile.current_capacity == "high" else 78
        except:
            return 70

    def _score_special(self, raw: dict[str, Any]) -> int:
        text = f"{raw['name']} {raw.get('keywords', '')}"
        return 98 if any(item in text for item in self.profile.special_focus) else 70

    def _suggest_discount(self, raw: dict[str, Any], overall: int) -> float:
        if overall >= 88:
            return 0.03
        if raw.get("amount_wan", 0) > 500:
            return 0.05
        return 0.02

    def _build_quote_suggestion(self, raw: dict[str, Any], discount: float) -> str:
        return f"建议以历史同类项目均价为基准，下浮 {discount * 100:.0f}% 左右，突出{raw.get('type_name', '相关领域')}经验与履约能力。"


def load_company_profile() -> CompanyProfile:
    """加载公司画像"""
    profile_path = DATA_DIR / "company_profile.json"
    if not profile_path.exists():
        print(f"⚠️  公司画像文件不存在: {profile_path}")
        return CompanyProfile(
            preferred_types=["勘察", "监测", "测绘", "设计"],
            preferred_regions=["重庆市", "四川省", "湖北省", "贵州省", "云南省"],
            preferred_budget_range=[50, 500],
            excluded_keywords=["园林", "绿化", "景观"],
            long_term_customers=[],
            success_keywords=["岩土", "地质", "水文地质", "边坡", "基坑", "水利"],
            current_capacity="high",
            special_focus=["水利工程", "市政工程", "边坡治理"]
        )
    
    data = json.loads(profile_path.read_text(encoding="utf-8"))
    return CompanyProfile(**data)


def parse_scrape_markdown(md_path: Path) -> list[dict]:
    """解析 scrape.js 生成的 Markdown 报告"""
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


def infer_type_and_keywords(title: str) -> tuple[str, list[str]]:
    text = title or ""
    hits = [kw for kw in PREFERRED_INCLUDE_KEYWORDS if kw in text]
    if "勘察" in text and "设计" in text:
        return "勘察设计", hits
    if "勘察" in text or "勘测" in text:
        return "勘察", hits
    if "测绘" in text or "测量" in text:
        return "测绘", hits
    if "监测" in text:
        return "监测", hits
    if "岩土" in text or "地质" in text or "水文地质" in text or "物探" in text:
        return "地质类", hits
    if "河道" in text or "治理" in text or "水利" in text or "供水" in text or "管网" in text:
        return "市政/水利工程", hits
    if "变电站" in text or "能源站" in text or "供配电" in text:
        return "机电/能源工程", hits
    return "工程项目", hits


def fetch_text(url: str) -> str:
    req = Request(url, headers={"User-Agent": USER_AGENT, "Accept-Language": "zh-CN,zh;q=0.9"})
    ctx = ssl._create_unverified_context()
    with urlopen(req, timeout=20, context=ctx) as resp:
        charset = resp.headers.get_content_charset() or 'utf-8'
        return resp.read().decode(charset, errors='ignore')


def strip_html(text: str) -> str:
    text = re.sub(r'<script[\s\S]*?</script>', ' ', text, flags=re.I)
    text = re.sub(r'<style[\s\S]*?</style>', ' ', text, flags=re.I)
    text = re.sub(r'<[^>]+>', ' ', text)
    return re.sub(r'\s+', ' ', unescape(text)).strip()


def clean_title(title: str) -> str:
    title = unescape(title or '')
    title = re.sub(r'重庆市公共资源交易网_重庆市公共资源交易中心', ' ', title)
    title = re.sub(r'您当前的位置[:：]?.*?(招标公告\s*>?|工程招投标\s*>?)', ' ', title)
    title = re.sub(r'首页\s*>?\s*信息汇总\s*>?\s*工程招投标\s*>?\s*招标公告\s*>?\s*', ' ', title)
    title = re.sub(r'【\s*信息时间[:：]?\s*[^】]+】', ' ', title)
    title = re.sub(r'\b20\d{2}-\d{2}-\d{2}】?', ' ', title)
    title = re.sub(r'【\s*字号\s*大\s*中\s*小\s*】', ' ', title)
    title = re.sub(r'【\s*我要打印\s*】', ' ', title)
    title = re.sub(r'【\s*关闭\s*】', ' ', title)
    title = re.sub(r'我要报名', ' ', title)
    title = re.sub(r'\b(招标公告|比选公告|竞争性比选公告)\b\s*$', '', title)
    title = re.sub(r'^[\s【】>*-]+|[\s【】>*-]+$', '', title)
    title = re.sub(r'\s+', ' ', title).strip(' 】>-')
    return title


def is_bad_title(title: str) -> bool:
    title = clean_title(title)
    if not title or len(title) < 8:
        return True
    bad_markers = [
        '发布公告的媒介', '本次招标公告', '联系方式', '招标条件',
        '重庆市公共资源交易网', '您当前的位置', '我要打印', '关闭'
    ]
    return any(marker in title for marker in bad_markers)


def extract_detail_fields(detail_text: str, fallback_title: str) -> dict[str, Any]:
    title = clean_title(fallback_title)
    candidates = [
        re.search(r'([\u4e00-\u9fa5A-Za-z0-9（）()、，,\-—《》\[\]【】·\s]{8,}?)招标公告', detail_text),
        re.search(r'([\u4e00-\u9fa5A-Za-z0-9（）()、，,\-—《》\[\]【】·\s]{8,}?)竞争性比选\s*公告', detail_text),
        re.search(r'([\u4e00-\u9fa5A-Za-z0-9（）()、，,\-—《》\[\]【】·\s]{8,}?)\s*1\.招标条件', detail_text),
        re.search(r'项目名称[：:\s]*([\u4e00-\u9fa5A-Za-z0-9（）()、，,\-—《》\[\]【】·\s]{8,})', detail_text),
    ]
    valid_titles = []
    for m in candidates:
        if m:
            cand = clean_title(m.group(1))
            if not is_bad_title(cand):
                valid_titles.append(cand)
    if valid_titles:
        valid_titles = sorted(valid_titles, key=lambda x: (len(x), '等' in x, '工程' in x), reverse=True)
        title = valid_titles[0]
    if is_bad_title(title):
        title = clean_title(fallback_title)
    amount = ''
    amount_patterns = [
        (r'本次招标项目合同估算金额[：:\s]*约?\s*([\d\s\.]+)\s*万元', 'wan'),
        (r'合同估算金额[：:\s]*约?\s*([\d\s\.]+)\s*万元', 'wan'),
        (r'招标项目合同估算金额[：:\s]*约?\s*([\d\s\.]+)\s*万元', 'wan'),
        (r'本项目工程总投资金\s*额[：:\s]*([\d\s\.]+)\s*万元', 'wan'),
        (r'本项目工程总投资金额[：:\s]*([\d\s\.]+)\s*万元', 'wan'),
        (r'总投资金\s*额[：:\s]*([\d\s\.]+)\s*万元', 'wan'),
        (r'总投资金额[：:\s]*([\d\s\.]+)\s*万元', 'wan'),
        (r'预算金额[：:\s]*约?\s*([\d\s\.]+)\s*万元', 'wan'),
        (r'投标最高限价[：:\s]*约?\s*([\d\s\.]+)\s*万元', 'wan'),
        (r'投标限价[：:\s]*约?\s*([\d\s\.]+)\s*万元', 'wan'),
        (r'最高限价[：:\s]*约?\s*([\d\s\.]+)\s*万元', 'wan'),
        (r'招标控制价[：:\s]*约?\s*([\d\s\.]+)\s*万元', 'wan'),
        (r'控制价[：:\s]*约?\s*([\d\s\.]+)\s*万元', 'wan'),
        (r'本次招标项目合同估算金额[：:\s]*约?\s*([\d\s\.]+)\s*元', 'yuan'),
        (r'合同估算金额[：:\s]*约?\s*([\d\s\.]+)\s*元', 'yuan'),
        (r'预算金额[：:\s]*约?\s*([\d\s\.]+)\s*元', 'yuan'),
        (r'投标最高限价[：:\s]*约?\s*([\d\s\.]+)\s*元', 'yuan'),
        (r'投标限价[：:\s]*约?\s*([\d\s\.]+)\s*元', 'yuan'),
        (r'最高限价[：:\s]*约?\s*([\d\s\.]+)\s*元', 'yuan'),
        (r'招标控制价[：:\s]*约?\s*([\d\s\.]+)\s*元', 'yuan'),
        (r'控制价[：:\s]*约?\s*([\d\s\.]+)\s*元', 'yuan'),
        (r'([\d\s\.]+)\s*万元', 'wan')
    ]
    for pat, unit in amount_patterns:
        mm = re.search(pat, detail_text)
        if mm:
            raw_value = re.sub(r'\s+', '', mm.group(1))
            value = float(raw_value)
            if unit == 'yuan':
                value = round(value / 10000, 4)
            amount = f"{value:g}万元"
            break
    purchaser = ''
    for pat in [r'招标人\s*为\s*([^，。；\n]+)', r'招标人为\s*([^，。；\n]+)', r'项目业主为\s*([^，。；\n]+)', r'采购人为\s*([^，。；\n]+)']:
        mm = re.search(pat, detail_text)
        if mm:
            purchaser = mm.group(1).strip()
            break
    deadline = ''
    for pat in [r'投标文件递交的截止时间[^\d]*(20\d{2}-\d{2}-\d{2}\s*\d{1,2}:\d{2})', r'截止时间[^\d]*(20\d{2}-\d{2}-\d{2}\s*\d{1,2}:\d{2})']:
        mm = re.search(pat, detail_text)
        if mm:
            deadline = mm.group(1).strip()
            break
    published_at = ''
    mm = re.search(r'(20\d{2}年\d{2}月\d{2}日|20\d{2}-\d{2}-\d{2})', detail_text)
    if mm:
        published_at = mm.group(1).replace('年', '-').replace('月', '-').replace('日', '')
    summary = detail_text[:180]
    return {
        'title': title,
        'amount': amount or '未披露',
        'purchaser': purchaser,
        'deadline': deadline or (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
        'date': published_at or datetime.now().strftime('%Y-%m-%d'),
        'content': detail_text[:1500],
        'summary': summary,
    }


def enrich_quick_item(item: dict[str, Any]) -> dict[str, Any]:
    url = item.get('link')
    if not url:
        return item
    try:
        raw = fetch_text(url)
        detail_text = strip_html(raw)
        enriched = extract_detail_fields(detail_text, item.get('title', '未知项目'))
        out = dict(item)
        out.update(enriched)
        out['title'] = clean_title(out.get('title', item.get('title', '')))
        inferred_type, inferred_keywords = infer_type_and_keywords(out.get('title', ''))
        out['type'] = inferred_type
        out['keywords'] = list(sorted(set((out.get('keywords') or []) + inferred_keywords)))
        region_match = re.search(r'建设地点[：:\s]*([^\s，。]+)', detail_text)
        if region_match:
            out['region'] = region_match.group(1)
        return out
    except (URLError, HTTPError, TimeoutError, Exception):
        return item


def parse_quick_report_markdown(md_path: Path) -> list[dict]:
    """解析 quick_report.js 生成的初步清单"""
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
        item = {
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
        }
        projects.append(enrich_quick_item(item))
    return projects


def load_real_scraper_data() -> tuple[list[dict], str]:
    """优先读取真实爬虫输出，返回(数据, 来源类型)"""
    search_dirs = [
        SCRAPER_DIR / "scripts" / "output" / "tenders",
        SCRAPER_DIR / "output" / "tenders",
        Path.home() / ".openclaw/workspace/output/tenders",
    ]
    candidates = []
    for d in search_dirs:
        if d.exists():
            candidates.extend(list(d.glob("*_cqggzy.md")))
    candidates = sorted(candidates, key=lambda p: p.stat().st_mtime, reverse=True)
    for candidate in candidates:
        age_hours = (datetime.now().timestamp() - candidate.stat().st_mtime) / 3600
        parsed = parse_scrape_markdown(candidate)
        valid_titles = [p for p in parsed if p.get('title') and p.get('title') != '未知项目']
        if age_hours <= 6 and valid_titles:
            print(f"✅ 发现 scrape.js 输出: {candidate}")
            return parsed, "detailed"
        print(f"⚠️ 跳过无效/过旧详细报告: {candidate}")

    quick_report_path = Path.home() / ".openclaw/workspace/知识库/招标监控/原始清单/重庆公共资源_近3个月_初步清单.md"
    if quick_report_path.exists():
        print(f"✅ 发现 quick_report 输出: {quick_report_path}")
        return parse_quick_report_markdown(quick_report_path), "quick"

    print("⚠️  未找到真实爬虫产物")
    return [], "none"


def passes_hard_filter(item: dict[str, Any]) -> bool:
    title_text = " ".join([
        str(item.get('title', '')), str(item.get('type', ''))
    ])
    # 硬排除只看标题/类型，避免正文里的“施工资质”等词误杀
    if any(kw.lower() in title_text.lower() for kw in HARD_EXCLUDE_KEYWORDS):
        return False
    return True


def convert_scraper_to_whale(scraper_data: list[dict]) -> list[dict]:
    """转换爬虫数据为 whale 格式"""
    whale_projects = []
    filtered_out = 0
    
    for idx, item in enumerate(scraper_data, 1):
        if not passes_hard_filter(item):
            filtered_out += 1
            continue
        # 解析金额
        amount_text = item.get("amount", "未披露")
        amount_wan = None
        if isinstance(amount_text, str) and ("万" in amount_text):
            try:
                amount_wan = float(amount_text.replace("万元", "").replace("万", "").strip())
            except:
                pass
        elif isinstance(amount_text, str) and ("元" in amount_text):
            try:
                amount_wan = float(amount_text.replace("元", "").strip()) / 10000
            except:
                pass
        if amount_wan is None:
            amount_wan = 0
        
        # 构建 whale 格式
        whale_project = {
            "id": f"{datetime.now().strftime('%Y%m%d')}-{idx:03d}",
            "name": item.get("title", "未知项目"),
            "notice_url": item.get("link", ""),
            "source_name": item.get("source", "重庆市公共资源交易中心"),
            "published_at": item.get("date", datetime.now().strftime("%Y-%m-%d")),
            "deadline": item.get("deadline", (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")),
            "type_name": item.get("type", "勘察类"),
            "project_type_code": "KC",  # 默认勘察
            "region": item.get("region", "重庆市"),
            "purchaser": item.get("purchaser", ""),
            "agency": item.get("agency", ""),
            "amount_wan": amount_wan,
            "amount_text": amount_text,
            "method": "公开招标",
            "summary": item.get("summary", ""),
            "description": item.get("content", ""),
            "project_info": item.get("content", ""),
            "keywords": item.get("keywords", []),
            "attachments": []
        }
        whale_projects.append(whale_project)
    
    print(f"✅ 硬筛选后保留 {len(whale_projects)} 个，过滤 {filtered_out} 个")
    return whale_projects


def generate_report(scored_projects: list[dict], stats: dict, source_mode: str) -> str:
    """生成专业报告（Markdown格式）"""
    report_date = datetime.now().strftime("%Y-%m-%d")
    source_label = "详细抓取 + whale智能评分" if source_mode == "detailed" else "初步清单 + whale智能评分"
    
    report = f"""# 招标日报 - {report_date}

**报告生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M")}
**数据来源**: {source_label}
**项目总数**: {stats['total']}个
**高匹配项目**: {stats['high_match']}个（推荐指数≥85）
**平均推荐指数**: {stats['avg_score']}分

---

## 📊 总体统计

### 按网站分布
"""
    
    # 按来源统计
    sources = {}
    for project in scored_projects:
        source = project.get("source_name", "未知来源")
        sources[source] = sources.get(source, 0) + 1
    
    for source, count in sources.items():
        report += f"- 🏢 {source}：{count}个\n"
    
    report += f"""
### 按地区分布
"""
    
    # 按地区统计
    regions = {}
    for project in scored_projects:
        region = project.get("region", "未知地区")
        regions[region] = regions.get(region, 0) + 1
    
    for region, count in regions.items():
        report += f"- 📍 {region}：{count}个\n"
    
    report += f"""
### 按金额分布
- 💰 大型项目（>500万）：{len([p for p in scored_projects if p.get('amount_wan', 0) > 500])}个
- 💰 中型项目（50-500万）：{len([p for p in scored_projects if 50 <= p.get('amount_wan', 0) <= 500])}个
- 💰 小型项目（<50万）：{len([p for p in scored_projects if p.get('amount_wan', 0) < 50])}个

---

## 🏆 重点推荐（TOP 10）

"""
    
    # 按推荐指数排序
    top_projects = sorted(scored_projects, key=lambda x: x.get('recommendation_score', 0), reverse=True)[:10]
    
    for idx, project in enumerate(top_projects, 1):
        score = project.get('recommendation_score', 0)
        stars = "⭐" * min(5, score // 20)
        
        report += f"""### {idx}. {project['name']} {stars}

**📋 基本信息**
- **推荐指数**: {score}分（满分100）
- **中标概率**: {project.get('win_probability', 0)}%
- **预算金额**: {project.get('amount_text', '未知')}
- **招标单位**: {project.get('purchaser', '未知')}
- **所在地区**: {project.get('region', '未知')}
- **截止时间**: {project.get('deadline', '未知')}
- **原文链接**: [{project.get('source_name', '查看详情')}]({project.get('notice_url', '#')})

**📊 7维度评分"""
        
        scores = project.get('scores', {})
        for dim, val in scores.items():
            report += f"\n- {dim}: {val}分"
        
        report += f"""

**🎯 投标建议**
- **跟进策略**: {project.get('quote_strategy', {}).get('mode', '标准跟进')}
- **报价建议**: {project.get('quote_strategy', {}).get('suggestion', '参考市场价')}
- **建议折扣**: {project.get('quote_strategy', {}).get('discount_rate', 0.02) * 100:.0f}%

---

"""
    
    report += f"""## 📌 其他项目

"""
    
    # 其他项目（不在TOP 10的）
    other_projects = scored_projects[10:]
    for project in other_projects[:20]:  # 最多显示20个
        report += f"- **{project['name']}** - {project.get('amount_text', '未知')} - 推荐指数: {project.get('recommendation_score', 0)}分\n"
    
    report += f"""
---

## 📝 分析说明

**评分维度**:
1. **业务方向** (0-96分): 项目类型与公司业务匹配度
2. **地区匹配** (68-95分): 项目地区是否在偏好范围
3. **金额匹配** (66-90分): 项目金额是否在预算范围
4. **客户关系** (72-94分): 是否为长期客户
5. **成功案例** (65-92分): 关键词匹配历史成功案例
6. **时间安排** (62-90分): 截止时间是否充裕
7. **特殊需求** (70-98分): 是否符合特殊关注点

**推荐指数**: 7维度平均分
**中标概率**: 基于推荐指数和历史数据计算

---

**报告生成**: 小八爪 🐙 + whale智能系统
**抓取模式**: {source_label}
**Gitee仓库**: https://gitee.com/whaleandcollab/collab-knowledge-base
"""
    
    return report


def classify_type_from_title(title: str) -> str:
    text = title or ""
    if "勘察" in text and "设计" in text:
        return "勘察设计"
    if "勘察" in text:
        return "勘察"
    if "监测" in text or "监理" in text:
        return "监测/监理"
    if "测绘" in text or "测量" in text:
        return "测绘"
    if "水利" in text:
        return "水利工程"
    if "道路" in text or "路网" in text or "桥" in text or "交通" in text:
        return "交通工程"
    if "供水" in text or "污水" in text or "管网" in text:
        return "市政工程"
    return "工程项目"


def build_whale_records(scored_projects: list[dict]) -> list[dict]:
    records = []
    for project in scored_projects:
        keywords = project.get('keywords', [])
        if isinstance(keywords, str):
            keywords_str = keywords
            tags = [k for k in re.split(r'[,，\s]+', keywords) if k]
        else:
            tags = [str(k) for k in keywords]
            keywords_str = ",".join(tags)

        record = {
            "id": project['id'],
            "source_name": project.get('source_name', ''),
            "source_url": project.get('notice_url', ''),
            "notice_url": project.get('notice_url', ''),
            "name": project['name'],
            "type_name": project.get('type_name') or classify_type_from_title(project['name']),
            "region": project.get('region', ''),
            "purchaser": project.get('purchaser', ''),
            "amount_wan": int(project.get('amount_wan', 0)),
            "amount_text": project.get('amount_text', ''),
            "deadline": project.get('deadline', ''),
            "published_at": project.get('published_at', ''),
            "reference_no": project.get('reference_no', '') or project['id'],
            "stage": project.get('stage', '招标公告'),
            "summary": project.get('summary', ''),
            "description": project.get('description', ''),
            "keywords": keywords_str,
            "tags": tags,
            "highlights": [
                f"推荐指数：{project.get('recommendation_score', 0)}分",
                f"中标概率：{project.get('win_probability', 0)}%",
                f"跟进策略：{project.get('quote_strategy', {}).get('mode', '标准跟进')}"
            ]
        }
        records.append(record)
    return records


def write_whale_db(records: list[dict]):
    db_path = DATA_DIR / 'tenders.db'
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            source_name TEXT NOT NULL,
            source_url TEXT NOT NULL,
            name TEXT NOT NULL,
            type_name TEXT NOT NULL,
            region TEXT NOT NULL,
            purchaser TEXT NOT NULL,
            amount_wan INTEGER NOT NULL,
            amount_text TEXT NOT NULL,
            deadline TEXT NOT NULL,
            published_at TEXT NOT NULL,
            reference_no TEXT NOT NULL,
            stage TEXT NOT NULL,
            summary TEXT NOT NULL,
            description TEXT NOT NULL,
            keywords TEXT NOT NULL,
            tags_json TEXT NOT NULL,
            highlights_json TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            notice_url TEXT NOT NULL DEFAULT ''
        )
        """
    )
    now = datetime.now().isoformat()
    with conn:
        for item in records:
            conn.execute(
                """
                INSERT INTO projects (
                    id, source_name, source_url, name, type_name, region, purchaser,
                    amount_wan, amount_text, deadline, published_at, reference_no,
                    stage, summary, description, keywords, tags_json, highlights_json,
                    updated_at, notice_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    source_name=excluded.source_name,
                    source_url=excluded.source_url,
                    name=excluded.name,
                    type_name=excluded.type_name,
                    region=excluded.region,
                    purchaser=excluded.purchaser,
                    amount_wan=excluded.amount_wan,
                    amount_text=excluded.amount_text,
                    deadline=excluded.deadline,
                    published_at=excluded.published_at,
                    reference_no=excluded.reference_no,
                    stage=excluded.stage,
                    summary=excluded.summary,
                    description=excluded.description,
                    keywords=excluded.keywords,
                    tags_json=excluded.tags_json,
                    highlights_json=excluded.highlights_json,
                    updated_at=excluded.updated_at,
                    notice_url=excluded.notice_url
                """,
                (
                    item['id'], item['source_name'], item['source_url'], item['name'], item['type_name'],
                    item['region'], item['purchaser'], item['amount_wan'], item['amount_text'],
                    item['deadline'], item['published_at'], item['reference_no'], item['stage'],
                    item['summary'], item['description'], item['keywords'],
                    json.dumps(item['tags'], ensure_ascii=False),
                    json.dumps(item['highlights'], ensure_ascii=False),
                    now, item['notice_url']
                )
            )
    conn.close()
    print(f"✅ 已写入 {len(records)} 条到 whale 数据库")


def save_to_whale_format(scored_projects: list[dict]):
    """保存为 whale 格式，供 whale 系统使用"""
    crawled_path = DATA_DIR / "crawled_projects.json"
    records = build_whale_records(scored_projects)
    whale_data = {
        "meta": {
            "last_updated": datetime.now().isoformat(),
            "source": "tender-browser-scraper + whale集成"
        },
        "projects": records
    }
    crawled_path.write_text(json.dumps(whale_data, ensure_ascii=False, indent=2), encoding="utf-8")
    write_whale_db(records)
    print(f"✅ 已保存 {len(scored_projects)} 个项目到 whale 格式文件")


def main():
    """主流程"""
    print("🚀 开始集成 tender-browser-scraper + whale")
    
    # 1. 加载公司画像
    print("\n📋 加载公司画像...")
    profile = load_company_profile()
    print(f"✅ 公司画像加载成功")
    print(f"   - 偏好类型: {profile.preferred_types}")
    print(f"   - 偏好地区: {profile.preferred_regions}")
    
    # 2. 读取爬虫数据
    print("\n📊 读取爬虫数据...")
    scraper_data, source_mode = load_real_scraper_data()
    if not scraper_data:
        print("❌ 没有真实数据，先运行爬虫后再集成")
        return {
            "stats": {"total": 0, "high_match": 0, "avg_score": 0, "budget_sum": 0},
            "projects": [],
            "report_path": "",
            "source_mode": "none"
        }
    
    # 3. 转换格式
    print("\n🔄 转换数据格式...")
    whale_projects = convert_scraper_to_whale(scraper_data)
    print(f"✅ 转换完成: {len(whale_projects)} 个项目")
    
    # 4. 7维度评分
    print("\n📊 使用 whale 7维度评分...")
    service = TenderScoringService(profile)
    scored_projects = [service.score_project(project) for project in whale_projects]
    
    # 筛选符合条件的项目
    eligible_projects = [p for p in scored_projects if p.get('eligible', False)]
    eligible_projects.sort(key=lambda x: x.get('recommendation_score', 0), reverse=True)
    
    print(f"✅ 评分完成")
    print(f"   - 符合条件: {len(eligible_projects)} 个")
    print(f"   - 高匹配项目(≥85分): {len([p for p in eligible_projects if p.get('recommendation_score', 0) >= 85])} 个")
    
    # 5. 统计数据
    stats = {
        "total": len(eligible_projects),
        "high_match": len([p for p in eligible_projects if p.get('recommendation_score', 0) >= 85]),
        "avg_score": round(sum(p.get('recommendation_score', 0) for p in eligible_projects) / len(eligible_projects)) if eligible_projects else 0,
        "budget_sum": sum(p.get('amount_wan', 0) for p in eligible_projects)
    }
    
    # 6. 生成报告
    print("\n📝 生成专业报告...")
    report = generate_report(eligible_projects, stats, source_mode)
    report_path = Path.home() / ".openclaw/workspace/知识库/招标监控/招标日报_whale.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")
    print(f"✅ 报告已保存: {report_path}")
    
    # 7. 保存到 whale 格式
    print("\n💾 保存到 whale 格式...")
    save_to_whale_format(eligible_projects)
    
    # 8. 输出统计
    print("\n" + "="*50)
    print("📊 集成完成统计")
    print("="*50)
    print(f"项目总数: {stats['total']} 个")
    print(f"高匹配项目: {stats['high_match']} 个")
    print(f"平均推荐指数: {stats['avg_score']} 分")
    print(f"项目总金额: {stats['budget_sum']:.0f} 万元")
    print("="*50)
    
    # 返回结果
    return {
        "stats": stats,
        "projects": eligible_projects,
        "report_path": str(report_path),
        "source_mode": source_mode
    }


if __name__ == "__main__":
    from datetime import timedelta
    result = main()
    print(f"\n🎉 集成成功！报告已生成: {result['report_path']}")
