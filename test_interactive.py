"""
测试交互式IK功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from robot_kinematics import ThreeLinkRobot


def test_basic_ik():
    """
    测试基本IK功能
    """
    print("=== Testing Basic IK Functionality ===")
    
    # 创建机器人
    robot = ThreeLinkRobot(link_lengths=[1.0, 1.0, 0.5])
    
    # 测试几个目标位置
    test_positions = [
        [1.5, 0, 0],     # 前方
        [0, 1.5, 0],     # 右侧
        [1.0, 1.0, 0],   # 对角线
        [0.5, 0.5, 0],   # 近距离
        [2.0, 0, 0],     # 远距离（可能不可达）
    ]
    
    for i, target_pos in enumerate(test_positions):
        print(f"\nTest {i+1}: Target position = {target_pos}")
        
        # 数值IK
        ik_numerical = robot.inverse_kinematics_numerical(target_pos)
        if ik_numerical is not None:
            print(f"  Numerical IK solution: {ik_numerical}")
            actual_pos = robot.get_end_effector_position(ik_numerical)
            error = np.linalg.norm(actual_pos - target_pos)
            print(f"  Position error: {error:.6f}")
        else:
            print("  Numerical IK: No solution")


def test_workspace():
    """
    测试工作空间计算
    """
    print("\n=== Testing Workspace Calculation ===")
    
    robot = ThreeLinkRobot(link_lengths=[1.0, 1.0, 0.5])
    
    # 计算工作空间边界
    x_coords, y_coords = robot.get_workspace_boundary(num_points=100)
    
    print(f"Workspace points: {len(x_coords)}")
    print(f"X range: [{min(x_coords):.2f}, {max(x_coords):.2f}]")
    print(f"Y range: [{min(y_coords):.2f}, {max(y_coords):.2f}]")
    
    # 检查一些点是否在工作空间内
    test_points = [
        [1.0, 0, 0],     # 应该可达
        [2.5, 0, 0],     # 可能不可达
        [0, 2.5, 0],     # 可能不可达
        [0.5, 0.5, 0],   # 应该可达
    ]
    
    for point in test_points:
        ik_solution = robot.inverse_kinematics_numerical(point)
        reachable = ik_solution is not None
        print(f"Point {point}: {'Reachable' if reachable else 'Unreachable'}")


def test_singularity():
    """
    测试奇异点检测
    """
    print("\n=== Testing Singularity Detection ===")
    
    robot = ThreeLinkRobot(link_lengths=[1.0, 1.0, 0.5])
    
    # 测试一些关节配置
    test_configurations = [
        [0, 0, 0],           # 零配置
        [np.pi/2, 0, 0],     # 第一个关节90度
        [0, np.pi, 0],       # 第二个关节180度（奇异点）
        [np.pi/4, np.pi/4, 0], # 正常配置
    ]
    
    for i, config in enumerate(test_configurations):
        is_singular = robot.check_singularity(config)
        print(f"Configuration {i+1} {config}: {'Singular' if is_singular else 'Normal'}")


def main():
    """
    主函数
    """
    print("Interactive IK Functionality Test")
    print("=" * 40)
    
    try:
        # 运行测试
        test_basic_ik()
        test_workspace()
        test_singularity()
        
        print("\n=== All tests completed ===")
        print("If all tests pass, you can run interactive demos:")
        print("  python interactive_ik_demo.py")
        print("  python interactive_ik_advanced.py")
        
    except Exception as e:
        print(f"Test failed: {e}")
        print("Please check if all TODO-marked functions have been implemented")


if __name__ == "__main__":
    main() 