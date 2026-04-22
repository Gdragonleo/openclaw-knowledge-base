"""
rss_fetcher.py — OpenClaw 公共 RSS 抓取器

供 daily-news / wife-daily-ai-digest 等需要抓 RSS/HTTP 源的 skill 复用。

设计原则：
- 单源超时 5s（可覆盖），总超时 120s（可覆盖）
- 任何单源失败都不阻塞其余源，返回部分结果 + 失败统计
- 零依赖外部 RSS 库：用 stdlib 的 xml.etree + feedparser 兼容格式
- 不做重试 —— cron 本身每天/每小时跑一次，失败就下次再来

Usage:
    from rss_fetcher import fetch_sources, SourceSpec

    sources = [
        SourceSpec(name="量子位", url="https://www.qbitai.com/feed", category="ai-cn"),
        SourceSpec(name="HuggingFace Blog", url="https://huggingface.co/blog/feed.xml", category="ai-global"),
    ]
    result = fetch_sources(sources, per_source_timeout=5, total_timeout=120)
    # result.articles: list[Article]
    # result.ok_count / result.fail_count / result.errors: dict[str, str]
"""
from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from email.utils import parsedate_to_datetime
from typing import Iterable, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from xml.etree import ElementTree as ET

logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Version/14.1 Safari/605.1.15 OpenClawRSSFetcher/1.0"
)


@dataclass(frozen=True)
class SourceSpec:
    """源描述.

    category 是自由字符串，调用方自己定约定（例如 "ai-cn", "ai-global",
    "data-annotation", "tech-cn"）；fetcher 不做解释.
    """
    name: str
    url: str
    category: str = ""
    enabled: bool = True


@dataclass
class Article:
    source_name: str
    source_url: str
    category: str
    title: str
    link: str
    summary: str = ""
    published: str = ""          # ISO 字符串或原始字串
    fetched_at: float = 0.0


@dataclass
class FetchResult:
    articles: list[Article] = field(default_factory=list)
    ok_count: int = 0
    fail_count: int = 0
    errors: dict[str, str] = field(default_factory=dict)   # source_name -> 错因
    per_source_count: dict[str, int] = field(default_factory=dict)


def _parse_rss_or_atom(xml_bytes: bytes, source: SourceSpec,
                      max_items: int) -> list[Article]:
    """最小 RSS 2.0 / Atom 解析器；失败抛 ET.ParseError."""
    root = ET.fromstring(xml_bytes)

    # Atom feed 命名空间
    ns_atom = {"atom": "http://www.w3.org/2005/Atom"}

    articles: list[Article] = []

    # RSS 2.0: <rss><channel><item>
    for item in root.findall(".//item")[:max_items]:
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        desc = (item.findtext("description") or "").strip()
        pub = (item.findtext("pubDate") or "").strip()
        if not title:
            continue
        articles.append(Article(
            source_name=source.name,
            source_url=source.url,
            category=source.category,
            title=title,
            link=link,
            summary=desc[:500],
            published=pub,
            fetched_at=time.time(),
        ))

    if articles:
        return articles

    # Atom: <feed><entry>
    for entry in root.findall("atom:entry", ns_atom)[:max_items]:
        title_el = entry.find("atom:title", ns_atom)
        link_el = entry.find("atom:link", ns_atom)
        summary_el = entry.find("atom:summary", ns_atom)
        published_el = entry.find("atom:published", ns_atom) or entry.find("atom:updated", ns_atom)

        title = (title_el.text or "").strip() if title_el is not None else ""
        link = link_el.get("href", "") if link_el is not None else ""
        summary = (summary_el.text or "").strip() if summary_el is not None else ""
        published = (published_el.text or "").strip() if published_el is not None else ""
        if not title:
            continue
        articles.append(Article(
            source_name=source.name,
            source_url=source.url,
            category=source.category,
            title=title,
            link=link,
            summary=summary[:500],
            published=published,
            fetched_at=time.time(),
        ))
    return articles


