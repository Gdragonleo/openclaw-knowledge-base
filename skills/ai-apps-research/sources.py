"""ai-apps-research 源 — 聚焦 AI 应用落地方向、新工具、案例."""
from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path.home() / ".openclaw" / "workspace" / "scripts" / "cron"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from rss_fetcher import SourceSpec  # noqa: E402

SOURCES: list[SourceSpec] = [
    # 国内 AI 新闻与实践
    SourceSpec(name="量子位", url="https://www.qbitai.com/feed",
               category="ai-cn", enabled=True),
    SourceSpec(name="36氪", url="https://36kr.com/feed",
               category="ai-cn", enabled=True),     # 和综合新闻重叠，但 36 氪 AI 创业案例密集

    # 海外 AI 工具 / 案例
    SourceSpec(name="Hugging Face Blog", url="https://huggingface.co/blog/feed.xml",
               category="ai-tools", enabled=True),
    SourceSpec(name="The Decoder", url="https://the-decoder.com/feed/",
               category="ai-global", enabled=True),
    SourceSpec(name="SyncedReview", url="https://syncedreview.com/feed/",
               category="ai-global", enabled=True),
    SourceSpec(name="Google Research Blog", url="https://research.google/blog/rss/",
               category="ai-tools", enabled=True),

    # 工程 / 实践
    SourceSpec(name="InfoQ 中国 AI", url="https://www.infoq.cn/feed.xml",
               category="ai-engineering", enabled=False),   # 451
    SourceSpec(name="Roboflow Blog", url="https://blog.roboflow.com/rss/",
               category="ai-tools", enabled=True),   # CV + 标注工具案例

    # ─── 扩展源 ─────────────────────────────
    SourceSpec(name="Anthropic News", url="https://www.anthropic.com/news",
               category="ai-global", enabled=False),   # 无 RSS
    SourceSpec(name="OpenAI Blog", url="https://openai.com/blog/rss.xml",
               category="ai-global", enabled=False),   # 403
]

CATEGORY_LABELS: dict[str, str] = {
    "ai-cn": "🇨🇳 国内 AI 落地",
    "ai-global": "🌍 海外 AI 动态",
    "ai-tools": "🛠 新工具 / 研究",
    "ai-engineering": "⚙️ 工程实践",
}

CATEGORY_ORDER: list[str] = ["ai-cn", "ai-tools", "ai-global", "ai-engineering"]


# 周一到周日轮换的聚焦方向（让 LLM prompt 注入）
WEEKDAY_FOCUS: dict[int, str] = {
    0: "本周 AI 落地案例回顾（周一回看上周发生了什么可落地的 AI 应用）",
    1: "最近国内 AI 应用落地案例（大厂 + 创业公司）",
    2: "国内外新 AI 开发工具 / 框架（可复现、可测试）",
    3: "AI 创业公司融资与产品动向（Agent / RAG / 多模态）",
    4: "行业趋势与权威分析（Gartner / 红杉 / a16z 等）",
    5: "小公司 / 开源项目的突破（可直接 star 或借鉴）",
    6: "本周 AI 应用方向复盘 + 可落地思路清单",
}
# 注意 Python datetime.weekday(): 周一=0, 周日=6
