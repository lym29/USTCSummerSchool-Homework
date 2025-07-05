"""
Advanced Interactive IK Demo Program
Includes animation effects, trajectory planning and more interactive features
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider
from matplotlib.animation import FuncAnimation
from robot_kinematics import ThreeLinkRobot
from visualization import RobotVisualizer


class AdvancedInteractiveIKDemo:
    """
    Advanced Interactive IK Demo Class
    """
    
    def __init__(self, link_lengths=[1.0, 1.0, 0.5]):
        """
        Initialize Advanced Interactive IK Demo
        
        Parameters:
            link_lengths: List of link lengths
        """
        self.robot = ThreeLinkRobot(link_lengths=link_lengths)
        self.visualizer = RobotVisualizer(self.robot)
        
        # Current state
        self.current_joint_angles = [0, 0, 0]
        self.target_position = None
        self.ik_solution = None
        self.animation_running = False
        self.trajectory_points = []
        
        # Create figure
        self.fig = plt.figure(figsize=(15, 10))
        self.setup_plot()
        
        # Connect events
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        
        # Add control elements
        self.setup_controls()
        
        # Initial drawing
        self.update_plot()
        
        # Animation object
        self.anim = None
    
    def setup_plot(self):
        """
        Setup plot
        """
        # Main plot area
        self.ax = plt.subplot2grid((3, 4), (0, 0), colspan=3, rowspan=2)
        self.ax.set_xlabel('X (m)')
        self.ax.set_ylabel('Y (m)')
        self.ax.set_title('Advanced Interactive IK Demo - Click to select target position, drag to create trajectory')
        self.ax.grid(True)
        self.ax.set_aspect('equal')
        
        # Set axis limits
        max_reach = sum(self.robot.link_lengths)
        self.ax.set_xlim(-max_reach*1.2, max_reach*1.2)
        self.ax.set_ylim(-max_reach*1.2, max_reach*1.2)
        
        # Show workspace
        x_coords, y_coords = self.robot.get_workspace_boundary(num_points=500)
        self.ax.scatter(x_coords, y_coords, c='lightblue', alpha=0.3, s=1, label='Workspace')
        
        # Joint angles display area
        self.ax_angles = plt.subplot2grid((3, 4), (2, 0), colspan=2)
        self.ax_angles.set_title('Joint Angles')
        self.ax_angles.set_xlabel('Joint')
        self.ax_angles.set_ylabel('Angle (rad)')
        self.ax_angles.grid(True)
        
        # Error display area
        self.ax_error = plt.subplot2grid((3, 4), (2, 2), colspan=2)
        self.ax_error.set_title('Position Error History')
        self.ax_error.set_xlabel('Time Step')
        self.ax_error.set_ylabel('Error (m)')
        self.ax_error.grid(True)
        
        # Error history
        self.error_history = []
        self.time_steps = []
        self.step_counter = 0
    
    def setup_controls(self):
        """
        设置控制元素
        """
        # 按钮区域
        button_width = 0.08
        button_height = 0.04
        
        # 重置按钮
        ax_reset = plt.axes([0.75, 0.85, button_width, button_height])
        self.btn_reset = Button(ax_reset, 'Reset')
        self.btn_reset.on_clicked(self.reset_robot)
        
        # 切换IK方法按钮
        ax_switch = plt.axes([0.85, 0.85, button_width, button_height])
        self.btn_switch = Button(ax_switch, 'Switch IK Method')
        self.btn_switch.on_clicked(self.switch_ik_method)
        
        # 清除轨迹按钮
        ax_clear = plt.axes([0.75, 0.80, button_width, button_height])
        self.btn_clear = Button(ax_clear, 'Clear Trajectory')
        self.btn_clear.on_clicked(self.clear_trajectory)
        
        # 播放轨迹按钮
        ax_play = plt.axes([0.85, 0.80, button_width, button_height])
        self.btn_play = Button(ax_play, 'Play Trajectory')
        self.btn_play.on_clicked(self.play_trajectory)
        
        # 动画速度滑块
        ax_speed = plt.axes([0.75, 0.70, button_width*2, button_height])
        self.slider_speed = Slider(ax_speed, 'Animation Speed', 0.1, 2.0, valinit=1.0)
        
        # 当前IK方法
        self.use_analytical_ik = True
        
        # 鼠标状态
        self.mouse_pressed = False
        self.last_mouse_pos = None
    
    def on_click(self, event):
        """
        处理鼠标点击事件
        """
        if event.inaxes != self.ax:
            return
        
        # 获取点击位置
        x, y = event.xdata, event.ydata
        
        if x is None or y is None:
            return
        
        # 设置目标位置
        self.target_position = [x, y, 0]
        
        # 添加到轨迹
        self.trajectory_points.append(self.target_position.copy())
        
        # 计算IK解
        self.solve_ik()
        
        # 更新图形
        self.update_plot()
        
        # 重绘
        self.fig.canvas.draw()
    
    def on_mouse_move(self, event):
        """
        处理鼠标移动事件（用于轨迹绘制）
        """
        if event.inaxes != self.ax:
            return
        
        if not self.mouse_pressed:
            return
        
        # 获取当前位置
        x, y = event.xdata, event.ydata
        
        if x is None or y is None:
            return
        
        # 检查是否与上一个点距离足够远
        if self.last_mouse_pos is None or \
           np.linalg.norm([x - self.last_mouse_pos[0], y - self.last_mouse_pos[1]]) > 0.1:
            
            self.target_position = [x, y, 0]
            self.trajectory_points.append(self.target_position.copy())
            self.last_mouse_pos = [x, y]
            
            # 计算IK解
            self.solve_ik()
            
            # 更新图形
            self.update_plot()
            
            # 重绘
            self.fig.canvas.draw()
    
    def solve_ik(self):
        """
        求解IK
        """
        if self.target_position is None:
            return
        
        try:
            if self.use_analytical_ik:
                # 解析IK
                self.ik_solution = self.robot.inverse_kinematics_analytical(
                    self.target_position, elbow_up=True
                )
                if self.ik_solution is None:
                    # 尝试肘部向下的解
                    self.ik_solution = self.robot.inverse_kinematics_analytical(
                        self.target_position, elbow_up=False
                    )
            else:
                # 数值IK
                self.ik_solution = self.robot.inverse_kinematics_numerical(
                    self.target_position, initial_guess=self.current_joint_angles
                )
            
            if self.ik_solution is not None:
                self.current_joint_angles = self.ik_solution.copy()
                
                # 计算误差
                actual_pos = self.robot.get_end_effector_position(self.ik_solution)
                error = np.linalg.norm(actual_pos - self.target_position)
                self.error_history.append(error)
                self.time_steps.append(self.step_counter)
                self.step_counter += 1
                
        except Exception as e:
            print(f"IK solution error: {e}")
            self.ik_solution = None
    
    def update_plot(self):
        """
        更新图形显示
        """
        # 清除主图形
        self.ax.clear()
        
        # 重新设置主图形
        max_reach = sum(self.robot.link_lengths)
        self.ax.set_xlim(-max_reach*1.2, max_reach*1.2)
        self.ax.set_ylim(-max_reach*1.2, max_reach*1.2)
        self.ax.set_xlabel('X (m)')
        self.ax.set_ylabel('Y (m)')
        self.ax.set_title('Advanced Interactive IK Demo')
        self.ax.grid(True)
        self.ax.set_aspect('equal')
        
        # 显示工作空间
        x_coords, y_coords = self.robot.get_workspace_boundary(num_points=500)
        self.ax.scatter(x_coords, y_coords, c='lightblue', alpha=0.3, s=1, label='Workspace')
        
        # 绘制轨迹
        if len(self.trajectory_points) > 1:
            traj_x = [p[0] for p in self.trajectory_points]
            traj_y = [p[1] for p in self.trajectory_points]
            self.ax.plot(traj_x, traj_y, 'g-', alpha=0.5, linewidth=2, label='Trajectory')
        
        # 绘制当前机器人配置
        joint_positions = self.visualizer._calculate_joint_positions(self.current_joint_angles)
        
        # 绘制连杆
        for i in range(len(joint_positions) - 1):
            start_pos = joint_positions[i]
            end_pos = joint_positions[i + 1]
            self.ax.plot([start_pos[0], end_pos[0]], 
                        [start_pos[1], end_pos[1]], 
                        'b-', linewidth=3, label='Robot Links' if i == 0 else "")
        
        # 绘制关节
        for i, pos in enumerate(joint_positions):
            self.ax.plot(pos[0], pos[1], 'ro', markersize=8, 
                        label=f'Joint {i+1}' if i == 0 else "")
        
        # 绘制目标位置
        if self.target_position is not None:
            self.ax.plot(self.target_position[0], self.target_position[1], 
                        'r*', markersize=15, label='Target Position')
            
            # 如果IK求解成功，显示信息
            if self.ik_solution is not None:
                # 显示关节角度信息
                angle_text = f"Joint angles: [{', '.join([f'{a:.2f}' for a in self.ik_solution])}]"
                self.ax.text(0.02, 0.98, angle_text, transform=self.ax.transAxes,
                           verticalalignment='top',
                           bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
                
                # 计算误差
                actual_pos = self.robot.get_end_effector_position(self.ik_solution)
                error = np.linalg.norm(actual_pos - self.target_position)
                error_text = f"Position error: {error:.4f}"
                self.ax.text(0.02, 0.93, error_text, transform=self.ax.transAxes,
                           verticalalignment='top',
                           bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
            else:
                # IK求解失败
                self.ax.text(0.02, 0.98, "IK solution failed - Target position unreachable", 
                           transform=self.ax.transAxes, verticalalignment='top',
                           bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.8))
        
        # 显示当前IK方法
        method_text = "Analytical IK" if self.use_analytical_ik else "Numerical IK"
        self.ax.text(0.02, 0.88, f"Current method: {method_text}", 
                    transform=self.ax.transAxes, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        
        # 更新图例
        handles, labels = self.ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        self.ax.legend(by_label.values(), by_label.keys(), loc='upper right')
        
        # 更新关节角度图
        self.update_angles_plot()
        
        # 更新误差图
        self.update_error_plot()
    
    def update_angles_plot(self):
        """
        更新关节角度图
        """
        self.ax_angles.clear()
        self.ax_angles.set_title('Joint Angles')
        self.ax_angles.set_xlabel('Joint')
        self.ax_angles.set_ylabel('Angle (rad)')
        self.ax_angles.grid(True)
        
        if self.ik_solution is not None:
            joints = ['Joint 1', 'Joint 2', 'Joint 3']
            angles = [np.degrees(a) for a in self.ik_solution]  # 转换为度
            bars = self.ax_angles.bar(joints, angles, color=['red', 'green', 'blue'])
            
            # 添加数值标签
            for bar, angle in zip(bars, angles):
                height = bar.get_height()
                self.ax_angles.text(bar.get_x() + bar.get_width()/2., height,
                                  f'{angle:.1f}°', ha='center', va='bottom')
    
    def update_error_plot(self):
        """
        更新误差图
        """
        self.ax_error.clear()
        self.ax_error.set_title('Position Error History')
        self.ax_error.set_xlabel('Time Step')
        self.ax_error.set_ylabel('Error (m)')
        self.ax_error.grid(True)
        
        if len(self.error_history) > 0:
            self.ax_error.plot(self.time_steps, self.error_history, 'r-', linewidth=2)
            self.ax_error.set_ylim(0, max(self.error_history) * 1.1 if self.error_history else 1)
    
    def reset_robot(self, event):
        """
        重置机器人到初始状态
        """
        self.current_joint_angles = [0, 0, 0]
        self.target_position = None
        self.ik_solution = None
        self.trajectory_points = []
        self.error_history = []
        self.time_steps = []
        self.step_counter = 0
        self.update_plot()
        self.fig.canvas.draw()
    
    def switch_ik_method(self, event):
        """
        切换IK求解方法
        """
        self.use_analytical_ik = not self.use_analytical_ik
        
        # 如果有目标位置，重新求解
        if self.target_position is not None:
            self.solve_ik()
        
        self.update_plot()
        self.fig.canvas.draw()
    
    def clear_trajectory(self, event):
        """
        清除轨迹
        """
        self.trajectory_points = []
        self.error_history = []
        self.time_steps = []
        self.step_counter = 0
        self.update_plot()
        self.fig.canvas.draw()
    
    def play_trajectory(self, event):
        """
        播放轨迹动画
        """
        if len(self.trajectory_points) < 2:
            print("Insufficient trajectory points, cannot play animation")
            return
        
        if self.animation_running:
            if self.anim:
                self.anim.event_source.stop()
            self.animation_running = False
            self.btn_play.label.set_text('Play Trajectory')
        else:
            self.animation_running = True
            self.btn_play.label.set_text('Stop Animation')
            self.animate_trajectory()
    
    def animate_trajectory(self):
        """
        轨迹动画
        """
        if not self.animation_running:
            return
        
        # 创建动画
        self.anim = FuncAnimation(
            self.fig, self.animation_frame, 
            frames=len(self.trajectory_points),
            interval=int(1000 / self.slider_speed.val),  # 毫秒
            repeat=True, blit=False
        )
    
    def animation_frame(self, frame):
        """
        动画帧
        """
        if frame < len(self.trajectory_points):
            self.target_position = self.trajectory_points[frame]
            self.solve_ik()
            self.update_plot()
        
        return []
    
    def run(self):
        """
        运行交互式演示
        """
        plt.tight_layout()
        plt.show()


def main():
    """
    主函数
    """
    print("=== Advanced Interactive IK Demo ===")
    print("Instructions:")
    print("1. Click anywhere on the plane to select target position")
    print("2. The program will automatically calculate IK solution and display robot configuration")
    print("3. Click 'Switch IK Method' button to toggle between analytical and numerical IK")
    print("4. Click 'Reset' button to restore robot to initial state")
    print("5. Click 'Clear Trajectory' button to clear all trajectory points")
    print("6. Click 'Play Trajectory' button to play trajectory animation")
    print("7. Use slider to adjust animation speed")
    print("8. Red star indicates target position, blue solid line indicates current robot configuration")
    print("9. Green line indicates trajectory path")
    print("10. Bottom charts show joint angles and error history")
    print("")
    
    # 创建交互式演示
    demo = AdvancedInteractiveIKDemo(link_lengths=[1.0, 1.0, 0.5])
    
    # 运行演示
    demo.run()


if __name__ == "__main__":
    main() 