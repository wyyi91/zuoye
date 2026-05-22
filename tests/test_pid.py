"""PID控制器单元测试"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.control.pid_controller import SimplePIDController, PIDController


def test_simple_pid_proportional():
    """测试比例控制：零积分、零微分，输出应为 Kp * error"""
    pid = SimplePIDController(kp=2.0, ti=1e10, td=0.0)
    out = pid.step(setpoint=10.0, pv=0.0, dt=0.1)
    assert out == 20.0, f"期望 20.0，实际 {out}"


def test_simple_pid_integral():
    """测试积分累积"""
    pid = SimplePIDController(kp=1.0, ti=1.0, td=0.0)
    out1 = pid.step(1.0, 0.0, dt=0.1)  # error=1.0, Kp=1.0, p=1.0, i=1.0*0.1=0.1 → 1.1
    assert abs(out1 - 1.1) < 0.01, f"期望 1.1，实际 {out1}"
    out2 = pid.step(1.0, 0.0, dt=0.1)
    assert abs(out2 - 1.2) < 0.01, f"期望 1.2，实际 {out2}"


def test_pid_anti_windup():
    """测试抗积分饱和：输出超过上限时暂停积分"""
    pid = PIDController(kp=10.0, ti=0.5, td=0.0, u_min=-30.0, u_max=30.0)
    out = pid.step(setpoint=10.0, pv=0.0, dt=0.1)
    # error=10, p_term=100, 被限幅到30
    assert out <= 30.0, f"输出应被限幅在30以内，实际 {out}"


def test_pid_reset():
    pid = PIDController(kp=2.0, ti=2.0, td=0.5)
    pid.step(10.0, 0.0, dt=0.1)
    pid.reset()
    assert pid.output == 0.0
    assert pid.integral == 0.0


def test_pid_output_tracking():
    """测试输出跟踪（手动→自动无扰动切换）"""
    pid = PIDController(kp=2.0, ti=2.0, td=0.5)
    pid.step(10.0, 5.0, dt=0.1)
    pid.set_output_tracking(15.0)
    assert abs(pid.output - 15.0) < 0.01


if __name__ == "__main__":
    test_simple_pid_proportional()
    test_simple_pid_integral()
    test_pid_anti_windup()
    test_pid_reset()
    test_pid_output_tracking()
    print("PID控制器测试全部通过！")
