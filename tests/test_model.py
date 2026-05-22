"""被控对象模型单元测试"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.model.two_inertia_model import FirstOrderLag, TwoInertiaModel


def test_first_order_lag_step_response():
    """测试一阶惯性环节阶跃响应"""
    lag = FirstOrderLag(time_constant=1.0)
    for _ in range(100):
        out = lag.step(1.0, dt=0.1)
    # 10秒后（10倍时间常数），输出应接近1.0
    assert abs(out - 1.0) < 0.01, f"期望接近1.0，实际 {out}"


def test_two_inertia_model():
    """测试双惯性环节"""
    model = TwoInertiaModel(t1=1.0, t2=2.0, gain=1.0)
    final_out = 0.0
    for _ in range(500):
        final_out, mid = model.step(1.0, dt=0.1)
    # 50秒后输出应接近1.0
    assert abs(final_out - 1.0) < 0.05, f"期望接近1.0，实际 {final_out}"


def test_model_reset():
    model = TwoInertiaModel(t1=1.0, t2=2.0, gain=2.0)
    for _ in range(50):
        model.step(1.0, dt=0.1)
    model.reset(10.0)
    assert abs(model.output - 10.0) < 0.01
    assert abs(model.mid_output - 5.0) < 0.5  # 中间值应为 output/gain


if __name__ == "__main__":
    test_first_order_lag_step_response()
    test_two_inertia_model()
    test_model_reset()
    print("被控对象模型测试全部通过！")
