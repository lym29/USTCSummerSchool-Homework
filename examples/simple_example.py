"""
简单示例：展示如何使用机器人控制框架
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import matplotlib.pyplot as plt

# 导入我们的模块
from robot_kinematics import ThreeLinkRobot
from dynamics_control import CartDynamics, MPCController
from visualization import RobotVisualizer, ControlVisualizer


def simple_fk_example():
    """
    简单的正向运动学示例
    """
    print("=== Simple FK Example ===")
    
    # 创建三连杆机器人
    robot = ThreeLinkRobot(link_lengths=[1.0, 1.0, 0.5])
    
    # 设置关节角度
    joint_angles = [np.pi/4, np.pi/4, 0]  # 45度, 45度, 0度
    
    # 计算末端位置
    end_position = robot.get_end_effector_position(joint_angles)
    
    print(f"Joint angles: {joint_angles}")
    print(f"End effector position: {end_position}")
    
    # 可视化
    viz = RobotVisualizer(robot)
    viz.plot_robot_configuration(joint_angles, title="Simple FK Example")


def simple_ik_example():
    """
    简单的逆向运动学示例
    """
    print("\n=== Simple IK Example ===")
    
    # 创建三连杆机器人
    robot = ThreeLinkRobot(link_lengths=[1.0, 1.0, 0.5])
    
    # 设置目标位置
    target_position = [1.5, 0.5, 0]
    
    # 求解逆运动学
    joint_angles = robot.inverse_kinematics_numerical(target_position)
    
    if joint_angles is not None:
        print(f"Target position: {target_position}")
        print(f"Calculated joint angles: {joint_angles}")
        
        # 验证结果
        actual_position = robot.get_end_effector_position(joint_angles)
        error = np.linalg.norm(actual_position - target_position)
        print(f"Position error: {error}")
        
        # 可视化
        viz = RobotVisualizer(robot)
        viz.plot_robot_configuration(joint_angles, target_position, 
                                   title="Simple IK Example")
    else:
        print("No solution found")


def simple_mpc_example():
    """
    简单的MPC控制示例
    """
    print("\n=== Simple MPC Example ===")
    
    # 创建动力学模型
    cart = CartDynamics(mass=1.0, damping=0.1)
    
    # 创建MPC控制器
    mpc = MPCController(cart, horizon=5, dt=0.1)
    
    # 设置初始和目标状态
    initial_state = [0.0, 0.0]  # 位置=0, 速度=0
    target_state = [1.0, 0.0]   # 目标位置=1, 目标速度=0
    
    # 运行仿真
    time_array, state_history, control_history = mpc.simulate_closed_loop(
        initial_state, target_state, simulation_time=3.0, dt=0.1
    )
    
    print(f"Initial state: {initial_state}")
    print(f"Target state: {target_state}")
    print(f"Final state: {state_history[-1]}")
    
    # 可视化结果
    viz = ControlVisualizer()
    viz.plot_control_results(time_array, state_history, control_history, 
                           target_state, title="Simple MPC Example")


def main():
    """
    运行所有简单示例
    """
    print("Robot Control Framework - Simple Examples")
    print("=" * 40)
    
    try:
        # 运行示例
        simple_fk_example()
        simple_ik_example()
        simple_mpc_example()
        
        print("\n=== All examples completed ===")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Please ensure all TODO-marked functions have been implemented")


if __name__ == "__main__":
    main() 