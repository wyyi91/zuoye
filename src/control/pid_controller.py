"""PID控制器实现 —— 位置式、增量式、抗积分饱和"""

from dataclasses import dataclass


@dataclass
class PIDParams:
    kp: float = 2.0
    ti: float = 2.0
    td: float = 0.5


class SimplePIDController:
    """普通PID控制器（无输出限幅，教学用）"""

    def __init__(self, kp: float = 2.0, ti: float = 2.0, td: float = 0.5):
        self.kp = kp
        self.ti = ti
        self.td = td
        self._integral = 0.0
        self._prev_error = 0.0
        self._output = 0.0

    def reset(self):
        self._integral = 0.0
        self._prev_error = 0.0
        self._output = 0.0

    def step(self, setpoint: float, pv: float, dt: float) -> float:
        error = setpoint - pv
        # 比例
        p_term = self.kp * error
        # 积分
        if self.ti > 0.001:
            self._integral += error * dt
        i_term = self.kp / self.ti * self._integral
        # 微分（不完全微分，低通滤波）
        if dt > 0:
            d_term = self.kp * self.td * (error - self._prev_error) / dt
        else:
            d_term = 0.0
        self._prev_error = error
        self._output = p_term + i_term + d_term
        return self._output

    @property
    def output(self) -> float:
        return self._output

    @property
    def integral(self) -> float:
        return self._integral


class PIDController:
    """带抗积分饱和的PID控制器（条件积分法）"""

    def __init__(self, kp: float = 2.0, ti: float = 2.0, td: float = 0.5,
                 u_min: float = -30.0, u_max: float = 30.0):
        self.kp = kp
        self.ti = ti
        self.td = td
        self.u_min = u_min
        self.u_max = u_max
        self._integral = 0.0
        self._prev_error = 0.0
        self._output = 0.0
        self._saturated = False

    def reset(self):
        self._integral = 0.0
        self._prev_error = 0.0
        self._output = 0.0
        self._saturated = False

    def set_output_tracking(self, manual_output: float):
        """手动模式下的输出跟踪（无扰动切换）"""
        self._output = manual_output
        # 反算积分项使输出连续
        if self.kp > 0:
            self._integral = (manual_output - self.kp * self._prev_error) / (self.kp / self.ti) if self.ti > 0.001 else 0.0

    def step(self, setpoint: float, pv: float, dt: float) -> float:
        error = setpoint - pv

        p_term = self.kp * error

        d_term = 0.0
        if self.td > 0 and dt > 0:
            d_term = self.kp * self.td * (error - self._prev_error) / dt

        # 先计算未限幅的输出，用于判断是否会饱和
        i_term = self.kp / self.ti * self._integral if self.ti > 0.001 else 0.0
        raw_output = p_term + i_term + d_term

        # 条件积分：判断饱和方向
        # 如果输出已超上限且误差仍为正（需要继续增大输出），暂停积分
        # 如果输出已超下限且误差仍为负（需要继续减小输出），暂停积分
        should_integrate = True
        if raw_output > self.u_max and error > 0:
            should_integrate = False
            self._saturated = True
        elif raw_output < self.u_min and error < 0:
            should_integrate = False
            self._saturated = True
        else:
            self._saturated = False

        if should_integrate and self.ti > 0.001:
            self._integral += error * dt

        i_term = self.kp / self.ti * self._integral if self.ti > 0.001 else 0.0
        self._output = p_term + i_term + d_term

        # 输出限幅
        if self.u_max != float("inf") and self.u_min != float("-inf"):
            self._output = max(self.u_min, min(self.u_max, self._output))

        self._prev_error = error
        return self._output

    @property
    def output(self) -> float:
        return self._output

    @property
    def integral(self) -> float:
        return self._integral

    @property
    def saturated(self) -> bool:
        return self._saturated
