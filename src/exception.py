"""全局异常处理 —— 自定义异常类、全局钩子、对话框辅助函数"""

import sys
import traceback
import logging
from datetime import datetime
from typing import Callable

from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QTimer

from src.config import Paths


# =============================================================================
# 自定义异常类
# =============================================================================
class CalculationException(Exception):
    """仿真计算异常（除零、溢出等）"""
    pass


class ParameterException(Exception):
    """参数校验异常（非法值、越界）"""
    pass


class DataAccessException(Exception):
    """数据读写异常"""
    pass


# =============================================================================
# 日志配置
# =============================================================================
def _setup_logging():
    Paths.ensure_dirs()
    logger = logging.getLogger("SimControl")
    logger.setLevel(logging.DEBUG)

    fh = logging.FileHandler(Paths.ERROR_LOG, encoding="utf-8")
    fh.setLevel(logging.ERROR)
    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    fh.setFormatter(fmt)
    logger.addHandler(fh)
    return logger


_logger = _setup_logging()


# =============================================================================
# 对话框工具函数
# =============================================================================
def show_error_dialog(parent, title: str, message: str):
    """显示错误对话框（阻塞式）"""
    QMessageBox.critical(parent, title, message)


def show_info_dialog(parent, title: str, message: str):
    """显示信息对话框"""
    QMessageBox.information(parent, title, message)


def show_warning_dialog(parent, title: str, message: str):
    """显示警告对话框"""
    QMessageBox.warning(parent, title, message)


def show_confirm_dialog(parent, title: str, message: str) -> bool:
    """显示确认对话框，返回 True/False"""
    return QMessageBox.question(
        parent, title, message,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    ) == QMessageBox.StandardButton.Yes


# =============================================================================
# 全局异常钩子
# =============================================================================
_original_excepthook = sys.excepthook


def _global_exception_handler(exc_type, exc_value, exc_tb):
    """全局未捕获异常处理 —— 写日志 + 弹窗，不退出"""
    try:
        tb_str = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
        _logger.error(f"未捕获异常:\n{tb_str}")

        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app and app.activeWindow():
            show_error_dialog(
                app.activeWindow(),
                "程序异常",
                f"发生了未预期的错误，程序将继续运行。\n\n"
                f"错误类型：{exc_type.__name__}\n"
                f"错误信息：{exc_value}\n\n"
                f"详细堆栈已写入日志文件。"
            )
    except Exception:
        # 异常处理器自身出错时的最后兜底
        _original_excepthook(exc_type, exc_value, exc_tb)


def install_exception_handler():
    """安装全局异常处理器"""
    sys.excepthook = _global_exception_handler
    # 捕获 Qt 事件循环中的异常
    from PyQt6.QtCore import qInstallMessageHandler

    def _qt_message_handler(mode, context, message):
        if mode in (3, 4):  # QtCriticalMsg, QtFatalMsg
            _logger.error(f"Qt [{mode}] {message}")
        else:
            _logger.debug(f"Qt [{mode}] {message}")

    qInstallMessageHandler(_qt_message_handler)


# =============================================================================
# safe_call —— 安全的函数调用装饰器
# =============================================================================
def safe_call(parent_getter: Callable = None):
    """装饰器：捕获被装饰函数中的所有异常，弹窗提示并记录日志"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                tb = traceback.format_exc()
                _logger.error(f"{func.__name__} 异常:\n{tb}")
                parent = parent_getter() if parent_getter else None
                show_error_dialog(
                    parent, "操作失败",
                    f"{func.__name__}: {e}\n\n详细信息已记录到日志。"
                )
                return None
        return wrapper
    return decorator
