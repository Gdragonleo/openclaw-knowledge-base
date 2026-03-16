#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
from datetime import datetime
import json

p = Path('/Users/danxiong/.openclaw/workspace/memory/今日提醒.md')
errors = []
info = []

today = datetime.now().strftime('%Y-%m-%d')

if not p.exists():
    errors.append(f'missing file: {p}')
else:
    info.append(f'exists: {p}')
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

payload = {'ok': not errors, 'errors': errors, 'info': info}
print(json.dumps(payload, ensure_ascii=False, indent=2))
raise SystemExit(1 if errors else 0)
