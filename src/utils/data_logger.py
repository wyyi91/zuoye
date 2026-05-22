"""数据记录器 —— 仿真数据记录与历史数据查询"""

import json
import os
import time
from collections import deque
from datetime import datetime, timedelta
from src.config import Paths


class DataLogger:
    """仿真数据记录器"""

    def __init__(self, max_buffer: int = 10000):
        self._buffer: deque[dict] = deque(maxlen=max_buffer)
        self._session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._recording = False

    def start(self):
        self._recording = True
        self._session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    def stop(self):
        self._recording = False

    def reset(self):
        self._buffer.clear()
        self._session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    def record(self, timestamp: float, sv: float, pv: float, u: float,
               disturbance: float, error: float = 0.0):
        """记录一行仿真数据"""
        if self._recording:
            self._buffer.append({
                "time": timestamp,
                "SV": sv,
                "PV": pv,
                "u": u,
                "disturbance": disturbance,
                "error": error,
            })

    def save_to_file(self) -> str:
        """将当前缓冲区数据保存到JSON文件，返回文件路径"""
        Paths.ensure_dirs()
        filename = f"sim_{self._session_id}.json"
        filepath = os.path.join(Paths.HISTORY_DIR, filename)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump({
                    "session_id": self._session_id,
                    "recorded_at": datetime.now().isoformat(),
                    "data": list(self._buffer),
                }, f, ensure_ascii=False, indent=2)
        except IOError:
            pass
        return filepath

    @property
    def data(self) -> list[dict]:
        return list(self._buffer)

    @property
    def count(self) -> int:
        return len(self._buffer)


class HistoryDataManager:
    """历史数据查询管理器"""

    def __init__(self):
        Paths.ensure_dirs()
        self._data_dir = Paths.HISTORY_DIR

    def get_session_list(self) -> list[dict]:
        """获取所有历史会话列表"""
        sessions = []
        if not os.path.exists(self._data_dir):
            return sessions

        for filename in sorted(os.listdir(self._data_dir), reverse=True):
            if filename.startswith("sim_") and filename.endswith(".json"):
                filepath = os.path.join(self._data_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    sessions.append({
                        "session_id": meta.get("session_id", filename),
                        "recorded_at": meta.get("recorded_at", ""),
                        "data_count": len(meta.get("data", [])),
                        "filepath": filepath,
                    })
                except (json.JSONDecodeError, IOError):
                    continue
        return sessions

    def load_session(self, session_id: str) -> list[dict] | None:
        """加载指定会话的数据"""
        filepath = os.path.join(self._data_dir, f"sim_{session_id}.json")
        if not os.path.exists(filepath):
            return None
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                meta = json.load(f)
            return meta.get("data", [])
        except (json.JSONDecodeError, IOError):
            return None

    def query_by_timerange(self, start_time: float, end_time: float,
                           session_id: str = None) -> list[dict]:
        """按时间范围查询数据"""
        data = self.load_session(session_id) if session_id else []
        if not data:
            sessions = self.get_session_list()
            for s in sessions:
                data = self.load_session(s["session_id"]) or []
                if data:
                    break

        return [d for d in data if start_time <= d["time"] <= end_time]

    def delete_session(self, session_id: str) -> bool:
        """删除指定会话数据"""
        filepath = os.path.join(self._data_dir, f"sim_{session_id}.json")
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                return True
            except OSError:
                return False
        return False
