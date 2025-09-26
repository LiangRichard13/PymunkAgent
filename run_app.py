#!/usr/bin/env python3
"""
Pymunk Agent Streamlit 应用启动脚本
"""

import subprocess
import sys
import os

def main():
    """启动Streamlit应用"""
    print("🚀 正在启动 Pymunk Agent 物理模拟器...")
    print("📱 应用将在浏览器中自动打开")
    print("🔗 如果浏览器没有自动打开，请访问: http://localhost:8501")
    print("⏹️  按 Ctrl+C 停止应用")
    print("-" * 50)
    
    try:
        # 启动streamlit应用
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("💡 请确保已安装所有依赖: pip install -r requirements.txt")

if __name__ == "__main__":
    main()
