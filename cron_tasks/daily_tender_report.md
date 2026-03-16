# 每日招标报告任务（正式版）

## 任务目标
每天凌晨运行当前正式版招标链路，基于真实抓取/解析数据生成 Markdown / HTML / JSON 产物，并私聊发送结果给小刘。

## 执行时间
每天凌晨 3:00 执行

## 当前正式链路
`tender-browser-scraper / quick_report → 补详情 → 硬筛选 → whale评分 → Markdown / HTML / JSON`

## 核心原则
1. **只允许真实数据**：禁止样例数据、补造内容、幻觉项目
2. **原链接必须可点击**：HTML 分享页必须保留回源链接
3. **硬筛选必须生效**：持续过滤 `监理` / `施工` / `EPC`
4. **当前由小八爪主负责**：不再走“小鲸鱼 03:30 兜底分析”旧链路

## 核心产物
- `知识库/招标监控/招标日报_whale.md`
- `知识库/招标监控/招标日报_whale.html`
- `知识库/招标监控/招标日报_whale_projects.json`
- `知识库/招标监控/招标日报_whale_summary.json`

## 执行步骤

### 1. 运行正式版链路
优先使用当前稳定脚本：
- `~/.openclaw/workspace/skills/tender-browser-scraper/run_whale_pipeline.sh`
- 必要时调用：
  - `~/.openclaw/workspace/skills/tender-browser-scraper/integrate_with_whale.py`
  - `~/.openclaw/workspace/skills/tender-browser-scraper/scripts/quick_report.js`

### 2. 更新报告产物
确保以下文件被刷新：
- Markdown 报告
- HTML 分享页
- 项目 JSON
- 汇总 JSON

### 3. 验证结果（必须执行）
执行后必须运行：
- `python3 /Users/danxiong/.openclaw/workspace/scripts/cron/verify_tender_outputs.py`

并验证：

#### 文件存在性
- Markdown 存在
- HTML 存在
- `projects.json` 存在
- `summary.json` 存在

#### 内容有效性
- Markdown 文件大小 > 1KB
- HTML 文件大小 > 1KB
- Markdown 包含“招标日报”标题
- HTML 包含原网页链接或 `target="_blank"`
- 汇总 JSON 中项目数 > 0 时，项目 JSON 不得为空

#### 业务有效性
- 不得出现样例/虚构项目
- 继续过滤 `监理` / `施工` / `EPC`
- 若项目数为 0，需要明确说明是“无符合条件项目”还是“链路异常”

### 4. 失败处理
若验证失败：
1. 立即记录失败原因
2. 允许重试 1 次主链路
3. 若仍失败，私聊小刘发送告警，不得假装成功

### 5. 私聊通知
通知内容至少包含：
- 日期
- 项目总数
- 平均推荐指数
- 项目总金额
- 产物路径或结果摘要
- 失败时的告警说明

## 禁止事项
- 禁止生成飞书文档替代正式产物
- 禁止把“执行成功”当成“结果可信”
- 禁止继续沿用旧版“小八爪+小鲸鱼兜底分析”描述

## 当前版本备注
- 当前可用版本已经够用，后续优化按 `知识库/招标监控/下一步优化计划_2026-03-16.md` 继续
- 后续重点：标题清洗、金额提取、招标单位/代理机构补全、稳定详细抓取

**最后更新**：2026-03-16 第二轮收口
**维护者**：小八爪 🐙
