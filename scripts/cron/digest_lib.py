"""digest_lib.py — OpenClaw 每日 digest 公共库.

给 wife-daily-ai-digest / daily-news-briefing / ai-apps-research 三类任务共用.
抓 RSS → enrich 原文 → LLM 摘要 → 渲染 4 行卡片 → POST 到 MultiAgents 平台.

使用方式：每个 skill 写一个 runner.py，提供 DigestConfig + SOURCES 即可，其余
由本库处理.

示例 runner.py：

    from digest_lib import DigestConfig, run_digest
    from sources import SOURCES

    CONFIG = DigestConfig(
        skill_name="daily-news-briefing",
        project_name="每日新闻简报",
        agent_name="news-briefing-bot",
        title_prefix="每日新闻简报",
        tags=["日报/新闻"],
        category_labels={"finance": "💰 财经", "tech": "🔬 科技", ...},
        system_prompt_extra="关注综合新闻，不偏 AI。",
    )

    if __name__ == "__main__":
        run_digest(SOURCES, CONFIG)
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import threading
import urllib.error
import urllib.request
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Optional

_SCRIPTS_DIR = Path.home() / ".openclaw" / "workspace" / "scripts" / "cron"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from rss_fetcher import fetch_sources, Article, FetchResult, SourceSpec  # noqa: E402

try:
    from article_fetcher import fetch_article_text  # noqa: E402
except ImportError:
    fetch_article_text = None   # type: ignore


logger = logging.getLogger("digest_lib")

PLATFORM_URL = os.environ.get("MULTIAGENTS_URL", "http://118.89.197.244:8000")
FALLBACK_BASE = Path.home() / ".openclaw" / "data" / "cron-fallback"


# ─── 配置 ──────────────────────────────────────────────

@dataclass
class DigestConfig:
    skill_name: str                      # 用于 fallback 路径和日志
    project_name: str                    # MultiAgents 平台 project
    agent_name: str                      # MultiAgents 平台 agent
    title_prefix: str                    # 上传 title 前缀（追加 YYYY-MM-DD）
    tags: list[str] = field(default_factory=list)
    category_labels: dict[str, str] = field(default_factory=dict)
    system_prompt_extra: str = ""        # 注入到系统 prompt 的特色指令
    tldr_top_n: int = 3
    category_top_n: int = 5
    llm_batch_size: int = 10
    enrich_workers: int = 4
    per_source_timeout: float = 5.0
    fetch_total_timeout: float = 120.0
    max_items_per_source: int = 5


# ─── 日期 / HTML 清洗工具 ─────────────────────────────

def format_date_mmdd(published: str) -> str:
    if not published:
        return ""
    try:
        return parsedate_to_datetime(published).strftime("%m-%d")
    except Exception:
        pass
    m = re.match(r"(\d{4})-(\d{2})-(\d{2})", published)
    if m:
        return f"{m.group(2)}-{m.group(3)}"
    return published[:10]


def clean_html(raw: str) -> str:
    if not raw:
        return ""
    raw = re.sub(r"<script[^>]*>.*?</script>", "", raw, flags=re.S)
    raw = re.sub(r"<style[^>]*>.*?</style>", "", raw, flags=re.S)
    raw = re.sub(r"<[^>]+>", " ", raw)
    raw = re.sub(r"&nbsp;", " ", raw)
    raw = re.sub(r"&amp;", "&", raw)
    raw = re.sub(r"&lt;", "<", raw)
    raw = re.sub(r"&gt;", ">", raw)
    raw = re.sub(r"&quot;", '"', raw)
    raw = re.sub(r"&#?\w+;", "", raw)
    raw = re.sub(r"\s+", " ", raw)
    return raw.strip()


# ─── enrich：如 RSS summary 太短，抓原文 ─────────────

def _enrich_one(article: Article, timeout: float = 6.0) -> None:
    article.summary = clean_html(article.summary)
    if len(article.summary) >= 400:
        return
    if not article.link or fetch_article_text is None:
        return
    text, source = fetch_article_text(article.link, timeout=timeout,
                                      min_length=200)
    if text:
        article.summary = text[:1500]
        logger.info("enriched: %s via=%s len=%d",
                    article.source_name, source, len(text))


def enrich_articles(articles: list[Article], workers: int = 4,
                    timeout: float = 6.0) -> None:
    if not articles:
        return

    lock = threading.Lock()
    queue = list(articles)

    def _worker() -> None:
        while True:
            with lock:
                if not queue:
                    return
                a = queue.pop(0)
            try:
                _enrich_one(a, timeout=timeout)
            except Exception as e:
                logger.info("enrich fail: %s: %s", a.source_name, e)

    threads = [threading.Thread(target=_worker, daemon=True)
               for _ in range(min(workers, len(articles)))]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=timeout * len(articles) + 5)


# ─── LLM 摘要 ───────────────────────────────────────

def _get_llm_config() -> Optional[dict]:
    try:
        keys = ["compile_llm_api_key", "compile_llm_base_url", "compile_llm_model"]
        cfg: dict[str, str] = {}
        for key in keys:
            req = urllib.request.Request(f"{PLATFORM_URL}/api/config/{key}")
            with urllib.request.urlopen(req, timeout=3) as resp:
                cfg[key] = json.loads(resp.read()).get("value", "").strip()
        if not all(cfg.values()):
            return None
        return {
            "api_key": cfg["compile_llm_api_key"],
            "base_url": cfg["compile_llm_base_url"],
            "model": cfg["compile_llm_model"],
        }
    except Exception as e:
        logger.info("LLM config unavailable: %s: %s", type(e).__name__, e)
        return None


BASE_SYSTEM_PROMPT = """你是中文编辑。给定一组文章（title + 原文正文），为每条返回：
- simplified_title: 精简中文标题（15-25 字，去掉"｜最前线""深度"等冗余尾巴）
- summary: 中文摘要，**必须包含以下 4 个要素，每个要素至少写 1-2 句话**：
    【事件】这是什么产品发布、研究突破、融资、或新动向？
    【数据】原文里的具体数字、金额、性能、规模、百分比（原文没有就写"暂未披露"，不要省略这行）
    【主角】涉及哪些机构、公司、人物、产品型号（至少 2 个专有名词）
    【意义】为什么值得关心？对行业/落地/读者有什么启发？
  4 个要素串成自然段落，**总字数不少于 180 字**。
  不重复 simplified_title 里的词。禁用"该公司""近日""据悉""据报道""总的来说""综上所述"等废话。
