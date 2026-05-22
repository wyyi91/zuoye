"""程序入口 —— 初始化→登录→主界面"""

import sys
import os

# 确保 src 父目录在 path 中，兼容开发和打包环境
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from src.config import Paths
from src.exception import install_exception_handler
from src.user.user_data import UserDataManager
from src.user.user_manager import UserManager
from src.user.login_window import LoginWindow
from src.ui.main_window import MainWindow


def main():
    # 1. 安装全局异常处理器
    install_exception_handler()

    # 2. 创建数据目录
    Paths.ensure_dirs()

    # 3. 初始化用户管理
    user_data = UserDataManager()
    try:
        user_data.load()
    except Exception:
        user_data._create_default_users()
        user_data.save()

    user_manager = UserManager(user_data)

    # 4. 创建 QApplication
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationName("PID温度控制仿真系统")
    app.setOrganizationName("SimControl")

    # 加载样式表
    style_path = Paths.STYLE_QSS
    if os.path.exists(style_path):
        with open(style_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())

    # 5. 登录循环
    while True:
        login = LoginWindow(user_manager)
        if login.exec() != LoginWindow.DialogCode.Accepted:
            break  # 用户关闭登录窗口

        if login.is_logged_in:
            # 6. 启动主界面
            main_window = MainWindow(user_manager)
            main_window.show()
            app.exec()

            # 检查是否需要重新登录
            if getattr(main_window, "should_relogin", False):
                continue
            else:
                break
        else:
            break

    sys.exit(0)


if __name__ == "__main__":
    main()
