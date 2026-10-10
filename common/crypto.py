# -*- coding: utf-8 -*-
"""AES 加密工具（复现前端 crypto.js 的 encrypt 逻辑）

前端加密方式：AES/ECB/Pkcs7，密钥 "-mall4j-password"，明文 = 时间戳 + 密码
"""
import base64
import time

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from config.settings import AES_KEY as AES_KEY_STR

AES_KEY: bytes = AES_KEY_STR.encode("utf-8")


def encrypt_password(password: str) -> str:
    """AES/ECB/Pkcs7 加密，明文 = 毫秒时间戳 + 密码"""
    ts: str = str(int(time.time() * 1000))
    plain: bytes = (ts + password).encode("utf-8")
    cipher = AES.new(AES_KEY, AES.MODE_ECB)
    encrypted: bytes = cipher.encrypt(pad(plain, AES.block_size))
    return base64.b64encode(encrypted).decode("utf-8")


def decrypt_password(encrypted: str) -> str:
    """解密：返回明文（时间戳 + 密码），用于端到端加密校验"""
    raw: bytes = base64.b64decode(encrypted)
    cipher = AES.new(AES_KEY, AES.MODE_ECB)
    plain: str = unpad(cipher.decrypt(raw), AES.block_size).decode("utf-8")
    return plain