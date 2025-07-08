"""
PathPlanning module for trajectory interpolation.
支持关节空间和操作空间的梯形速度轨迹插值。
"""
import numpy as np

class PathPlanner:
    @staticmethod
    def _calculate_trapezoid_profile(distance, num_points, vmax, amax):
        """
        计算梯形速度轨迹
        参数：
            distance: 位移距离
            num_points: 插值点数
            vmax: 最大速度
            amax: 最大加速度
        返回：
            s: 位移序列
            t: 时间序列
            
        TODO:
        1. 实现梯形速度轨迹的计算
           - 计算加速和减速时间
           - 处理加速、匀速和减速三个阶段
           - 确保满足最大速度和加速度约束
           - 处理总距离过短的特殊情况（需要重新计算最大速度）
        """
        # 计算加速和减速时间
        t_acc = vmax / amax
        d_acc = 0.5 * amax * t_acc**2
        
        # 如果加减速距离之和大于总位移，需要调整最大速度
        if 2 * d_acc > abs(distance):
            # 重新计算实际可达的最大速度
            vmax = np.sqrt(amax * abs(distance))
            t_acc = vmax / amax
            t_const = 0
        else:
            # 计算匀速运动时间
            d_const = abs(distance) - 2 * d_acc
            t_const = d_const / vmax
        
        # 总时间
        total_time = 2 * t_acc + t_const
        
        # 生成时间序列
        t = np.linspace(0, total_time, num_points)
        
        # 计算位移序列
        s = np.zeros_like(t)
        for i, ti in enumerate(t):
            if ti <= t_acc:  # 加速阶段
                s[i] = 0.5 * amax * ti**2
            elif ti <= t_acc + t_const:  # 匀速阶段
                s[i] = d_acc + vmax * (ti - t_acc)
            else:  # 减速阶段
                ti_dec = ti - (t_acc + t_const)
                s[i] = abs(distance) - 0.5 * amax * (t_acc - ti_dec)**2
        
        return s, t, total_time

    @staticmethod
    def interpolate_joint_space(waypoints, num_points=10, vmax=1.0, amax=1.0):
        """
        关节空间插值（梯形速度轨迹）
        参数：
            waypoints: List of joint angle waypoints, shape (N, dof)
            num_points: Number of interpolation points
            vmax: Maximum velocity (per joint)
            amax: Maximum acceleration (per joint)
        返回：
            traj: Interpolated joint trajectory, shape (num_points, dof)
            
        TODO:
        1. 实现关节空间的轨迹插值(梯形速度轨迹)
        进阶: 实现其他轨迹插值方法

        """
        waypoints = np.array(waypoints)
        if len(waypoints) < 2:
            return waypoints
            
        n_segments = len(waypoints) - 1
        n_dof = waypoints.shape[1]
        
        # 计算每段的点数（根据段数平均分配）
        points_per_segment = num_points // n_segments
        extra_points = num_points % n_segments
        
        # 存储完整轨迹
        full_trajectory = []
        
        # 对每段进行梯形速度插值
        for i in range(n_segments):
            # 当前段的起点和终点
            start = waypoints[i]
            end = waypoints[i + 1]
            
            # 当前段的点数（最后一段包含余下的点）
            current_points = points_per_segment + (extra_points if i == n_segments-1 else 0)
            
            # 计算当前段的位移
            displacement = end - start
            
            # 初始化该段轨迹
            segment_traj = np.zeros((current_points, n_dof))
            max_time = 0
            
            # 对每个关节计算轨迹
            for j in range(n_dof):
                # 如果这个关节没有位移，直接使用起始位置
                if abs(displacement[j]) < 1e-6:
                    segment_traj[:, j] = start[j]
                    continue
                
                # 计算梯形速度轨迹
                s, _, total_time = PathPlanner._calculate_trapezoid_profile(
                    displacement[j], current_points, vmax, amax)
                
                # 更新最长时间
                max_time = max(max_time, total_time)
                
                # 根据运动方向设置位置
                if displacement[j] >= 0:
                    segment_traj[:, j] = start[j] + s
                else:
                    segment_traj[:, j] = start[j] - s
            
            # 添加到完整轨迹中（除了最后一段，去掉最后一个点以避免重复）
            if i < n_segments - 1:
                full_trajectory.append(segment_traj[:-1])
            else:
                full_trajectory.append(segment_traj)
        
        # 合并所有段的轨迹
        return np.vstack(full_trajectory)

    @staticmethod
    def interpolate_operational_space(waypoints, num_points=10, vmax=1.0, amax=1.0, robot=None, initial_joint_angles=None):
        """
        操作空间插值（梯形速度轨迹）
        参数：
            waypoints: List of end-effector positions, shape (N, dim)
            num_points: Number of interpolation points
            vmax: Maximum velocity (per dimension)
            amax: Maximum acceleration (per dimension)
            robot: ThreeLinkRobot instance for IK calculation
            initial_joint_angles: Initial joint angles for IK calculation
        返回：
            traj: Interpolated joint angle trajectory, shape (num_points, dof)
            
        TODO:
        1. 实现操作空间的轨迹插值(梯形速度轨迹)
        进阶: 实现其他轨迹插值方法

        """
        if robot is None:
            raise ValueError("Robot instance must be provided for operational space interpolation")
            
        waypoints = np.array(waypoints)
        if len(waypoints) < 2:
            return waypoints
            
        n_segments = len(waypoints) - 1
        
        # 计算每段的点数（根据段数平均分配）
        points_per_segment = num_points // n_segments
        extra_points = num_points % n_segments
        
        # 存储完整轨迹
        full_trajectory = []
        current_joint_angles = initial_joint_angles if initial_joint_angles is not None else np.zeros(robot.n_joints)
        
        # 对每段进行梯形速度插值
        for i in range(n_segments):
            # 当前段的起点和终点
            start = waypoints[i]
            end = waypoints[i + 1]
            
            # 当前段的点数（最后一段包含余下的点）
            current_points = points_per_segment + (extra_points if i == n_segments-1 else 0)
            
            # 计算当前段的位移
            displacement = end - start
            total_distance = np.linalg.norm(displacement)
            
            # 计算梯形速度轨迹
            s, _, _ = PathPlanner._calculate_trapezoid_profile(
                total_distance, current_points, vmax, amax)
            
            # 初始化该段轨迹
            segment_traj = np.zeros((current_points, robot.n_joints))
            
            # 计算每个时间点的位置
            for j in range(current_points):
                # 计算当前位置
                ratio = s[j] / total_distance if total_distance > 0 else 1
                current_pos = start + ratio * displacement
                
                # 计算IK解
                ik_solution = robot.inverse_kinematics_optimization(
                    np.append(current_pos, 0),  # 添加z坐标为0
                    initial_guess=current_joint_angles
                )
                
                if ik_solution is None:
                    raise RuntimeError(f"IK solution not found at point {j} in segment {i}")
                
                segment_traj[j] = ik_solution
                current_joint_angles = ik_solution
            
            # 添加到完整轨迹中（除了最后一段，去掉最后一个点以避免重复）
            if i < n_segments - 1:
                full_trajectory.append(segment_traj[:-1])
            else:
                full_trajectory.append(segment_traj)
        
        # 合并所有段的轨迹
        return np.vstack(full_trajectory) 