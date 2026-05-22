"""历史数据查询窗口"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QComboBox, QTableWidget, QTableWidgetItem, QFileDialog,
    QMessageBox, QSplitter, QGroupBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction

from src.utils.data_logger import HistoryDataManager
from src.utils.excel_exporter import export_to_excel
from src.ui.plot_widget import HistoryPlotWidget
from src.exception import show_error_dialog


class HistoryWindow(QMainWindow):
    """历史数据查询窗口"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("历史曲线查询")
        self.setMinimumSize(900, 600)
        self._data_manager = HistoryDataManager()
        self._current_data: list[dict] = []

        self._setup_ui()
        self._refresh_session_list()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # 工具栏区域
        toolbar_layout = QHBoxLayout()

        toolbar_layout.addWidget(QLabel("历史会话:"))
        self._session_combo = QComboBox()
        self._session_combo.setMinimumWidth(250)
        self._session_combo.currentIndexChanged.connect(self._on_session_selected)
        toolbar_layout.addWidget(self._session_combo)

        refresh_btn = QPushButton("刷新列表")
        refresh_btn.clicked.connect(self._refresh_session_list)
        toolbar_layout.addWidget(refresh_btn)

        toolbar_layout.addSpacing(20)

        export_btn = QPushButton("导出Excel")
        export_btn.clicked.connect(self._export_excel)
        toolbar_layout.addWidget(export_btn)

        delete_btn = QPushButton("删除选中会话")
        delete_btn.clicked.connect(self._delete_session)
        toolbar_layout.addWidget(delete_btn)

        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)

        # 分割区域：图形 + 数据表
        splitter = QSplitter(Qt.Orientation.Vertical)

        # 绘图区域
        plot_group = QGroupBox("波形曲线")
        plot_layout = QVBoxLayout(plot_group)
        self._plot = HistoryPlotWidget()
        plot_layout.addWidget(self._plot)
        splitter.addWidget(plot_group)

        # 数据表格
        table_group = QGroupBox("数据明细")
        table_layout = QVBoxLayout(table_group)
        self._table = QTableWidget()
        self._table.setColumnCount(6)
        self._table.setHorizontalHeaderLabels(
            ["时间(s)", "SV", "PV", "控制量u", "干扰", "误差"]
        )
        table_layout.addWidget(self._table)
        splitter.addWidget(table_group)

        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter)

    def _refresh_session_list(self):
        self._session_combo.blockSignals(True)
        self._session_combo.clear()
        sessions = self._data_manager.get_session_list()
        for s in sessions:
            label = f"{s['session_id']} | {s['recorded_at']} | {s['data_count']}条"
            self._session_combo.addItem(label, s["session_id"])
        self._session_combo.blockSignals(False)

        if self._session_combo.count() > 0:
            self._session_combo.setCurrentIndex(0)

    def _on_session_selected(self, index: int):
        if index < 0:
            return
        session_id = self._session_combo.currentData()
        data = self._data_manager.load_session(session_id)
        self._current_data = data or []
        self._plot.load_data(self._current_data)
        self._populate_table(self._current_data)

    def _populate_table(self, data: list[dict]):
        self._table.setRowCount(len(data))
        for i, row in enumerate(data):
            items = [
                QTableWidgetItem(f"{row.get('time', 0):.3f}"),
                QTableWidgetItem(f"{row.get('SV', 0):.4f}"),
                QTableWidgetItem(f"{row.get('PV', 0):.4f}"),
                QTableWidgetItem(f"{row.get('u', 0):.4f}"),
                QTableWidgetItem(f"{row.get('disturbance', 0):.4f}"),
                QTableWidgetItem(f"{row.get('error', 0):.4f}"),
            ]
            for j, item in enumerate(items):
                self._table.setItem(i, j, item)

    def _export_excel(self):
        if not self._current_data:
            QMessageBox.information(self, "提示", "没有数据可导出")
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "导出数据", "simulation_data.csv",
            "CSV文件 (*.csv);;所有文件 (*)"
        )
        if filepath:
            if export_to_excel(self._current_data, filepath):
                QMessageBox.information(self, "成功", f"数据已导出到:\n{filepath}")
            else:
                show_error_dialog(self, "导出失败", "无法写入文件，请检查磁盘空间和权限。")

    def _delete_session(self):
        index = self._session_combo.currentIndex()
        if index < 0:
            return
        session_id = self._session_combo.currentData()
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除会话 '{session_id}' 的所有数据吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._data_manager.delete_session(session_id)
            self._refresh_session_list()
