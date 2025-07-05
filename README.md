# 机器人控制编程作业

## 作业目标
本作业旨在帮助学生掌握机器人学中的核心概念：
1. **正向运动学 (Forward Kinematics, FK)** - 计算机器人末端执行器的位置和姿态
2. **逆向运动学 (Inverse Kinematics, IK)** - 根据期望的末端位置计算关节角度
3. **基于动力学的控制** - 使用模型预测控制(MPC)实现精确的位置控制

## 项目结构
```
robot_control_homework/
├── README.md                 # 本文件
├── requirements.txt          # 依赖包
├── main.py                   # 主程序入口
├── robot_kinematics/         # 运动学模块
│   ├── __init__.py
│   ├── three_link_robot.py   # 三连杆机器人实现
│   └── utils.py              # 工具函数
├── dynamics_control/         # 动力学控制模块
│   ├── __init__.py
│   ├── mpc_controller.py     # MPC控制器
│   └── cart_dynamics.py      # 一维小车动力学模型
└── visualization/            # 可视化模块
    ├── __init__.py
    ├── robot_visualizer.py   # 机器人可视化
    └── control_visualizer.py # 控制结果可视化
```

## 学习任务

### 任务1: 正向运动学 (FK)
- 实现三连杆机器人的正向运动学计算
- 理解DH参数和齐次变换矩阵
- 计算末端执行器的位置和姿态

### 任务2: 逆向运动学 (IK)
- 实现三连杆机器人的逆向运动学
- 使用解析解和数值解方法
- 处理多解和奇异点问题
- **新增**: 交互式IK演示，可以在平面上点击选择目标位置

### 任务3: 基于动力学的MPC控制
- 建立一维小车的动力学模型
- 实现模型预测控制器
- 设计目标函数和约束条件

### 任务4: 交互式演示
- 基础交互式IK演示：点击选择目标位置
- 高级交互式IK演示：包含动画、轨迹规划和实时反馈

## 运行方式
```bash
# 安装依赖
pip install -r requirements.txt

# 运行主程序
python main.py

# 运行简单示例
python examples/simple_example.py

# 运行交互式IK演示
python interactive_ik_demo.py

# 运行高级交互式IK演示（包含动画和轨迹）
python interactive_ik_advanced.py
```
