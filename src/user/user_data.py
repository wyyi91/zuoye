"""用户数据持久化 —— JSON文件读写与加密"""

import json
import os
import hashlib
import base64
from typing import Optional
from src.config import Paths, UserRole
from src.exception import DataAccessException


def _hash_password(password: str) -> str:
    """SHA256哈希密码"""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _check_password(password: str, hashed: str) -> bool:
    return _hash_password(password) == hashed


class UserDataManager:
    """用户数据管理器"""

    def __init__(self, filepath: str = None):
        self._filepath = filepath or Paths.USERS_FILE
        self._users: dict[str, dict] = {}

    def load(self):
        """从JSON文件加载用户数据"""
        try:
            if os.path.exists(self._filepath):
                with open(self._filepath, "r", encoding="utf-8") as f:
                    self._users = json.load(f)
            else:
                self._create_default_users()
                self.save()
        except (json.JSONDecodeError, IOError) as e:
            raise DataAccessException(f"用户数据加载失败: {e}")

    def save(self):
        """保存用户数据到JSON文件"""
        try:
            os.makedirs(os.path.dirname(self._filepath), exist_ok=True)
            with open(self._filepath, "w", encoding="utf-8") as f:
                json.dump(self._users, f, ensure_ascii=False, indent=2)
        except IOError as e:
            raise DataAccessException(f"用户数据保存失败: {e}")

    def _create_default_users(self):
        self._users = {
            "admin": {
                "user_id": "admin",
                "password": _hash_password("admin123"),
                "role": UserRole.ADMIN.value,
                "display_name": "管理员",
            },
            "user": {
                "user_id": "user",
                "password": _hash_password("user123"),
                "role": UserRole.USER.value,
                "display_name": "普通用户",
            },
        }

    def verify_login(self, user_id: str, password: str) -> Optional[dict]:
        """验证登录，成功返回用户信息，失败返回None"""
        user = self._users.get(user_id)
        if user and _check_password(password, user["password"]):
            return {
                "user_id": user["user_id"],
                "role": UserRole(user["role"]),
                "display_name": user.get("display_name", user["user_id"]),
            }
        return None

    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """修改密码，返回是否成功"""
        user = self._users.get(user_id)
        if not user:
            return False
        if not _check_password(old_password, user["password"]):
            return False
        user["password"] = _hash_password(new_password)
        self.save()
        return True

    def admin_reset_password(self, user_id: str, new_password: str) -> bool:
        """管理员重置用户密码"""
        user = self._users.get(user_id)
        if not user:
            return False
        user["password"] = _hash_password(new_password)
        self.save()
        return True

    def add_user(self, user_id: str, password: str, role: UserRole,
                 display_name: str = "") -> bool:
        """添加新用户"""
        if user_id in self._users:
            return False
        self._users[user_id] = {
            "user_id": user_id,
            "password": _hash_password(password),
            "role": role.value,
            "display_name": display_name or user_id,
        }
        self.save()
        return True

    def remove_user(self, user_id: str) -> bool:
        """删除用户（不能删除admin）"""
        if user_id == "admin" or user_id not in self._users:
            return False
        del self._users[user_id]
        self.save()
        return True

    def update_user_role(self, user_id: str, role: UserRole) -> bool:
        """更新用户角色"""
        if user_id not in self._users:
            return False
        self._users[user_id]["role"] = role.value
        self.save()
        return True

    def update_user_display_name(self, user_id: str, display_name: str) -> bool:
        """更新用户显示名"""
        if user_id not in self._users:
            return False
        self._users[user_id]["display_name"] = display_name
        self.save()
        return True

    def get_all_users(self) -> list[dict]:
        """获取所有用户列表（不含密码）"""
        return [
            {
                "user_id": u["user_id"],
                "role": u["role"],
                "display_name": u.get("display_name", ""),
            }
            for u in self._users.values()
        ]

    def user_exists(self, user_id: str) -> bool:
        return user_id in self._users
