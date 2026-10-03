# -*- coding: utf-8 -*-
"""纯单元测试（不依赖后端）"""
import base64
import time

import pytest
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad

from api.login_api import encrypt_password

AES_KEY = b"-mall4j-password"


class TestEncryptPassword:

    def test_encrypt_returns_string(self):
        assert isinstance(encrypt_password("123456"), str)

    def test_encrypt_not_empty(self):
        assert len(encrypt_password("123456")) > 0

    def test_encrypt_differs_by_timestamp(self):
        """相同密码不同时间戳，密文应不同"""
        r1 = encrypt_password("123456")
        time.sleep(0.005)
        r2 = encrypt_password("123456")
        assert r1 != r2

    def test_encrypt_can_be_decrypted(self):
        """密文可解回原始明文格式（时间戳 + 密码）"""
        password = "123456"
        encrypted = encrypt_password(password)
        raw = base64.b64decode(encrypted)
        cipher = AES.new(AES_KEY, AES.MODE_ECB)
        plain = unpad(cipher.decrypt(raw), AES.block_size).decode("utf-8")
        # 明文 = 13 位时间戳 + 密码
        assert plain.endswith(password)
        ts_part = plain[: -len(password)]
        assert len(ts_part) == 13
        assert ts_part.isdigit()

    def test_encrypt_different_passwords(self):
        """不同密码，即使时间戳相同也应不同密文"""
        r1 = encrypt_password("abc")
        r2 = encrypt_password("xyz")
        assert r1 != r2

    @pytest.mark.parametrize("pwd", ["123456", "a", "!@#$%", "长密码测试"])
    def test_encrypt_various_passwords(self, pwd):
        """各种密码都能加密"""
        r = encrypt_password(pwd)
        assert isinstance(r, str)
        assert len(r) > 0