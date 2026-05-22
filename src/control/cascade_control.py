"""串级控制器 —— 外环+内环双回路"""

from src.control.pid_controller import PIDController, PIDParams


class CascadeController:
    """串级PID控制器：外环控制最终输出，内环控制中间变量"""

    def __init__(self,
                 outer_kp: float = 2.0, outer_ti: float = 2.0, outer_td: float = 0.5,
                 inner_kp: float = 1.0, inner_ti: float = 2.0, inner_td: float = 0.0,
                 u_min: float = -30.0, u_max: float = 30.0):
        self.outer = PIDController(outer_kp, outer_ti, outer_td, u_min=-1e10, u_max=1e10)
        self.inner = PIDController(inner_kp, inner_ti, inner_td, u_min=u_min, u_max=u_max)
        self._output = 0.0

    def reset(self):
        self.outer.reset()
        self.inner.reset()
        self._output = 0.0

    def set_output_tracking(self, manual_output: float):
        self._output = manual_output
        self.inner.set_output_tracking(manual_output)

    def step(self, setpoint: float, pv_outer: float, pv_inner: float, dt: float) -> float:
        """执行一步串级控制
        Args:
            setpoint: 设定值
            pv_outer: 外环反馈值（最终输出+干扰经过反馈环节）
            pv_inner: 内环反馈值（第一惯性环节输出）
            dt: 时间步长
        """
        # 外环计算内环设定值
        inner_setpoint = self.outer.step(setpoint, pv_outer, dt)
        # 内环计算控制量
        self._output = self.inner.step(inner_setpoint, pv_inner, dt)
        return self._output

    @property
    def output(self) -> float:
        return self._output


class CascadeWithFeedforward(CascadeController):
    """串级+前馈控制器"""

    def __init__(self,
                 outer_kp: float = 2.0, outer_ti: float = 2.0, outer_td: float = 0.5,
                 inner_kp: float = 1.0, inner_ti: float = 2.0, inner_td: float = 0.0,
                 ff_gain: float = -0.5,
                 u_min: float = -30.0, u_max: float = 30.0):
        super().__init__(outer_kp, outer_ti, outer_td, inner_kp, inner_ti, inner_td,
                         u_min, u_max)
        self.ff_gain = ff_gain

    def step(self, setpoint: float, pv_outer: float, pv_inner: float,
             disturbance: float = 0.0, dt: float = 0.1) -> float:
        # 前馈补偿
        ff_signal = self.ff_gain * disturbance
        # 串级控制
        inner_setpoint = self.outer.step(setpoint, pv_outer, dt)
        base_output = self.inner.step(inner_setpoint, pv_inner, dt)
        self._output = base_output + ff_signal
        # 限幅
        self._output = max(self.inner.u_min, min(self.inner.u_max, self._output))
        return self._output
