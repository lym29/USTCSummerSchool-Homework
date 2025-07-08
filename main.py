"""
机器人控制编程作业主程序
包含FK、IK和MPC控制的演示
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib.pyplot as plt

from robot_kinematics import ThreeLinkRobot
from dynamics_control import CartDynamics, MPCController
from visualization import RobotVisualizer, ControlVisualizer


def test_forward_kinematics():
    """
    测试正向运动学
    """
    print("=== Testing Forward Kinematics (FK) ===")
    
    # 创建三连杆机器人
    robot = ThreeLinkRobot(link_lengths=[1.0, 1.0, 0.5])
    
    # 测试不同的关节角度
    test_angles = [
        [0, 0, 0],           # 零角度
        [np.pi/4, np.pi/4, 0],  # 45度
        [np.pi/2, -np.pi/4, 0], # 90度和-45度
        [np.pi, np.pi/2, 0]     # 180度和90度
    ]
    
    for i, angles in enumerate(test_angles):
        print(f"\nTest {i+1}: Joint angles = {[f'{a:.2f}' for a in angles]}")
        
        # 计算末端位置
        end_pos = robot.get_end_effector_position(angles)
        print(f"End effector position: [{end_pos[0]:.3f}, {end_pos[1]:.3f}, {end_pos[2]:.3f}]")
        
        # 检查奇异点
        is_singular = robot.check_singularity(angles)
        print(f"Is singular point: {is_singular}")


def test_inverse_kinematics():
    """
    测试逆向运动学
    """
    print("\n=== Testing Inverse Kinematics (IK) ===")
    
    # 创建三连杆机器人
    robot = ThreeLinkRobot(link_lengths=[1.0, 1.0, 0.5])
    
    # 测试不同的目标位置
    test_positions = [
        [1.5, 0, 0],     # 前方
        [0, 1.5, 0],     # 右侧
        [1.0, 1.0, 0],   # 对角线
        [0.5, 0.5, 0]    # 近距离
    ]
    
    for i, target_pos in enumerate(test_positions):
        print(f"\nTest {i+1}: Target position = {target_pos}")
        
        # 数值逆运动学
        ik_numerical = robot.inverse_kinematics_numerical(target_pos)
        if ik_numerical is not None:
            print(f"Numerical solution: [{', '.join([f'{a:.3f}' for a in ik_numerical])}]")
            
            # 验证解的正确性
            actual_pos = robot.get_end_effector_position(ik_numerical)
            error = np.linalg.norm(actual_pos - target_pos)
            print(f"Position error: {error:.6f}")
        else:
            print("Numerical solution: No solution")


def test_mpc_control():
    """
    测试MPC控制
    """
    print("\n=== Testing MPC Control ===")
    
    # 创建动力学模型
    cart_dynamics = CartDynamics(mass=1.0, damping=0.1)
    
    # 创建MPC控制器
    mpc_controller = MPCController(cart_dynamics, horizon=10, dt=0.1)
    
    # 设置初始状态和目标状态
    initial_state = np.array([0.0, 0.0])  # 位置=0, 速度=0
    target_state = np.array([2.0, 0.0])   # 目标位置=2, 目标速度=0
    
    print(f"Initial state: position={initial_state[0]:.1f}m, velocity={initial_state[1]:.1f}m/s")
    print(f"Target state: position={target_state[0]:.1f}m, velocity={target_state[1]:.1f}m/s")
    
    # 闭环仿真
    simulation_time = 5.0
    dt = 0.1
    
    time_array, state_history, control_history = mpc_controller.simulate_closed_loop(
        initial_state, target_state, simulation_time, dt
    )
    
    print(f"Simulation completed, time steps: {len(time_array)}")
    print(f"Final position: {state_history[-1, 0]:.3f}m")
    print(f"Final velocity: {state_history[-1, 1]:.3f}m/s")
    
    return time_array, state_history, control_history, target_state


def visualize_results():
    """
    可视化结果
    """
    print("\n=== Visualizing Results ===")
    
    # 创建机器人
    robot = ThreeLinkRobot(link_lengths=[1.0, 1.0, 0.5])
    
    # 创建可视化器
    robot_viz = RobotVisualizer(robot)
    control_viz = ControlVisualizer()
    
    # 1. 绘制机器人工作空间
    print("Plotting robot workspace...")
    robot_viz.plot_workspace()
    
    # 2. 绘制机器人配置
    print("Plotting robot configuration...")
    joint_angles = [np.pi/4, np.pi/4, 0]
    target_position = [1.5, 0.5, 0]
    robot_viz.plot_robot_configuration(joint_angles, target_position)
    
    # 3. 测试MPC控制并可视化
    print("Testing MPC control...")
    time_array, state_history, control_history, target_state = test_mpc_control()
    
    # 绘制控制结果
    print("Plotting control results...")
    control_viz.plot_control_results(time_array, state_history, control_history, target_state)
    
    # 绘制相图
    print("Plotting phase portrait...")
    control_viz.plot_phase_portrait(state_history, target_state)
    
    # 绘制误差分析
    print("Plotting error analysis...")
    rmse_pos, rmse_vel = control_viz.plot_error_analysis(
        time_array, state_history, target_state
    )
    print(f"Position RMSE: {rmse_pos:.4f}")
    print(f"Velocity RMSE: {rmse_vel:.4f}")


def run_student_exercises():
    """
    运行学生练习
    """
    print("\n=== Student Exercises ===")
    print("Please complete the following exercises:")
    print("1. Implement DH transformation matrix calculation in robot_kinematics/utils.py")
    print("2. Implement FK and IK in robot_kinematics/three_link_robot.py")
    print("3. Implement dynamics model in dynamics_control/cart_dynamics.py")
    print("4. Implement MPC controller in dynamics_control/mpc_controller.py")
    print("5. Implement visualization functions in visualization/")
    print("\nRun this program after completion to see results!")


def main():
    """
    主函数
    """
    print("Robot Control Programming Assignment")
    print("=" * 50)
    
    try:
        # 测试正向运动学
        test_forward_kinematics()
        
        # 测试逆向运动学
        test_inverse_kinematics()
        
        # 测试MPC控制
        test_mpc_control()
        
        # 可视化结果
        visualize_results()
        
        print("\n=== All tests completed ===")
        
    except Exception as e:
        print(f"\nError: {e}")
        print("Please check if all TODO-marked functions have been implemented")
        run_student_exercises()


if __name__ == "__main__":
    main() 