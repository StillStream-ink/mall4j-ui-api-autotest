# -*- coding: utf-8 -*-
"""RBAC API wrapper: 用户 / 角色 / 菜单"""
import time
import uuid
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64

from common.logger import get_logger

logger = get_logger(__name__)

AES_KEY = b"-mall4j-password"


def encrypt_password(password: str) -> str:
    """复用前端的 AES 加密逻辑"""
    ts = str(int(time.time() * 1000))
    plain = (ts + password).encode("utf-8")
    cipher = AES.new(AES_KEY, AES.MODE_ECB)
    return base64.b64encode(cipher.encrypt(pad(plain, AES.block_size))).decode("utf-8")


class SysUserCrudApi:
    """系统-管理员 CRUD"""
    def __init__(self, client):
        self.client = client

    def page(self, current=1, size=100, username=None):
        params = {"current": current, "size": size}
        if username:
            params["username"] = username
        return self.client.get("/sys/user/page", params=params)

    def info(self, user_id):
        return self.client.get(f"/sys/user/info/{user_id}")

    def create(self, username, password, email=None, mobile=None, role_id_list=None):
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

    def update(self, user_id, username, email=None, mobile=None, role_id_list=None, status=1):
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

    def delete(self, user_ids):
        return self.client.session.request(
            "DELETE",
            f"{self.client.base_url}/sys/user",
            json=user_ids,
            timeout=self.client.timeout,
        )

    def find_by_username(self, username):
        body = self.page(username=username).json()
        records = body.get("data", {}).get("records", [])
        for r in records:
            if r.get("username") == username:
                return r
        return None


class SysMenuApi:
    """系统-菜单"""
    def __init__(self, client):
        self.client = client

    def list_all(self):
        return self.client.get("/sys/menu/list")

    def nav(self):
        """当前用户的导航菜单"""
        return self.client.get("/sys/menu/nav")


class RBACLoginApi:
    """独立登录（用于新用户登录测试）"""
    def __init__(self, base_url):
        self.base_url = base_url

    def login(self, username, password):
        import requests
        return requests.post(
            f"{self.base_url}/adminLogin",
            json={
                "userName": username,
                "passWord": encrypt_password(password),
                "captchaVerification": "",
            },
            timeout=15,
        )
