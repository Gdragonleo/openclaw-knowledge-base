---
name: ai-apps-research
description: |
  每日 22:00 生成 AI 应用落地方向日报，POST 到 MultiAgents 平台
  project=AI-Apps-Research.23:00 工作汇报会自动读取今日结果并引用.

  替代原 "每日科研调研" cron 任务（基于 research skill + feishu message，
  VPN 断时 ENOTFOUND open.feishu.cn 连错 22 次）.

  采用 wife-daily-ai-digest 同款架构，差异点：
  - 源偏 AI 工具 + 案例（量子位、HF、SyncedReview、Google Research、Roboflow）
  - prompt 带周一到周日子方向轮换（落地案例 / 新工具 / 融资 / 趋势等）
  - prompt 强调"能用来做什么 / 门槛高不高 / 和已有产品的区别"

  触发方式：
  - cron "每日科研调研" 22:00 自动触发
  - 或手动 python3 ~/.openclaw/workspace/skills/ai-apps-research/runner.py
user_invocable: true
---

# 🔬 AI 应用落地方向日报

## 周一到周日聚焦轮换

| 星期 | 聚焦方向 |
|---|---|
| 周一 | 最近国内 AI 应用落地案例（大厂 + 创业公司）|
| 周二 | 国内外新 AI 开发工具 / 框架 |
| 周三 | AI 创业公司融资 + 产品动向（Agent / RAG / 多模态）|
| 周四 | 行业趋势与权威分析（Gartner / 红杉 / a16z）|
| 周五 | 小公司 / 开源项目突破 |
| 周六 | 本周 AI 应用方向复盘 + 可落地思路 |
| 周日 | 下周值得关注的 AI 落地案例 |

轮换通过 `sources.py` 的 `WEEKDAY_FOCUS` 字典注入到 LLM system prompt.

## 分类

- 🇨🇳 国内 AI 落地
- 🌍 海外 AI 动态
- 🛠 新工具 / 研究
- ⚙️ 工程实践

## 与每日新闻简报（09:00）+ 老婆日报（11:30）的差异

| 维度 | 09:00 新闻简报 | 11:30 老婆日报 | 22:00 AI 研究 |
|---|---|---|---|
| 聚焦 | 综合（国内/国际/科技/财经）| AI + 数据标注 | AI 应用落地方向 |
| 读者 | 小刘 | 小刘老婆 | 小刘（做开发决策）|
| 摘要视角 | 客观陈述 | 行业从业者关心 | "我能用来做什么" |

## 验证

```bash
# dry-run 不上传
python3 ~/.openclaw/workspace/skills/ai-apps-research/runner.py --dry-run

# 实际上传
python3 ~/.openclaw/workspace/skills/ai-apps-research/runner.py
```

## 23:00 工作汇报读取路径

工作汇报 payload 已经配置为：
```
curl -s "http://118.89.197.244:8000/api/outputs?project=AI-Apps-Research&limit=5"
# 然后按 title 日期字符串匹配今日条目
```

本 skill 上传的 title 格式是 `AI 应用落地方向日报 YYYY-MM-DD`，工作汇报能匹配到.
