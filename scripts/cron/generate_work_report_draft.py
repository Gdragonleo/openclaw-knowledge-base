#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from datetime import datetime
import json

workspace = Path('/Users/danxiong/.openclaw/workspace')
today = datetime.now().strftime('%Y-%m-%d')
mem = workspace / 'memory' / f'{today}.md'
jobs = Path('/Users/danxiong/.openclaw/cron/jobs.json')

mem_text = ''
if mem.exists():
    mem_text = mem.read_text(encoding='utf-8', errors='ignore')[:4000]

job_summary = []
if jobs.exists():
    data = json.loads(jobs.read_text(encoding='utf-8'))
    for job in data.get('jobs', []):
        state = job.get('state', {})
        if job.get('enabled'):
            job_summary.append(f"- {job.get('name')}：last={state.get('lastRunStatus')}, next={state.get('nextRunAtMs')}")

report = f'''# 每日工作汇报草稿 - {today}

## 今日推进
- 今日已推进事项：
- 招标系统 / 定时任务 / 协作事项：

## 当前状态
- 触手数量：参考 IDENTITY / MEMORY
- 今日关键进展：
- 定时任务概况：
{chr(10).join(job_summary[:6])}

## 风险/提醒
- 需要关注的异常：
- 需要继续收口的事项：

## 明日关注
- 
- 

---

## 今日记忆摘录（供汇报时参考）
{mem_text if mem_text else '（今日记忆文件暂无内容）'}
'''
print(report)
