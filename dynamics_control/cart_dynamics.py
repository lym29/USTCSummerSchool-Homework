"""
一维小车动力学模型
包含状态方程和观测方程
"""

import numpy as np
from scipy.integrate import odeint


class CartDynamics:
    """
    一维小车动力学模型
    状态: [位置, 速度]
    控制输入: 力
    """
    
    def __init__(self, mass=1.0, damping=0.1):
        """
        初始化小车动力学模型
        
        参数:
            mass: 小车质量 (kg)
            damping: 阻尼系数 (N/(m/s))
        """
        self.mass = mass
        self.damping = damping
        
        # 状态维度
        self.n_states = 2  # [位置, 速度]
        self.n_inputs = 1  # [力]
        
        # 系统矩阵 (连续时间)
        self.A = np.array([
            [0, 1],
            [0, -damping/mass]
        ])
        
        self.B = np.array([
            [0],
            [1/mass]
        ])
    
    def dynamics(self, state, t, control):
        """
        连续时间动力学方程
        
        参数:
            state: 当前状态 [位置, 速度]
            t: 时间
            control: 控制输入 [力]
        
        返回:
            状态导数 [位置导数, 速度导数]
        """
        # TODO: 需要实现这个函数
        # 提示: 使用牛顿第二定律 F = ma
        
        position, velocity = state
        force = control[0]
        
        # 牛顿第二定律: F = ma
        # 考虑阻尼力: F - damping * velocity = mass * acceleration
        acceleration = (force - self.damping * velocity) / self.mass
        
        return [velocity, acceleration]
    
    def discrete_dynamics(self, state, control, dt):
        """
        离散时间动力学方程 (使用欧拉积分)
        
        参数:
            state: 当前状态 [位置, 速度]
            control: 控制输入 [力]
            dt: 时间步长
        
        返回:
            下一时刻状态 [位置, 速度]
        """
        # TODO: 需要实现这个函数
        # 提示: 使用欧拉积分方法 x[k+1] = x[k] + dt * dx/dt
        
        # 计算状态导数
        state_derivative = self.dynamics(state, 0, control)
        
        # 欧拉积分
        next_state = np.array(state) + dt * np.array(state_derivative)
        
        return next_state
    
    def simulate(self, initial_state, control_sequence, dt, t_span):
        """
        模拟小车运动
        
        参数:
            initial_state: 初始状态 [位置, 速度]
            control_sequence: 控制序列
            dt: 时间步长
            t_span: 时间范围 [t_start, t_end]
        
        返回:
            time_array: 时间数组
            state_history: 状态历史
        """
        # TODO: 需要实现这个函数
        # 提示: 使用scipy.integrate.odeint或手动积分
        
        t_start, t_end = t_span
        time_array = np.arange(t_start, t_end + dt, dt)
        n_steps = len(time_array)
        
        state_history = np.zeros((n_steps, self.n_states))
        state_history[0] = initial_state
        
        # 手动积分
        for i in range(1, n_steps):
            if i < len(control_sequence):
                control = control_sequence[i-1]
            else:
                control = [0]  # 如果没有控制输入，设为0
            
            state_history[i] = self.discrete_dynamics(
                state_history[i-1], control, dt
            )
        
        return time_array, state_history
    
    def linearize(self, state_eq, control_eq):
        """
        在平衡点附近线性化系统
        
        参数:
            state_eq: 平衡状态 [位置, 速度]
            control_eq: 平衡控制输入 [力]
        
        返回:
            A_lin, B_lin: 线性化后的系统矩阵
        """
        # TODO: 需要实现这个函数
        # 提示: 使用数值微分计算雅可比矩阵
        
        epsilon = 1e-6
        
        # 计算A矩阵 (状态雅可比)
        A_lin = np.zeros((self.n_states, self.n_states))
        for i in range(self.n_states):
            state_perturbed = state_eq.copy()
            state_perturbed[i] += epsilon
            
            deriv_original = self.dynamics(state_eq, 0, control_eq)
            deriv_perturbed = self.dynamics(state_perturbed, 0, control_eq)
            
            A_lin[:, i] = (np.array(deriv_perturbed) - np.array(deriv_original)) / epsilon
        
        # 计算B矩阵 (控制雅可比)
        B_lin = np.zeros((self.n_states, self.n_inputs))
        for i in range(self.n_inputs):
            control_perturbed = control_eq.copy()
            control_perturbed[i] += epsilon
            
            deriv_original = self.dynamics(state_eq, 0, control_eq)
            deriv_perturbed = self.dynamics(state_eq, 0, control_perturbed)
            
            B_lin[:, i] = (np.array(deriv_perturbed) - np.array(deriv_original)) / epsilon
        
        return A_lin, B_lin
    
    def get_equilibrium_point(self, target_position):
        """
        计算目标位置对应的平衡点
        
        参数:
            target_position: 目标位置
        
        返回:
            state_eq, control_eq: 平衡状态和控制输入
        """
        # TODO: 需要实现这个函数
        # 提示: 在平衡点，状态导数应该为0
        
        # 在平衡点，速度应该为0
        state_eq = [target_position, 0]
        
        # 在平衡点，力应该抵消阻尼力
        control_eq = [0]  # 如果速度为0，则不需要力
        
        return state_eq, control_eq 