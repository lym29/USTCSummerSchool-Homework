"""
机器人控制作业包安装配置
"""

from setuptools import setup, find_packages

setup(
    name="robot_control_homework",
    version="1.0.0",
    description="机器人控制编程作业框架",
    author="Robot Control Course",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21.0",
        "matplotlib>=3.5.0",
        "scipy>=1.7.0",
        "cvxpy>=1.2.0",
        "transforms3d>=0.3.1",
    ],
    python_requires=">=3.7",
) 