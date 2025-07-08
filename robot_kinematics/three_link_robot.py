"""
三连杆机器人运动学实现
包含正向运动学(FK)和逆向运动学(IK)
"""

import numpy as np
from scipy.optimize import minimize
from .utils import jacobian_matrix


class ThreeLinkRobot:
    """
    三连杆平面机器人
    所有关节都在XY平面内，第三个关节为末端执行器
    """
    
    def __init__(self, link_lengths=[1.0, 1.0, 0.5]):
        """
        初始化三连杆机器人
        
        参数:
            link_lengths: 连杆长度列表 [L1, L2, L3]
        """
        self.link_lengths = np.array(link_lengths)
        self.n_joints = 3
        
        # DH参数 (a, alpha, d, theta)
        # 对于平面机器人，alpha=0, d=0
        self.dh_params = []
        for i, length in enumerate(link_lengths):
            self.dh_params.append([length, 0, 0, 0])  # theta将在FK中设置
    
    def forward_kinematics(self, joint_angles):
        """
        正向运动学 - 根据关节角度计算末端执行器位置
        
        参数:
            joint_angles: 关节角度数组 [theta1, theta2, theta3] (弧度)
        
        返回:
            4x4 齐次变换矩阵，表示末端执行器的位置和姿态
        """
        # TODO: 实现Forward Kinematic
        # 提示: 
        # 1. 使用DH参数计算每个连杆的变换矩阵
        # 2. 将所有变换矩阵相乘得到末端位置
        # 3. 注意关节角度的累积效应
        
        # 对于平面三连杆机器人，使用简单的几何方法
        # 累积关节角度
        raise NotImplementedError("Not implemented")
    
    def get_end_effector_position(self, joint_angles):
        """
        获取末端执行器的位置
        
        参数:
            joint_angles: 关节角度数组
        
        返回:
            [x, y, z] 位置坐标
        """
        T = self.forward_kinematics(joint_angles)
        return T[:3, 3]
    
    def inverse_kinematics_optimization(self, target_position, initial_guess=None):
        """
        优化逆运动学 - 使用优化方法求解
        
        参数:
            target_position: 目标位置 [x, y, z]
            initial_guess: 初始猜测的关节角度
        
        返回:
            关节角度数组 [theta1, theta2, theta3]
        """
        
        if initial_guess is None:
            initial_guess = np.zeros(self.n_joints)
        
        def objective_function(joint_angles):
            """目标函数：最小化当前位置到目标位置的距离"""
            current_pos = self.get_end_effector_position(joint_angles)
            return np.linalg.norm(current_pos[:2] - target_position[:2])
        
        # 设置关节角度约束 (-π 到 π)
        bounds = [(-np.pi, np.pi) for _ in range(self.n_joints)]
        
        # 使用优化算法求解
        result = minimize(
            objective_function,
            initial_guess,
            method='L-BFGS-B',
            bounds=bounds,
            options={'maxiter': 2000, 'ftol': 1e-6}
        )
        
        if result.success and result.fun < 0.1:  # 确保误差足够小
            return result.x
        else:
            return None
    
    def check_singularity(self, joint_angles):
        """
        检查机器人是否处于奇异点
        
        奇异点检测的目的：
        1. 识别机器人配置中的奇异点，这些点会导致雅可比矩阵接近奇异
        2. 在奇异点附近，IK求解可能不稳定或无法收敛
        3. 帮助用户了解机器人的运动限制和潜在问题区域
        4. 为路径规划和运动控制提供重要的几何信息
        
        调用位置：
        - main.py: test_forward_kinematics() 函数中用于测试不同关节配置
        - test_interactive.py: test_singularity() 函数中专门测试奇异点检测
        - 可视化程序中可以用于标记奇异配置

        参数:
            joint_angles: 关节角度数组
        
        返回:
            bool: 是否处于奇异点
        """
        # 计算雅可比矩阵
        J = jacobian_matrix(self, joint_angles)
        
        # 对于平面机器人，只考虑位置雅可比（前2x2子矩阵）
        position_jacobian = J[:2, :2]
        
        # 计算雅可比矩阵的行列式
        det = np.linalg.det(position_jacobian)
        
        # 如果行列式接近0，则认为处于奇异点
        # 阈值设为1e-6，可以根据需要调整
        return abs(det) < 1e-6
    
    def get_workspace_boundary(self, num_points=100):
        """
        计算机器人的工作空间边界
        
        参数:
            num_points: 采样点数量
        
        返回:
            x_coords, y_coords: 工作空间边界坐标
        """
        
        theta1_range = np.linspace(-np.pi, np.pi, num_points)
        theta2_range = np.linspace(-np.pi, np.pi, num_points)
        
        x_coords = []
        y_coords = []
        
        for theta1 in theta1_range:
            for theta2 in theta2_range:
                joint_angles = [theta1, theta2, 0]
                pos = self.get_end_effector_position(joint_angles)
                x_coords.append(pos[0])
                y_coords.append(pos[1])
        
        return np.array(x_coords), np.array(y_coords)
    
    def inverse_kinematics_jacobian(self, target_position, initial_guess=None, max_iterations=200, tolerance=1e-4, step_size=0.05):
        """
        基于雅可比矩阵的逆运动学 - 使用雅可比矩阵伪逆迭代求解
        
        原理：
        1. 使用雅可比矩阵建立关节速度与末端执行器速度的关系
        2. 通过雅可比矩阵的伪逆计算关节角度增量
        3. 迭代更新关节角度直到收敛到目标位置
        
        优势：
        - 计算速度快，适合实时应用
        - 可以处理冗余机器人
        - 易于添加关节限制和避障约束
        
        参数:
            target_position: 目标位置 [x, y, z]
            initial_guess: 初始猜测的关节角度
            max_iterations: 最大迭代次数
            tolerance: 收敛容差
            step_size: 步长参数（阻尼因子）
        
        返回:
            关节角度数组 [theta1, theta2, theta3] 或 None (如果未收敛)
        """
        # TODO: 实现基于雅可比矩阵的逆运动学求解
        # 提示:
        # 1. 使用雅可比矩阵建立线性关系：Δx = J * Δθ
        # 2. 计算雅可比矩阵的伪逆：Δθ = J^+ * Δx
        # 3. 迭代更新关节角度：θ_new = θ_old + Δθ
        # 4*. (进阶) 添加阻尼因子避免奇异点问题 (Damped least squares)
        
        raise NotImplementedError("Not implemented")