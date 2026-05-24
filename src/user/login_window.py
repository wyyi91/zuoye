"""登录界面"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QMessageBox, QFrame,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.user.user_manager import UserManager
from src.config import Paths


class LoginWindow(QDialog):
    """登录对话框"""

    def __init__(self, user_manager: UserManager, parent=None):
        super().__init__(parent)
        self._user_manager = user_manager
        self._logged_in = False
        self._remembered_user = ""
        self._remembered_pwd = ""

        self.setWindowTitle("PID温度控制仿真系统 - 登录")
        self.setFixedSize(400, 300)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(40, 30, 40, 30)

        # 标题
        title = QLabel("PID温度控制仿真系统")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        layout.addSpacing(10)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        layout.addSpacing(10)

        # 用户ID
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("用户ID:"))
        self._user_id_edit = QLineEdit()
        self._user_id_edit.setPlaceholderText("请输入用户ID")
        row1.addWidget(self._user_id_edit)
        layout.addLayout(row1)

        # 密码
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("密  码:"))
        self._password_edit = QLineEdit()
        self._password_edit.setPlaceholderText("请输入密码")
        self._password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self._password_edit.returnPressed.connect(self._on_login)
        row2.addWidget(self._password_edit)
        layout.addLayout(row2)

        # 记住密码
        self._remember_check = QCheckBox("记住密码")
        layout.addWidget(self._remember_check)

        layout.addSpacing(10)

        # 登录按钮
        self._login_btn = QPushButton("登  录")
        self._login_btn.setFixedHeight(36)
        self._login_btn.clicked.connect(self._on_login)
        layout.addWidget(self._login_btn)

        layout.addStretch()

        # 提示信息
        hint = QLabel("默认账号: admin/admin123  或  user/user123")
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        hint.setStyleSheet("color: #555555; font-size: 12px; font-weight: bold;")
        layout.addWidget(hint)

        self._user_id_edit.setFocus()

    def _on_login(self):
        user_id = self._user_id_edit.text().strip()
        password = self._password_edit.text()

        if not user_id:
            QMessageBox.warning(self, "提示", "请输入用户ID")
            return

        if self._user_manager.login(user_id, password):
            self._logged_in = True
            if self._remember_check.isChecked():
                self._remembered_user = user_id
                self._remembered_pwd = password
            else:
                self._remembered_user = ""
                self._remembered_pwd = ""
            self.accept()
        else:
            QMessageBox.warning(self, "登录失败", "用户ID或密码错误，请重试。")
            self._password_edit.clear()
            self._password_edit.setFocus()

    def _apply_style(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #eef2f7;
            }
            QLabel {
                color: #1a1a2e;
                font-size: 13px;
            }
            QLineEdit {
                padding: 7px;
                border: 2px solid #888;
                border-radius: 4px;
                background: white;
                color: #1a1a1a;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #e74c3c;
                border-width: 2px;
            }
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
            QCheckBox {
                color: #333;
                font-size: 12px;
            }
        """)

    @property
    def is_logged_in(self) -> bool:
        return self._logged_in

    @property
    def remembered_user(self) -> str:
        return self._remembered_user

    @property
    def remembered_password(self) -> str:
        return self._remembered_pwd
