"""全局配置模块 —— 路径、参数范围、权限常量、控制策略枚举"""

from enum import Enum, auto
import sys
import os


# =============================================================================
# 路径配置 —— 自适应开发与打包环境
# =============================================================================
class Paths:
    if getattr(sys, "frozen", False):
        BASE_DIR = os.path.dirname(sys.executable)
        # PyInstaller onefile: bundled read-only assets extracted to _MEIPASS
        ASSETS_SRC = os.path.join(getattr(sys, "_MEIPASS", BASE_DIR), "assets")
    else:
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ASSETS_SRC = os.path.join(BASE_DIR, "assets")

    DATA_DIR = os.path.join(BASE_DIR, "data")
    HISTORY_DIR = os.path.join(DATA_DIR, "history_data")
    USERS_DIR = os.path.join(DATA_DIR, "users")
    LOGS_DIR = os.path.join(DATA_DIR, "logs")

    USERS_FILE = os.path.join(USERS_DIR, "users.json")
    ERROR_LOG = os.path.join(LOGS_DIR, "error.log")

    STYLE_QSS = os.path.join(ASSETS_SRC, "style.qss")

    @classmethod
    def ensure_dirs(cls):
        for d in [cls.DATA_DIR, cls.HISTORY_DIR, cls.USERS_DIR, cls.LOGS_DIR]:
            os.makedirs(d, exist_ok=True)


# =============================================================================
# 用户角色与权限
# =============================================================================
class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"


class Permissions:
    CHANGE_OWN_PASSWORD = "change_own_password"
    MANAGE_USERS = "manage_users"
    MODIFY_PERMISSIONS = "modify_permissions"
    RUN_SIMULATION = "run_simulation"
    EXPORT_DATA = "export_data"

    ROLE_PERMISSIONS = {
        UserRole.ADMIN: [
            CHANGE_OWN_PASSWORD, MANAGE_USERS, MODIFY_PERMISSIONS,
            RUN_SIMULATION, EXPORT_DATA,
        ],
        UserRole.USER: [
            CHANGE_OWN_PASSWORD, RUN_SIMULATION, EXPORT_DATA,
        ],
    }


# =============================================================================
# 控制策略枚举
# =============================================================================
class ControlStrategy(Enum):
    SIMPLE_PID = auto()           # 普通PID（无限幅）
    SINGLE_LOOP_PID = auto()      # 单回路PID（带抗饱和）
    FEEDFORWARD_FEEDBACK = auto()  # 前馈+反馈
    CASCADE_PID = auto()          # 串级PID
    CASCADE_FEEDFORWARD = auto()  # 串级+前馈


CONTROL_STRATEGY_LABELS = {
    ControlStrategy.SIMPLE_PID: "普通PID（无限幅）",
    ControlStrategy.SINGLE_LOOP_PID: "单回路PID（抗饱和）",
    ControlStrategy.FEEDFORWARD_FEEDBACK: "前馈+反馈",
    ControlStrategy.CASCADE_PID: "串级PID",
    ControlStrategy.CASCADE_FEEDFORWARD: "串级+前馈",
}


# =============================================================================
# 温度控制参数
# =============================================================================
class TempConfig:
    SV_MIN = 0.0
    SV_MAX = 30.0
    SV_DEFAULT = 20.0
    PV_INITIAL = 0.0

    U_AUTO_RANGE = (-30.0, 30.0)
    U_MANUAL_RANGE = (-30.0, 30.0)

    T1_DEFAULT = 1.0
    T2_DEFAULT = 2.0
    GAIN_DEFAULT = 1.0
    TC_DEFAULT = 0.1  # 反馈环节时间常数

    DISTURBANCE_AMPLITUDE_DEFAULT = 0.0
    DISTURBANCE_DURATION_DEFAULT = 5.0

    DISPLAY_POINTS_MAX = 5000
    TIMER_INTERVAL_MS = 100  # 仿真步长（毫秒）


# =============================================================================
# PID 默认参数
# =============================================================================
class PIDDefaults:
    KP = 2.0
    TI = 2.0
    TD = 0.5

    CASCADE_OUTER_KP = 2.0
    CASCADE_OUTER_TI = 2.0
    CASCADE_OUTER_TD = 0.5

    CASCADE_INNER_KP = 1.0
    CASCADE_INNER_TI = 2.0
    CASCADE_INNER_TD = 0.0

    FEEDFORWARD_GAIN = -0.5

    KP_MIN = 0.0
    TI_MIN = 0.001  # 避免除零
    TD_MIN = 0.0
