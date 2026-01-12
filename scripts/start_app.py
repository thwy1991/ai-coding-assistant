# -*- coding: utf-8 -*-
"""
AI Coding Assistant 启动脚本
"""

import os
import sys
import subprocess


def main():
    """启动应用"""
    print("AI Coding Assistant 启动中...")

    # 检查是否安装了依赖
    try:
        import streamlit
    except ImportError:
        print("未安装依赖，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("依赖安装完成!")

    # 检查环境变量
    env_file = ".env"
    if not os.path.exists(env_file):
        print(f"\n警告: 未找到 {env_file} 文件")
        print("请复制 .env.example 为 .env 并配置API密钥")
        print("命令: cp .env.example .env\n")

    # 启动Streamlit应用
    print("启动Web界面...")
    print("访问地址: http://localhost:8501\n")

    subprocess.run([
        sys.executable, "-m", "streamlit",
        "run", "src/ai_coding/frontend/streamlit_app.py",
        "--server.port=8501"
    ])


if __name__ == "__main__":
    main()
