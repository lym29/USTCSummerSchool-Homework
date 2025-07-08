"""
测试和比较不同的IK方法
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import time
from robot_kinematics import ThreeLinkRobot
from robot_kinematics.utils import jacobian_matrix


def test_ik_methods():
    """
    测试和比较数值IK和雅可比IK方法
    """
    print("=== Testing and Comparing IK Methods ===")
    
    # 创建机器人
    robot = ThreeLinkRobot(link_lengths=[1.0, 1.0, 0.5])
    
    # 测试目标位置
    test_positions = [
        [1.5, 0, 0],     # 前方
        [0, 1.5, 0],     # 右侧
        [1.0, 1.0, 0],   # 对角线
        [0.5, 0.5, 0],   # 近距离
        [1.8, 0.8, 0],   # 远距离
    ]
    
    print(f"{'Target Position':<15} {'Method':<12} {'Solution':<25} {'Error':<10} {'Time (ms)':<10}")
    print("-" * 80)
    
    for target_pos in test_positions:
        print(f"\n{target_pos}")
        
        # 测试数值IK
        start_time = time.time()
        ik_numerical = robot.inverse_kinematics_numerical(target_pos)
        numerical_time = (time.time() - start_time) * 1000
        
        if ik_numerical is not None:
            actual_pos = robot.get_end_effector_position(ik_numerical)
            error = np.linalg.norm(actual_pos - target_pos)
            print(f"{'':<15} {'Numerical':<12} {str(ik_numerical):<25} {error:.6f} {numerical_time:.2f}")
        else:
            print(f"{'':<15} {'Numerical':<12} {'No solution':<25} {'N/A':<10} {numerical_time:.2f}")
        
        # 测试雅可比IK
        start_time = time.time()
        ik_jacobian = robot.inverse_kinematics_jacobian(target_pos)
        jacobian_time = (time.time() - start_time) * 1000
        
        if ik_jacobian is not None:
            actual_pos = robot.get_end_effector_position(ik_jacobian)
            error = np.linalg.norm(actual_pos - target_pos)
            print(f"{'':<15} {'Jacobian':<12} {str(ik_jacobian):<25} {error:.6f} {jacobian_time:.2f}")
        else:
            print(f"{'':<15} {'Jacobian':<12} {'No solution':<25} {'N/A':<10} {jacobian_time:.2f}")


def test_convergence():
    """
    测试雅可比IK的收敛性
    """
    print("\n=== Testing Jacobian IK Convergence ===")
    
    robot = ThreeLinkRobot(link_lengths=[1.0, 1.0, 0.5])
    target_pos = [1.0, 1.0, 0]
    
    print(f"Target position: {target_pos}")
    print(f"{'Iteration':<10} {'Error':<15} {'Joint Angles':<30}")
    print("-" * 55)
    
    # 使用较小的步长和更多的迭代次数来观察收敛过程
    joint_angles = np.zeros(3)
    
    for i in range(20):
        current_pos = robot.get_end_effector_position(joint_angles)
        error = np.linalg.norm(current_pos[:2] - target_pos[:2])
        
        print(f"{i:<10} {error:<15.6f} {str(joint_angles):<30}")
        
        if error < 1e-6:
            print("Converged!")
            break
        
        # 计算雅可比矩阵
        J = jacobian_matrix(robot, joint_angles)
        J_pos = J[:2, :]
        
        # 使用阻尼最小二乘法
        lambda_damp = 0.01
        J_damped = J_pos.T @ J_pos + lambda_damp * np.eye(J_pos.shape[1])
        J_pinv = np.linalg.solve(J_damped, J_pos.T)
        
        # 计算位置误差
        position_error = np.array(target_pos[:2]) - np.array(current_pos[:2])
        
        # 计算关节角度增量
        delta_theta = J_pinv @ position_error
        delta_theta = 0.1 * delta_theta  # 步长
        
        # 更新关节角度
        joint_angles += delta_theta
        joint_angles = np.arctan2(np.sin(joint_angles), np.cos(joint_angles))


def test_singularity_handling():
    """
    测试奇异点处理
    """
    print("\n=== Testing Singularity Handling ===")
    
    robot = ThreeLinkRobot(link_lengths=[1.0, 1.0, 0.5])
    
    # 测试接近奇异点的配置
    test_configs = [
        [0, 0, 0],           # 奇异点
        [0.1, 0.1, 0],       # 接近奇异点
        [np.pi/2, 0, 0],     # 奇异点
        [np.pi/2 + 0.1, 0.1, 0],  # 接近奇异点
    ]
    
    target_pos = [1.0, 1.0, 0]
    
    for config in test_configs:
        print(f"\nInitial config: {config}")
        
        # 检查是否接近奇异点
        is_singular = robot.check_singularity(config)
        print(f"Is singular: {is_singular}")
        
        # 尝试雅可比IK
        start_time = time.time()
        ik_solution = robot.inverse_kinematics_jacobian(target_pos, initial_guess=config)
        solve_time = (time.time() - start_time) * 1000
        
        if ik_solution is not None:
            actual_pos = robot.get_end_effector_position(ik_solution)
            error = np.linalg.norm(actual_pos - target_pos)
            print(f"Solution: {ik_solution}")
            print(f"Error: {error:.6f}")
            print(f"Time: {solve_time:.2f} ms")
        else:
            print("No solution found")
            print(f"Time: {solve_time:.2f} ms")


def main():
    """
    主函数
    """
    print("IK Methods Comparison Test")
    print("=" * 40)
    
    try:
        # 测试IK方法
        test_ik_methods()
        
        # 测试收敛性
        test_convergence()
        
        # 测试奇异点处理
        test_singularity_handling()
        
        print("\n=== All tests completed ===")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 