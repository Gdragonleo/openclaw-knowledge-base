#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path('/Users/danxiong/.openclaw/workspace')
BASE = WORKSPACE / '知识库/招标监控'
STATE_DIR = WORKSPACE / '运行状态/cron-validation'
STATE_DIR.mkdir(parents=True, exist_ok=True)
STAMP = datetime.now().strftime('%Y-%m-%d')
STATE_FILE = STATE_DIR / 'tender_validation_latest.json'
STATE_HISTORY = STATE_DIR / f'tender_validation_{STAMP}.json'

FILES = {
    'markdown': BASE / '招标日报_whale.md',
    'html': BASE / '招标日报_whale.html',
    'projects': BASE / '招标日报_whale_projects.json',
    'summary': BASE / '招标日报_whale_summary.json',
}

errors: list[str] = []
info: list[str] = []
meta: dict = {'checkedAt': datetime.now().isoformat()}

def check_exists(key: str):
    p = FILES[key]
    if not p.exists():
        errors.append(f'{key} missing: {p}')
        return None
    info.append(f'{key} exists: {p}')
    return p

md = check_exists('markdown')
html = check_exists('html')
projects = check_exists('projects')
summary = check_exists('summary')

if md and md.stat().st_size <= 1024:
    errors.append('markdown too small (<=1KB)')
if html and html.stat().st_size <= 1024:
    errors.append('html too small (<=1KB)')
if projects and projects.stat().st_size <= 50:
    errors.append('projects json unexpectedly tiny')
if summary and summary.stat().st_size <= 20:
    errors.append('summary json unexpectedly tiny')

if md:
    md_text = md.read_text(encoding='utf-8', errors='ignore')
    meta['markdownBytes'] = md.stat().st_size
    if '招标日报' not in md_text:
        errors.append('markdown missing title 招标日报')
    bad_words = ['样例数据', '示例项目', '测试项目', '虚构项目']
    for w in bad_words:
        if w in md_text:
            errors.append(f'markdown contains forbidden word: {w}')

if html:
    html_text = html.read_text(encoding='utf-8', errors='ignore')
    meta['htmlBytes'] = html.stat().st_size
    if ('target="_blank"' not in html_text) and ('原网页' not in html_text) and ('href="https://www.cqggzy.com' not in html_text):
        errors.append('html missing clickable source-link markers')

summary_projects = None
if summary:
    try:
        s = json.loads(summary.read_text(encoding='utf-8'))
        summary_projects = s.get('total_projects')
        meta['summaryTotalProjects'] = summary_projects
        info.append(f"summary total_projects={summary_projects}")
    except Exception as e:
        errors.append(f'summary json parse failed: {e}')

if projects:
    try:
        p = json.loads(projects.read_text(encoding='utf-8'))
        if isinstance(p, dict):
            proj = p.get('projects') if 'projects' in p else p.get('data')
            count = len(proj) if isinstance(proj, list) else None
        elif isinstance(p, list):
            count = len(p)
        else:
            count = None
        meta['projectsCount'] = count
        info.append(f'projects count={count}')
        if summary_projects and (count is not None) and summary_projects > 0 and count == 0:
            errors.append('summary says projects > 0 but projects json empty')
    except Exception as e:
        errors.append(f'projects json parse failed: {e}')

payload = {
    'ok': not errors,
    'errors': errors,
    'info': info,
    'meta': meta,
}
STATE_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
STATE_HISTORY.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(payload, ensure_ascii=False, indent=2))
raise SystemExit(1 if errors else 0)