def _fetch_one(source: SourceSpec, timeout: float,
               max_items: int) -> tuple[list[Article], Optional[str]]:
    """抓一个源.返回 (articles, error or None).任何异常都转成 error 字符串."""
    try:
        req = Request(source.url, headers={"User-Agent": USER_AGENT})
        with urlopen(req, timeout=timeout) as resp:
            body = resp.read()
    except HTTPError as e:
        return [], f"HTTP {e.code}"
    except URLError as e:
        reason = str(e.reason) if hasattr(e, "reason") else str(e)
        return [], f"URLError: {reason}"
    except Exception as e:      # TimeoutError / socket.timeout / etc.
        return [], f"{type(e).__name__}: {e}"

    try:
        articles = _parse_rss_or_atom(body, source, max_items)
    except ET.ParseError as e:
        return [], f"ParseError: {e}"
    except Exception as e:
        return [], f"parse-{type(e).__name__}: {e}"

    if not articles:
        return [], "no-items-parsed"
    return articles, None


def fetch_sources(
    sources: Iterable[SourceSpec],
    *,
    per_source_timeout: float = 5.0,
    total_timeout: float = 120.0,
    max_items_per_source: int = 5,
) -> FetchResult:
    """并行抓取一组源.

    Args:
        sources: SourceSpec 列表（`enabled=False` 的自动跳过）
        per_source_timeout: 单源 HTTP 超时（秒）
        total_timeout: 总超时（秒）；超时后仍返回已完成的结果
        max_items_per_source: 每源最多取最近 N 条

    Returns:
        FetchResult（articles + 统计）
    """
    enabled = [s for s in sources if s.enabled]
    if not enabled:
        return FetchResult()

    result = FetchResult()
    lock = threading.Lock()

    def _worker(src: SourceSpec) -> None:
        articles, err = _fetch_one(src, per_source_timeout, max_items_per_source)
        with lock:
            if err:
                result.fail_count += 1
                result.errors[src.name] = err
                logger.info("rss_fetch fail: %s: %s", src.name, err)
            else:
                result.ok_count += 1
                result.articles.extend(articles)
                result.per_source_count[src.name] = len(articles)
                logger.info("rss_fetch ok: %s items=%d", src.name, len(articles))

    threads = [threading.Thread(target=_worker, args=(s,), daemon=True) for s in enabled]
    for t in threads:
        t.start()

    deadline = time.time() + total_timeout
    for t in threads:
        remaining = max(0.0, deadline - time.time())
        t.join(timeout=remaining)
        if t.is_alive():
            logger.warning("rss_fetch total timeout hit; joining remaining threads was skipped")
            break

    # 按发布时间降序（没有发布时间的放末尾）
    def _sort_key(a: Article) -> float:
        if not a.published:
            return 0.0
        try:
            return parsedate_to_datetime(a.published).timestamp()
        except Exception:
            return 0.0

    result.articles.sort(key=_sort_key, reverse=True)
    return result


# ─── CLI helper：直接跑测试 ────────────────────────────
if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser()
    parser.add_argument("--url", action="append", required=True,
                        help="源 URL，可多个 --url 叠加")
    parser.add_argument("--per-source-timeout", type=float, default=5.0)
    parser.add_argument("--total-timeout", type=float, default=30.0)
    parser.add_argument("--max-items", type=int, default=3)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    sources = [
        SourceSpec(name=f"src{i+1}", url=url, category="test")
        for i, url in enumerate(args.url)
    ]
    result = fetch_sources(
        sources,
        per_source_timeout=args.per_source_timeout,
        total_timeout=args.total_timeout,
        max_items_per_source=args.max_items,
    )
    print(json.dumps({
        "ok_count": result.ok_count,
        "fail_count": result.fail_count,
        "errors": result.errors,
        "per_source_count": result.per_source_count,
        "articles": [
            {"src": a.source_name, "title": a.title[:80], "link": a.link[:80],
             "published": a.published}
            for a in result.articles
        ],
    }, ensure_ascii=False, indent=2))
