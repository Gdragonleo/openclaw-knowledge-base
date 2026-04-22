"""daily-news-briefing 源白名单（已手测全部可达）."""
from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path.home() / ".openclaw" / "workspace" / "scripts" / "cron"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from rss_fetcher import SourceSpec  # noqa: E402

SOURCES: list[SourceSpec] = [
    # 国内综合 / 科技商业
    SourceSpec(name="36氪", url="https://36kr.com/feed",
               category="news-cn", enabled=True),
    SourceSpec(name="少数派", url="https://sspai.com/feed",
               category="news-cn", enabled=True),

    # 国际时事
    SourceSpec(name="BBC World", url="https://feeds.bbci.co.uk/news/world/rss.xml",
               category="world", enabled=True),
    SourceSpec(name="The Guardian World", url="https://www.theguardian.com/world/rss",
               category="world", enabled=True),
    SourceSpec(name="NYT World", url="https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
               category="world", enabled=True),

    # 全球科技
    SourceSpec(name="TechCrunch", url="https://techcrunch.com/feed/",
               category="tech-global", enabled=True),
    SourceSpec(name="Ars Technica", url="https://feeds.arstechnica.com/arstechnica/index",
               category="tech-global", enabled=True),
    SourceSpec(name="Hacker News", url="https://feeds.feedburner.com/ycombinator",
               category="tech-global", enabled=True),

    # 财经市场
    SourceSpec(name="Bloomberg Markets", url="https://feeds.bloomberg.com/markets/news.rss",
               category="finance", enabled=True),

    # ─── 扩展源（待验证） ─────────────────────────────
    SourceSpec(name="华尔街见闻", url="https://wallstreetcn.com/rss.xml",
               category="finance", enabled=False),   # 非标准 RSS
    SourceSpec(name="财联社", url="https://www.cls.cn/rss",
               category="finance", enabled=False),   # 418 拦截
    SourceSpec(name="虎嗅", url="https://www.huxiu.com/rss/0.xml",
               category="news-cn", enabled=False),   # 网络错误
    SourceSpec(name="Reuters Top News", url="https://feeds.reuters.com/reuters/topNews",
               category="world", enabled=False),   # 停止服务
]

CATEGORY_LABELS: dict[str, str] = {
    "news-cn": "🇨🇳 国内",
    "world": "🌍 国际",
    "tech-global": "🔬 全球科技",
    "finance": "💰 财经市场",
}

CATEGORY_ORDER: list[str] = ["news-cn", "world", "tech-global", "finance"]
