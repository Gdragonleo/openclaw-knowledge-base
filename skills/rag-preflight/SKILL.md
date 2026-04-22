---
name: rag-preflight
description: |
  OpenClaw 派发编码 / 研究 / 方案类任务**前**，自动查询 MultiAgents 知识库平台，
  把 top-3 相关历史产出注入任务 spec，供下游编码 agent 参考，避免重复造轮子。

  触发词（匹配任一即尝试触发）:
  实现、开发、写代码、编写、重构、修 bug、加功能、新接口、新模块、
  研究、调研、分析、方案、设计、梳理、对比、
  implement, develop, build, write, refactor, fix, add feature,
  research, investigate, analyze, design

  排除词（即使匹配上面触发词也**跳过**）:
  删除、回滚、撤销、停掉、关闭、kill, stop, cancel, rollback

  降级原则: 平台不可达 / 响应异常 / 无高相关结果 → **静默跳过**，不阻塞任务派发。
  30 秒本进程失败冷却（best effort，OpenClaw 若 fork 子进程执行则失效）。
user_invocable: false
---

# 📚 RAG Preflight Skill（仅 OpenClaw 用）

## 用途

在 OpenClaw（Zoe）把任务派发给下游编码 agent（Claude / GPT-Codex / Kimi 等）之前，
先查一下 MultiAgents 平台的 `/api/knowledge/search`，把 top-3 最相关的历史产出
精炼成一段"📚 相关历史知识"注入到任务 spec 的**开头**。

## 何时**不触发**

下列情况直接 return 空串，走正常派发流程：

1. 任务描述匹配**排除词**（删除 / 回滚 / 停掉 / kill / stop / cancel 等）
2. 任务描述**不匹配**任何触发词（闲聊、状态查询、纯文档查询）
3. 在 30 秒失败冷却期内（上次调用异常）
4. 平台 `/api/knowledge/search` 返回异常（网络 / HTTP / JSON / shape）
5. 所有返回结果 score < `score_threshold`（当前 0.4）（ChromaDB cosine 低相关度阈值）
6. `render_injection` 内部异常（远端返回字段脏导致格式化崩）

## 触发 → 执行流程

```
接到任务 → 判断触发词 → build_query(项目名 + 标题[:60] + 描述[:120])
  → POST /api/knowledge/search  (top_k=3, timeout=5s)
  → shape 校验 + 过滤非 Mapping 条目
  → score >= `score_threshold`（当前 0.4）过滤
  → valid[:3] 兜底
  → render_injection(useful) → "📚 相关历史知识" 段
  → 注入到任务 spec 开头
  → 派发给下游编码 agent
```

## 注入段格式

```
## 📚 相关历史知识（RAG 预检自动注入，N 条，来自 MultiAgents 平台）

> 在开始前，参考以下相关的历史产出。**不要盲目复用**，要判断是否适用当前任务。

1. **[标题]** (相关度 0.72 · @agent-name · project-name)
   - 标签: tag-a, tag-b
   - 摘要: 前 200 字...
   - 详情: http://118.89.197.244:8000/outputs/42

2. ...

---
<原任务 spec>
```

## 平台端点

- 主地址: `http://118.89.197.244:8000/api/knowledge/search`
- 覆盖: 环境变量 `RAG_BASE_URL`（本地开发设 `http://localhost:8000`）
- 请求方法: **POST**（JSON body）
- Body: `{"query": str, "project": str|None, "top_k": 3}`
- 返回: `list[dict]`，每条含 `output_id / title / content_preview / agent_name / project_name / tags / score / created_at`

## 配置（硬编码，≤5 用户不做配置化）

| 项 | 值 | 说明 |
|---|---|---|
| `top_k` | 3 | 避免注入过多挤压 agent token 预算 |
| `score_threshold` | 0.4 | ChromaDB cosine；2026-04-20 按真实数据校准（相关招标/安全条目 score ~0.41） |
| `timeout` | 5s | 单一总超时 |
| `cooldown` | 30s | 本进程失败冷却（best effort） |
| `max_hits` | 3 | 客户端兜底，防服务端不遵守 top_k |

## 完整 Python 实现

把 `preflight.py` 放在本 skill 目录下，OpenClaw 接到任务时:

```python
from preflight import preflight

injection = preflight(task_title, task_description, project_name)
final_task_spec = injection + original_spec if injection else original_spec
```

见 `./preflight.py`。

## 降级语义声明

`try` 块边界**必须严格**:
- **try 1**: 只包 `httpx.post + raise_for_status + .json()`
- **try 2**: 只包 `render_injection(useful)`
- `build_query()` 是纯本地逻辑，**不要**包 try —— 编程错误应直接暴露

扩大 try 作用域会吞掉编程错误（`NameError` / `TypeError`），让 bug 静默失效。

## 日志级别

- 远端请求异常 / shape 异常: `logger.warning`（首次可见）
- render 崩: `logger.exception`（带 traceback）
- 冷却期跳过 / 无命中 / 注入成功: `logger.info`（低噪音）

## 验证 checklist

落地后手动验证 4 + 1 场景:

| # | 场景 | 预期 |
|---|---|---|
| 1 | 发"帮 X 项目实现 Y 功能" | 触发 → 查询 → 注入相关知识段 |
| 2 | 发"停掉后端服务" | 不触发（排除词） |
| 3 | 发"今天天气怎么样" | 不触发（无触发词） |
| 4 | 临时停掉平台，再发触发类任务 | 触发但静默跳过，走 cooldown，任务正常派发 |
| 5 | 发 3-5 个真实任务，观察 `raw_hits` 和 `valid_hits` 日志 | 根据 score 分布决定是否调 `score_threshold`（0.5 → 0.4 或 → 0.6） |

## 注意事项

1. **不要盲目复用**注入的历史知识 —— agent 必须判断是否适用当前任务。skill 在注入文案里已明示此点。
2. **冷却是 best effort**：如果 OpenClaw 每次 fork 子进程执行 skill，`_last_fail_ts` 全局变量在新进程中是初值，冷却失效。若后续发现批量派发时都打满 5s 超时，再考虑用文件系统状态 / Redis。
3. **score_threshold 曾以 0.5 起步，2026-04-20 按真实数据校准为 0.4**：上线 2 周后，人工看一眼 OpenClaw 日志里的 `raw=X valid=Y` 分布，如果有效注入率低，再降到 0.35；如果 useful 条目偏弱（agent 反馈"注入的没用"），升到 0.5。
4. **不改平台端 API**：skill 只调用现有 `POST /api/knowledge/search`，不新增 endpoint。
5. **详情链接**从 `RAG_BASE_URL` 派生，不硬编码 IP，方便本地开发。
