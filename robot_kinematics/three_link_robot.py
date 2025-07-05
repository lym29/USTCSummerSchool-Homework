"""
三连杆机器人运动学实现
包含正向运动学(FK)和逆向运动学(IK)
"""

import numpy as np
from scipy.optimize import minimize
from .utils import dh_transform_matrix, jacobian_matrix


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
        # TODO: 学生需要实现这个函数
        # 提示: 
        # 1. 使用DH参数计算每个连杆的变换矩阵
        # 2. 将所有变换矩阵相乘得到末端位置
        # 3. 注意关节角度的累积效应
        
        # 对于平面三连杆机器人，使用简单的几何方法
        # 累积关节角度
        cumulative_theta = 0
        x, y = 0, 0
        
        for i, length in enumerate(self.link_lengths):
            cumulative_theta += joint_angles[i]
            x += length * np.cos(cumulative_theta)
            y += length * np.sin(cumulative_theta)
        
        # 构建齐次变换矩阵
        T = np.eye(4)
        T[:2, 3] = [x, y]
        
        return T
    
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
    
    def inverse_kinematics_analytical(self, target_position, elbow_up=True):
        """
        解析逆运动学 - 使用几何方法求解
        
        参数:
            target_position: 目标位置 [x, y, z]
            elbow_up: 是否使用肘部向上的解
        
        返回:
            关节角度数组 [theta1, theta2, theta3] 或 None (如果无解)
        """
        # TODO: 学生需要实现这个函数
        # 提示:
        # 1. 使用余弦定理求解关节角度
        # 2. 考虑多解情况（肘部向上/向下）
        # 3. 检查解的有效性（在工作空间内）
        
        x, y = target_position[:2]  # 平面机器人，忽略z坐标
        L1, L2, L3 = self.link_lengths
        
        # 计算到目标位置的距离
        r = np.sqrt(x**2 + y**2)
        
        # 检查是否在工作空间内
        max_reach = L1 + L2 + L3
        min_reach = max(0, abs(L1 - L2) - L3)
        
        if r > max_reach or r < min_reach:
            return None
        
        # 计算第一个关节角度（基座旋转）
        theta1 = np.arctan2(y, x)
        
        # 对于三连杆机器人，我们需要考虑第三个连杆的影响
        # 第三个连杆会从第二个连杆的末端延伸L3距离
        # 所以前两个连杆需要达到的位置是目标位置减去第三个连杆的贡献
        
        # 计算前两个连杆需要达到的位置
        # 这里我们假设第三个连杆指向目标方向
        effective_target_r = r - L3
        
        # 检查前两个连杆是否能达到这个位置
        if effective_target_r < 0 or effective_target_r > L1 + L2:
            return None
        
        # 使用余弦定理计算第二个关节角度
        cos_theta2 = (effective_target_r**2 - L1**2 - L2**2) / (2 * L1 * L2)
        
        # 检查解的有效性
        if abs(cos_theta2) > 1:
            return None
        
        if elbow_up:
            theta2 = np.arccos(cos_theta2)
        else:
            theta2 = -np.arccos(cos_theta2)
        
        # 计算第三个关节角度
        # 第三个关节的角度应该使得末端执行器达到目标位置
        # 计算前两个连杆的末端位置
        x2 = L1 * np.cos(theta1) + L2 * np.cos(theta1 + theta2)
        y2 = L1 * np.sin(theta1) + L2 * np.sin(theta1 + theta2)
        
        # 计算从第二个关节到目标的向量
        dx = x - x2
        dy = y - y2
        
        # 第三个关节的角度（相对于第二个连杆）
        theta3 = np.arctan2(dy, dx) - (theta1 + theta2)
        
        # 确保角度在合理范围内
        theta3 = np.arctan2(np.sin(theta3), np.cos(theta3))
        
        return np.array([theta1, theta2, theta3])
    
    def inverse_kinematics_numerical(self, target_position, initial_guess=None):
        """
        数值逆运动学 - 使用优化方法求解
        
        参数:
            target_position: 目标位置 [x, y, z]
            initial_guess: 初始猜测的关节角度
        
        返回:
            关节角度数组 [theta1, theta2, theta3]
        """
        # TODO: 学生需要实现这个函数
        # 提示:
        # 1. 定义目标函数（当前位置到目标位置的距离）
        # 2. 使用scipy.optimize.minimize进行优化
        # 3. 添加关节角度约束
        
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
        
        参数:
            joint_angles: 关节角度数组
        
        返回:
            bool: 是否处于奇异点
        """
        # TODO: 学生需要实现这个函数
        # 提示: 计算雅可比矩阵的行列式，如果接近0则为奇异点
        
        J = jacobian_matrix(self, joint_angles)
        det = np.linalg.det(J[:2, :2])  # 只考虑位置雅可比
        
        return abs(det) < 1e-6
    
    def get_workspace_boundary(self, num_points=100):
        """
        计算机器人的工作空间边界
        
        参数:
            num_points: 采样点数量
        
        返回:
            x_coords, y_coords: 工作空间边界坐标
        """
        # TODO: 学生需要实现这个函数
        # 提示: 通过采样关节角度空间来获得工作空间边界
        
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