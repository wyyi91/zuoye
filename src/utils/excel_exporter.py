"""Excel导出功能"""

from datetime import datetime
from src.utils.time_format import get_current_time_str


def export_to_excel(data: list[dict], filepath: str,
                    session_id: str = "") -> bool:
    """将仿真数据导出为Excel文件（使用csv格式以去除openpyxl依赖）"""
    import csv
    try:
        with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
            if data:
                writer = csv.writer(f)
                headers = ["时间(s)", "SV", "PV", "控制量u", "干扰", "误差"]
                writer.writerow(headers)
                for row in data:
                    writer.writerow([
                        round(row.get("time", 0), 3),
                        round(row.get("SV", 0), 4),
                        round(row.get("PV", 0), 4),
                        round(row.get("u", 0), 4),
                        round(row.get("disturbance", 0), 4),
                        round(row.get("error", 0), 4),
                    ])
        return True
    except (IOError, PermissionError):
        return False
