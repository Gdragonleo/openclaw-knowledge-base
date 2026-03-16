#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查询Gitee协作仓库Issues
"""

import os
import json
import subprocess
from datetime import datetime

# 加载Gitee Token
token_file = os.path.expanduser("~/.openclaw/workspace/config/gitee_token.sh")
if os.path.exists(token_file):
    with open(token_file, 'r') as f:
        for line in f:
            if line.startswith('export GITEE_TOKEN='):
                token = line.split('=')[1].strip().strip('"')
                break
else:
    print("❌ Token文件不存在")
    exit(1)

# Gitee API
url = "https://gitee.com/api/v5/repos/whaleandcollab/agent-collaboration/issues"
params = {
    "access_token": token,
    "state": "open",
    "labels": "pending",
    "sort": "updated",
    "direction": "desc",
    "per_page": 10
}

try:
    result = subprocess.run(
        ["curl", "-s", "-H", f"Authorization: token {token}", 
         f"{url}?access_token={token}&state=open&labels=pending&sort=updated&direction=desc&per_page=10"],
        capture_output=True,
        text=True
    )
    
    issues = json.loads(result.stdout)
    
    print(f"\n✅ 查询成功！找到 {len(issues)} 个待处理Issues\n")
    
    for issue in issues:
        print(f"\n{'='*60}")
        print(f"Issue #{issue['number']}: {issue['title']}")
        print(f"状态: {issue['state']}")
        print(f"标签: {', '.join(issue.get('labels', []))}")
        print(f"更新时间: {issue['updated_at']}")
        print(f"URL: {issue['html_url']}")
        
except Exception as e:
    print(f"❌ 查询失败: {e}")
