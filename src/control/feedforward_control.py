"""前馈控制器 —— 静态增益补偿 + 动态前馈"""

from src.control.pid_controller import PIDController


class FeedforwardController:
    """纯前馈控制器（静态增益补偿）"""

    def __init__(self, ff_gain: float = -0.5):
        self.ff_gain = ff_gain
        self._output = 0.0

    def reset(self):
        self._output = 0.0

    def step(self, disturbance: float) -> float:
        self._output = self.ff_gain * disturbance
        return self._output

    @property
    def output(self) -> float:
        return self._output


class FeedforwardFeedbackController:
    """前馈+反馈复合控制器"""

    def __init__(self,
                 kp: float = 2.0, ti: float = 2.0, td: float = 0.5,
                 ff_gain: float = -0.5,
                 u_min: float = -30.0, u_max: float = 30.0):
        self.pid = PIDController(kp, ti, td, u_min=u_min, u_max=u_max)
        self.ff = FeedforwardController(ff_gain)
        self._output = 0.0

    def reset(self):
        self.pid.reset()
        self.ff.reset()
        self._output = 0.0

    def set_output_tracking(self, manual_output: float):
        self._output = manual_output
        self.pid.set_output_tracking(manual_output)

    def step(self, setpoint: float, pv: float, disturbance: float = 0.0, dt: float = 0.1) -> float:
        ff_signal = self.ff.step(disturbance)
        fb_signal = self.pid.step(setpoint, pv, dt)
        self._output = fb_signal + ff_signal
        # 限幅
        self._output = max(self.pid.u_min, min(self.pid.u_max, self._output))
        return self._output

    @property
    def output(self) -> float:
        return self._output
