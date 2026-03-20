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

## [LRN-20260317-001] 区分浏览器登录态权限与 API token 权限

**Logged**: 2026-03-17T15:12:00+08:00
**Priority**: high
**Status**: pending
**Area**: config
**Category**: correction

### Summary
浏览器访问 Gitee Issue 返回 403，不代表本地 Gitee token 无效；应优先用 token 走 API 验证读写能力

### Details
- 用户已提供并保存 Gitee token
- 我先走浏览器页面访问，因未登录态/页面权限受限返回 403
- 错误地把页面 403 混同为整体“受限”
- 后续定位到 `config/gitee_token.sh`，改用 Gitee API 后成功读取 issue 并成功发表评论

### Suggested Action
1. 涉及外部平台写操作时，先检查本地 token / 凭据文件
2. 页面失败与 API 失败要分开判断
3. 优先验证 API 可读可写，再决定是否需要处理浏览器登录态
4. 对用户汇报时说明具体失败链路，避免笼统说“没权限”

### Metadata
- Source: user_feedback
- Related Files: config/gitee_token.sh
- Tags: gitee, token, api, browser, auth
- Pattern-Key: harden.auth_path_selection
- Recurrence-Count: 1
- First-Seen: 2026-03-17
- Last-Seen: 2026-03-17
- See Also: 2026-03-14 08:00 未确认就声称已确认

---
