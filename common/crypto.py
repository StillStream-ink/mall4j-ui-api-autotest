# -*- coding: utf-8 -*-
"""AES 加密工具（复现前端 crypto.js 的 encrypt 逻辑）

前端加密方式：AES/ECB/Pkcs7，密钥 "-mall4j-password"，明文 = 时间戳 + 密码
"""
import base64
import time# -*- coding: utf-8 -*-
"""AES 加密工具（复现前端 crypto.js 的 encrypt 逻辑）

前端加密方式：AES/ECB/Pkcs7，密钥 "-mall4j-password"，明文 = 时间戳 + 密码
"""
import base64
import time

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

AES_KEY = b"-mall4j-password"


def encrypt_password(password: str) -> str:
    """AES/ECB/Pkcs7 加密，明文 = 毫秒时间戳 + 密码"""
    ts = str(int(time.time() * 1000))
    plain = (ts + password).encode("utf-8")
    cipher = AES.new(AES_KEY, AES.MODE_ECB)
    encrypted = cipher.encrypt(pad(plain, AES.block_size))
    return base64.b64encode(encrypted).decode("utf-8")


def decrypt_password(encrypted: str) -> str:
    """解密：返回明文（时间戳 + 密码）

    用途：端到端加密验证时，拿到密文解密后校验格式
    """
    raw = base64.b64decode(encrypted)
    cipher = AES.new(AES_KEY, AES.MODE_ECB)
    plain = unpad(cipher.decrypt(raw), AES.block_size).decode("utf-8")
    return plain

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

AES_KEY = b"-mall4j-password"


def encrypt_password(password: str) -> str:
    """AES/ECB/Pkcs7 加密，明文 = 毫秒时间戳 + 密码"""
    ts = str(int(time.time() * 1000))
    plain = (ts + password).encode("utf-8")
    cipher = AES.new(AES_KEY, AES.MODE_ECB)
    encrypted = cipher.encrypt(pad(plain, AES.block_size))
    return base64.b64encode(encrypted).decode("utf-8")