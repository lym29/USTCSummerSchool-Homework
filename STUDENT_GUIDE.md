# 学生指南：机器人控制编程作业

## 作业概述

本作业旨在帮助你掌握机器人学中的三个核心概念：
1. **正向运动学 (Forward Kinematics, FK)**
2. **逆向运动学 (Inverse Kinematics, IK)**  
3. **基于动力学的控制 (Model Predictive Control, MPC)**

## 学习目标

完成本作业后，你应该能够：
- 理解并实现DH参数和齐次变换矩阵
- 计算三连杆机器人的正向和逆向运动学
- 建立一维小车的动力学模型
- 实现模型预测控制器
- 分析和可视化控制结果

## 作业结构

### 任务1: 正向运动学 (30分)

**文件**: `robot_kinematics/utils.py` 和 `robot_kinematics/three_link_robot.py`

**需要实现的功能**:
1. `dh_transform_matrix()` - 计算DH变换矩阵
2. `forward_kinematics()` - 实现正向运动学
3. `get_end_effector_position()` - 获取末端位置

**关键概念**:
- DH参数 (Denavit-Hartenberg parameters)
- 齐次变换矩阵
- 连杆变换的累积

**提示**:
- 使用DH参数计算每个连杆的变换矩阵
- 将所有变换矩阵相乘得到末端位置
- 注意关节角度的累积效应

### 任务2: 逆向运动学 (30分)

**文件**: `robot_kinematics/three_link_robot.py`

**需要实现的功能**:
1. `inverse_kinematics_analytical()` - 解析逆运动学
2. `inverse_kinematics_numerical()` - 数值逆运动学
3. `check_singularity()` - 检查奇异点

**关键概念**:
- 几何方法求解逆运动学
- 优化方法求解逆运动学
- 奇异点检测

**提示**:
- 使用余弦定理求解关节角度
- 考虑多解情况（肘部向上/向下）
- 使用scipy.optimize.minimize进行数值优化

### 任务3: 基于动力学的MPC控制 (30分)

**文件**: `dynamics_control/cart_dynamics.py` 和 `dynamics_control/mpc_controller.py`

**需要实现的功能**:
1. `dynamics()` - 连续时间动力学方程
2. `discrete_dynamics()` - 离散时间动力学方程
3. `setup_optimization_problem()` - 设置MPC优化问题
4. `solve_mpc()` - 求解MPC问题

**关键概念**:
- 牛顿第二定律
- 状态空间模型
- 模型预测控制
- 优化问题求解

**提示**:
- 使用牛顿第二定律建立动力学模型
- 使用欧拉积分进行离散化
- 使用cvxpy设置和求解优化问题

### 任务4: 可视化 (10分)

**文件**: `visualization/robot_visualizer.py` 和 `visualization/control_visualizer.py`

**需要实现的功能**:
1. 机器人配置可视化
2. 工作空间可视化
3. 控制结果可视化
4. 误差分析

### 任务5: 交互式演示 (额外加分)

**文件**: `interactive_ik_demo.py` 和 `interactive_ik_advanced.py`

**功能特点**:
1. **基础交互式IK演示**: 点击平面选择目标位置，实时计算关节角度
2. **高级交互式IK演示**: 包含动画效果、轨迹规划和实时反馈
3. **多种IK方法**: 可在解析IK和数值IK之间切换
4. **实时可视化**: 显示关节角度、位置误差和轨迹历史
5. **动画控制**: 可调节动画速度，播放轨迹动画

## 实现步骤

### 第一步：环境准备
```bash
# 安装依赖
pip install -r requirements.txt
```

### 第二步：理解代码结构
1. 阅读 `README.md` 了解项目结构
2. 查看 `examples/simple_example.py` 了解使用方法
3. 理解各个模块的接口

### 第三步：逐步实现
1. **从工具函数开始**: 实现 `robot_kinematics/utils.py` 中的函数
2. **实现正向运动学**: 完成 `ThreeLinkRobot` 类中的FK相关方法
3. **实现逆向运动学**: 完成IK相关方法
4. **实现动力学模型**: 完成 `CartDynamics` 类
5. **实现MPC控制器**: 完成 `MPCController` 类
6. **实现可视化**: 完成可视化功能

### 第四步：测试和验证
```bash
# 运行主程序
python main.py

# 运行简单示例
python examples/simple_example.py

# 测试交互式功能
python test_interactive.py

# 运行交互式演示
python interactive_ik_demo.py
python interactive_ik_advanced.py
```

## 评分标准

### 功能正确性 (80%)
- FK计算准确性 (20%)
- IK求解正确性 (20%)
- MPC控制性能 (25%)
- 可视化效果 (15%)

### 代码质量 (20%)
- 代码结构清晰
- 注释完整
- 错误处理
- 文档规范

## 常见问题

### Q: 如何开始实现？
A: 建议从 `robot_kinematics/utils.py` 中的 `dh_transform_matrix()` 函数开始，这是其他功能的基础。

### Q: 如何处理奇异点？
A: 奇异点是指雅可比矩阵行列式接近0的情况。可以通过检查雅可比矩阵的条件数来检测。

### Q: MPC优化问题求解失败怎么办？
A: 检查约束条件是否合理，权重矩阵是否正定，初始猜测是否合适。

### Q: 可视化不显示怎么办？
A: 确保matplotlib后端配置正确，在Jupyter notebook中使用 `%matplotlib inline`。

## 扩展练习

完成基本任务后，可以尝试以下扩展：

1. **多解处理**: 实现IK的多解选择策略
2. **轨迹规划**: 实现关节空间的轨迹规划
3. **鲁棒控制**: 在MPC中加入不确定性处理
4. **3D机器人**: 扩展到3D空间的三连杆机器人
5. **实时控制**: 实现实时MPC控制

## 提交要求

1. **代码文件**: 完整的Python代码
2. **实验报告**: 包含实现过程、结果分析和讨论
3. **演示**: 运行截图或视频
4. **文档**: 代码注释和README

## 参考资料

- 《机器人学导论》- John J. Craig
- 《现代控制工程》- Katsuhiko Ogata
- 《模型预测控制》- James B. Rawlings
- [DH参数教程](https://en.wikipedia.org/wiki/Denavit%E2%80%93Hartenberg_parameters)
- [MPC教程](https://en.wikipedia.org/wiki/Model_predictive_control)

## 联系方式

如有问题，请通过以下方式联系：
- 课程论坛
- 助教邮箱
- 办公时间

祝学习愉快！ 