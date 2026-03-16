# LEARNINGS.md - 小八爪的学习记录

**用途**: 记录用户纠正、知识盲区、最佳实践

**优先级**: low | medium | high | critical
**状态**: pending | in_progress | resolved | wont_fix | promoted

---

## [LRN-20260316-001] 系统性错误预防

**Logged**: 2026-03-16T10:54:00+08:00
**Priority**: critical
**Status**: pending
**Area**: config
**Category**: best_practice

### Summary
招标报告连续3天(03-13~03-15)未生成,但定时任务显示执行成功

### Details
- cron日志显示任务正常触发
- 但子智能体执行不完整(只执行了1分钟就结束)
- 没有错误通知机制,导致停了3天才发现
- tender-browser-scraper技能可能存在问题

### Suggested Action
1. 添加每日报告生成验证(检查文件是否真的生成)
2. 失败时自动告警(私聊通知小刘)
3. 优化爬虫稳定性
4. 增加子智能体执行超时检测

### Metadata
- Source: error
- Related Files: cron_tasks/daily_tender_report.md
- Tags: automation, cron, monitoring
- Pattern-Key: harden.task_verification
- Recurrence-Count: 1
- First-Seen: 2026-03-16
- Last-Seen: 2026-03-16

---
