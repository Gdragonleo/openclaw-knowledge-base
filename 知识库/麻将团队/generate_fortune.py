#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成麻将运势测试数据
生成3天的运势JSON文件
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import date, timedelta
from 易经算法 import MahjongFortune
import json

# 生成3天的数据
dates = [
    date(2026, 3, 15),
    date(2026, 3, 16),
    date(2026, 3, 17)
]

for target_date in dates:
    print(f"正在生成 {target_date} 的运势数据...")
    
    # 创建运势对象
    fortune = MahjongFortune(target_date=target_date)
    
    # 获取完整运势
    full_fortune = fortune.get_full_fortune()
    
    # 保存文件
    filename = f"daily_fortune_{target_date.strftime('%Y-%m-%d')}.json"
    filepath = os.path.join(os.path.dirname(__file__), filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(full_fortune, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已保存: {filename}")

print("\n🎉 3天运势数据生成完成！")
