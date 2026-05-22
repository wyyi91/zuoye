"""用户管理业务逻辑 —— 增删改查"""

from src.config import UserRole
from src.user.user_data import UserDataManager
from src.user.permission import CurrentUser, Permissions


class UserManager:
    """用户管理逻辑层"""

    def __init__(self, data_manager: UserDataManager = None):
        self._data = data_manager or UserDataManager()
        self._data.load()

    def login(self, user_id: str, password: str) -> bool:
        """登录验证，成功则设置当前用户上下文"""
        user = self._data.verify_login(user_id, password)
        if user:
            CurrentUser.set(user["user_id"], user["role"], user["display_name"])
            return True
        return False

    def logout(self):
        CurrentUser.clear()

    def change_own_password(self, old_pwd: str, new_pwd: str) -> bool:
        if not CurrentUser.is_logged_in():
            return False
        return self._data.change_password(CurrentUser.get().user_id, old_pwd, new_pwd)

    def add_user(self, user_id: str, password: str, role: UserRole,
                 display_name: str = "") -> tuple[bool, str]:
        """添加用户，检查权限"""
        if not CurrentUser.has_permission(Permissions.MANAGE_USERS):
            return False, "无权限：只有管理员可以管理用户"
        if not user_id.strip():
            return False, "用户ID不能为空"
        if not password.strip():
            return False, "密码不能为空"
        if self._data.user_exists(user_id):
            return False, f"用户 '{user_id}' 已存在"
        ok = self._data.add_user(user_id.strip(), password, role, display_name.strip())
        return ok, "" if ok else "添加用户失败"

    def remove_user(self, user_id: str) -> tuple[bool, str]:
        if not CurrentUser.has_permission(Permissions.MANAGE_USERS):
            return False, "无权限"
        if user_id == CurrentUser.get().user_id:
            return False, "不能删除当前登录用户"
        ok = self._data.remove_user(user_id)
        return ok, "" if ok else f"用户 '{user_id}' 不存在或无法删除"

    def update_user_role(self, user_id: str, role: UserRole) -> tuple[bool, str]:
        if not CurrentUser.has_permission(Permissions.MODIFY_PERMISSIONS):
            return False, "无权限"
        ok = self._data.update_user_role(user_id, role)
        return ok, "" if ok else f"用户 '{user_id}' 不存在"

    def reset_user_password(self, user_id: str, new_password: str) -> tuple[bool, str]:
        if not CurrentUser.has_permission(Permissions.MANAGE_USERS):
            return False, "无权限"
        ok = self._data.admin_reset_password(user_id, new_password)
        return ok, "" if ok else f"用户 '{user_id}' 不存在"

    def get_all_users(self) -> list[dict]:
        return self._data.get_all_users()

    def reload(self):
        self._data.load()
