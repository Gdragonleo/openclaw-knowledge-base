---
name: daily-news-briefing
description: |
  每日 09:00 自动生成综合新闻简报（国内 + 国际 + 全球科技 + 财经市场），
  POST 到 MultiAgents 平台 project=每日新闻简报.

  替代原 daily-news skill（长期 timeout），采用 wife-daily-ai-digest 同款架构：
  RSS 并行抓 → scrapling 抓原文 → GLM-4-flash 摘要 → 4 行卡片式 markdown.

  触发方式：
  - 由 cron 任务 "每日新闻简报" 09:00 自动触发
  - 或手动 python3 ~/.openclaw/workspace/skills/daily-news-briefing/runner.py
user_invocable: true
---

# 📰 每日新闻简报

## 产出目标

一份结构化 markdown，分 4 类：
- 🇨🇳 国内（36氪、少数派）
- 🌍 国际（BBC、The Guardian、NYT）
- 🔬 全球科技（TechCrunch、Ars Technica、Hacker News）
- 💰 财经市场（Bloomberg Markets）

上传路径：POST http://118.89.197.244:8000/api/outputs
- project: 每日新闻简报
- agent: news-briefing-bot
- title: 每日新闻简报 YYYY-MM-DD
- tags: [日报/新闻, 日报/综合]

## 和 wife-daily-ai-digest 的区别

| 维度 | wife-daily-ai-digest (11:30) | daily-news-briefing (09:00) |
|---|---|---|
| 聚焦 | AI 行业 + 数据标注 | 综合新闻 |
| 读者 | 小刘老婆（AI 行业从业者） | 小刘（想了解大环境） |
| 源 | 量子位 / HF / Roboflow 等 AI 源 | 36氪 / BBC / NYT 等综合源 |
| 分类 | ai-cn / ai-global / data-annotation | news-cn / world / tech-global / finance |

## 实现

调用公共 `digest_lib.run_digest()`，通过 `DigestConfig` 注入：
- skill_name / project_name / agent_name
- 分类映射
- system prompt 特色指令（"不偏 AI"）

核心逻辑都在 `~/.openclaw/workspace/scripts/cron/digest_lib.py`，和老婆日报共用.

## 验证

```bash
# 手动 dry-run（不上传）
python3 ~/.openclaw/workspace/skills/daily-news-briefing/runner.py --dry-run

# 不调 LLM（调试结构）
python3 ~/.openclaw/workspace/skills/daily-news-briefing/runner.py --no-llm --dry-run

# 真实上传
python3 ~/.openclaw/workspace/skills/daily-news-briefing/runner.py
```

## 平台准备

首次运行前建项目（若未建会由 agent 创建但 project=None）：
```bash
curl -X POST http://118.89.197.244:8000/api/projects \
  -H 'Content-Type: application/json' \
  -d '{"name":"每日新闻简报","description":"每日综合新闻（国内+国际+科技+财经）"}'
```
