"""
交互式IK演示程序
用户可以在平面上点击选择末端执行器位置，实时计算关节角度
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from robot_kinematics import ThreeLinkRobot
from visualization import RobotVisualizer


class InteractiveIKDemo:
    """
    交互式IK演示类
    """
    
    def __init__(self, link_lengths=[1.0, 1.0, 0.5]):
        """
        初始化交互式IK演示
        
        参数:
            link_lengths: 连杆长度列表
        """
        self.robot = ThreeLinkRobot(link_lengths=link_lengths)
        self.visualizer = RobotVisualizer(self.robot)
        
        # 当前状态
        self.current_joint_angles = [0, 0, 0]
        self.target_position = None
        self.ik_solution = None
        
        # 创建图形
        self.fig, self.ax = plt.subplots(figsize=(12, 10))
        self.setup_plot()
        
        # 连接事件
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        
        # 添加按钮
        self.setup_buttons()
        
        # 初始绘制
        self.update_plot()
    
    def setup_plot(self):
        """
        设置图形
        """
        self.ax.set_xlabel('X (m)')
        self.ax.set_ylabel('Y (m)')
        self.ax.set_title('Interactive IK Demo - Click on the plane to select target position')
        self.ax.grid(True)
        self.ax.set_aspect('equal')
        
        # 设置坐标轴范围
        max_reach = sum(self.robot.link_lengths)
        self.ax.set_xlim(-max_reach*1.2, max_reach*1.2)
        self.ax.set_ylim(-max_reach*1.2, max_reach*1.2)
        
        # 显示工作空间
        x_coords, y_coords = self.robot.get_workspace_boundary(num_points=500)
        self.ax.scatter(x_coords, y_coords, c='lightblue', alpha=0.3, s=1, label='Workspace')
        
        # 添加说明文字
        self.ax.text(0.02, 0.98, 'Click on the plane to select target position\n Red dot: target position\n Blue line: robot link\n Green line: IK solution', 
                    transform=self.ax.transAxes, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    def setup_buttons(self):
        """
        设置控制按钮
        """
        # 按钮位置
        button_width = 0.15
        button_height = 0.05
        
        # 重置按钮
        ax_reset = plt.axes([0.7, 0.05, button_width, button_height])
        self.btn_reset = Button(ax_reset, 'Reset')
        self.btn_reset.on_clicked(self.reset_robot)
        
        # 切换IK方法按钮
        ax_switch = plt.axes([0.85, 0.05, button_width, button_height])
        self.btn_switch = Button(ax_switch, 'Switch IK Method')
        self.btn_switch.on_clicked(self.switch_ik_method)
        
        # 当前IK方法
        self.use_analytical_ik = True
    
    def on_click(self, event):
        """
        处理鼠标点击事件
        
        参数:
            event: 鼠标事件
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
                print(f"Use Analytical IK, target position: {self.target_position}")
                # 解析IK
                self.ik_solution = self.robot.inverse_kinematics_analytical(
                    self.target_position, elbow_up=True
                )
                if self.ik_solution is None:
                    print("No solution with elbow up, trying elbow down...")
                    # 尝试肘部向下的解
                    self.ik_solution = self.robot.inverse_kinematics_analytical(
                        self.target_position, elbow_up=False
                    )
            else:
                print(f"Use Numerical IK, target position: {self.target_position}")
                # 数值IK
                self.ik_solution = self.robot.inverse_kinematics_numerical(
                    self.target_position, initial_guess=self.current_joint_angles
                )
            
            if self.ik_solution is not None:
                print(f"IK solution found: {self.ik_solution}")
                self.current_joint_angles = self.ik_solution.copy()
            else:
                print("IK solution not found")
                
        except Exception as e:
            print(f"IK求解错误: {e}")
            self.ik_solution = None
    
    def update_plot(self):
        """
        更新图形显示
        """
        # 清除之前的绘制
        self.ax.clear()
        
        # 重新设置图形
        self.setup_plot()
        
        # 绘制当前机器人配置
        joint_positions = self.visualizer._calculate_joint_positions(self.current_joint_angles)
        
        # 绘制连杆
        for i in range(len(joint_positions) - 1):
            start_pos = joint_positions[i]
            end_pos = joint_positions[i + 1]
            self.ax.plot([start_pos[0], end_pos[0]], 
                        [start_pos[1], end_pos[1]], 
                        'b-', linewidth=3, label='Robot Link' if i == 0 else "")
        
        # 绘制关节
        for i, pos in enumerate(joint_positions):
            self.ax.plot(pos[0], pos[1], 'ro', markersize=8, 
                        label=f'Joint {i+1}' if i == 0 else "")
        
        # 绘制目标位置
        if self.target_position is not None:
            self.ax.plot(self.target_position[0], self.target_position[1], 
                        'r*', markersize=15, label='Target Position')
            
            # 如果IK求解成功，绘制解
            if self.ik_solution is not None:
                # 计算IK解对应的机器人配置
                ik_joint_positions = self.visualizer._calculate_joint_positions(self.ik_solution)
                
                # 绘制IK解的连杆（绿色虚线）
                for i in range(len(ik_joint_positions) - 1):
                    start_pos = ik_joint_positions[i]
                    end_pos = ik_joint_positions[i + 1]
                    self.ax.plot([start_pos[0], end_pos[0]], 
                                [start_pos[1], end_pos[1]], 
                                'g--', linewidth=2, alpha=0.7, 
                                label='IK Solution' if i == 0 else "")
                
                # 显示关节角度信息
                angle_text = f"Joint Angles: [{', '.join([f'{a:.2f}' for a in self.ik_solution])}]"
                self.ax.text(0.02, 0.9, angle_text, transform=self.ax.transAxes,
                           bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
                
                # 计算误差
                actual_pos = self.robot.get_end_effector_position(self.ik_solution)
                error = np.linalg.norm(actual_pos - self.target_position)
                error_text = f"Error: {error:.4f}"
                self.ax.text(0.02, 0.85, error_text, transform=self.ax.transAxes,
                           bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
            else:
                # IK求解失败
                self.ax.text(0.02, 0.9, "Failed to solve IK - Target position unreachable", 
                           transform=self.ax.transAxes,
                           bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.8))
        
        # 显示当前IK方法
        method_text = "Analytical IK" if self.use_analytical_ik else "Numerical IK"
        self.ax.text(0.02, 0.8, f"Current Method: {method_text}", 
                    transform=self.ax.transAxes,
                    bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        
        # 更新图例
        handles, labels = self.ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        self.ax.legend(by_label.values(), by_label.keys(), loc='upper right')
    
    def reset_robot(self, event):
        """
        重置机器人到初始状态
        """
        self.current_joint_angles = [0, 0, 0]
        self.target_position = None
        self.ik_solution = None
        self.update_plot()
        self.fig.canvas.draw()
    
    def switch_ik_method(self, event):
        """
        切换IK求解方法
        """
        self.use_analytical_ik = not self.use_analytical_ik
        method_name = "Analytical IK" if self.use_analytical_ik else "Numerical IK"
        print(f"Switch to {method_name} method")
        
        # 如果有目标位置，重新求解
        if self.target_position is not None:
            self.solve_ik()
        
        self.update_plot()
        self.fig.canvas.draw()
    
    def run(self):
        """
        运行交互式演示
        """
        plt.show()


def main():
    """
    主函数
    """
    print("=== Interactive IK Demo ===")
    print("Instructions:")
    print("1. Click anywhere on the plane to select target position")
    print("2. The program will automatically calculate IK solution and display robot configuration")
    print("3. Click 'Switch IK Method' button to toggle between analytical and numerical IK")
    print("4. Click 'Reset' button to restore robot to initial state")
    print("5. Red star indicates target position, blue solid line indicates current robot configuration")
    print("6. Green dashed line indicates IK solution (if successful)")
    print("")
    
    # 创建交互式演示
    demo = InteractiveIKDemo(link_lengths=[1.0, 1.0, 0.5])
    
    # 运行演示
    demo.run()


if __name__ == "__main__":
    main() 