- importance: 0-1 浮点数，综合相关度 + 新鲜度 + 影响力

输出是 JSON 数组，每项 i, simplified_title, summary, importance 四个字段。
只输出 JSON 数组，不要任何解释、代码块标记、前言。
输出前请检查每条 summary 字数是否不低于 180 字，不足请补充【意义】段落直到达标。"""


def _llm_one_batch(batch: list[Article], cfg: dict,
                   system_extra: str = "") -> dict[int, dict]:
    items = []
    for i, a in enumerate(batch):
        items.append({
            "i": i,
            "title": a.title[:200],
            "source": a.source_name,
            "body": a.summary[:1500],
        })

    system_prompt = BASE_SYSTEM_PROMPT
    if system_extra:
        system_prompt = system_extra + "\n\n" + system_prompt

    body = json.dumps({
        "model": cfg["model"],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(items, ensure_ascii=False)},
        ],
        "temperature": 0.3,
        "max_tokens": 8000,
    }).encode("utf-8")

    req = urllib.request.Request(
        cfg["base_url"].rstrip("/") + "/chat/completions",
        data=body,
        headers={
            "Authorization": f"Bearer {cfg['api_key']}",
            "Content-Type": "application/json",
        },
    )

    import time as _time
    data = None
    for attempt in (1, 2):
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = json.loads(resp.read())
                break
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt == 1:
                logger.info("LLM 429 rate limit, sleeping 15s and retrying")
                _time.sleep(15)
                continue
            logger.warning("LLM HTTP error: %s", e.code)
            return {}
        except Exception as e:
            logger.warning("LLM batch failed: %s: %s", type(e).__name__, e)
            return {}
    if data is None:
        return {}

    try:
        content = data["choices"][0]["message"]["content"].strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
        parsed = json.loads(content)
    except Exception as e:
        logger.warning("LLM parse failed: %s: %s", type(e).__name__, e)
        return {}

    result: dict[int, dict] = {}
    for item in parsed:
        if not isinstance(item, dict) or "i" not in item:
            continue
        try:
            imp = float(item.get("importance", 0.5))
        except (TypeError, ValueError):
            imp = 0.5
        if imp != imp or imp in (float("inf"), float("-inf")):
            imp = 0.5
        result[int(item["i"])] = {
            "simplified_title": str(item.get("simplified_title") or "").strip()[:80],
            "summary": str(item.get("summary") or "").strip()[:500],
            "importance": max(0.0, min(1.0, imp)),
        }
    return result


def llm_enrich_articles(articles: list[Article], cfg: dict,
                         batch_size: int = 10,
                         system_extra: str = "") -> None:
    for start in range(0, len(articles), batch_size):
        batch = articles[start:start + batch_size]
        result = _llm_one_batch(batch, cfg, system_extra=system_extra)
        for local_i, a in enumerate(batch):
            r = result.get(local_i)
            if r:
                a._simplified_title = r["simplified_title"] or a.title
                a._summary_cn = r["summary"]
                a._importance = r["importance"]
            else:
                a._simplified_title = a.title
                a._summary_cn = a.summary[:300]
                a._importance = 0.4
        logger.info("LLM batch %d: %d/%d ok",
                    start // batch_size + 1, len(result), len(batch))


# ─── Markdown 渲染 ───────────────────────────────────

def _render_article_card(a: Article) -> list[str]:
    title = getattr(a, "_simplified_title", None) or a.title
    summary = getattr(a, "_summary_cn", None) or a.summary[:300]
    pub_mmdd = format_date_mmdd(a.published)
    lines = [
        f"- **{title}**",
        f"  {summary}",
        f"  [查看原文 →]({a.link})",
        f"  · {a.source_name}" + (f" · {pub_mmdd}" if pub_mmdd else ""),
        "",
    ]
    return lines


def render_markdown(result: FetchResult, cfg: DigestConfig, date_str: str,
                    category_order: list[str]) -> str:
    for a in result.articles:
        if not hasattr(a, "_importance"):
            a._importance = 0.3
            a._simplified_title = a.title
            a._summary_cn = a.summary[:300]

    result.articles.sort(key=lambda a: -a._importance)
    tldr = result.articles[:cfg.tldr_top_n]

    by_cat: dict[str, list[Article]] = defaultdict(list)
    for a in result.articles:
        by_cat[a.category or "other"].append(a)
    for cat in list(by_cat.keys()):
        by_cat[cat] = by_cat[cat][:cfg.category_top_n]

    lines: list[str] = [
        f"# {cfg.title_prefix} · {date_str}",
        "",
    ]

    if tldr:
        lines.append("## 🔥 今日看点")
        lines.append("")
        for i, a in enumerate(tldr, 1):
            t = getattr(a, "_simplified_title", None) or a.title
            lines.append(f"{i}. **[{t}]({a.link})** — {a.source_name}")
        lines.append("")

    for cat_key in category_order:
        label = cfg.category_labels.get(cat_key, cat_key)
        lines.append(f"## {label}")
        lines.append("")
        items = by_cat.get(cat_key, [])
        if not items:
            lines.append("_今日暂无新内容_")
            lines.append("")
        else:
            for a in items:
                lines.extend(_render_article_card(a))

    lines.append("---")
    lines.append(
        f"抓取时间 {datetime.now().strftime('%m-%d %H:%M')} · "
        f"源成功率 {result.ok_count}/{result.ok_count + result.fail_count} · "
        f"共 {len(result.articles)} 条入选 {sum(len(v) for v in by_cat.values())} 条"
    )
    if result.errors:
        fail_line = "失败源: " + " · ".join(
            f"{name} ({reason[:40]})" for name, reason in result.errors.items()
        )
        lines.append(fail_line)

    return "\n".join(lines)


# ─── 平台上传 + fallback ────────────────────────────

def _push_to_platform(cfg: DigestConfig, title: str, content: str) -> bool:
    body = json.dumps({
        "agent": cfg.agent_name,
        "title": title,
        "content": content,
        "content_type": "markdown",
        "project": cfg.project_name,
        "tags": cfg.tags,
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{PLATFORM_URL}/api/outputs",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            logger.info("push success: output_id=%s", data.get("id"))
            return True
    except Exception as e:
        logger.warning("push failed: %s: %s", type(e).__name__, e)
        return False


def _write_fallback(cfg: DigestConfig, content: str, date_str: str,
                    reason: str) -> Path:
    fallback_dir = FALLBACK_BASE / cfg.skill_name
    fallback_dir.mkdir(parents=True, exist_ok=True)
    path = fallback_dir / f"{date_str}.md"
    path.write_text(
        f"<!-- fallback reason: {reason} -->\n{content}\n", encoding="utf-8"
    )
    logger.info("wrote fallback: %s", path)
    return path


# ─── 主入口 ─────────────────────────────────────────

def run_digest(
    sources: list[SourceSpec],
    config: DigestConfig,
    category_order: list[str],
) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-enrich", action="store_true")
    parser.add_argument("--no-llm", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    date_str = datetime.now().strftime("%Y-%m-%d")

    # 1. 抓 RSS
    enabled = [s for s in sources if s.enabled]
    logger.info("%s: fetching RSS (enabled=%d)", config.skill_name, len(enabled))
    result = fetch_sources(
        sources,
        per_source_timeout=config.per_source_timeout,
        total_timeout=config.fetch_total_timeout,
        max_items_per_source=config.max_items_per_source,
    )
    logger.info("rss fetched: ok=%d fail=%d articles=%d",
                result.ok_count, result.fail_count, len(result.articles))

    title = f"{config.title_prefix} {date_str}"

    if not result.articles:
        markdown = render_markdown(result, config, date_str, category_order)
        if args.dry_run:
            print(markdown)
            return 0
        if _push_to_platform(config, title, markdown):
            return 0
        _write_fallback(config, markdown, date_str, "empty + push failed")
        return 0

    # 2. enrich
    if not args.no_enrich:
        logger.info("enriching %d articles (workers=%d)",
                    len(result.articles), config.enrich_workers)
        enrich_articles(result.articles, workers=config.enrich_workers)

    # 3. LLM 摘要
    if not args.no_llm:
        cfg = _get_llm_config()
        if cfg:
            logger.info("LLM summarizing %d (batches of %d) with %s",
                        len(result.articles), config.llm_batch_size, cfg["model"])
            llm_enrich_articles(result.articles, cfg,
                                batch_size=config.llm_batch_size,
                                system_extra=config.system_prompt_extra)
        else:
            logger.info("LLM config unavailable, skipping summarization")

    # 4. 渲染
    markdown = render_markdown(result, config, date_str, category_order)

    if args.dry_run:
        print(markdown)
        return 0

    # 5. 上传 or fallback
    if _push_to_platform(config, title, markdown):
        logger.info("%s delivered ok", config.skill_name)
        return 0
    _write_fallback(config, markdown, date_str, "platform POST failed")
    logger.warning("%s fell back to local disk", config.skill_name)
    return 0
