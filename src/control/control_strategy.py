"""控制策略管理器 —— 5种策略切换、手动/自动模式、无扰动切换"""

from enum import Enum
from src.config import ControlStrategy, TempConfig, PIDDefaults
from src.control.pid_controller import SimplePIDController, PIDController
from src.control.cascade_control import CascadeController, CascadeWithFeedforward
from src.control.feedforward_control import FeedforwardFeedbackController


class ControlMode(Enum):
    AUTO = "auto"
    MANUAL = "manual"


class ControlStrategyManager:
    """控制策略管理器"""

    def __init__(self):
        self._mode = ControlMode.AUTO
        self._strategy_type = ControlStrategy.SINGLE_LOOP_PID
        self._manual_output = 0.0

        # 初始化所有控制器
        self._simple_pid = SimplePIDController(
            PIDDefaults.KP, PIDDefaults.TI, PIDDefaults.TD
        )
        self._single_loop_pid = PIDController(
            PIDDefaults.KP, PIDDefaults.TI, PIDDefaults.TD,
            u_min=TempConfig.U_AUTO_RANGE[0], u_max=TempConfig.U_AUTO_RANGE[1]
        )
        self._ff_fb = FeedforwardFeedbackController(
            PIDDefaults.KP, PIDDefaults.TI, PIDDefaults.TD,
            ff_gain=PIDDefaults.FEEDFORWARD_GAIN,
            u_min=TempConfig.U_AUTO_RANGE[0], u_max=TempConfig.U_AUTO_RANGE[1]
        )
        self._cascade = CascadeController(
            PIDDefaults.CASCADE_OUTER_KP, PIDDefaults.CASCADE_OUTER_TI, PIDDefaults.CASCADE_OUTER_TD,
            PIDDefaults.CASCADE_INNER_KP, PIDDefaults.CASCADE_INNER_TI, PIDDefaults.CASCADE_INNER_TD,
            u_min=TempConfig.U_AUTO_RANGE[0], u_max=TempConfig.U_AUTO_RANGE[1]
        )
        self._cascade_ff = CascadeWithFeedforward(
            PIDDefaults.CASCADE_OUTER_KP, PIDDefaults.CASCADE_OUTER_TI, PIDDefaults.CASCADE_OUTER_TD,
            PIDDefaults.CASCADE_INNER_KP, PIDDefaults.CASCADE_INNER_TI, PIDDefaults.CASCADE_INNER_TD,
            ff_gain=PIDDefaults.FEEDFORWARD_GAIN,
            u_min=TempConfig.U_AUTO_RANGE[0], u_max=TempConfig.U_AUTO_RANGE[1]
        )

        self._controllers = {
            ControlStrategy.SIMPLE_PID: self._simple_pid,
            ControlStrategy.SINGLE_LOOP_PID: self._single_loop_pid,
            ControlStrategy.FEEDFORWARD_FEEDBACK: self._ff_fb,
            ControlStrategy.CASCADE_PID: self._cascade,
            ControlStrategy.CASCADE_FEEDFORWARD: self._cascade_ff,
        }

    # ---- 模式切换 ----

    @property
    def mode(self) -> ControlMode:
        return self._mode

    def set_auto_mode(self):
        """切换到自动模式（无扰动切换：当前输出跟踪）"""
        if self._mode == ControlMode.MANUAL:
            self._set_all_output_tracking(self._manual_output)
        self._mode = ControlMode.AUTO

    def set_manual_mode(self):
        """切换到手动模式"""
        self._mode = ControlMode.MANUAL

    def set_manual_output(self, value: float):
        self._manual_output = value

    # ---- 策略切换 ----

    @property
    def strategy_type(self) -> ControlStrategy:
        return self._strategy_type

    def set_strategy(self, strategy: ControlStrategy):
        """切换控制策略"""
        if strategy != self._strategy_type:
            # 跟踪当前输出，避免策略切换冲击
            current_output = self.output
            ctrl = self._controllers[strategy]
            if hasattr(ctrl, "set_output_tracking"):
                ctrl.set_output_tracking(current_output)
            elif hasattr(ctrl, "reset"):
                ctrl.reset()
            self._strategy_type = strategy

    @property
    def active_controller(self):
        return self._controllers[self._strategy_type]

    # ---- PID参数实时更新 ----

    def set_pid_params(self, kp: float = None, ti: float = None, td: float = None):
        """设置单回路PID参数（不影响串级）"""
        for ctrl in [self._simple_pid, self._single_loop_pid, self._ff_fb.pid]:
            if kp is not None:
                ctrl.kp = kp
            if ti is not None:
                ctrl.ti = max(ti, 0.001)
            if td is not None:
                ctrl.td = td

    def set_cascade_outer_params(self, kp: float = None, ti: float = None, td: float = None):
        for ctrl in [self._cascade, self._cascade_ff]:
            if kp is not None:
                ctrl.outer.kp = kp
            if ti is not None:
                ctrl.outer.ti = max(ti, 0.001)
            if td is not None:
                ctrl.outer.td = td

    def set_cascade_inner_params(self, kp: float = None, ti: float = None, td: float = None):
        for ctrl in [self._cascade, self._cascade_ff]:
            if kp is not None:
                ctrl.inner.kp = kp
            if ti is not None:
                ctrl.inner.ti = max(ti, 0.001)
            if td is not None:
                ctrl.inner.td = td

    def set_feedforward_gain(self, ff_gain: float):
        self._ff_fb.ff.ff_gain = ff_gain
        self._cascade_ff.ff_gain = ff_gain

    # ---- 仿真步进 ----

    def step(self, setpoint: float, pv: float, pv_inner: float = 0.0,
             disturbance: float = 0.0, dt: float = 0.1) -> float:
        """执行一步控制计算，返回控制量"""
        if self._mode == ControlMode.MANUAL:
            self._set_all_output_tracking(self._manual_output)
            return self._manual_output

        if self._strategy_type == ControlStrategy.SIMPLE_PID:
            return self._simple_pid.step(setpoint, pv, dt)

        elif self._strategy_type == ControlStrategy.SINGLE_LOOP_PID:
            return self._single_loop_pid.step(setpoint, pv, dt)

        elif self._strategy_type == ControlStrategy.FEEDFORWARD_FEEDBACK:
            return self._ff_fb.step(setpoint, pv, disturbance, dt)

        elif self._strategy_type == ControlStrategy.CASCADE_PID:
            return self._cascade.step(setpoint, pv, pv_inner, dt)

        elif self._strategy_type == ControlStrategy.CASCADE_FEEDFORWARD:
            return self._cascade_ff.step(setpoint, pv, pv_inner, disturbance, dt)

        return 0.0

    @property
    def output(self) -> float:
        return self.active_controller.output if hasattr(self.active_controller, "output") else 0.0

    def reset(self):
        for ctrl in self._controllers.values():
            ctrl.reset()
        self._manual_output = 0.0

    def _set_all_output_tracking(self, output: float):
        for ctrl in self._controllers.values():
            if hasattr(ctrl, "set_output_tracking"):
                ctrl.set_output_tracking(output)
