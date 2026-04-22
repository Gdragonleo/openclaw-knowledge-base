"""AI 应用落地方向日报 runner — 22:00 每日触发.

替代原 OpenClaw "每日科研调研" (research skill + feishu message)，这种方式
连续失败 22+ 次（ENOTFOUND open.feishu.cn —— VPN 没开时 DNS 解析不到飞书）.

新方案采用 wife-daily-ai-digest 同款架构：RSS 抓 AI 源 → 抓原文 → GLM-4-flash
摘要（带"AI 应用落地"视角 prompt + 当日轮换子方向）→ POST 到平台
project=AI-Apps-Research.不走飞书.
"""
from __future__ import annotations

import logging
import sys
from datetime import datetime
from pathlib import Path

_SCRIPTS = Path.home() / ".openclaw" / "workspace" / "scripts" / "cron"
_SKILL = Path(__file__).resolve().parent
for p in (_SCRIPTS, _SKILL):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from digest_lib import DigestConfig, run_digest  # noqa: E402
from sources import SOURCES, CATEGORY_LABELS, CATEGORY_ORDER, WEEKDAY_FOCUS  # noqa: E402


logger = logging.getLogger("ai-apps-research")


def _build_prompt_extra() -> str:
    weekday = datetime.now().weekday()
    focus = WEEKDAY_FOCUS.get(weekday, "AI 应用落地方向")
    return (
        "你正在写一份 AI 应用落地方向日报给小刘，他是开发者 + 小团队运营者，"
        "想知道哪些 AI 应用可以在他的工作或业务里落地。写摘要时请额外关注：\n"
        f"- 今日聚焦方向（周{'一二三四五六日'[weekday]}）：{focus}\n"
        "- 每条都试着回答『这东西能用来做什么』、『门槛高不高』、『和已有产品的区别是什么』。\n"
        "- 优先选真实案例、融资、开源工具、可复现方法；少选空谈趋势文章。\n"
        "- 对国内公司要写清楚是哪家、产品叫什么，避免泛化为『某 AI 公司』。"
    )


CONFIG = DigestConfig(
    skill_name="ai-apps-research",
    project_name="AI-Apps-Research",
    agent_name="ai-research-bot",
    title_prefix="AI 应用落地方向日报",
    tags=["研究/AI应用", "日报/科研调研"],
    category_labels=CATEGORY_LABELS,
    system_prompt_extra=_build_prompt_extra(),
)


if __name__ == "__main__":
    try:
        sys.exit(run_digest(SOURCES, CONFIG, CATEGORY_ORDER))
    except Exception:
        logger.exception("ai-apps-research crashed")
        sys.exit(0)
