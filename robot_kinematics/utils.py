"""
运动学计算工具函数
"""

import numpy as np
from scipy.spatial.transform import Rotation


def dh_transform_matrix(a, alpha, d, theta):
    """
    计算DH参数对应的齐次变换矩阵
    
    参数:
        a: 连杆长度
        alpha: 连杆扭角
        d: 连杆偏移
        theta: 关节角
    
    返回:
        4x4 齐次变换矩阵
    """
    # TODO: 学生需要实现这个函数
    # 提示: 使用DH参数计算旋转和平移矩阵，然后组合成齐次变换矩阵
    
    # 计算旋转矩阵
    ct = np.cos(theta)
    st = np.sin(theta)
    ca = np.cos(alpha)
    sa = np.sin(alpha)
    
    # 构建齐次变换矩阵
    T = np.array([
        [ct, -st*ca, st*sa, a*ct],
        [st, ct*ca, -ct*sa, a*st],
        [0, sa, ca, d],
        [0, 0, 0, 1]
    ])
    
    return T


def rotation_matrix_to_euler(R):
    """
    将旋转矩阵转换为欧拉角 (ZYX顺序)
    
    参数:
        R: 3x3 旋转矩阵
    
    返回:
        [roll, pitch, yaw] 欧拉角 (弧度)
    """
    # TODO: 学生需要实现这个函数
    # 提示: 使用scipy.spatial.transform.Rotation或手动计算
    
    # 使用scipy的方法
    r = Rotation.from_matrix(R)
    euler = r.as_euler('xyz')
    return euler


def euler_to_rotation_matrix(roll, pitch, yaw):
    """
    将欧拉角转换为旋转矩阵 (ZYX顺序)
    
    参数:
        roll, pitch, yaw: 欧拉角 (弧度)
    
    返回:
        3x3 旋转矩阵
    """
    # TODO: 学生需要实现这个函数
    # 提示: 使用scipy.spatial.transform.Rotation或手动计算
    
    # 使用scipy的方法
    r = Rotation.from_euler('xyz', [roll, pitch, yaw])
    return r.as_matrix()


def jacobian_matrix(robot, joint_angles):
    """
    计算机器人的雅可比矩阵
    
    参数:
        robot: 机器人对象
        joint_angles: 关节角度数组
    
    返回:
        6xN 雅可比矩阵 (N为关节数)
    """
    # TODO: 学生需要实现这个函数
    # 提示: 使用数值微分方法计算雅可比矩阵
    
    epsilon = 1e-6
    n_joints = len(joint_angles)
    J = np.zeros((6, n_joints))
    
    # 计算当前末端位置
    current_pose = robot.forward_kinematics(joint_angles)
    current_pos = current_pose[:3, 3]
    current_rot = current_pose[:3, :3]
    
    # 数值微分计算雅可比矩阵
    for i in range(n_joints):
        # 扰动第i个关节
        perturbed_angles = joint_angles.copy()
        perturbed_angles[i] += epsilon
        
        # 计算扰动后的位置
        perturbed_pose = robot.forward_kinematics(perturbed_angles)
        perturbed_pos = perturbed_pose[:3, 3]
        perturbed_rot = perturbed_pose[:3, :3]
        
        # 计算位置雅可比
        J[:3, i] = (perturbed_pos - current_pos) / epsilon
        
        # 计算姿态雅可比 (简化处理)
        # 这里可以进一步改进为角速度雅可比
        J[3:, i] = np.zeros(3)
    
    return J 