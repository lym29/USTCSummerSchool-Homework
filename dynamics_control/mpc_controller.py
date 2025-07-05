"""
模型预测控制(MPC)实现
用于一维小车的位置控制
"""

import numpy as np
import cvxpy as cp


class MPCController:
    """
    模型预测控制器
    使用线性MPC控制一维小车位置
    """
    
    def __init__(self, dynamics_model, horizon=10, dt=0.1):
        """
        初始化MPC控制器
        
        参数:
            dynamics_model: 动力学模型对象
            horizon: 预测时域长度
            dt: 时间步长
        """
        self.dynamics = dynamics_model
        self.horizon = horizon
        self.dt = dt
        
        # 状态和控制维度
        self.n_states = dynamics_model.n_states
        self.n_inputs = dynamics_model.n_inputs
        
        # 权重矩阵
        self.Q = np.diag([10.0, 1.0])  # 状态误差权重
        self.R = np.diag([0.1])        # 控制输入权重
        
        # 控制约束
        self.u_min = -5.0  # 最小力
        self.u_max = 5.0   # 最大力
        
        # 状态约束
        self.x_min = np.array([-10.0, -5.0])  # 最小位置和速度
        self.x_max = np.array([10.0, 5.0])    # 最大位置和速度
    
    def setup_optimization_problem(self, current_state, target_state):
        """
        设置MPC优化问题
        
        参数:
            current_state: 当前状态
            target_state: 目标状态
        
        返回:
            problem, variables: 优化问题和变量
        """
        # TODO: 学生需要实现这个函数
        # 提示:
        # 1. 定义状态和控制变量
        # 2. 添加动力学约束
        # 3. 定义目标函数
        # 4. 添加状态和控制约束
        
        # 定义变量
        x = cp.Variable((self.n_states, self.horizon + 1))
        u = cp.Variable((self.n_inputs, self.horizon))
        
        # 目标函数
        cost = 0
        
        # 终端成本
        cost += cp.quad_form(x[:, -1] - target_state, self.Q)
        
        # 运行成本
        for k in range(self.horizon):
            cost += cp.quad_form(x[:, k] - target_state, self.Q)
            cost += cp.quad_form(u[:, k], self.R)
        
        # 约束条件
        constraints = []
        
        # 初始状态约束
        constraints.append(x[:, 0] == current_state)
        
        # 动力学约束
        for k in range(self.horizon):
            # 线性化动力学模型
            next_state = (np.eye(self.n_states) + self.dynamics.A * self.dt) @ x[:, k] + \
                        self.dynamics.B * self.dt @ u[:, k]
            constraints.append(x[:, k + 1] == next_state)
        
        # 控制约束
        for k in range(self.horizon):
            constraints.append(u[:, k] >= self.u_min)
            constraints.append(u[:, k] <= self.u_max)
        
        # 状态约束
        for k in range(self.horizon + 1):
            constraints.append(x[:, k] >= self.x_min)
            constraints.append(x[:, k] <= self.x_max)
        
        # 创建优化问题
        problem = cp.Problem(cp.Minimize(cost), constraints)
        
        return problem, (x, u)
    
    def solve_mpc(self, current_state, target_state):
        """
        求解MPC问题
        
        参数:
            current_state: 当前状态
            target_state: 目标状态
        
        返回:
            optimal_control: 最优控制序列
            optimal_states: 最优状态序列
        """
        # TODO: 学生需要实现这个函数
        # 提示: 调用setup_optimization_problem并求解
        
        # 设置优化问题
        problem, (x, u) = self.setup_optimization_problem(current_state, target_state)
        
        # 求解
        try:
            problem.solve(solver=cp.OSQP, verbose=False)
            
            if problem.status == cp.OPTIMAL:
                optimal_control = u.value
                optimal_states = x.value
                return optimal_control, optimal_states
            else:
                print(f"MPC求解失败，状态: {problem.status}")
                return None, None
                
        except Exception as e:
            print(f"MPC求解出错: {e}")
            return None, None
    
    def get_control_action(self, current_state, target_state):
        """
        获取当前时刻的控制动作
        
        参数:
            current_state: 当前状态
            target_state: 目标状态
        
        返回:
            control_action: 控制动作
        """
        # TODO: 学生需要实现这个函数
        # 提示: 求解MPC问题，返回第一个控制动作
        
        optimal_control, _ = self.solve_mpc(current_state, target_state)
        
        if optimal_control is not None:
            return optimal_control[:, 0]  # 返回第一个控制动作
        else:
            return np.zeros(self.n_inputs)  # 如果求解失败，返回零控制
    
    def simulate_closed_loop(self, initial_state, target_state, simulation_time, dt):
        """
        闭环仿真
        
        参数:
            initial_state: 初始状态
            target_state: 目标状态
            simulation_time: 仿真时间
            dt: 时间步长
        
        返回:
            time_array: 时间数组
            state_history: 状态历史
            control_history: 控制历史
        """
        # TODO: 学生需要实现这个函数
        # 提示: 在每个时间步调用MPC控制器
        
        n_steps = int(simulation_time / dt)
        time_array = np.arange(0, simulation_time + dt, dt)
        
        state_history = np.zeros((n_steps + 1, self.n_states))
        control_history = np.zeros((n_steps, self.n_inputs))
        
        state_history[0] = initial_state
        
        for i in range(n_steps):
            current_state = state_history[i]
            
            # 获取控制动作
            control_action = self.get_control_action(current_state, target_state)
            control_history[i] = control_action
            
            # 更新状态
            next_state = self.dynamics.discrete_dynamics(current_state, control_action, dt)
            state_history[i + 1] = next_state
        
        return time_array, state_history, control_history
    
    def tune_weights(self, Q_new=None, R_new=None):
        """
        调整MPC权重
        
        参数:
            Q_new: 新的状态权重矩阵
            R_new: 新的控制权重矩阵
        """
        if Q_new is not None:
            self.Q = Q_new
        if R_new is not None:
            self.R = R_new
    
    def set_constraints(self, u_min=None, u_max=None, x_min=None, x_max=None):
        """
        设置约束条件
        
        参数:
            u_min, u_max: 控制约束
            x_min, x_max: 状态约束
        """
        if u_min is not None:
            self.u_min = u_min
        if u_max is not None:
            self.u_max = u_max
        if x_min is not None:
            self.x_min = x_min
        if x_max is not None:
            self.x_max = x_max 