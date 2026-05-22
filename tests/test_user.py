"""用户管理单元测试"""

import sys
import os
import tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.user.user_data import UserDataManager
from src.user.user_manager import UserManager
from src.user.permission import CurrentUser
from src.config import UserRole, Permissions


def test_default_users():
    """测试默认用户创建和登录"""
    data = UserDataManager(filepath=os.path.join(tempfile.gettempdir(), "test_users.json"))
    data._create_default_users()

    # 验证admin登录
    user = data.verify_login("admin", "admin123")
    assert user is not None
    assert user["role"] == UserRole.ADMIN

    # 验证user登录
    user = data.verify_login("user", "user123")
    assert user is not None
    assert user["role"] == UserRole.USER

    # 验证错误密码
    assert data.verify_login("admin", "wrong") is None

    # 清理
    import os as _os
    try:
        _os.remove(os.path.join(tempfile.gettempdir(), "test_users.json"))
    except OSError:
        pass


def test_user_crud():
    """测试用户增删改"""
    import os as _os
    tmpfile = os.path.join(tempfile.gettempdir(), "test_users_crud.json")
    try:
        _os.remove(tmpfile)
    except OSError:
        pass

    data = UserDataManager(filepath=tmpfile)
    data._create_default_users()

    # 添加用户
    assert data.add_user("test1", "pass123", UserRole.USER, "测试用户1")
    assert data.user_exists("test1")
    assert not data.add_user("test1", "pass", UserRole.USER)  # 重复

    # 删除用户
    assert data.remove_user("test1")
    assert not data.user_exists("test1")
    assert not data.remove_user("admin")  # 不能删除admin

    try:
        _os.remove(tmpfile)
    except OSError:
        pass


def test_change_password():
    import os as _os
    tmpfile = os.path.join(tempfile.gettempdir(), "test_users_pwd.json")
    try:
        _os.remove(tmpfile)
    except OSError:
        pass

    data = UserDataManager(filepath=tmpfile)
    data._create_default_users()

    # 正确修改
    assert data.change_password("user", "user123", "newpass")
    assert data.verify_login("user", "newpass") is not None
    assert data.verify_login("user", "user123") is None

    # 错误原密码
    assert not data.change_password("user", "wrong", "newpass2")

    try:
        _os.remove(tmpfile)
    except OSError:
        pass


def test_permissions():
    """测试权限系统"""
    CurrentUser.clear()
    assert not CurrentUser.is_logged_in()

    CurrentUser.set("admin", UserRole.ADMIN, "管理员")
    assert CurrentUser.is_admin()
    assert CurrentUser.has_permission(Permissions.MANAGE_USERS)
    assert CurrentUser.has_permission(Permissions.RUN_SIMULATION)

    CurrentUser.set("user", UserRole.USER, "普通用户")
    assert not CurrentUser.is_admin()
    assert not CurrentUser.has_permission(Permissions.MANAGE_USERS)
    assert CurrentUser.has_permission(Permissions.RUN_SIMULATION)

    CurrentUser.clear()


if __name__ == "__main__":
    test_default_users()
    test_user_crud()
    test_change_password()
    test_permissions()
    print("用户管理测试全部通过！")
