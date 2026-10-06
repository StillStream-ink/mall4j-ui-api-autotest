# -*- coding: utf-8 -*-
"""RBAC API wrapper: 用户 / 角色 / 菜单"""
import uuid

from api.client import APIClient
from common.crypto import encrypt_password
from common.logger import get_logger

logger = get_logger(__name__)


class SysUserCrudApi:
    """系统-管理员 CRUD"""

    def __init__(self, client: APIClient):
        self.client = client

    def page(self, current: int = 1, size: int = 100, username: str = None):
        params = {"current": current, "size": size}
        if username:
            params["username"] = username
        return self.client.get("/sys/user/page", params=params)

    def info(self, user_id: int):
        return self.client.get(f"/sys/user/info/{user_id}")

    def create(self, username: str, password: str, email: str = None,
               mobile: str = None, role_id_list: list = None):
        # email 和 mobile 是 @NotBlank 必填
        email = email or f"{username}@autotest.com"
        # 手机号规则：0?1[0-9]{10}
        mobile = mobile or "138" + uuid.uuid4().hex[:8].translate(str.maketrans("abcdef", "012345"))[:8]
        return self.client.post("/sys/user", json={
            "username": username,
            "password": encrypt_password(password),
            "email": email,
            "mobile": mobile,
            "roleIdList": role_id_list or [],
            "status": 1,
        })

    def update(self, user_id: int, username: str, email: str = None,
               mobile: str = None, role_id_list: list = None, status: int = 1):
        email = email or f"{username}@autotest.com"
        mobile = mobile or "138" + uuid.uuid4().hex[:8].translate(str.maketrans("abcdef", "012345"))[:8]
        return self.client.put("/sys/user", json={
            "userId": user_id,
            "username": username,
            "email": email,
            "mobile": mobile,
            "roleIdList": role_id_list or [],
            "status": status,
        })

    def delete(self, user_ids: list):
        return self.client.delete_json("/sys/user", user_ids)

    def find_by_username(self, username: str):
        body = self.page(username=username).json()
        records = body.get("data", {}).get("records", [])
        for r in records:
            if r.get("username") == username:
                return r
        return None


class SysMenuApi:
    """系统-菜单"""

    def __init__(self, client: APIClient):
        self.client = client

    def list_all(self):
        return self.client.get("/sys/menu/list")

    def nav(self):
        """当前用户的导航菜单"""
        return self.client.get("/sys/menu/nav")


class RBACLoginApi:
    """独立登录（用于新用户登录测试）"""

    def __init__(self, client: APIClient):
        self.client = client

    def login(self, username: str, password: str):
        return self.client.post("/adminLogin", json={
            "userName": username,
            "passWord": encrypt_password(password),
            "captchaVerification": "",
        })