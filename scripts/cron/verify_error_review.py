#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from datetime import datetime
import json

workspace = Path('/Users/danxiong/.openclaw/workspace')
state_dir = workspace / '运行状态/cron-validation'
state_dir.mkdir(parents=True, exist_ok=True)
today = datetime.now().strftime('%Y-%m-%d')
state_file = state_dir / 'error_review_validation_latest.json'
state_history = state_dir / f'error_review_validation_{today}.json'

p = workspace / 'memory/今日提醒.md'
errors = []
info = []
meta = {'checkedAt': datetime.now().isoformat()}

if not p.exists():
    errors.append(f'missing file: {p}')
else:
    info.append(f'exists: {p}')
    meta['bytes'] = p.stat().st_size
    if p.stat().st_size <= 200:
        errors.append('今日提醒.md too small (<=200B)')
    text = p.read_text(encoding='utf-8', errors='ignore')
    if today not in text and today.replace('-', '.') not in text:
        errors.append(f'today marker missing: {today}')
    hint_markers = ['预防措施', '今日提醒', '必须遵守', '需要注意', '规则']
    if not any(m in text for m in hint_markers):
        errors.append('missing actionable reminder markers')
    if '高频错误' not in text and '暂无高频错误' not in text:
        errors.append('missing 高频错误/暂无高频错误 statement')

payload = {'ok': not errors, 'errors': errors, 'info': info, 'meta': meta}
state_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
state_history.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(payload, ensure_ascii=False, indent=2))
raise SystemExit(1 if errors else 0)
