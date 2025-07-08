# Basics of Robotics: Kinematics and Dynamics

This is a take-away homework for [USTC Summer School: Embodied AI Courses](http://staff.ustc.edu.cn/~fuxm/course/SummerSchool_2025/program.html).

这是[中科大暑期学校：具身智能课程](http://staff.ustc.edu.cn/~fuxm/course/SummerSchool_2025/program.html)的一份编程作业。
用于演示机器人运动学，主要包含三连杆机器人的运动学分析和轨迹规划功能。

课程资料：https://lym29.github.io/USTCSummerSchool-Homework/

## 演示视频

https://github.com/user-attachments/assets/0fc06d7b-1cdf-4608-891a-851adae5c116


上面的视频展示了完成作业后的运行效果。

## 项目结构

```
USTCSummerSchool-Homework/
├── robot_kinematics/       # 运动学相关代码
│   ├── three_link_robot.py # 三连杆机器人的运动学实现
│   ├── path_planning.py    # 轨迹规划算法
│   └── utils.py           # 工具函数
├── visualization/          # 可视化相关代码
│   └── robot_visualizer.py # 机器人可视化
├── main.py                 # 主程序入口
├── test.py                # 测试文件
└── requirements.txt       # 项目依赖文件
```

## 主要功能

1. **三连杆机器人运动学**
   - 正运动学计算
   - 逆运动学求解（优化方法和雅可比方法）
   - 工作空间分析

2. **轨迹规划**
   - 关节空间插值
   - 操作空间插值
   - 速度和加速度约束

3. **交互式演示**
   - 可视化机器人构型
   - 实时逆运动学求解
   - 轨迹规划和动画展示
   - 支持不同IK方法切换
   - 支持不同插值模式切换

## 使用说明

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行交互式演示

```bash
python main.py
```

### 交互式演示功能

1. **点击操作**
   - 在工作空间内点击以设置目标位置
   - 系统会自动计算逆运动学解并显示机器人构型

2. **轨迹生成**
   - 通过多次点击创建轨迹点
   - 使用"Play Trajectory"按钮播放轨迹动画

3. **控制选项**
   - 切换IK方法（优化法/雅可比法）
   - 切换插值模式（关节空间/操作空间）
   - 调整动画播放速度
   - 重置机器人位置
   - 清除已创建的轨迹

## TODO 实现任务

本项目包含以下需要实现的功能：

### 1. 三连杆机器人运动学
- **基本任务**: 
  - 实现正运动学(FK)计算
    - 计算末端执行器的位置和姿态
    - 考虑关节角度限制
  - 实现逆运动学(IK)求解
    - 基于优化的方法
    - 基于雅可比矩阵的方法
- **进阶任务**:
  - 处理IK的多解情况
  - 确保解在关节限制范围内
  - 处理不可达位置的情况
  - 优化求解效率
- **相关文件**: `robot_kinematics/three_link_robot.py`
- **入口函数**: 
  - `ThreeLinkRobot.forward_kinematics()`
  - `ThreeLinkRobot.inverse_kinematics_jacobian()`
- **使用示例**: `main.py`

### 2. 梯形速度轨迹生成
- **基本任务**: 实现梯形速度轨迹的计算
  - 计算加速和减速时间
  - 处理加速、匀速和减速三个阶段
  - 确保满足最大速度和加速度约束
  - 处理总距离过短的特殊情况（需要重新计算最大速度）
- **相关文件**: `robot_kinematics/path_planning.py`
- **入口函数**: `PathPlanner._calculate_trapezoid_profile()`
- **使用示例**: `main.py`

### 3. 关节空间轨迹插值
- **基本任务**: 实现关节空间的梯形速度轨迹插值
- **进阶任务**: 实现其他轨迹插值方法，例如：
  - 三次样条插值
  - 五次多项式插值
- **相关文件**: `robot_kinematics/path_planning.py`
- **入口函数**: `PathPlanner.interpolate_joint_space()`
- **使用示例**: `main.py`

### 4. 操作空间轨迹插值 (`interpolate_operational_space`)
- **基本任务**: 实现操作空间的梯形速度轨迹插值
- **进阶任务**: 实现其他轨迹插值方法，例如：
  - 圆弧轨迹插值
  - 贝塞尔曲线插值
- **相关文件**: `robot_kinematics/path_planning.py`
- **入口函数**: `PathPlanner.interpolate_operational_space()`
- **使用示例**: `main.py`

### 实现建议
1. 建议按照上述顺序实现功能，因为后面的功能会依赖前面的实现
2. 每个功能都提供了基本任务和进阶任务，建议先完成基本任务
3. 可以参考 `test.py` 的示例来测试实现的功能
4. 使用 `main.py` 可以直观地验证实现效果

### 测试方法
1. 运行 `main.py` 进行交互式测试
2. 使用不同的插值方法和参数进行对比
3. 观察轨迹的连续性和平滑性
4. 验证是否满足速度和加速度约束

## 注意事项

1. 确保安装了所有必要的Python依赖
2. 运行演示程序时，建议先阅读使用说明
3. 在进行轨迹规划时，注意避免机器人运动到奇异位置
4. 不同IK方法可能会得到不同的解，这是正常现象

