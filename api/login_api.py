# -*- coding: utf-8 -*-
"""Mall4j 后台登录接口封装"""
from api.client import APIClient
from common.crypto import encrypt_password
from common.logger import get_logger

logger = get_logger(__name__)


class LoginApi:
    def __init__(self, client: APIClient):
        self.client = client

    def admin_login(self, username: str, password: str, captcha: str = ""):
        """后台登录 /adminLogin"""
        data = {
            "userName": username,
            "passWord": encrypt_password(password),
            "captchaVerification": captcha,
        }
        return self.client.post("/adminLogin", json=data)