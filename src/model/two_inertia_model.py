"""双惯性环节串联被控对象模型 G(s) = Gain / ((T1*s + 1)(T2*s + 1))"""

import math


class FirstOrderLag:
    """一阶惯性环节 1/(T*s + 1)，使用离散化递推"""

    def __init__(self, time_constant: float = 1.0):
        self.time_constant = time_constant
        self._output = 0.0

    def reset(self, initial_value: float = 0.0):
        self._output = initial_value

    def step(self, input_val: float, dt: float) -> float:
        if self.time_constant <= 0:
            self._output = input_val
        else:
            alpha = dt / (self.time_constant + dt)
            self._output += alpha * (input_val - self._output)
        return self._output

    @property
    def output(self) -> float:
        return self._output


class TwoInertiaModel:
    """双惯性环节串联模型：out = Gain / ((T1*s+1)(T2*s+1)) * input"""

    def __init__(self, t1: float = 1.0, t2: float = 2.0, gain: float = 1.0):
        self.t1 = t1
        self.t2 = t2
        self.gain = gain
        self._first = FirstOrderLag(t1)
        self._second = FirstOrderLag(t2)
        self._mid_output = 0.0  # 中间变量（第一环节输出）
        self._output = 0.0

    def reset(self, initial_value: float = 0.0):
        self._first.reset(initial_value / self.gain if self.gain != 0 else 0.0)
        self._second.reset(initial_value)
        self._mid_output = self._first.output
        self._output = initial_value

    def step(self, input_val: float, dt: float) -> tuple[float, float]:
        """执行一步仿真，返回 (最终输出, 中间变量)"""
        self._mid_output = self._first.step(input_val * self.gain, dt)
        self._output = self._second.step(self._mid_output, dt)
        return self._output, self._mid_output

    @property
    def output(self) -> float:
        return self._output

    @property
    def mid_output(self) -> float:
        return self._mid_output
