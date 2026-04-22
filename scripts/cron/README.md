# OpenClaw 每日 Digest 系统

自动抓 RSS → 摘要 → 上传 MultiAgents 平台的共享架构，支持多个 skill 复用。

## 组件

```
~/.openclaw/workspace/
├── scripts/cron/
│   ├── rss_fetcher.py         # 并行 RSS 抓取器（5s 单源 / 120s 总）
│   ├── article_fetcher.py     # 基于 Scrapling 的原文正文抽取（域名专用 CSS 选择器 + 兜底）
│   ├── digest_lib.py          # 共享流水线：fetch → enrich → LLM → render → push
│   └── sync_to_multiagents.py # 其他 cron：扫 memory/知识库 目录同步到平台
│
└── skills/
    ├── wife-daily-ai-digest/         # 11:30 老婆日报（AI + 数据标注）
    ├── daily-news-briefing/          # 09:00 新闻简报（国内/国际/科技/财经）
    └── ai-apps-research/             # 22:00 AI 应用落地方向调研
```

## 流水线

`digest_lib.run_digest()` 执行 5 步：

1. **RSS 抓取** — `rss_fetcher.fetch_sources()` 并行调多源，异常不崩返回部分结果
2. **原文增强** — RSS summary < 400 字时用 `article_fetcher` 抓原文正文（Scrapling + 域名 selector）
3. **LLM 摘要** — 分批调智谱 GLM-4-flash，每条生成 `simplified_title + summary(180字+) + importance`
4. **Markdown 渲染** — 顶部 🔥 今日看点 3 条，分类卡片式，每条 4 行（标题/摘要/查看原文按钮/源日期）
5. **平台上传** — POST `/api/outputs`，失败时落盘 `~/.openclaw/data/cron-fallback/<skill>/YYYY-MM-DD.md`

## 3 个 skill 的配置差异

| 配置 | wife-daily-ai-digest | daily-news-briefing | ai-apps-research |
|---|---|---|---|
| 触发时间 | 11:30 | 09:00 | 22:00 |
| 读者 | 小刘老婆（AI 从业者） | 小刘（综合） | 小刘（开发决策） |
| 聚焦 | AI 落地 + 数据标注 | 国内/国际/科技/财经 | AI 应用落地方向 |
| 分类 | ai-cn / ai-global / data-annotation | news-cn / world / tech-global / finance | ai-cn / ai-tools / ai-global / ai-engineering |
| 源数 | 7 | 9 | 6 |
| prompt 特色 | "老婆关心 AI + 标注" | "不偏 AI，综合新闻" | "能用来做什么 + 门槛 + 差异" + 周一到周日轮换 |
| 平台 project | 家庭日报 | 每日新闻简报 | AI-Apps-Research |

## 新增一个 digest skill 的 5 步

例如想加一个"每周学术论文简报"。

1. **建目录** `~/.openclaw/workspace/skills/weekly-paper-digest/`
2. **写 `sources.py`**：
   ```python
   from rss_fetcher import SourceSpec
   SOURCES = [
       SourceSpec(name="arXiv cs.CL", url="...", category="arxiv-ai", enabled=True),
       # ...
   ]
   CATEGORY_LABELS = {"arxiv-ai": "📄 AI 论文"}
   CATEGORY_ORDER = ["arxiv-ai"]
   ```
3. **写 `runner.py`** (20 行)：
   ```python
   from digest_lib import DigestConfig, run_digest
   from sources import SOURCES, CATEGORY_LABELS, CATEGORY_ORDER

   CONFIG = DigestConfig(
       skill_name="weekly-paper-digest",
       project_name="每周论文简报",
       agent_name="paper-digest-bot",
       title_prefix="每周论文简报",
       tags=["周报/论文"],
       category_labels=CATEGORY_LABELS,
       system_prompt_extra="...",
   )
   if __name__ == "__main__":
       sys.exit(run_digest(SOURCES, CONFIG, CATEGORY_ORDER))
   ```
4. **写 `SKILL.md`**（参考现有 skill）
5. **加 cron 任务**：编辑 `~/.openclaw/cron/jobs.json` 追加一条，payload 调 runner.py 即可

## 依赖

- Python 3.10+
- `scrapling[all]` 用于原文抓取（`pip install 'scrapling[all]'`）
- 平台需配置 LLM：在 MultiAgents 平台 configs 表设 `compile_llm_api_key / base_url / model`

## 手动调试

```bash
# dry-run（不上传平台）
python3 ~/.openclaw/workspace/skills/wife-daily-ai-digest/runner.py --dry-run

# 不调 LLM（看原始 RSS 结构）
python3 ~/.openclaw/workspace/skills/daily-news-briefing/runner.py --no-llm --dry-run

# 不抓原文（只用 RSS 自带 summary）
python3 ~/.openclaw/workspace/skills/ai-apps-research/runner.py --no-enrich --dry-run

# 实际上传
python3 ~/.openclaw/workspace/skills/wife-daily-ai-digest/runner.py

# 上传到本地 dev 平台（MULTIAGENTS_URL 环境变量覆盖默认 URL）
MULTIAGENTS_URL=http://localhost:8000 python3 <runner.py>
```

## 故障排查

### cron 任务 `lastRunStatus: error`
```bash
# 看最近跑的记录（OpenClaw gateway 日志）
tail -100 ~/.openclaw/logs/gateway.log | grep -iE "每日|digest|error"
```

### LLM 批次失败（JSON parse 错）
GLM-4-flash 偶发返回不合 JSON 的内容。runner 已做 try/except，该批跳过。
如果整天都是 0/N ok，检查 platform configs：
```bash
curl http://118.89.197.244:8000/api/config/compile_llm_api_key
```

### 源失败率高
- `IncompleteRead`：对方服务器 Content-Length 和实际不一致。偶发，不影响整体
- `timeout`：调大 `DigestConfig.per_source_timeout`（默认 5s）
- `DNS ENOTFOUND`：LetsVPN 没开（海外源需要代理）

### fallback 文件在哪
```bash
ls ~/.openclaw/data/cron-fallback/<skill_name>/
```

## 历史沿革

- **2026-04-20** 创建第一个 `wife-daily-ai-digest` 给老婆看 AI + 数据标注行业日报
- **2026-04-22** 抽出 `digest_lib.py`，新建 `daily-news-briefing`（替换死掉的 OpenClaw daily-news skill）+ `ai-apps-research`（替换 VPN 断就挂的科研调研）
