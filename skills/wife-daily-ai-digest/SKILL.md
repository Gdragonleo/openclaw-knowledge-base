---
name: wife-daily-ai-digest
description: |
  每日 11:30 为小刘的老婆生成一份 AI 行业资讯 + 数据标注行业日报，
  POST 到 MultiAgents 平台（project=家庭日报, agent=family-digest-bot），
  失败时本地落盘到 ~/.openclaw/data/cron-fallback/

  不走飞书，不走 VPN 探活，直接对每源设 5s 超时；海外源不可达时静默
  跳过，不阻塞整个任务。

  触发方式：
  - 由 cron 任务 "每日AI资讯与数据标注日报" 11:30 自动触发
  - 或手动 /wife-digest
user_invocable: true
---

# 👩 老婆的每日 AI + 数据标注日报

## 产出目标

一份结构化 markdown，内容：
- 🇨🇳 国内 AI 行业动态（大厂、创业公司、融资、落地案例）
- 🌍 海外 AI 行业动态（前沿研究、新产品、争议/政策）
- 🛠 数据标注新工具/平台（国内外）
- 📏 数据标注质量标准/方法（学术和行业实践）

上传路径：`POST http://118.89.197.244:8000/api/outputs`
- `agent`: `family-digest-bot`
- `project`: `家庭日报`
- `title`: `AI+数据标注日报 YYYY-MM-DD`
- `content_type`: `markdown`
- `tags`: `["日报/AI", "日报/数据标注"]`

## 数据源（v1 白名单，6 个经验证源）

见 `./sources.py`。

| 源 | URL | 分类 | 需要 VPN |
|---|---|---|---|
| 量子位 | https://www.qbitai.com/feed | ai-cn | 否 |
| 机器之心 | https://www.jiqizhixin.com/rss | ai-cn | 否 |
| Hugging Face Blog | https://huggingface.co/blog/feed.xml | ai-global | 弱 VPN |
| The Decoder | https://the-decoder.com/feed/ | ai-global | 弱 VPN |
| Scale AI Blog | https://scale.com/blog/rss.xml | data-annotation | 弱 VPN |
| Labelbox Blog | https://labelbox.com/blog/rss/ | data-annotation | 弱 VPN |

**扩展源（`enabled=False`，后续再验证）**：36氪、InfoQ、Anthropic、OpenAI、Snorkel、Encord、爱数智慧。

## 执行流程

1. 加载源配置（`sources.py` 里 `enabled=True` 的）
2. 并行抓取 RSS（`rss_fetcher.py`，单源 5s 超时，总 120s）
3. 失败统计：记录每源失败原因
4. LLM 摘要：调 `compile_llm_*` 平台配置（GLM-4-flash），做分类 + 去重 + 中文摘要
   - 若 LLM 不可达：跳过摘要，直接用原始 title + summary 拼接
5. 生成 markdown（模板见下）
6. POST 到平台；失败则写 `~/.openclaw/data/cron-fallback/wife-daily-ai-digest/YYYY-MM-DD.md`

## 完整 Python 实现

见 `./runner.py`。

## Markdown 模板

```markdown
# AI + 数据标注日报 · YYYY-MM-DD

> 今日抓取 X 源（国内 N / 海外 M），成功 Y 源，共获得 Z 条内容。

## 🇨🇳 国内 AI

- **[标题](link)** · 量子位 · 20XX-XX-XX XX:XX
  > 摘要……

## 🌍 海外 AI

- **[Title](link)** · Hugging Face · YYYY-MM-DD
  > Summary……

## 🛠 数据标注新工具

- **[Title](link)** · Scale AI · YYYY-MM-DD
  > Summary……

## 📏 数据标注质量标准

- （若无新内容则空着或写 "今日暂无新进展"）

---
抓取时间: YYYY-MM-DD HH:MM  ·  源成功率: Y/X
失败源: 源1 (reason) · 源2 (reason)
```

## 降级策略

| 场景 | 行为 |
|---|---|
| 部分海外源抓不到（VPN 断） | 照常生成日报，头部标注 "Y/X 源成功"，失败列表附底部 |
| 所有源都失败 | 日报内容为空，但仍 POST 平台（let user see the failure）+ fallback 落盘 |
| LLM 不可达 | 跳过摘要，原始 title + summary 直接拼接 |
| 平台 POST 失败（网络/HTTP/JSON/5xx） | 落盘到 `~/.openclaw/data/cron-fallback/wife-daily-ai-digest/YYYY-MM-DD.md` |
| 所有异常（任何 Python exception） | 写 stderr 日志但不抛出；cron 任务 exit 0 |

## 冷启动 / 平台准备

首次运行前需在 MultiAgents 平台建项目（若未建会由 agent 创建但 project=None）：
```bash
curl -X POST http://118.89.197.244:8000/api/projects \
  -H 'Content-Type: application/json' \
  -d '{"name":"家庭日报","description":"给家人看的每日精选"}'
```

## 时间点说明

cron 设为 `30 11 * * *`（11:30 触发），抓取 + LLM 摘要通常 3-6 分钟，
老婆 12:00 午饭时打开 `http://118.89.197.244:8000/outputs?project=家庭日报`
就能看到当天的。
