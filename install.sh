#!/bin/bash

# 机器人控制作业安装脚本

echo "=== 机器人控制编程作业安装脚本 ==="

# 检查Python版本
python_version=$(python3 --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+')
echo "检测到Python版本: $python_version"

# 安装依赖包
echo "安装依赖包..."
pip3 install -r requirements.txt

# 安装当前包（开发模式）
echo "安装机器人控制作业包..."
pip3 install -e .

echo "=== 安装完成 ==="
echo ""
echo "现在你可以运行以下命令来测试安装："
echo "  python3 main.py"
echo "  python3 examples/simple_example.py"
echo ""
echo "注意：如果遇到导入错误，请确保在robot_control_homework目录下运行程序" 