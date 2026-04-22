"""每日新闻简报 runner — 09:00 每日触发.

替代原 OpenClaw daily-news skill（180s timeout 长期失败）.
采用 wife-daily-ai-digest 同款架构：RSS 抓 → scrapling 抓原文 → GLM-4-flash 摘要 → POST 平台.
"""
from __future__ import annotations

import logging
import sys
from pathlib import Path

_SCRIPTS = Path.home() / ".openclaw" / "workspace" / "scripts" / "cron"
_SKILL = Path(__file__).resolve().parent
for p in (_SCRIPTS, _SKILL):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from digest_lib import DigestConfig, run_digest  # noqa: E402
from sources import SOURCES, CATEGORY_LABELS, CATEGORY_ORDER  # noqa: E402


CONFIG = DigestConfig(
    skill_name="daily-news-briefing",
    project_name="每日新闻简报",
    agent_name="news-briefing-bot",
    title_prefix="每日新闻简报",
    tags=["日报/新闻", "日报/综合"],
    category_labels=CATEGORY_LABELS,
    system_prompt_extra=(
        "你正在写一份每日综合新闻简报，给关心国内外大事、财经市场和科技动态的"
        "小刘。不要偏 AI（AI 已经有别的专门日报）。要真实、有信息密度、覆盖"
        "政治/经济/科技/社会多个面向。"
    ),
)


logger = logging.getLogger("daily-news-briefing")


if __name__ == "__main__":
    try:
        sys.exit(run_digest(SOURCES, CONFIG, CATEGORY_ORDER))
    except Exception:
        logger.exception("daily-news-briefing crashed")
        sys.exit(0)
