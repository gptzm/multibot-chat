#!/bin/bash

# 设置虚拟环境路径（如果你使用虚拟环境）
VENV_PATH="./venv"

# 激活虚拟环境（如果存在）
if [ -d "$VENV_PATH" ]; then
    source "$VENV_PATH/bin/activate"
    echo "Virtual environment activated."
else
    echo "Virtual environment not found. Using system Python."
fi

# 设置环境变量
export PYTHONIOENCODING=utf-8

# 启动 Streamlit 应用
streamlit run app.py

# 如果使用了虚拟环境，在脚本结束时取消激活
if [ -d "$VENV_PATH" ]; then
    deactivate
    echo "Virtual environment deactivated."
fi