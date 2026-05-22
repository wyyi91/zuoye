"""时间格式化工具"""

from datetime import datetime


def get_current_time_str(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """获取当前时间字符串"""
    return datetime.now().strftime(fmt)


def format_seconds(seconds: float) -> str:
    """将秒数格式化为可读字符串"""
    if seconds < 60:
        return f"{seconds:.1f}秒"
    elif seconds < 3600:
        m = int(seconds // 60)
        s = seconds % 60
        return f"{m}分{s:.0f}秒"
    else:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        return f"{h}小时{m}分"


def format_timestamp(ts: float) -> str:
    """将时间戳格式化为时间字符串"""
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
