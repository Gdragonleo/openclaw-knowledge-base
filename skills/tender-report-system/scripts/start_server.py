#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
招标智能报告系统 - Web服务
启动localhost服务
"""

import sys
import subprocess
import time
from pathlib import Path

# 小鲸鱼系统路径
WHALE_DIR = Path("/Users/danxiong/Desktop/项目管理平台代码/whale/whale")


def main():
    """主函数"""
    print("="*60)
    print("🌐 招标智能报告系统 - Web服务")
    print("="*60)
    
    # 检查小鲸鱼代码是否存在
    app_path = WHALE_DIR / "app.py"
    if not app_path.exists():
        print(f"❌ 错误: 找不到 {app_path}")
        print("请确保小鲸鱼的代码在正确位置")
        return
    
    # 启动服务
    print(f"\n🚀 启动Web服务...")
    print(f"📂 工作目录: {WHALE_DIR}")
    print(f"🌐 访问地址: http://127.0.0.1:8080")
    print(f"📊 API地址: http://127.0.0.1:8080/api/projects")
    print(f"❤️ 健康检查: http://127.0.0.1:8080/api/health")
    print("\n" + "="*60)
    print("⚠️ 按 Ctrl+C 停止服务")
    print("="*60 + "\n")
    
    try:
        # 启动Flask服务
        subprocess.run(
            [sys.executable, str(app_path)],
            cwd=str(WHALE_DIR)
        )
    except KeyboardInterrupt:
        print("\n\n👋 服务已停止")
    except Exception as e:
        print(f"\n❌ 服务启动失败: {e}")


if __name__ == "__main__":
    main()
