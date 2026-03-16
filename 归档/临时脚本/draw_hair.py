#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重新画小刘画像 - 浓密头发版
"""

from PIL import Image, ImageDraw
import math

# 创建图片
width, height = 800, 1000
img = Image.new('RGB', (width, height), color='#667eea')
draw = ImageDraw.Draw(img)

# 背景渐变
for i in range(height):
    r = int(102 + i * 0.1)
    g = int(126 + i * 0.1)
    b = int(234 - i * 0.05)
    draw.rectangle([(0, i), (width, i+1)], fill=(r, g, b))

# 字体
try:
    from PIL import ImageFont
    title_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 48)
    label_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 28)
    small_font = ImageFont.truetype("/System/Library/Fonts/PingFang.ttc", 20)
except:
    title_font = ImageFont.load_default()
    label_font = ImageFont.load_default()
    small_font = ImageFont.load_default()

# 标题
draw.text((400, 50), '👨‍💼 小刘画像（修正版）', fill='white', font=title_font, anchor='mm')
draw.text((400, 100), '（浓密头发版）', fill='#ffeaa7', font=label_font, anchor='mm')

# 头发（浓密版！）
# 很多层头发
for i in range(30):
    y = 180 + i * 3
    # 左边头发
    draw.ellipse([250, y, 400, y + 40], fill='#2d3436')
    # 右边头发
    draw.ellipse([400, y, 550, y + 40], fill='#2d3436')
    # 顶部头发
    if i < 15:
        draw.ellipse([300, y - 30, 500, y + 30], fill='#2d3436')

# 画更多头发丝
for angle in range(0, 180, 10):
    rad = math.radians(angle)
    x1 = 400 + int(130 * math.cos(rad))
    y1 = 200 - int(80 * math.sin(rad))
    x2 = 400 + int(100 * math.cos(rad))
    y2 = 200 - int(50 * math.sin(rad))
    draw.line([x1, y1, x2, y2], fill='#1a1a1a', width=3)

# 头部（肤色）
draw.ellipse([320, 250, 480, 410], fill='#ffeaa7', outline='#fdcb6e', width=5)

# 眼睛
draw.ellipse([355, 300, 385, 330], fill='white', outline='#2d3436', width=3)
draw.ellipse([415, 300, 445, 330], fill='white', outline='#2d3436', width=3)

# 眼珠
draw.ellipse([365, 308, 380, 323], fill='#2d3436')
draw.ellipse([425, 308, 440, 323], fill='#2d3436')

# 眼镜
draw.rectangle([350, 295, 390, 335], outline='#636e72', width=4)
draw.rectangle([410, 295, 450, 335], outline='#636e72', width=4)
draw.line([390, 315, 410, 315], fill='#636e72', width=4)

# 微笑
draw.arc([365, 340, 435, 380], 20, 160, fill='#e17055', width=5)

# 身体（蓝色西装）
body = [(300, 430), (500, 430), (500, 780), (300, 780)]
draw.polygon(body, fill='#0984e3', outline='#0652DD')

# 领带（红色）
tie = [(400, 430), (370, 580), (400, 730), (430, 580)]
draw.polygon(tie, fill='#e74c3c', outline='#c0392b')

# 手臂
draw.rectangle([180, 450, 300, 650], fill='#0984e3', outline='#0652DD')
draw.rectangle([500, 450, 620, 650], fill='#0984e3', outline='#0652DD')

# 手机
draw.rounded_rectangle([530, 520, 570, 580], radius=5, fill='#2d3436')
draw.text((550, 550), '🐙', fill='white', font=label_font, anchor='mm')

# 标签
labels = [
    ('💡 创造者', '#e74c3c', 100, 880),
    ('🏠 家人', '#f39c12', 280, 880),
    ('🎯 理想主义', '#3498db', 460, 880),
    ('💪 奋斗者', '#9b59b6', 640, 880),
    ('🤝 协作者', '#1abc9c', 190, 930),
    ('❤️ 温暖', '#e84393', 460, 930),
]

for text, color, x, y in labels:
    draw.rounded_rectangle([x-60, y-15, x+60, y+15], radius=10, fill=color)
    draw.text((x, y), text, fill='white', font=label_font, anchor='mm')

# 底部文字
draw.text((400, 960), '💕 浓密头发的小刘 💕', fill='#ffeaa7', font=label_font, anchor='mm')
draw.text((400, 990), '🐙 小八爪 重新作 | 2026-03-15', fill='#b2bec3', font=small_font, anchor='mm')

# 保存
output_path = '/Users/danxiong/.openclaw/workspace/memory/xiaoliu_portrait_v2.png'
img.save(output_path, 'PNG')
print(f'✅ 浓密头发版已保存: {output_path}')
