# FEATURE_REQUESTS.md - 功能需求

**用途**: 记录用户想要但目前不存在的功能

**优先级**: low | medium | high | critical
**状态**: pending | in_progress | resolved | wont_fix

---

## [FEAT-20260316-001] 定时任务执行验证

**Logged**: 2026-03-16T10:54:00+08:00
**Priority**: high
**Status**: pending
**Area**: infra

### Requested Capability
定时任务执行后,自动验证结果是否真的生成

### User Context
招标报告连续3天未生成,但定时任务显示成功,导致停了3天才发现

### Complexity Estimate
medium

### Suggested Implementation
1. 每个定时任务配置expected_output字段
2. 执行完成后,检查expected_output是否存在
3. 如果不存在,标记为失败并发送告警
4. 在cron/jobs.json中添加验证状态

### Metadata
- Frequency: first_time
- Related Features: cron系统, 错误告警

---
