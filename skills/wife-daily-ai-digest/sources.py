"""wife-daily-ai-digest 的源白名单.

v1 只启用 6 个经 Claude 手测验证过的源；扩展源 enabled=False，后续逐个启用.
"""
from __future__ import annotations

import sys
from pathlib import Path

# 让本文件能直接从 skill 目录 import ~/.openclaw/workspace/scripts/cron/rss_fetcher
_SCRIPTS = Path.home() / ".openclaw" / "workspace" / "scripts" / "cron"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from rss_fetcher import SourceSpec  # noqa: E402


# ─── v1 白名单（enabled=True）─────────────────────────────
# 每源都经过手测：`python3 rss_fetcher.py --url <url>` 能返回 ≥ 1 条.

SOURCES: list[SourceSpec] = [
    # 国内 AI
    SourceSpec(name="量子位", url="https://www.qbitai.com/feed",
               category="ai-cn", enabled=True),
    SourceSpec(name="36氪", url="https://36kr.com/feed",
               category="ai-cn", enabled=True),

    # 海外 AI
    SourceSpec(name="Hugging Face Blog", url="https://huggingface.co/blog/feed.xml",
               category="ai-global", enabled=True),
    SourceSpec(name="The Decoder", url="https://the-decoder.com/feed/",
               category="ai-global", enabled=True),
    SourceSpec(name="SyncedReview", url="https://syncedreview.com/feed/",
               category="ai-global", enabled=True),    # 机器之心英文版
    SourceSpec(name="Google Research Blog", url="https://research.google/blog/rss/",
               category="ai-global", enabled=True),

    # 数据标注
    SourceSpec(name="Roboflow Blog", url="https://blog.roboflow.com/rss/",
               category="data-annotation", enabled=True),

    # ─── 扩展源（enabled=False，后续验证） ────────────
    # 数据标注：无公开 RSS，需特殊 HTML/API 抓取
    SourceSpec(name="Labelbox Blog", url="https://labelbox.com/blog",
               category="data-annotation", enabled=False),   # 无 RSS
    SourceSpec(name="Scale AI Blog", url="https://scale.com/blog",
               category="data-annotation", enabled=False),   # 无 RSS
    SourceSpec(name="Snorkel AI Blog", url="https://snorkel.ai/blog/",
               category="data-annotation", enabled=False),   # 无 RSS feed
    SourceSpec(name="Encord Blog", url="https://encord.com/blog/",
               category="data-annotation", enabled=False),   # 无 RSS feed
    # AI 官方：需特殊抓
    SourceSpec(name="机器之心", url="https://www.jiqizhixin.com/rss",
               category="ai-cn", enabled=False),    # RSS 格式错，换 SyncedReview
    SourceSpec(name="Anthropic News", url="https://www.anthropic.com/news",
               category="ai-global", enabled=False),   # 无 RSS
    SourceSpec(name="OpenAI Blog", url="https://openai.com/blog/rss.xml",
               category="ai-global", enabled=False),   # 403
    SourceSpec(name="InfoQ 中国 AI", url="https://www.infoq.cn/feed.xml",
               category="ai-cn", enabled=False),   # 451
]

CATEGORY_LABELS: dict[str, str] = {
    "ai-cn": "🇨🇳 国内 AI",
    "ai-global": "🌍 海外 AI",
    "data-annotation": "🛠 数据标注",
}
