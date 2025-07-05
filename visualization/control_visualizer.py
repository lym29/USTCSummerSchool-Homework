"""
Control Results Visualization
"""

import numpy as np
import matplotlib.pyplot as plt


class ControlVisualizer:
    """
    Control results visualization class
    """
    
    def __init__(self):
        """
        Initialize visualizer
        """
        pass
    
    def plot_control_results(self, time_array, state_history, control_history, 
                           target_state=None, title="Control Results"):
        """
        Plot control results
        
        Parameters:
            time_array: Time array
            state_history: State history
            control_history: Control history
            target_state: Target state
            title: Plot title
        """
        # TODO: Students need to implement this function
        # Hint: Plot state trajectories, control inputs and target state
        
        fig, axes = plt.subplots(3, 1, figsize=(12, 10))
        
        # Plot position
        axes[0].plot(time_array, state_history[:, 0], 'b-', linewidth=2, label='Position')
        if target_state is not None:
            axes[0].axhline(y=target_state[0], color='r', linestyle='--', label='Target Position')
        axes[0].set_ylabel('Position (m)')
        axes[0].grid(True)
        axes[0].legend()
        
        # Plot velocity
        axes[1].plot(time_array, state_history[:, 1], 'g-', linewidth=2, label='Velocity')
        if target_state is not None:
            axes[1].axhline(y=target_state[1], color='r', linestyle='--', label='Target Velocity')
        axes[1].set_ylabel('Velocity (m/s)')
        axes[1].grid(True)
        axes[1].legend()
        
        # Plot control input
        axes[2].plot(time_array[:-1], control_history, 'r-', linewidth=2, label='Control Force')
        axes[2].set_xlabel('Time (s)')
        axes[2].set_ylabel('Force (N)')
        axes[2].grid(True)
        axes[2].legend()
        
        plt.suptitle(title)
        plt.tight_layout()
        plt.show()
    
    def plot_phase_portrait(self, state_history, target_state=None, title="Phase Portrait"):
        """
        Plot phase portrait
        
        Parameters:
            state_history: State history
            target_state: Target state
            title: Plot title
        """
        # TODO: Students need to implement this function
        # Hint: Plot position-velocity phase portrait
        
        plt.figure(figsize=(10, 8))
        
        # Plot trajectory
        plt.plot(state_history[:, 0], state_history[:, 1], 'b-', linewidth=2, label='Trajectory')
        
        # Plot start and end points
        plt.plot(state_history[0, 0], state_history[0, 1], 'go', markersize=10, label='Start')
        plt.plot(state_history[-1, 0], state_history[-1, 1], 'ro', markersize=10, label='End')
        
        # Plot target point
        if target_state is not None:
            plt.plot(target_state[0], target_state[1], 'k*', markersize=15, label='Target')
        
        plt.xlabel('Position (m)')
        plt.ylabel('Velocity (m/s)')
        plt.title(title)
        plt.grid(True)
        plt.legend()
        plt.axis('equal')
        plt.show()
    
    def plot_control_comparison(self, time_arrays, state_histories, control_histories, 
                              labels, target_state=None, title="Control Comparison"):
        """
        比较不同控制器的性能
        
        参数:
            time_arrays: 时间数组列表
            state_histories: 状态历史列表
            control_histories: 控制历史列表
            labels: 标签列表
            target_state: 目标状态
            title: 图表标题
        """
        # TODO: 学生需要实现这个函数
        # 提示: 在同一图中绘制不同控制器的结果
        
        colors = ['b', 'g', 'r', 'c', 'm', 'y']
        
        fig, axes = plt.subplots(3, 1, figsize=(12, 10))
        
        for i, (time_array, state_history, control_history, label) in enumerate(
            zip(time_arrays, state_histories, control_histories, labels)
        ):
            color = colors[i % len(colors)]
            
            # 绘制位置
            axes[0].plot(time_array, state_history[:, 0], color=color, 
                        linewidth=2, label=f'{label} Position')
            
            # 绘制速度
            axes[1].plot(time_array, state_history[:, 1], color=color, 
                        linewidth=2, label=f'{label} Velocity')
            
            # 绘制控制输入
            axes[2].plot(time_array[:-1], control_history, color=color, 
                        linewidth=2, label=f'{label} Control')
        
        # 绘制目标
        if target_state is not None:
            for ax in axes[:2]:
                ax.axhline(y=target_state[0] if ax == axes[0] else target_state[1], 
                          color='k', linestyle='--', alpha=0.5, label='Target')
        
        # 设置标签
        axes[0].set_ylabel('Position (m)')
        axes[0].grid(True)
        axes[0].legend()
        
        axes[1].set_ylabel('Velocity (m/s)')
        axes[1].grid(True)
        axes[1].legend()
        
        axes[2].set_xlabel('Time (s)')
        axes[2].set_ylabel('Force (N)')
        axes[2].grid(True)
        axes[2].legend()
        
        plt.suptitle(title)
        plt.tight_layout()
        plt.show()
    
    def plot_error_analysis(self, time_array, state_history, target_state, title="Error Analysis"):
        """
        绘制误差分析
        
        参数:
            time_array: 时间数组
            state_history: 状态历史
            target_state: 目标状态
            title: 图表标题
        """
        # TODO: 学生需要实现这个函数
        # 提示: 计算并绘制位置误差和速度误差
        
        # 计算误差
        position_error = state_history[:, 0] - target_state[0]
        velocity_error = state_history[:, 1] - target_state[1]
        
        # 计算误差统计
        rmse_position = np.sqrt(np.mean(position_error**2))
        rmse_velocity = np.sqrt(np.mean(velocity_error**2))
        
        fig, axes = plt.subplots(2, 1, figsize=(12, 8))
        
        # 绘制位置误差
        axes[0].plot(time_array, position_error, 'r-', linewidth=2, label='Position Error')
        axes[0].axhline(y=0, color='k', linestyle='--', alpha=0.5)
        axes[0].set_ylabel('Position Error (m)')
        axes[0].grid(True)
        axes[0].legend()
        axes[0].text(0.02, 0.98, f'RMSE: {rmse_position:.4f}', 
                    transform=axes[0].transAxes, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        # 绘制速度误差
        axes[1].plot(time_array, velocity_error, 'b-', linewidth=2, label='Velocity Error')
        axes[1].axhline(y=0, color='k', linestyle='--', alpha=0.5)
        axes[1].set_xlabel('Time (s)')
        axes[1].set_ylabel('Velocity Error (m/s)')
        axes[1].grid(True)
        axes[1].legend()
        axes[1].text(0.02, 0.98, f'RMSE: {rmse_velocity:.4f}', 
                    transform=axes[1].transAxes, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.suptitle(title)
        plt.tight_layout()
        plt.show()
        
        return rmse_position, rmse_velocity 