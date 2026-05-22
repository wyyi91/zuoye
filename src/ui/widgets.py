"""自定义控件 —— PID参数面板、状态栏等"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QGridLayout, QStatusBar as QtStatusBar,
    QComboBox, QDoubleSpinBox, QCheckBox,
)
from PyQt6.QtCore import pyqtSignal, Qt


class PIDParamGroup(QGroupBox):
    """PID参数设置面板"""

    params_changed = pyqtSignal(float, float, float)  # kp, ti, td

    def __init__(self, title: str = "PID参数",
                 kp: float = 2.0, ti: float = 2.0, td: float = 0.5,
                 show_td: bool = True, parent=None):
        super().__init__(title, parent)
        self._setup_ui(kp, ti, td, show_td)
        self._connect_signals()

    def _setup_ui(self, kp: float, ti: float, td: float, show_td: bool):
        layout = QGridLayout(self)
        layout.setSpacing(6)

        layout.addWidget(QLabel("Kp:"), 0, 0)
        self._kp_spin = QDoubleSpinBox()
        self._kp_spin.setRange(0, 9999)
        self._kp_spin.setValue(kp)
        self._kp_spin.setDecimals(2)
        self._kp_spin.setSingleStep(0.1)
        layout.addWidget(self._kp_spin, 0, 1)

        layout.addWidget(QLabel("Ti:"), 1, 0)
        self._ti_spin = QDoubleSpinBox()
        self._ti_spin.setRange(0.001, 9999)
        self._ti_spin.setValue(ti)
        self._ti_spin.setDecimals(2)
        self._ti_spin.setSingleStep(0.1)
        layout.addWidget(self._ti_spin, 1, 1)

        layout.addWidget(QLabel("Td:"), 2, 0)
        self._td_spin = QDoubleSpinBox()
        self._td_spin.setRange(0, 9999)
        self._td_spin.setValue(td)
        self._td_spin.setDecimals(2)
        self._td_spin.setSingleStep(0.1)
        self._td_spin.setVisible(show_td)
        layout.addWidget(self._td_spin, 2, 1)

    def _connect_signals(self):
        self._kp_spin.valueChanged.connect(self._emit_changed)
        self._ti_spin.valueChanged.connect(self._emit_changed)
        self._td_spin.valueChanged.connect(self._emit_changed)

    def _emit_changed(self):
        self.params_changed.emit(self._kp_spin.value(),
                                 self._ti_spin.value(),
                                 self._td_spin.value())

    @property
    def kp(self) -> float:
        return self._kp_spin.value()

    @property
    def ti(self) -> float:
        return self._ti_spin.value()

    @property
    def td(self) -> float:
        return self._td_spin.value()

    def set_params(self, kp: float, ti: float, td: float):
        self._kp_spin.blockSignals(True)
        self._ti_spin.blockSignals(True)
        self._td_spin.blockSignals(True)
        self._kp_spin.setValue(kp)
        self._ti_spin.setValue(ti)
        self._td_spin.setValue(td)
        self._kp_spin.blockSignals(False)
        self._ti_spin.blockSignals(False)
        self._td_spin.blockSignals(False)


class StatusBar(QtStatusBar):
    """自定义状态栏"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._mode_label = QLabel("模式: --")
        self._strategy_label = QLabel("策略: --")
        self._user_label = QLabel("用户: --")
        self.addWidget(self._mode_label)
        self.addWidget(self._strategy_label)
        self.addPermanentWidget(self._user_label)

    def set_mode(self, text: str):
        self._mode_label.setText(f"模式: {text}")

    def set_strategy(self, text: str):
        self._strategy_label.setText(f"策略: {text}")

    def set_user(self, text: str):
        self._user_label.setText(f"用户: {text}")

    def show_message(self, msg: str, timeout: int = 3000):
        self.showMessage(msg, timeout)


class ControlPanel(QGroupBox):
    """仿真控制面板"""

    start_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    pause_clicked = pyqtSignal(bool)  # True = 暂停
    disturb_clicked = pyqtSignal(float, float)  # amplitude, duration

    def __init__(self, parent=None):
        super().__init__("仿真控制", parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # 控制按钮行
        btn_layout = QHBoxLayout()
        self._start_btn = QPushButton("开始仿真")
        self._start_btn.setStyleSheet("background-color: #27ae60; color: white;")
        self._pause_btn = QPushButton("暂停")
        self._pause_btn.setCheckable(True)
        self._stop_btn = QPushButton("停止")
        self._stop_btn.setStyleSheet("background-color: #e74c3c; color: white;")
        btn_layout.addWidget(self._start_btn)
        btn_layout.addWidget(self._pause_btn)
        btn_layout.addWidget(self._stop_btn)
        layout.addLayout(btn_layout)

        self._start_btn.clicked.connect(self._on_start)
        self._pause_btn.toggled.connect(self._on_pause)
        self._stop_btn.clicked.connect(self._on_stop)

        # 干扰控制行
        disturb_layout = QHBoxLayout()
        disturb_layout.addWidget(QLabel("振幅:"))
        self._dist_amp = QDoubleSpinBox()
        self._dist_amp.setRange(0, 100)
        self._dist_amp.setValue(0)
        self._dist_amp.setDecimals(1)
        disturb_layout.addWidget(self._dist_amp)

        disturb_layout.addWidget(QLabel("时长(s):"))
        self._dist_dur = QDoubleSpinBox()
        self._dist_dur.setRange(0.1, 600)
        self._dist_dur.setValue(5.0)
        self._dist_dur.setDecimals(1)
        disturb_layout.addWidget(self._dist_dur)

        self._disturb_btn = QPushButton("施加方波干扰")
        self._disturb_btn.clicked.connect(self._on_disturb)
        disturb_layout.addWidget(self._disturb_btn)
        layout.addLayout(disturb_layout)

    def _on_start(self):
        self.start_clicked.emit()

    def _on_pause(self, checked: bool):
        self.pause_clicked.emit(checked)

    def _on_stop(self):
        self.stop_clicked.emit()

    def _on_disturb(self):
        self.disturb_clicked.emit(self._dist_amp.value(), self._dist_dur.value())

    def set_disturb_button_locked(self, locked: bool, remaining: float = 0.0):
        self._disturb_btn.setEnabled(not locked)
        if locked:
            self._disturb_btn.setText(f"干扰中... {remaining:.1f}s")
        else:
            self._disturb_btn.setText("施加方波干扰")

    def set_running_state(self, running: bool, paused: bool = False):
        self._start_btn.setEnabled(not running)
        self._stop_btn.setEnabled(running)
        self._pause_btn.setEnabled(running)
        if running:
            self._pause_btn.setChecked(paused)
