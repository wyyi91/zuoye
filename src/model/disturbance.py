"""干扰信号发生器 —— 方波干扰"""

from dataclasses import dataclass
import time


@dataclass
class DisturbanceConfig:
    amplitude: float = 0.0
    duration: float = 5.0  # 秒


class SquareWaveDisturbance:
    """方波干扰发生器"""

    def __init__(self, amplitude: float = 0.0, duration: float = 5.0):
        self.amplitude = amplitude
        self.duration = duration
        self._active = False
        self._start_time = 0.0
        self._elapsed = 0.0

    def trigger(self, amplitude: float = None, duration: float = None):
        if amplitude is not None:
            self.amplitude = amplitude
        if duration is not None:
            self.duration = duration
        self._active = True
        self._start_time = time.time()
        self._elapsed = 0.0

    def update(self, dt: float) -> float:
        """更新干扰状态，返回当前干扰值"""
        if self._active:
            self._elapsed += dt
            if self._elapsed >= self.duration:
                self._active = False
                return 0.0
            return self.amplitude
        return 0.0

    def reset(self):
        self._active = False
        self._elapsed = 0.0

    @property
    def is_active(self) -> bool:
        return self._active

    @property
    def remaining_time(self) -> float:
        if not self._active:
            return 0.0
        return max(0.0, self.duration - self._elapsed)


class DisturbanceGenerator:
    """干扰管理类 —— 封装方波干扰的触发与更新"""

    def __init__(self):
        self._disturbance = SquareWaveDisturbance()

    def trigger(self, amplitude: float, duration: float):
        self._disturbance.trigger(amplitude, duration)

    def update(self, dt: float) -> float:
        return self._disturbance.update(dt)

    def reset(self):
        self._disturbance.reset()

    @property
    def is_active(self) -> bool:
        return self._disturbance.is_active

    @property
    def remaining_time(self) -> float:
        return self._disturbance.remaining_time

    @property
    def amplitude(self) -> float:
        return self._disturbance.amplitude

    @property
    def duration(self) -> float:
        return self._disturbance.duration
