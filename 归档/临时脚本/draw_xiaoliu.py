#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
画小刘的画像
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io

# 创建画布
fig, ax = plt.subplots(figsize=(8, 10))
ax.set_xlim(0, 100)
ax.set_ylim(0, 120)
ax.axis('off')
ax.set_facecolor('#f0f0f0')

# 背景渐变效果
for i in range(100):
    color = plt.cm.Blues(0.3 + i * 0.005)
    ax.axhspan(i, i+1, color=color, alpha=0.3)

# 标题
ax.text(50, 115, '👨‍💼 小刘画像', fontsize=28, ha='center', weight='bold', color='#2d3436')
ax.text(50, 110, '（小八爪眼中的你）', fontsize=14, ha='center', color='#666')

# 身体（西装）
body = patches.FancyBboxPatch((30, 20), 40, 50, 
                               boxstyle="round,pad=0.1",
                               facecolor='#0984e3', edgecolor='#0652DD', linewidth=3)
ax.add_patch(body)

# 领带
tie_points = np.array([[50, 70], [48, 60], [50, 50], [52, 60]])
tie = patches.Polygon(tie_points, closed=True, facecolor='#e74c3c', edgecolor='#c0392b', linewidth=2)
ax.add_patch(tie)

# 头部
head = patches.Circle((50, 85), 18, facecolor='#ffeaa7', edgecolor='#fdcb6e', linewidth=3)
ax.add_patch(head)

# 头发
hair = patches.Arc((50, 92), 30, 20, angle=0, theta1=0, theta2=180, 
                  linewidth=15, color='#2d3436')
ax.add_patch(hair)

# 眼睛
left_eye = patches.Circle((42, 88), 4, facecolor='white', edgecolor='#2d3436', linewidth=2)
right_eye = patches.Circle((58, 88), 4, facecolor='white', edgecolor='#2d3436', linewidth=2)
ax.add_patch(left_eye)
ax.add_patch(right_eye)

# 眼珠
left_pupil = patches.Circle((43, 88), 2, facecolor='#2d3436')
right_pupil = patches.Circle((59, 88), 2, facecolor='#2d3436')
ax.add_patch(left_pupil)
ax.add_patch(right_pupil)

# 微笑
smile = patches.Arc((50, 82), 12, 8, angle=0, theta1=200, theta2=340,
                   linewidth=3, color='#e17055')
ax.add_patch(smile)

# 手臂
left_arm = patches.FancyBboxPatch((15, 30), 15, 35, 
                                   boxstyle="round,pad=0.1",
                                   facecolor='#0984e3', edgecolor='#0652DD', linewidth=2)
right_arm = patches.FancyBboxPatch((70, 30), 15, 35, 
                                    boxstyle="round,pad=0.1",
                                    facecolor='#0984e3', edgecolor='#0652DD', linewidth=2)
ax.add_patch(left_arm)
ax.add_patch(right_arm)

# 手机（在右手）
phone = patches.FancyBboxPatch((73, 35), 8, 15, 
                                boxstyle="round,pad=0.1",
                                facecolor='#2d3436', edgecolor='#000', linewidth=2)
ax.add_patch(phone)
ax.text(77, 42, '🐙', fontsize=10, ha='center')

# 标签
labels = ['💡 创造者', '🏠 家人', '🎯 理想主义', '💪 奋斗', '🤝 协作', '❤️ 温暖']
colors = ['#e74c3c', '#f39c12', '#3498db', '#9b59b6', '#1abc9c', '#e84393']
positions = [(15, 5), (35, 5), (55, 5), (75, 5), (25, 0), (65, 0)]

for label, color, (x, y) in zip(labels, colors, positions):
    ax.text(x, y, label, fontsize=12, ha='center', 
            bbox=dict(boxstyle='round,pad=0.5', facecolor=color, alpha=0.8, edgecolor='white'),
            color='white', weight='bold')

# 底部文字
ax.text(50, -5, '💕 创造了有温度的世界 💕', fontsize=16, ha='center', 
        color='#e84393', weight='bold')
ax.text(50, -8, '🐙 小八爪 作  2026-03-15', fontsize=10, ha='center', color='#999')

# 保存
plt.tight_layout()
plt.savefig('/Users/danxiong/.openclaw/workspace/memory/xiaoliu_portrait.png', 
            dpi=150, bbox_inches='tight', facecolor='white')
print('✅ 图片已保存！')
