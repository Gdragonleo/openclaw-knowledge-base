# Workspace 分区说明

**更新时间**: 2026-03-16 18:05

## 目标
把知识库、记忆、运行状态、临时脚本分开，避免混放导致记忆污染。

## 分区规则

### 1. 根目录
只保留：身份/配置/核心说明类文件
- AGENTS.md
- SOUL.md
- USER.md
- MEMORY.md
- TOOLS.md
- HEARTBEAT.md
- README.md
- WORKSPACE_GUIDE.md

### 2. 知识库/
长期可复用内容
- 招标监控/
- 学习笔记/
- 历史报告/
- 各团队知识

### 3. memory/
仅放记忆类文本
- 每日日志
- 错误日志
- 今日提醒
- 与长期记忆有关的文字材料

### 4. 运行状态/
运行时状态、json状态文件、检查日志
- heartbeat-state.json
- issue-check-log.json

### 5. 归档/临时脚本/
一次性脚本、调试脚本、已完成脚本

### 6. 归档/画像与设计/
图片、svg、html画像等视觉产物

## 特殊说明
`tender-browser-scraper` 的 quick_report 输出已经改到：
`知识库/招标监控/原始清单/重庆公共资源_近3个月_初步清单.md`

后续新增文件尽量按这个规则放，避免再次混乱。
