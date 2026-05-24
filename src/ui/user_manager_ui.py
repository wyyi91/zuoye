"""用户管理界面（管理员专用）"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QDialog,
    QFormLayout, QLineEdit, QComboBox, QMessageBox, QGroupBox,
)
from PyQt6.QtCore import Qt

from src.config import UserRole
from src.user.user_manager import UserManager


class AddUserDialog(QDialog):
    """添加用户对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加用户")
        self.setFixedSize(350, 250)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self._user_id = QLineEdit()
        self._user_id.setPlaceholderText("请输入用户ID")
        form.addRow("用户ID:", self._user_id)

        self._password = QLineEdit()
        self._password.setEchoMode(QLineEdit.EchoMode.Password)
        self._password.setPlaceholderText("请输入密码")
        form.addRow("密码:", self._password)

        self._display_name = QLineEdit()
        self._display_name.setPlaceholderText("请输入显示名称")
        form.addRow("显示名称:", self._display_name)

        self._role_combo = QComboBox()
        self._role_combo.addItem("普通用户 (User)", UserRole.USER)
        self._role_combo.addItem("管理员 (Admin)", UserRole.ADMIN)
        form.addRow("角色:", self._role_combo)

        layout.addLayout(form)
        layout.addSpacing(12)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        ok_btn = QPushButton("添加")
        ok_btn.setStyleSheet(
            "background-color: #e74c3c; color: white; font-weight: bold; font-size: 13px;"
        )
        ok_btn.clicked.connect(self._on_ok)
        btn_layout.addWidget(ok_btn)
        layout.addLayout(btn_layout)

    def _on_ok(self):
        user_id = self._user_id.text().strip()
        password = self._password.text()
        display_name = self._display_name.text().strip()

        if not user_id:
            QMessageBox.warning(self, "提示", "请输入用户ID")
            return
        if not password:
            QMessageBox.warning(self, "提示", "请输入密码")
            return
        if len(password) < 3:
            QMessageBox.warning(self, "提示", "密码长度不能少于3位")
            return

        self._result = (user_id, password, self._role_combo.currentData(), display_name)
        self.accept()

    def get_result(self):
        return getattr(self, "_result", None)


class UserManagerWindow(QMainWindow):
    """用户管理窗口"""

    def __init__(self, user_manager: UserManager, parent=None):
        super().__init__(parent)
        self._user_manager = user_manager
        self.setWindowTitle("用户管理")
        self.setMinimumSize(600, 450)
        self._setup_ui()
        self._refresh_table()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # 按钮区域
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("添加用户")
        add_btn.clicked.connect(self._add_user)
        btn_layout.addWidget(add_btn)

        reset_pwd_btn = QPushButton("重置密码")
        reset_pwd_btn.clicked.connect(self._reset_password)
        btn_layout.addWidget(reset_pwd_btn)

        delete_btn = QPushButton("删除用户")
        delete_btn.setStyleSheet("color: #e74c3c; font-weight: bold; font-size: 14px;")
        delete_btn.clicked.connect(self._delete_user)
        btn_layout.addWidget(delete_btn)

        btn_layout.addStretch()

        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self._refresh_table)
        btn_layout.addWidget(refresh_btn)

        layout.addLayout(btn_layout)

        # 用户表格
        self._table = QTableWidget()
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(["用户ID", "显示名称", "角色", "操作"])
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self._table)

    def _refresh_table(self):
        users = self._user_manager.get_all_users()
        self._table.setRowCount(len(users))
        for i, u in enumerate(users):
            self._table.setItem(i, 0, QTableWidgetItem(u["user_id"]))
            self._table.setItem(i, 1, QTableWidgetItem(u.get("display_name", "")))
            role_text = "管理员" if u["role"] == UserRole.ADMIN.value else "普通用户"
            self._table.setItem(i, 2, QTableWidgetItem(role_text))

            # 角色切换按钮
            if u["user_id"] != "admin":
                btn_text = "降为普通用户" if u["role"] == UserRole.ADMIN.value else "提升为管理员"
                toggle_btn = QPushButton(btn_text)
                toggle_btn.clicked.connect(lambda checked, uid=u["user_id"],
                                           r=u["role"]: self._toggle_role(uid, r))
                self._table.setCellWidget(i, 3, toggle_btn)

    def _add_user(self):
        dlg = AddUserDialog(self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            result = dlg.get_result()
            if result:
                user_id, password, role, display_name = result
                ok, msg = self._user_manager.add_user(user_id, password, role, display_name)
                if ok:
                    QMessageBox.information(self, "成功", f"用户 '{user_id}' 已添加")
                    self._refresh_table()
                else:
                    QMessageBox.warning(self, "失败", msg)

    def _reset_password(self):
        row = self._table.currentRow()
        if row < 0:
            QMessageBox.information(self, "提示", "请先选择要重置密码的用户")
            return
        user_id = self._table.item(row, 0).text()
        if user_id == "admin":
            QMessageBox.warning(self, "提示", "不能重置admin的密码")
            return

        # 简单实现：重置为默认密码
        reply = QMessageBox.question(
            self, "确认", f"确定要将用户 '{user_id}' 的密码重置为 '123456' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            ok, msg = self._user_manager.reset_user_password(user_id, "123456")
            if ok:
                QMessageBox.information(self, "成功", f"用户 '{user_id}' 的密码已重置为 '123456'")
            else:
                QMessageBox.warning(self, "失败", msg)

    def _delete_user(self):
        row = self._table.currentRow()
        if row < 0:
            QMessageBox.information(self, "提示", "请先选择要删除的用户")
            return
        user_id = self._table.item(row, 0).text()
        if user_id == "admin":
            QMessageBox.warning(self, "提示", "不能删除admin用户！")
            return

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要永久删除用户 '{user_id}' 吗？此操作不可恢复！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            ok, msg = self._user_manager.remove_user(user_id)
            if ok:
                QMessageBox.information(self, "成功", f"用户 '{user_id}' 已删除")
                self._refresh_table()
            else:
                QMessageBox.warning(self, "失败", msg)

    def _toggle_role(self, user_id: str, current_role: str):
        new_role = UserRole.USER if current_role == UserRole.ADMIN.value else UserRole.ADMIN
        ok, msg = self._user_manager.update_user_role(user_id, new_role)
        if ok:
            self._refresh_table()
        else:
            QMessageBox.warning(self, "失败", msg)
