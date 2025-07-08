"""
Robot Kinematics Visualization
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from mpl_toolkits.mplot3d import Axes3D


class RobotVisualizer:
    """
    Three-link robot visualization class
    """
    
    def __init__(self, robot):
        """
        Initialize visualizer
        
        Parameters:
            robot: Three-link robot object
        """
        self.robot = robot
        self.fig = None
        self.ax = None
    
    def plot_robot_configuration(self, joint_angles, target_position=None, 
                                show_workspace=True, title="Robot Configuration"):
        """
        Plot robot configuration
        
        Parameters:
            joint_angles: Joint angles
            target_position: Target position
            show_workspace: Whether to show workspace
            title: Plot title
        """
        # Create figure
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        
        # Calculate joint positions
        joint_positions = self._calculate_joint_positions(joint_angles)
        
        # Draw links
        for i in range(len(joint_positions) - 1):
            start_pos = joint_positions[i]
            end_pos = joint_positions[i + 1]
            self.ax.plot([start_pos[0], end_pos[0]], 
                        [start_pos[1], end_pos[1]], 
                        'b-', linewidth=3, label=f'Link {i+1}' if i == 0 else "")
        
        # Draw joints
        for i, pos in enumerate(joint_positions):
            self.ax.plot(pos[0], pos[1], 'ro', markersize=8, 
                        label=f'Joint {i+1}' if i == 0 else "")
        
        # Draw target position
        if target_position is not None:
            self.ax.plot(target_position[0], target_position[1], 'g*', 
                        markersize=15, label='Target')
        
        # Show workspace
        if show_workspace:
            x_coords, y_coords = self.robot.get_workspace_boundary()
            self.ax.scatter(x_coords, y_coords, c='lightblue', alpha=0.3, 
                           s=1, label='Workspace')
        
        # Set plot properties
        self.ax.set_xlabel('X (m)')
        self.ax.set_ylabel('Y (m)')
        self.ax.set_title(title)
        self.ax.legend()
        self.ax.grid(True)
        self.ax.set_aspect('equal')
        
        # Set axis limits
        max_reach = sum(self.robot.link_lengths)
        self.ax.set_xlim(-max_reach*1.2, max_reach*1.2)
        self.ax.set_ylim(-max_reach*1.2, max_reach*1.2)
        
        plt.tight_layout()
        plt.show()
    
    def _calculate_joint_positions(self, joint_angles):
        """
        Calculate joint positions
        
        Parameters:
            joint_angles: Joint angles
        
        Returns:
            joint_positions: List of joint positions
        """  
        joint_positions = [np.array([0, 0])]  # Base position
        
        # Accumulate joint angles
        cumulative_theta = 0
        
        for i, length in enumerate(self.robot.link_lengths):
            cumulative_theta += joint_angles[i]
            
            # Calculate current joint position
            x = joint_positions[-1][0] + length * np.cos(cumulative_theta)
            y = joint_positions[-1][1] + length * np.sin(cumulative_theta)
            
            joint_positions.append(np.array([x, y]))
        
        return joint_positions
    
    def animate_robot_motion(self, joint_angle_sequence, target_positions=None, 
                           interval=100, save_path=None):
        """
        动画显示机器人运动
        
        参数:
            joint_angle_sequence: 关节角度序列
            target_positions: 目标位置序列
            interval: 动画间隔 (ms)
            save_path: 保存路径
        """
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # 初始化图形元素
        lines = []
        joints = []
        targets = []
        
        # 创建连杆线条
        for i in range(len(self.robot.link_lengths)):
            line, = ax.plot([], [], 'b-', linewidth=3)
            lines.append(line)
        
        # 创建关节点
        for i in range(len(self.robot.link_lengths) + 1):
            joint, = ax.plot([], [], 'ro', markersize=8)
            joints.append(joint)
        
        # 创建目标点
        if target_positions is not None:
            target, = ax.plot([], [], 'g*', markersize=15)
            targets.append(target)
        
        # 设置坐标轴
        max_reach = sum(self.robot.link_lengths)
        ax.set_xlim(-max_reach*1.2, max_reach*1.2)
        ax.set_ylim(-max_reach*1.2, max_reach*1.2)
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_title('Robot Motion Animation')
        ax.grid(True)
        ax.set_aspect('equal')
        
        def animate(frame):
            # 更新关节位置
            joint_positions = self._calculate_joint_positions(
                joint_angle_sequence[frame]
            )
            
            # 更新连杆
            for i, line in enumerate(lines):
                start_pos = joint_positions[i]
                end_pos = joint_positions[i + 1]
                line.set_data([start_pos[0], end_pos[0]], 
                             [start_pos[1], end_pos[1]])
            
            # 更新关节
            for i, joint in enumerate(joints):
                pos = joint_positions[i]
                joint.set_data([pos[0]], [pos[1]])
            
            # 更新目标
            if target_positions is not None and frame < len(target_positions):
                target = targets[0]
                target.set_data([target_positions[frame][0]], 
                               [target_positions[frame][1]])
            
            return lines + joints + targets
        
        # 创建动画
        anim = FuncAnimation(fig, animate, frames=len(joint_angle_sequence),
                           interval=interval, blit=True, repeat=True)
        
        # 保存动画
        if save_path:
            anim.save(save_path, writer='pillow')
        
        plt.show()
        return anim
    
    def plot_workspace(self, num_points=1000):
        """
        绘制机器人工作空间
        
        参数:
            num_points: 采样点数量
        """
        x_coords, y_coords = self.robot.get_workspace_boundary(num_points)
        
        plt.figure(figsize=(10, 8))
        plt.scatter(x_coords, y_coords, c='blue', alpha=0.6, s=1)
        plt.xlabel('X (m)')
        plt.ylabel('Y (m)')
        plt.title('Robot Workspace')
        plt.grid(True)
        plt.axis('equal')
        plt.show()
    
    def plot_joint_trajectories(self, joint_angle_sequence, time_array=None):
        """
        绘制关节轨迹
        
        参数:
            joint_angle_sequence: 关节角度序列
            time_array: 时间数组
        """
        if time_array is None:
            time_array = np.arange(len(joint_angle_sequence))
        
        joint_angles = np.array(joint_angle_sequence)
        
        plt.figure(figsize=(12, 8))
        
        for i in range(self.robot.n_joints):
            plt.subplot(self.robot.n_joints, 1, i + 1)
            plt.plot(time_array, joint_angles[:, i], 'b-', linewidth=2)
            plt.ylabel(f'Joint {i+1} (rad)')
            plt.grid(True)
            
            if i == self.robot.n_joints - 1:
                plt.xlabel('Time (s)')
        
        plt.suptitle('Joint Trajectories')
        plt.tight_layout()
        plt.show() 