"""
rag-preflight skill 实现 — 仅 OpenClaw 使用。

降级原则: 任何远端异常（网络 / HTTP / JSON / shape / 字段）都静默跳过，
不阻塞 OpenClaw 主流程。本地编程错误（build_query 等）不吞。

Usage:
    from preflight import preflight
    injection = preflight(task_title, task_description, project_name)
    final_spec = injection + original_spec if injection else original_spec
"""
from __future__ import annotations

import logging
import os
import time
from collections.abc import Mapping

# 注意: httpx 在 preflight() 里延迟导入，避免 OpenClaw 运行环境未装 httpx
# 时本 skill 加载即崩溃（违反"降级不阻塞"硬约束）。

logger = logging.getLogger(__name__)

RAG_BASE_URL = os.environ.get("RAG_BASE_URL", "http://118.89.197.244:8000")

# 轻量快速失败冷却（本进程 best effort，跨进程无效）
_last_fail_ts: float = 0.0
_FAIL_COOLDOWN_SEC: int = 30
_MAX_HITS: int = 3
_SCORE_THRESHOLD: float = 0.4  # 基于真实 MultiAgents 平台数据分布校准（2026-04-20）

# 触发白名单 / 黑名单
_TRIGGER_WORDS = (
    # 中文
    "实现", "开发", "写代码", "编写", "重构", "修 bug", "修bug",
    "加功能", "新接口", "新模块",
    "研究", "调研", "分析", "方案", "设计", "梳理", "对比",
    # 英文
    "implement", "develop", "build", "write", "refactor", "fix",
    "add feature", "research", "investigate", "analyze", "design",
)
_EXCLUDE_WORDS = (
    "删除", "回滚", "撤销", "停掉", "关闭",
    "kill", "stop", "cancel", "rollback",
)


def should_trigger(task_title: str, task_description: str) -> bool:
    """判断是否应该触发 RAG 预检."""
    text = f"{task_title} {task_description}".lower()
    # 黑名单优先
    for w in _EXCLUDE_WORDS:
        if w.lower() in text:
            return False
    # 白名单
    for w in _TRIGGER_WORDS:
        if w.lower() in text:
            return True
    return False


def _safe_score(v: object) -> float:
    """远端 score 可能是 None / str / list / dict，统一归一化为 float，异常返回 0."""
    try:
        s = float(v)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0.0
    if s != s or s in (float("inf"), float("-inf")):  # NaN / inf 防护
        return 0.0
    return s


def build_query(
    task_title: str,
    task_description: str,
    project: str | None,
) -> str:
    """纯本地逻辑，编程错误应直接暴露，不要包 try."""
    parts: list[str] = []
    if project:
        parts.append(project)
    parts.append(task_title[:60])
    if task_description:
        parts.append(task_description[:120])
    return " ".join(parts).strip()


def render_injection(hits: list[dict]) -> str:
    """字段缺失时给默认值，尽量不抛异常地拼装注入段."""
    lines: list[str] = [
        f"## 📚 相关历史知识（RAG 预检自动注入，{len(hits)} 条，来自 MultiAgents 平台）",
        "",
        "> 在开始前，参考以下相关的历史产出。**不要盲目复用**，要判断是否适用当前任务。",
        "",
    ]
    for i, h in enumerate(hits, 1):
        title = str(h.get("title") or "未命名产出")
        agent = str(h.get("agent_name") or "-")
        project = str(h.get("project_name") or "-")
        tags = h.get("tags") or []
        tags_str = (
            ", ".join(str(t) for t in tags)
            if isinstance(tags, list) else "-"
        )
        preview = str(h.get("content_preview") or "")[:200]
        oid = h.get("output_id") or h.get("id") or "?"
        score = h.get("_score_normalized", 0.0)
        lines.extend([
            f"{i}. **[{title}]** (相关度 {score:.2f} · @{agent} · {project})",
            f"   - 标签: {tags_str}",
            f"   - 摘要: {preview}",
            f"   - 详情: {RAG_BASE_URL}/outputs/{oid}",
            "",
        ])
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def preflight(
    task_title: str,
    task_description: str = "",
    project: str | None = None,
) -> str:
    """
    任务派发前 RAG 预检。返回注入段（含换行），异常/无命中/冷却中/不触发 返回空串。

    Args:
        task_title: 任务标题
        task_description: 任务详细描述（可选）
        project: 项目名（如果 OpenClaw 能推断出来）

    Returns:
        注入段 markdown 文本，或空串。

    Note:
        降级原则: 任何远端异常都静默跳过，不阻塞 OpenClaw 主流程。
        冷却说明: `_last_fail_ts` 是模块级全局变量，只在同一 Python 进程内有效。
        若 OpenClaw 每次 fork 子进程执行 skill，冷却会失效。当前是 best effort。
    """
    global _last_fail_ts

    # 触发判断
    if not should_trigger(task_title, task_description):
        return ""

    now = time.time()

    # 冷却期跳过
    if _last_fail_ts and (now - _last_fail_ts) < _FAIL_COOLDOWN_SEC:
        logger.info(
            "RAG preflight skipped: in cooldown (%.0fs left)",
            _FAIL_COOLDOWN_SEC - (now - _last_fail_ts),
        )
        return ""

    # 本地逻辑，无 try
    query = build_query(task_title, task_description, project)
    if not query:
        return ""

    # httpx 延迟导入：环境未装则静默跳过，符合"降级不阻塞"硬约束
    try:
        import httpx
    except ImportError as e:
        _last_fail_ts = now
        logger.warning("RAG preflight skipped: httpx unavailable: %s", e)
        return ""

    # try 1: 只包远端调用 + JSON 解析
    try:
        resp = httpx.post(
            f"{RAG_BASE_URL}/api/knowledge/search",
            json={"query": query, "project": project, "top_k": _MAX_HITS},
            timeout=5.0,
        )
        resp.raise_for_status()
        payload = resp.json()
    except Exception as e:
        _last_fail_ts = now
        logger.warning(
            "RAG preflight skipped: %s: %s", type(e).__name__, e
        )
        return ""

    # shape 校验
    if not isinstance(payload, list):
        _last_fail_ts = now
        preview = ""
        if isinstance(payload, Mapping):
            preview = f" keys={list(payload.keys())[:5]}"
        logger.warning(
            "RAG preflight skipped: unexpected response shape=%s%s",
            type(payload).__name__, preview,
        )
        return ""

    # 过滤 + 归一化 + 客户端兜底 cap
    valid: list[dict] = []
    for h in payload:
        if not isinstance(h, Mapping):
            continue
        score = _safe_score(h.get("score"))
        if score < _SCORE_THRESHOLD:
            continue
        enriched = dict(h)
        enriched["_score_normalized"] = score
        valid.append(enriched)
    valid = valid[:_MAX_HITS]

    if not valid:
        logger.info(
            "RAG preflight: no hits above %.2f threshold (raw=%d)",
            _SCORE_THRESHOLD, len(payload),
        )
        return ""

    # try 2: render 独立降级
    try:
        result = render_injection(valid)
    except Exception:
        _last_fail_ts = time.time()
        logger.exception("RAG preflight skipped: render failed")
        return ""

    logger.info("RAG preflight: injecting %d hits", len(valid))
    return result


__all__ = [
    "preflight",
    "should_trigger",
    "build_query",
    "render_injection",
    "RAG_BASE_URL",
]
