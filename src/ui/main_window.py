"""主界面 —— 菜单、控制面板、波形显示、仿真循环"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QMenuBar, QMenu, QMessageBox, QLabel, QDoubleSpinBox,
    QGroupBox, QComboBox, QPushButton, QGridLayout, QFrame,
    QTabWidget,
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QAction

from src.config import (
    ControlStrategy, CONTROL_STRATEGY_LABELS,
    TempConfig, PIDDefaults, UserRole, Permissions,
)
from src.control.control_strategy import ControlStrategyManager, ControlMode
from src.model.two_inertia_model import TwoInertiaModel
from src.model.feedback_model import FeedbackModel
from src.model.disturbance import DisturbanceGenerator
from src.user.user_manager import UserManager
from src.user.permission import CurrentUser
from src.ui.plot_widget import PlotWidget
from src.ui.widgets import ControlPanel, PIDParamGroup, StatusBar
from src.ui.history_window import HistoryWindow
from src.ui.user_manager_ui import UserManagerWindow
from src.ui.change_pwd_ui import ChangePasswordDialog
from src.utils.data_logger import DataLogger
from src.utils.validator import validate_sv, validate_manual_output
from src.exception import show_error_dialog, show_info_dialog


class MainWindow(QMainWindow):
    """仿真系统主界面"""

    def __init__(self, user_manager: UserManager):
        super().__init__()
        self._user_manager = user_manager

        # 仿真模型
        self._plant = TwoInertiaModel(TempConfig.T1_DEFAULT,
                                       TempConfig.T2_DEFAULT,
                                       TempConfig.GAIN_DEFAULT)
        self._feedback = FeedbackModel(TempConfig.TC_DEFAULT)
        self._disturbance = DisturbanceGenerator()

        # 控制策略管理器
        self._ctrl_manager = ControlStrategyManager()

        # 数据记录器
        self._logger = DataLogger()

        # 仿真状态
        self._sim_time = 0.0
        self._running = False
        self._paused = False
        self._sv = TempConfig.SV_DEFAULT  # 设定值
        self._pv = TempConfig.PV_INITIAL   # 过程值
        self._u = 0.0                      # 控制量
        self._current_strategy = ControlStrategy.SINGLE_LOOP_PID

        # 窗口引用
        self._history_window = None
        self._user_manager_window = None

        self._setup_ui()
        self._setup_timer()
        self._update_status_bar()

    # =========================================================================
    # UI 构建
    # =========================================================================
    def _setup_ui(self):
        self.setWindowTitle("PID温度控制仿真系统")
        self.setMinimumSize(1100, 750)

        self._setup_menu()
        self._setup_central()
        self._setup_statusbar()

    def _setup_menu(self):
        mb = self.menuBar()

        # 系统菜单
        sys_menu = mb.addMenu("系统")
        logout_action = QAction("退出登录", self)
        logout_action.triggered.connect(self._on_logout)
        sys_menu.addAction(logout_action)

        exit_action = QAction("退出程序", self)
        exit_action.triggered.connect(self.close)
        sys_menu.addAction(exit_action)

        # 功能菜单
        func_menu = mb.addMenu("功能")
        history_action = QAction("历史曲线", self)
        history_action.triggered.connect(self._open_history)
        func_menu.addAction(history_action)

        # 用户管理菜单
        self._user_menu = mb.addMenu("用户管理")
        change_pwd_action = QAction("修改密码", self)
        change_pwd_action.triggered.connect(self._change_password)
        self._user_menu.addAction(change_pwd_action)

        manage_user_action = QAction("管理用户", self)
        manage_user_action.triggered.connect(self._open_user_manager)
        self._user_menu.addAction(manage_user_action)
        self._manage_user_action = manage_user_action

        # 帮助菜单
        help_menu = mb.addMenu("帮助")
        about_action = QAction("关于软件", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

        self._update_menu_permissions()

    def _setup_central(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(6, 6, 6, 6)

        # ---- 左侧面板 ----
        left_panel = QWidget()
        left_panel.setFixedWidth(380)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)

        # 设定值
        sv_group = QGroupBox("温度设定")
        sv_layout = QHBoxLayout(sv_group)
        sv_layout.addWidget(QLabel("SV 设定温度:"))
        self._sv_spin = QDoubleSpinBox()
        self._sv_spin.setRange(TempConfig.SV_MIN, TempConfig.SV_MAX)
        self._sv_spin.setValue(TempConfig.SV_DEFAULT)
        self._sv_spin.setDecimals(1)
        self._sv_spin.setSuffix(" °C")
        self._sv_spin.valueChanged.connect(self._on_sv_changed)
        sv_layout.addWidget(self._sv_spin)
        left_layout.addWidget(sv_group)

        # 控制模式 & 策略
        mode_group = QGroupBox("控制模式与策略")
        mode_layout = QGridLayout(mode_group)
        mode_layout.setSpacing(6)

        mode_layout.addWidget(QLabel("模式:"), 0, 0)
        self._mode_combo = QComboBox()
        self._mode_combo.addItem("自动", ControlMode.AUTO)
        self._mode_combo.addItem("手动", ControlMode.MANUAL)
        self._mode_combo.currentIndexChanged.connect(self._on_mode_changed)
        mode_layout.addWidget(self._mode_combo, 0, 1)

        mode_layout.addWidget(QLabel("策略:"), 1, 0)
        self._strategy_combo = QComboBox()
        for s in ControlStrategy:
            self._strategy_combo.addItem(CONTROL_STRATEGY_LABELS[s], s)
        self._strategy_combo.currentIndexChanged.connect(self._on_strategy_changed)
        mode_layout.addWidget(self._strategy_combo, 1, 1)

        # 手动输出
        mode_layout.addWidget(QLabel("手动输出u:"), 2, 0)
        self._manual_u_spin = QDoubleSpinBox()
        self._manual_u_spin.setRange(-30, 30)
        self._manual_u_spin.setValue(0)
        self._manual_u_spin.setDecimals(2)
        self._manual_u_spin.setEnabled(False)
        self._manual_u_spin.valueChanged.connect(self._on_manual_u_changed)
        mode_layout.addWidget(self._manual_u_spin, 2, 1)

        left_layout.addWidget(mode_group)

        # PID参数面板（选项卡）
        pid_tabs = QTabWidget()
        self._main_pid_panel = PIDParamGroup("主控制器PID",
                                              PIDDefaults.KP, PIDDefaults.TI, PIDDefaults.TD)
        self._main_pid_panel.params_changed.connect(self._on_main_pid_changed)
        pid_tabs.addTab(self._main_pid_panel, "主PID")

        self._cascade_panel = QWidget()
        cascade_layout = QVBoxLayout(self._cascade_panel)
        self._outer_pid = PIDParamGroup("外环PID",
                                         PIDDefaults.CASCADE_OUTER_KP,
                                         PIDDefaults.CASCADE_OUTER_TI,
                                         PIDDefaults.CASCADE_OUTER_TD)
        self._outer_pid.params_changed.connect(self._on_outer_pid_changed)
        self._inner_pid = PIDParamGroup("内环PID",
                                         PIDDefaults.CASCADE_INNER_KP,
                                         PIDDefaults.CASCADE_INNER_TI,
                                         PIDDefaults.CASCADE_INNER_TD)
        self._inner_pid.params_changed.connect(self._on_inner_pid_changed)
        cascade_layout.addWidget(self._outer_pid)
        cascade_layout.addWidget(self._inner_pid)
        cascade_layout.addStretch()
        pid_tabs.addTab(self._cascade_panel, "串级PID")

        self._ff_panel = QWidget()
        ff_layout = QVBoxLayout(self._ff_panel)
        ff_gain_group = QGroupBox("前馈增益")
        ff_gain_hlayout = QHBoxLayout(ff_gain_group)
        ff_gain_hlayout.addWidget(QLabel("Gff:"))
        self._ff_gain_spin = QDoubleSpinBox()
        self._ff_gain_spin.setRange(-10, 10)
        self._ff_gain_spin.setValue(PIDDefaults.FEEDFORWARD_GAIN)
        self._ff_gain_spin.setDecimals(2)
        self._ff_gain_spin.setSingleStep(0.1)
        self._ff_gain_spin.valueChanged.connect(self._on_ff_gain_changed)
        ff_gain_hlayout.addWidget(self._ff_gain_spin)
        ff_layout.addWidget(ff_gain_group)
        ff_layout.addStretch()
        pid_tabs.addTab(self._ff_panel, "前馈")

        left_layout.addWidget(pid_tabs)

        # 仿真控制按钮
        self._control_panel = ControlPanel()
        self._control_panel.start_clicked.connect(self._start_sim)
        self._control_panel.stop_clicked.connect(self._stop_sim)
        self._control_panel.pause_clicked.connect(self._toggle_pause)
        self._control_panel.disturb_clicked.connect(self._apply_disturbance)
        left_layout.addWidget(self._control_panel)

        # 实时值显示
        values_group = QGroupBox("实时数值")
        values_layout = QGridLayout(values_group)
        values_layout.setSpacing(4)
        self._pv_label = QLabel("0.00")
        self._pv_label.setStyleSheet("font-size: 16px; font-weight: bold; color: green;")
        self._u_label = QLabel("0.00")
        self._u_label.setStyleSheet("font-size: 16px; font-weight: bold; color: blue;")
        self._error_label = QLabel("0.00")
        self._dist_status_label = QLabel("无干扰")

        values_layout.addWidget(QLabel("PV:"), 0, 0)
        values_layout.addWidget(self._pv_label, 0, 1)
        values_layout.addWidget(QLabel("u:"), 0, 2)
        values_layout.addWidget(self._u_label, 0, 3)
        values_layout.addWidget(QLabel("误差:"), 1, 0)
        values_layout.addWidget(self._error_label, 1, 1)
        values_layout.addWidget(QLabel("干扰:"), 1, 2)
        values_layout.addWidget(self._dist_status_label, 1, 3)
        left_layout.addWidget(values_group)

        left_layout.addStretch()

        # ---- 右侧波形显示 ----
        self._plot = PlotWidget()
        self._plot.enable_auto_range()

        # 主布局
        main_layout.addWidget(left_panel)
        main_layout.addWidget(self._plot, stretch=1)

    def _setup_statusbar(self):
        self._status_bar = StatusBar()
        self.setStatusBar(self._status_bar)

    def _setup_timer(self):
        self._sim_timer = QTimer()
        self._sim_timer.timeout.connect(self._sim_step)
        self._disturb_timer = QTimer()
        self._disturb_timer.timeout.connect(self._update_disturb_button)
        self._disturb_timer.start(200)

    # =========================================================================
    # 菜单动作
    # =========================================================================
    def _on_logout(self):
        reply = QMessageBox.question(
            self, "确认", "确定要退出登录吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._stop_sim()
            self._user_manager.logout()
            self.close()
            # 发出信号让main.py重新显示登录
            self._should_relogin = True

    def _open_history(self):
        if self._history_window is None:
            self._history_window = HistoryWindow(self)
        self._history_window.show()
        self._history_window.raise_()

    def _change_password(self):
        dlg = ChangePasswordDialog(self._user_manager, self)
        dlg.exec()

    def _open_user_manager(self):
        if not CurrentUser.has_permission(Permissions.MANAGE_USERS):
            show_error_dialog(self, "权限不足", "只有管理员可以管理用户。")
            return
        if self._user_manager_window is None:
            self._user_manager_window = UserManagerWindow(self._user_manager)
        self._user_manager_window.show()
        self._user_manager_window.raise_()

    def _show_about(self):
        show_info_dialog(
            self, "关于软件",
            "PID温度控制仿真系统 v1.0\n\n"
            "基于双惯性环节模型的温度控制仿真教学软件。\n"
            "支持5种控制策略的对比演示。\n\n"
            "技术栈: Python + PyQt6 + pyqtgraph"
        )

    # =========================================================================
    # 仿真控制
    # =========================================================================
    def _on_sv_changed(self, value: float):
        self._sv = value

    def _on_mode_changed(self, index: int):
        mode = self._mode_combo.currentData()
        if mode == ControlMode.AUTO:
            self._ctrl_manager.set_auto_mode()
            self._manual_u_spin.setEnabled(False)
        else:
            self._ctrl_manager.set_manual_mode()
            self._manual_u_spin.setEnabled(True)
        self._update_status_bar()

    def _on_strategy_changed(self, index: int):
        strategy = self._strategy_combo.currentData()
        self._current_strategy = strategy
        self._ctrl_manager.set_strategy(strategy)
        # 更新PID面板可见性
        is_cascade = strategy in (ControlStrategy.CASCADE_PID,
                                   ControlStrategy.CASCADE_FEEDFORWARD)
        is_ff = strategy in (ControlStrategy.FEEDFORWARD_FEEDBACK,
                             ControlStrategy.CASCADE_FEEDFORWARD)
        self._update_status_bar()

    def _on_main_pid_changed(self, kp: float, ti: float, td: float):
        self._ctrl_manager.set_pid_params(kp, ti, td)

    def _on_outer_pid_changed(self, kp: float, ti: float, td: float):
        self._ctrl_manager.set_cascade_outer_params(kp, ti, td)

    def _on_inner_pid_changed(self, kp: float, ti: float, td: float):
        self._ctrl_manager.set_cascade_inner_params(kp, ti, td)

    def _on_ff_gain_changed(self, value: float):
        self._ctrl_manager.set_feedforward_gain(value)

    def _on_manual_u_changed(self, value: float):
        self._ctrl_manager.set_manual_output(value)

    def _start_sim(self):
        self._running = True
        self._paused = False
        self._sim_time = 0.0
        self._plant.reset()
        self._feedback.reset()
        self._disturbance.reset()
        self._ctrl_manager.reset()
        self._plot.clear()
        self._logger.reset()
        self._logger.start()
        self._sim_timer.start(TempConfig.TIMER_INTERVAL_MS)
        self._control_panel.set_running_state(True)
        self._update_status_bar()

    def _stop_sim(self):
        self._running = False
        self._sim_timer.stop()
        self._logger.stop()
        if self._logger.count > 0:
            self._logger.save_to_file()
        self._control_panel.set_running_state(False)
        self._status_bar.show_message("仿真已停止")
        self._update_status_bar()

    def _toggle_pause(self, paused: bool):
        self._paused = paused
        if paused:
            self._sim_timer.stop()
            self._status_bar.show_message("仿真已暂停")
        else:
            self._sim_timer.start(TempConfig.TIMER_INTERVAL_MS)
            self._status_bar.show_message("仿真继续运行")

    def _apply_disturbance(self, amplitude: float, duration: float):
        if not self._running:
            show_error_dialog(self, "提示", "请先开始仿真再施加干扰。")
            return
        self._disturbance.trigger(amplitude, duration)
        self._status_bar.show_message(f"施加方波干扰: 振幅={amplitude}, 持续={duration}s")

    # =========================================================================
    # 仿真步进
    # =========================================================================
    def _sim_step(self):
        if not self._running or self._paused:
            return

        dt = TempConfig.TIMER_INTERVAL_MS / 1000.0
        self._sim_time += dt

        try:
            # 更新干扰
            dist_value = self._disturbance.update(dt)

            # 控制计算
            pv_feedback = self._feedback.output  # 反馈环节输出
            pv_plant = self._plant.output         # 被控对象原始输出
            pv_inner = self._plant.mid_output     # 中间变量

            self._u = self._ctrl_manager.step(
                self._sv, pv_feedback, pv_inner, dist_value, dt
            )

            # 被控对象步进
            plant_out, mid = self._plant.step(self._u, dt)

            # 叠加干扰到最终输出
            plant_with_dist = plant_out + dist_value

            # 反馈环节
            self._pv = self._feedback.step(plant_with_dist, dt)

            # 记录数据
            error = self._sv - self._pv
            self._logger.record(self._sim_time, self._sv, self._pv, self._u,
                                dist_value, error)

            # 更新波形
            self._plot.add_data(self._sim_time, self._sv, self._pv, self._u,
                                dist_value, error)

            # 每200ms刷新一次UI，减少开销
            self._plot.update_plot()

            # 更新实时数值显示
            self._pv_label.setText(f"{self._pv:.2f}")
            self._u_label.setText(f"{self._u:.2f}")
            self._error_label.setText(f"{error:.2f}")

            # 干扰状态
            if self._disturbance.is_active:
                self._dist_status_label.setText(
                    f"{dist_value:.1f} ({self._disturbance.remaining_time:.1f}s)"
                )
            else:
                self._dist_status_label.setText(f"{dist_value:.1f}")

        except Exception as e:
            show_error_dialog(self, "仿真计算错误", str(e))

    def _update_disturb_button(self):
        if self._disturbance.is_active:
            remaining = self._disturbance.remaining_time
            self._control_panel.set_disturb_button_locked(True, remaining)
        else:
            self._control_panel.set_disturb_button_locked(False)

    # =========================================================================
    # 辅助
    # =========================================================================
    def _update_status_bar(self):
        mode_text = "自动" if self._ctrl_manager.mode == ControlMode.AUTO else "手动"
        strategy_text = CONTROL_STRATEGY_LABELS.get(self._current_strategy, "--")
        user_text = CurrentUser.get().display_name or "--"

        self._status_bar.set_mode(mode_text)
        self._status_bar.set_strategy(strategy_text)
        self._status_bar.set_user(user_text)

    def _update_menu_permissions(self):
        is_admin = CurrentUser.is_admin()
        self._manage_user_action.setVisible(is_admin)

    @property
    def should_relogin(self) -> bool:
        return getattr(self, "_should_relogin", False)
