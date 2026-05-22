"""实时波形显示组件 —— 基于pyqtgraph"""

import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from collections import deque
import numpy as np

# Qt PenStyle constants
DASH_LINE = Qt.PenStyle.DashLine
DASH_DOT_LINE = Qt.PenStyle.DashDotLine


class PlotWidget(QWidget):
    """实时波形显示组件"""

    def __init__(self, max_points: int = 5000, parent=None):
        super().__init__(parent)
        self._max_points = max_points

        self._time_data = deque(maxlen=max_points)
        self._sv_data = deque(maxlen=max_points)
        self._pv_data = deque(maxlen=max_points)
        self._u_data = deque(maxlen=max_points)
        self._disturbance_data = deque(maxlen=max_points)
        self._error_data = deque(maxlen=max_points)

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._plot_widget = pg.PlotWidget()
        self._plot_widget.setLabel("left", "温度 / 控制量")
        self._plot_widget.setLabel("bottom", "时间", units="s")
        self._plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self._plot_widget.addLegend()

        pen_sv = pg.mkPen(color=(255, 0, 0), width=2)
        pen_pv = pg.mkPen(color=(0, 200, 0), width=2)
        pen_u = pg.mkPen(color=(0, 100, 255), width=2)
        pen_dist = pg.mkPen(color=(160, 0, 200), width=1.5, style=DASH_LINE)
        pen_err = pg.mkPen(color=(0, 180, 180), width=1.5, style=DASH_DOT_LINE)

        self._curve_sv = self._plot_widget.plot([], [], pen=pen_sv, name="SV")
        self._curve_pv = self._plot_widget.plot([], [], pen=pen_pv, name="PV")
        self._curve_u = self._plot_widget.plot([], [], pen=pen_u, name="u")
        self._curve_dist = self._plot_widget.plot([], [], pen=pen_dist, name="干扰")
        self._curve_err = self._plot_widget.plot([], [], pen=pen_err, name="误差")

        layout.addWidget(self._plot_widget)

    def add_data(self, time_val: float, sv: float, pv: float, u: float,
                 disturbance: float, error: float = 0.0):
        self._time_data.append(time_val)
        self._sv_data.append(sv)
        self._pv_data.append(pv)
        self._u_data.append(u)
        self._disturbance_data.append(disturbance)
        self._error_data.append(error)

    def update_plot(self):
        times = np.array(self._time_data, dtype=float)
        if len(times) < 2:
            return

        self._curve_sv.setData(times, np.array(self._sv_data, dtype=float))
        self._curve_pv.setData(times, np.array(self._pv_data, dtype=float))
        self._curve_u.setData(times, np.array(self._u_data, dtype=float))
        self._curve_dist.setData(times, np.array(self._disturbance_data, dtype=float))
        self._curve_err.setData(times, np.array(self._error_data, dtype=float))

    def clear(self):
        self._time_data.clear()
        self._sv_data.clear()
        self._pv_data.clear()
        self._u_data.clear()
        self._disturbance_data.clear()
        self._error_data.clear()
        self._curve_sv.clear()
        self._curve_pv.clear()
        self._curve_u.clear()
        self._curve_dist.clear()
        self._curve_err.clear()

    def set_y_range(self, y_min: float, y_max: float):
        self._plot_widget.setYRange(y_min, y_max)

    def enable_auto_range(self):
        self._plot_widget.enableAutoRange(axis='y')


class HistoryPlotWidget(QWidget):
    """历史曲线查看组件（支持缩放/平移）"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._plot = pg.PlotWidget()
        self._plot.setLabel("left", "温度 / 控制量")
        self._plot.setLabel("bottom", "时间", units="s")
        self._plot.showGrid(x=True, y=True, alpha=0.3)
        self._plot.addLegend()

        pen_sv = pg.mkPen(color=(255, 0, 0), width=2)
        pen_pv = pg.mkPen(color=(0, 200, 0), width=2)
        pen_u = pg.mkPen(color=(0, 100, 255), width=2)
        pen_dist = pg.mkPen(color=(160, 0, 200), width=1.5, style=DASH_LINE)
        pen_err = pg.mkPen(color=(0, 180, 180), width=1.5, style=DASH_DOT_LINE)

        self._curve_sv = self._plot.plot([], [], pen=pen_sv, name="SV")
        self._curve_pv = self._plot.plot([], [], pen=pen_pv, name="PV")
        self._curve_u = self._plot.plot([], [], pen=pen_u, name="u")
        self._curve_dist = self._plot.plot([], [], pen=pen_dist, name="干扰")
        self._curve_err = self._plot.plot([], [], pen=pen_err, name="误差")

        layout.addWidget(self._plot)

    def load_data(self, data: list[dict]):
        if not data:
            return
        times = np.array([d["time"] for d in data], dtype=float)
        sv = np.array([d["SV"] for d in data], dtype=float)
        pv = np.array([d["PV"] for d in data], dtype=float)
        u = np.array([d["u"] for d in data], dtype=float)
        dist = np.array([d.get("disturbance", 0) for d in data], dtype=float)
        err = np.array([d.get("error", 0) for d in data], dtype=float)

        self._curve_sv.setData(times, sv)
        self._curve_pv.setData(times, pv)
        self._curve_u.setData(times, u)
        self._curve_dist.setData(times, dist)
        self._curve_err.setData(times, err)
        self._plot.autoRange()

    def clear(self):
        self._curve_sv.clear()
        self._curve_pv.clear()
        self._curve_u.clear()
        self._curve_dist.clear()
        self._curve_err.clear()
