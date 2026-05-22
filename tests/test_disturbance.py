"""干扰信号单元测试"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.model.disturbance import SquareWaveDisturbance, DisturbanceGenerator


def test_square_wave_trigger():
    """测试方波触发和衰减"""
    sw = SquareWaveDisturbance(amplitude=5.0, duration=2.0)
    sw.trigger()

    assert sw.is_active
    assert sw.amplitude == 5.0

    # 模拟2秒内的输出
    for _ in range(200):
        val = sw.update(dt=0.01)

    assert not sw.is_active
    assert sw.remaining_time == 0.0


def test_disturbance_zero_when_inactive():
    sw = SquareWaveDisturbance(amplitude=3.0, duration=1.0)
    val = sw.update(dt=0.1)
    assert val == 0.0
    assert not sw.is_active


def test_disturbance_generator():
    gen = DisturbanceGenerator()
    gen.trigger(amplitude=4.0, duration=1.0)
    assert gen.is_active

    val = gen.update(dt=0.5)
    assert val == 4.0
    assert abs(gen.remaining_time - 0.5) < 0.01


if __name__ == "__main__":
    test_square_wave_trigger()
    test_disturbance_zero_when_inactive()
    test_disturbance_generator()
    print("干扰信号测试全部通过！")
