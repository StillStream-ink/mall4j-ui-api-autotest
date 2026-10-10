# -*- coding: utf-8 -*-
"""买家端登录封装"""
from typing import Any, Dict

import requests

from common.crypto import encrypt_password

BASE_URL: str = "http://127.0.0.1:8086"


class BuyerLogin:
    def __init__(self) -> None:
        self.token: str = ""

    def login(
        self,
        username: str = "13000000001",
        password: str = "123456",
    ) -> str:
        resp = requests.post(
            f"{BASE_URL}/login",
            json={"userName": username, "passWord": encrypt_password(password)},
            timeout=10,
        )
        result: Dict[str, Any] = resp.json()
        assert result["code"] == "00000", f"登录失败: {result['msg']}"
        self.token = result["data"]["accessToken"]
        return self.token

    def get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": self.token,
            "Content-Type": "application/json",
        }