#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用PIL画小刘画像
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
    
    # 创建图片
    width, height = 800, 1000
    img = Image.new('RGB', (width, height), color='#667eea')
    draw = ImageDraw.Draw(img)
    
    # 背景渐变（简化版）
    for i in range(height):
        r = int(102 + i * 0.1)
        g = int(126 + i * 0.1)
        b = int(234 - i * 0.05)
        draw.rectangle([(0, i), (width, i+1)], fill=(r, g, b))
    
    # 标题
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 48)
        label_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 28)
        small_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 20)
    except:
        title_font = ImageFont.load_default()
        label_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    
    # 标题
    draw.text((400, 50), '👨‍💼 小刘画像', fill='white', font=title_font, anchor='mm')
    draw.text((400, 100), '（小八爪眼中的你）', fill='#ffeaa7', font=label_font, anchor='mm')
    
    # 身体（蓝色西装）
    body = [(300, 400), (500, 400), (500, 750), (300, 750)]
    draw.polygon(body, fill='#0984e3', outline='#0652DD')
    
    # 领带（红色）
    tie = [(400, 400), (370, 550), (400, 700), (430, 550)]
    draw.polygon(tie, fill='#e74c3c', outline='#c0392b')
    
    # 手臂
    draw.rectangle([180, 420, 300, 620], fill='#0984e3', outline='#0652DD')
    draw.rectangle([500, 420, 620, 620], fill='#0984e3', outline='#0652DD')
    
    # 头部（肤色圆）
    draw.ellipse([320, 220, 480, 380], fill='#ffeaa7', outline='#fdcb6e', width=5)
    
    # 头发
    draw.arc([310, 200, 490, 320], 0, 180, fill='#2d3436', width=20)
    
    # 眼睛
    draw.ellipse([355, 270, 385, 300], fill='white', outline='#2d3436', width=3)
    draw.ellipse([415, 270, 445, 300], fill='white', outline='#2d3436', width=3)
    
    # 眼珠
    draw.ellipse([365, 278, 380, 293], fill='#2d3436')
    draw.ellipse([425, 278, 440, 293], fill='#2d3436')
    
    # 眼镜
    draw.rectangle([350, 265, 390, 305], outline='#636e72', width=4)
    draw.rectangle([410, 265, 450, 305], outline='#636e72', width=4)
    draw.line([390, 285, 410, 285], fill='#636e72', width=4)
    
    # 微笑
    draw.arc([365, 310, 435, 350], 20, 160, fill='#e17055', width=5)
    
    # 标签（简化）
    labels = [
        ('💡 创造者', '#e74c3c', 100, 850),
        ('🏠 家人', '#f39c12', 280, 850),
        ('🎯 理想主义', '#3498db', 460, 850),
        ('💪 奋斗者', '#9b59b6', 640, 850),
        ('🤝 协作者', '#1abc9c', 190, 900),
        ('❤️ 温暖', '#e84393', 460, 900),
    ]
    
    for text, color, x, y in labels:
        # 标签背景
        draw.rounded_rectangle([x-60, y-15, x+60, y+15], radius=10, fill=color)
        # 标签文字
        draw.text((x, y), text, fill='white', font=label_font, anchor='mm')
    
    # 底部文字
    draw.text((400, 960), '💕 创造了有温度的世界 💕', fill='#ffeaa7', font=label_font, anchor='mm')
    draw.text((400, 990), '🐙 小八爪 作 | 2026-03-15', fill='#b2bec3', font=small_font, anchor='mm')
    
    # 保存
    output_path = '/Users/danxiong/.openclaw/workspace/memory/xiaoliu_portrait.png'
    img.save(output_path, 'PNG')
    print(f'✅ 图片已保存: {output_path}')
    
except Exception as e:
    print(f'❌ 错误: {e}')
    import traceback
    traceback.print_exc()
