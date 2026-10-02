# -*- coding: utf-8 -*-
"""Mall4j 后台登录接口封装"""
import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64

from api.client import APIClient
from common.logger import get_logger

logger = get_logger(__name__)

# 前端 crypto.js 里写死的 key
AES_KEY = b"-mall4j-password"


def encrypt_password(password: str) -> str:
    """复现前端 encrypt()：AES/ECB/Pkcs7，明文 = 时间戳 + 密码"""
    ts = str(int(time.time() * 1000))  # 毫秒时间戳
    plain = (ts + password).encode("utf-8")
    cipher = AES.new(AES_KEY, AES.MODE_ECB)
    encrypted = cipher.encrypt(pad(plain, AES.block_size))
    return base64.b64encode(encrypted).decode("utf-8")


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