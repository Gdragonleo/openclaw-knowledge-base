"""wife-daily-ai-digest v3 — 基于 digest_lib 的精简版.

旧版 runner.py 仍保留作为 backup，但不再 active.当前 jobs.json 走这个版本后，
其 import 跟 daily-news-briefing / ai-apps-research 一致.
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
from sources import SOURCES, CATEGORY_LABELS  # noqa: E402


CATEGORY_ORDER = ["ai-cn", "ai-global", "data-annotation"]


CONFIG = DigestConfig(
    skill_name="wife-daily-ai-digest",
    project_name="家庭日报",
    agent_name="family-digest-bot",
    title_prefix="AI+数据标注日报",
    tags=["日报/AI", "日报/数据标注"],
    category_labels=CATEGORY_LABELS,
    system_prompt_extra=(
        "你在写一份 AI + 数据标注行业日报给小刘的老婆，她是 AI 行业从业者，"
        "关心：AI 应用落地（尤其国内）+ 数据标注行业新工具 / 质量标准。"
    ),
)


logger = logging.getLogger("wife-daily-ai-digest")


if __name__ == "__main__":
    try:
        sys.exit(run_digest(SOURCES, CONFIG, CATEGORY_ORDER))
    except Exception:
        logger.exception("wife-daily-ai-digest crashed")
        sys.exit(0)
