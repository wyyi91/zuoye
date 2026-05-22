"""异常处理工具类 —— 错误日志记录与用户提示"""

import traceback
import logging
from typing import Callable


class ExceptionUtil:
    """异常处理辅助工具"""

    _logger = logging.getLogger("SimControl.ExceptionUtil")

    @classmethod
    def log_exception(cls, exc: Exception, context: str = ""):
        """记录异常到日志"""
        tb = traceback.format_exc()
        ctx = f"[{context}] " if context else ""
        cls._logger.error(f"{ctx}{type(exc).__name__}: {exc}\n{tb}")

    @classmethod
    def safe_execute(cls, func: Callable, *args,
                     on_error: Callable = None,
                     default_return=None,
                     **kwargs):
        """安全执行函数，捕获所有异常"""
        try:
            return func(*args, **kwargs)
        except Exception as e:
            cls.log_exception(e, func.__name__)
            if on_error:
                on_error(e)
            return default_return
