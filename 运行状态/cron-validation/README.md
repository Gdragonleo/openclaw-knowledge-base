# cron-validation

本目录存放定时任务的验证结果与草稿状态，便于排查“任务显示 ok 但结果无效”的问题。

## 当前文件说明

- `tender_validation_latest.json`：最近一次招标报告校验结果
- `tender_validation_YYYY-MM-DD.json`：当日招标报告校验快照
- `error_review_validation_latest.json`：最近一次错误复盘校验结果
- `error_review_validation_YYYY-MM-DD.json`：当日错误复盘校验快照
- `work_report_draft_latest.json`：最近一次工作汇报草稿生成状态
- `work_report_draft_YYYY-MM-DD.json`：当日工作汇报草稿生成快照

## 用途

1. 判断任务是否真的生成了有效产物
2. 为每日汇报提供状态依据
3. 快速定位失败发生在哪一环

**建立时间**：2026-03-16 第五轮收口
