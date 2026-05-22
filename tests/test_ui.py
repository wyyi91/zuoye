"""UI组件测试（基础冒烟测试，需在GUI环境下运行）"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_imports():
    """测试所有模块能否正常导入"""
    from src.config import Paths, TempConfig, PIDDefaults, ControlStrategy, UserRole, Permissions
    from src.control.pid_controller import SimplePIDController, PIDController
    from src.control.cascade_control import CascadeController, CascadeWithFeedforward
    from src.control.feedforward_control import FeedforwardController, FeedforwardFeedbackController
    from src.control.control_strategy import ControlStrategyManager, ControlMode
    from src.model.two_inertia_model import FirstOrderLag, TwoInertiaModel
    from src.model.feedback_model import FeedbackModel, SensorWithNoise
    from src.model.disturbance import SquareWaveDisturbance, DisturbanceGenerator
    from src.utils.data_logger import DataLogger, HistoryDataManager
    from src.utils.excel_exporter import export_to_excel
    from src.utils.validator import validate_pid_params, validate_sv, validate_manual_output
    from src.utils.time_format import get_current_time_str, format_seconds
    print("所有模块导入成功！")


def test_control_strategy_manager():
    """测试控制策略管理器"""
    from src.control.control_strategy import ControlStrategyManager, ControlMode
    from src.config import ControlStrategy

    mgr = ControlStrategyManager()

    # 默认自动模式
    assert mgr.mode == ControlMode.AUTO

    # 切换到手动
    mgr.set_manual_mode()
    assert mgr.mode == ControlMode.MANUAL

    # 手动模式输出
    mgr.set_manual_output(5.0)
    out = mgr.step(setpoint=20.0, pv=0.0, dt=0.1)
    assert out == 5.0

    # 切换回自动
    mgr.set_auto_mode()
    out = mgr.step(setpoint=20.0, pv=0.0, dt=0.1)
    assert out > 0  # 应该有正输出

    # 切换策略
    mgr.set_strategy(ControlStrategy.SIMPLE_PID)
    assert mgr.strategy_type == ControlStrategy.SIMPLE_PID

    # 修改参数
    mgr.set_pid_params(kp=5.0, ti=1.0, td=0.0)
    out = mgr.step(setpoint=20.0, pv=10.0, dt=0.1)
    assert out > 0


def test_validator():
    from src.utils.validator import validate_pid_params, validate_sv

    ok, params, msg = validate_pid_params("2.0", "2.0", "0.5")
    assert ok
    assert params["kp"] == 2.0

    ok, params, msg = validate_pid_params("-1", "2.0", "0.5")
    assert not ok  # Kp不能为负

    ok, val, msg = validate_sv("25")
    assert ok
    assert val == 25.0

    ok, val, msg = validate_sv("999")
    assert not ok  # 超出范围


def test_data_logger():
    import tempfile
    import os as _os

    from src.utils.data_logger import DataLogger, HistoryDataManager

    logger = DataLogger()
    logger.start()
    logger.record(0.0, 20.0, 0.0, 0.0, 0.0, 20.0)
    logger.record(0.1, 20.0, 5.0, 10.0, 0.0, 15.0)
    logger.stop()

    assert logger.count == 2
    assert len(logger.data) == 2

    # 测试保存
    filepath = logger.save_to_file()
    assert _os.path.exists(filepath)


def test_excel_export():
    import tempfile
    import os as _os

    from src.utils.excel_exporter import export_to_excel

    data = [
        {"time": 0.0, "SV": 20.0, "PV": 0.0, "u": 0.0, "disturbance": 0.0, "error": 20.0},
        {"time": 0.1, "SV": 20.0, "PV": 5.0, "u": 10.0, "disturbance": 0.0, "error": 15.0},
    ]

    tmpfile = _os.path.join(tempfile.gettempdir(), "test_export.csv")
    ok = export_to_excel(data, tmpfile)
    assert ok
    assert _os.path.exists(tmpfile)

    with open(tmpfile, "r", encoding="utf-8-sig") as f:
        content = f.read()
        assert "SV" in content
        assert "20.0" in content

    _os.remove(tmpfile)


if __name__ == "__main__":
    test_imports()
    test_control_strategy_manager()
    test_validator()
    test_data_logger()
    test_excel_export()
    print("UI相关组件测试全部通过！")
