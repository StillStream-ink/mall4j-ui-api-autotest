# -*- coding: utf-8 -*-
"""Mall4j 后台登录接口封装"""
from typing import Any, Dict

from api.client import APIClient
from common.crypto import encrypt_password


class LoginApi:
    def __init__(self, client: APIClient) -> None:
        self.client = client

    def admin_login(
        self,
        username: str,
        password: str,
        captcha: str = "",
    ) -> Any:
        """后台登录 /adminLogin"""
        data: Dict[str, str] = {
            "userName": username,
            "passWord": encrypt_password(password),
            "captchaVerification": captcha,
        }
        return self.client.post("/adminLogin", json=data)