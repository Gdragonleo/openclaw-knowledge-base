"""article_fetcher.py — 用 OpenClaw 的 scrapling skill 抓原文正文.

对每个源域名使用已知的 CSS selector 抽正文；未知域名走通用 body 文本 + 常见
selector 兜底.

依赖: scrapling[all]（OpenClaw scrapling skill 的底层），pip install 'scrapling[all]'

Usage:
    from article_fetcher import fetch_article_text
    text = fetch_article_text("https://36kr.com/p/xxx", timeout=5)
"""
from __future__ import annotations

import logging
import re
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


# 各域名的已知正文选择器（经验抓取的优选）
_DOMAIN_SELECTORS: dict[str, list[str]] = {
    "36kr.com": [".article-content", ".articleDetailContent", "article"],
    "qbitai.com": [".article-content", ".entry-content", "article"],
    "huggingface.co": [".blog-content", "article", "main"],
    "the-decoder.com": [".entry-content", "article", "main"],
    "syncedreview.com": [".entry-content", "article"],
    "research.google": [".article-body", "article", "main"],
    "blog.roboflow.com": ["article", ".post-content", "main"],
}

# 通用后备（任何域名都试一遍）
_FALLBACK_SELECTORS = [
    "article",
    ".article-content",
    ".entry-content",
    ".post-content",
    ".post-body",
    ".article-body",
    "main",
    "[role=main]",
]


def _clean_text(text: str) -> str:
    """去掉多余空白 + 常见噪声字符."""
    if not text:
        return ""
    # \xa0 全角空格转普通空格
    text = text.replace("\xa0", " ").replace("\u3000", " ")
    # 多个换行 → 两个
    text = re.sub(r"\n{3,}", "\n\n", text)
    # 多个空格 → 一个
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def _host_of(url: str) -> str:
    try:
        host = urlparse(url).hostname or ""
        # 剥 www.
        if host.startswith("www."):
            host = host[4:]
        return host
    except Exception:
        return ""


def fetch_article_text(
    url: str,
    *,
    timeout: float = 5.0,
    min_length: int = 200,
) -> tuple[str, str]:
    """抓原文并返回 (clean_text, source)；失败返回 ("", error).

    source ∈ {"domain-selector", "fallback-selector", "body-text"}
    """
    try:
        from scrapling.fetchers import Fetcher
    except ImportError:
        return "", "scrapling-not-installed"

    host = _host_of(url)

    try:
        page = Fetcher.get(url, stealthy_headers=True, timeout=timeout)
    except Exception as e:
        return "", f"fetch-error: {type(e).__name__}"

    if page.status != 200:
        return "", f"http-{page.status}"

    # 1. 域名专用 selector
    domain_selectors = _DOMAIN_SELECTORS.get(host, [])
    for sel in domain_selectors:
        try:
            elems = page.css(sel)
            if elems:
                first = elems[0] if hasattr(elems, "__getitem__") else elems
                text = _clean_text(first.get_all_text())
                if len(text) >= min_length:
                    return text, "domain-selector"
        except Exception:
            continue

    # 2. 通用 fallback selector
    for sel in _FALLBACK_SELECTORS:
        try:
            elems = page.css(sel)
            if elems:
                first = elems[0] if hasattr(elems, "__getitem__") else elems
                text = _clean_text(first.get_all_text())
                if len(text) >= min_length:
                    return text, "fallback-selector"
        except Exception:
            continue

    # 3. 最后兜底：全页面文本去导航栏（取中段）
    try:
        full = _clean_text(page.get_all_text())
        if len(full) >= min_length:
            # 很多页面前 1/5 是导航/页头，直接扔掉
            start = len(full) // 5
            return full[start:start + 4000], "body-text"
    except Exception as e:
        return "", f"body-text-error: {type(e).__name__}"

    return "", "content-too-short"


# CLI for manual testing
if __name__ == "__main__":
    import argparse
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--timeout", type=float, default=5.0)
    args = ap.parse_args()
    text, source = fetch_article_text(args.url, timeout=args.timeout)
    print(f"=== source={source} len={len(text)} ===")
    print(text[:2000])
