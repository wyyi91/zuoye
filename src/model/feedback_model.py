"""反馈环节模型 —— 一阶低通滤波器 H(s) = 1/(Tc*s + 1)，模拟传感器动态特性"""

import random


class FeedbackModel:
    """一阶低通滤波反馈环节"""

    def __init__(self, time_constant: float = 0.1):
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


class SensorWithNoise(FeedbackModel):
    """带测量噪声的传感器模型"""

    def __init__(self, time_constant: float = 0.1, noise_std: float = 0.05):
        super().__init__(time_constant)
        self.noise_std = noise_std

    def step(self, input_val: float, dt: float) -> float:
        clean = super().step(input_val, dt)
        noisy = clean + random.gauss(0, self.noise_std)
        self._output = noisy
        return noisy
