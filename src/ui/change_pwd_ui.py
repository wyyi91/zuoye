"""修改密码对话框"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFormLayout,
)
from PyQt6.QtCore import Qt

from src.user.user_manager import UserManager


class ChangePasswordDialog(QDialog):
    """修改密码对话框"""

    def __init__(self, user_manager: UserManager, parent=None):
        super().__init__(parent)
        self._user_manager = user_manager
        self.setWindowTitle("修改密码")
        self.setFixedSize(350, 220)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(30, 20, 30, 20)

        form = QFormLayout()
        form.setSpacing(8)

        self._old_pwd_edit = QLineEdit()
        self._old_pwd_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self._old_pwd_edit.setPlaceholderText("请输入原密码")
        form.addRow("原密码:", self._old_pwd_edit)

        self._new_pwd_edit = QLineEdit()
        self._new_pwd_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self._new_pwd_edit.setPlaceholderText("请输入新密码")
        form.addRow("新密码:", self._new_pwd_edit)

        self._confirm_pwd_edit = QLineEdit()
        self._confirm_pwd_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self._confirm_pwd_edit.setPlaceholderText("请再次输入新密码")
        form.addRow("确认密码:", self._confirm_pwd_edit)

        layout.addLayout(form)

        layout.addSpacing(8)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        self._ok_btn = QPushButton("确认修改")
        self._ok_btn.clicked.connect(self._on_confirm)
        self._ok_btn.setStyleSheet("background-color: #4a90d9; color: white;")
        btn_layout.addWidget(self._ok_btn)

        layout.addLayout(btn_layout)

    def _on_confirm(self):
        old_pwd = self._old_pwd_edit.text()
        new_pwd = self._new_pwd_edit.text()
        confirm_pwd = self._confirm_pwd_edit.text()

        if not old_pwd:
            QMessageBox.warning(self, "提示", "请输入原密码")
            return
        if not new_pwd:
            QMessageBox.warning(self, "提示", "请输入新密码")
            return
        if len(new_pwd) < 3:
            QMessageBox.warning(self, "提示", "新密码长度不能少于3位")
            return
        if new_pwd != confirm_pwd:
            QMessageBox.warning(self, "提示", "两次输入的新密码不一致")
            return

        if self._user_manager.change_own_password(old_pwd, new_pwd):
            QMessageBox.information(self, "成功", "密码修改成功！")
            self.accept()
        else:
            QMessageBox.warning(self, "失败", "原密码错误，修改失败。")
