"""权限系统 —— 当前用户上下文、权限常量与校验"""

from dataclasses import dataclass
from src.config import UserRole, Permissions


@dataclass
class CurrentUser:
    """当前登录用户上下文（全局单例）"""
    user_id: str = ""
    role: UserRole = UserRole.USER
    display_name: str = ""

    _instance: "CurrentUser" = None

    @classmethod
    def get(cls) -> "CurrentUser":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def set(cls, user_id: str, role: UserRole, display_name: str):
        inst = cls.get()
        inst.user_id = user_id
        inst.role = role
        inst.display_name = display_name

    @classmethod
    def clear(cls):
        inst = cls.get()
        inst.user_id = ""
        inst.role = UserRole.USER
        inst.display_name = ""

    @classmethod
    def is_logged_in(cls) -> bool:
        return cls.get().user_id != ""

    @classmethod
    def is_admin(cls) -> bool:
        return cls.get().role == UserRole.ADMIN

    @classmethod
    def has_permission(cls, permission: str) -> bool:
        inst = cls.get()
        perms = Permissions.ROLE_PERMISSIONS.get(inst.role, [])
        return permission in perms
