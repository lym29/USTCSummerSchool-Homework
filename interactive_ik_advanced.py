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
from robot_kinematics.path_planning import PathPlanner


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
        self.trajectory_joint_angles = []
        
        # IK方法选择 (0: 优化IK, 1: 雅可比IK)
        self.ik_method = 0
        
        # 插值方式 (0: joint space, 1: operational space)
        self.interp_mode = 0  # 0: joint space, 1: operational space
        self.interp_mode_names = ["Joint Space", "Operational Space"]
        
        # Create figure
        self.fig = plt.figure(figsize=(15, 10))
        self.setup_plot()
        
        # Connect events
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)
        
        # Add control elements
        self.setup_controls()
        
        # Error tracking
        self.error_history = []
        self.time_steps = []
        self.step_counter = 0

        # Initial drawing
        self.update_plot()
        
        # Animation object
        self.anim = None
        
        # Mouse tracking
        self.mouse_pressed = False
        self.last_mouse_pos = None
        self.status_message = ''
    
    def setup_plot(self):
        """
        Setup the plot layout
        """
        # Main robot plot
        self.ax = plt.subplot2grid((2, 3), (0, 0), colspan=2, rowspan=2)
        
        # Joint angles plot
        self.ax_angles = plt.subplot2grid((2, 3), (0, 2))
        
        # 去掉 error plot
        # self.ax_error = plt.subplot2grid((2, 3), (1, 2))
        
        # Setup main plot
        max_reach = sum(self.robot.link_lengths)
        self.ax.set_xlim(-max_reach*1.2, max_reach*1.2)
        self.ax.set_ylim(-max_reach*1.2, max_reach*1.2)
        self.ax.set_xlabel('X (m)')
        self.ax.set_ylabel('Y (m)')
        self.ax.set_title('Advanced Interactive IK Demo')
        self.ax.grid(True)
        self.ax.set_aspect('equal')
        
        # Show workspace
        x_coords, y_coords = self.robot.get_workspace_boundary(num_points=500)
        self.ax.scatter(x_coords, y_coords, c='lightblue', alpha=0.3, s=1, label='Workspace')
    
    def setup_controls(self):
        """
        Setup control buttons and sliders (vertical layout at right, below Joint Angle plot)
        """
        x = 0.7
        w = 0.16
        h = 0.06
        gap = 0.01
        y0 = 0.40
        # Reset button
        ax_reset = plt.axes([x, y0, w, h])
        self.btn_reset = Button(ax_reset, 'Reset')
        self.btn_reset.on_clicked(self.reset_robot)
        # Switch IK method button
        ax_switch = plt.axes([x, y0-h-gap, w, h])
        self.btn_switch = Button(ax_switch, 'Switch IK')
        self.btn_switch.on_clicked(self.switch_ik_method)
        # Clear trajectory button
        ax_clear = plt.axes([x, y0-2*(h+gap), w, h])
        self.btn_clear = Button(ax_clear, 'Clear Trajectory')
        self.btn_clear.on_clicked(self.clear_trajectory)
        # Play trajectory button
        ax_play = plt.axes([x, y0-3*(h+gap), w, h])
        self.btn_play = Button(ax_play, 'Play Trajectory')
        self.btn_play.on_clicked(self.play_trajectory)
        # Switch interpolation mode button
        ax_interp = plt.axes([x, y0-4*(h+gap), w, h])
        self.btn_interp = Button(ax_interp, 'Switch Interp Mode')
        self.btn_interp.on_clicked(self.switch_interp_mode)
        # Animation speed slider
        ax_speed = plt.axes([x, y0-5*(h+gap), w, h])
        self.speed_slider = Slider(ax_speed, 'Speed', 0.1, 2.0, valinit=1.0)
        self.speed_slider.on_changed(self.on_speed_change)
    
    def on_click(self, event):
        if self.animation_running:
            return
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
        
        # 计算IK解
        if self.ik_method == 0:
            ik_solution = self.robot.inverse_kinematics_optimization(self.target_position, initial_guess=self.current_joint_angles)
        else:
            ik_solution = self.robot.inverse_kinematics_jacobian(self.target_position, initial_guess=self.current_joint_angles)
        if ik_solution is not None:
            self.current_joint_angles = ik_solution
            self.ik_solution = ik_solution
            self.trajectory_points.append(list(self.target_position))
            self.trajectory_joint_angles.append(list(ik_solution))
            self.status_message = ''
        else:
            self.status_message = 'IK Solution failed!'
        
        # 更新图形
        self.update_plot()
        
        # 重绘
        self.fig.canvas.draw_idle()
    
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
            if self.ik_method == 0:
                # 优化IK
                self.ik_solution = self.robot.inverse_kinematics_optimization(
                    self.target_position, initial_guess=self.current_joint_angles
                )
            else:
                # 雅可比IK
                self.ik_solution = self.robot.inverse_kinematics_jacobian(
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
        method_name = "Simp Optim IK" if self.ik_method == 0 else "Jacobian IK"
        interp_name = self.interp_mode_names[self.interp_mode]
        self.ax.text(0.02, 0.88, f"Current method: {method_name}", 
                    transform=self.ax.transAxes, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        self.ax.text(0.02, 0.82, f"Interp mode: {interp_name}",
                    transform=self.ax.transAxes, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
        
        # 更新图例
        handles, labels = self.ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        self.ax.legend(by_label.values(), by_label.keys(), loc='upper right')
        
        # 更新关节角度图
        self.update_angles_plot()
        
        # 移除 update_error_plot 的调用
        # self.update_error_plot()
        # 在主图右下角显示status_message
        if hasattr(self, 'status_message') and self.status_message:
            self.ax.text(0.02, 0.05, self.status_message, transform=self.ax.transAxes,
                         fontsize=10, color='red', verticalalignment='bottom',
                         bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
    
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
    
    # 移除 update_error_plot 方法
    # def update_error_plot(self):
    #     """
    #     更新误差图
    #     """
    #     self.ax_error.clear()
    #     self.ax_error.set_title('Position Error History')
    #     self.ax_error.set_xlabel('Time Step')
    #     self.ax_error.set_ylabel('Error (m)')
    #     self.ax_error.grid(True)
        
    #     if len(self.error_history) > 0:
    #         self.ax_error.plot(self.time_steps, self.error_history, 'r-', linewidth=2)
    #         self.ax_error.set_ylim(0, max(self.error_history) * 1.1 if self.error_history else 1)
    
    def reset_robot(self, event):
        if self.animation_running:
            return
        """
        重置机器人到初始状态
        """
        self.current_joint_angles = [0, 0, 0]
        self.target_position = None
        self.ik_solution = None
        self.trajectory_points = []
        self.trajectory_joint_angles = []
        self.error_history = []
        self.time_steps = []
        self.step_counter = 0
        self.status_message = ''
        self.update_plot()
        self.fig.canvas.draw()
    
    def switch_ik_method(self, event):
        if self.animation_running:
            return
        """
        切换IK方法，并尝试将当前目标点加入轨迹（如果新方法求解成功且未重复）
        """
        self.ik_method = 1 - self.ik_method
        print(f"Switched IK method to: {'Jacobian' if self.ik_method else 'Optimization'}")
        # 对当前目标点重新求解
        if self.target_position is not None:
            if self.ik_method == 0:
                ik_solution = self.robot.inverse_kinematics_optimization(self.target_position, initial_guess=self.current_joint_angles)
            else:
                ik_solution = self.robot.inverse_kinematics_jacobian(self.target_position, initial_guess=self.current_joint_angles)
            if ik_solution is not None:
                self.current_joint_angles = ik_solution
                self.ik_solution = ik_solution
                # 只在不是最后一个点时添加
                if not (self.trajectory_points and self.trajectory_points[-1] == list(self.target_position)):
                    self.trajectory_points.append(list(self.target_position))
                    self.trajectory_joint_angles.append(list(ik_solution))
                self.status_message = ''
            else:
                self.status_message = 'IK Solution failed!'
        self.update_plot()
        self.fig.canvas.draw_idle()
    
    def clear_trajectory(self, event):
        if self.animation_running:
            return
        """
        清除所有轨迹点，并停止动画（如果正在播放）
        """
        if self.animation_running:
            if self.anim is not None and getattr(self.anim, 'event_source', None) is not None:
                self.anim.event_source.stop()
                print("Animation stopped due to trajectory clear.")
            self.animation_running = False
        self.trajectory_points = []
        self.trajectory_joint_angles = []
        self.status_message = ''
        self.update_plot()
        self.fig.canvas.draw_idle()
    
    def play_trajectory(self, event):
        if self.animation_running:
            return
        """
        播放轨迹动画（一次性播放，期间禁用所有按钮）
        """
        if len(self.trajectory_joint_angles) < 2:
            print("No trajectory to play")
            return
        self.animation_running = True
        self.btn_play.label.set_text('Playing...')
        try:
            if self.interp_mode == 0:
                interp_traj = PathPlanner.interpolate_joint_space(
                    self.trajectory_joint_angles, 
                    num_points=20, 
                    vmax=1.0, 
                    amax=1.0
                )
            else:
                interp_traj = PathPlanner.interpolate_operational_space(
                    self.trajectory_points, 
                    num_points=20, 
                    vmax=1.0, 
                    amax=1.0,
                    robot=self.robot,
                    initial_joint_angles=self.current_joint_angles
                )
            self.interpolated_traj = interp_traj
            self.status_message = ''
        except Exception as e:
            msg = f"[Warning] Interpolation failed: {e}\nUsing waypoints as trajectory."
            print(msg)
            self.interpolated_traj = np.array(self.trajectory_joint_angles)
            self.status_message = msg
        self.anim = FuncAnimation(self.fig, self.animation_frame, frames=len(self.interpolated_traj),
                                  interval=30 / self.speed_slider.val, repeat=False)
        print("Animation started")
        self.fig.canvas.draw_idle()
    
    def animation_frame(self, frame):
        """
        动画每一帧的更新函数
        """
        # 更新当前关节角度为轨迹点对应的IK解
        if frame < len(self.interpolated_traj)-1:
            self.current_joint_angles = self.interpolated_traj[frame]
            self.ik_solution = self.current_joint_angles
        else:
            # 如果动画帧数超过插值轨迹长度，则停止动画
            self.current_joint_angles = self.interpolated_traj[-1]
            self.ik_solution = self.current_joint_angles
            self.animation_running = False
            if self.anim is not None:
                self.anim.event_source.stop()
            self.btn_play.label.set_text('Play Trajectory')
            
        self.update_plot()
        # 返回一个空列表，兼容 blit=False
        return []
    
    def on_speed_change(self, val):
        if self.animation_running:
            return
        """
        速度改变回调
        """
        if self.animation_running and self.anim is not None:
            self.anim.event_source.interval = int(1000 / val)
    
    def switch_interp_mode(self, event):
        if self.animation_running:
            return
        """
        切换插值方式
        """
        self.interp_mode = 1 - self.interp_mode
        print(f"Switched interpolation mode to: {self.interp_mode_names[self.interp_mode]}")
        self.update_plot()
        self.fig.canvas.draw_idle()
    
    def run(self):
        """
        运行演示
        """
        plt.show()


def main():
    """
    主函数
    """
    print("=== Advanced Interactive IK Demo ===")
    print("Instructions:")
    print("1. Click on the plane to select target positions")
    print("2. Create trajectory by clicking multiple points")
    print("3. Use 'Play Trajectory' to animate the robot movement")
    print("4. Adjust animation speed with the slider")
    print("5. Use 'Clear Trajectory' to remove all trajectory points")
    print("6. Use 'Reset' to restore initial state")
    print("")
    
    # 创建高级交互式演示
    demo = AdvancedInteractiveIKDemo(link_lengths=[1.0, 1.0, 0.5])
    
    # 运行演示
    demo.run()


if __name__ == "__main__":
    main() 