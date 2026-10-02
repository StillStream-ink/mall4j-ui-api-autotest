# -*- coding: utf-8 -*-
"""BUG-002 专项验证：登录成功后应清除密码错误计数

源码：PasswordCheckManager.checkPassword()
问题：密码错误时 count++，但密码正确时没有清除 count
"""
import allure
import pytest
import redis

from config.settings import API_URL, ADMIN
from api.client import APIClient
from api.login_api import LoginApi

REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
LOCK_KEY_PATTERN = "*checkUserInputErrorPassword*"


@allure.feature("BUG-002 专项验证")
@pytest.mark.api
class TestLoginCounterReset:

    @pytest.fixture
    def client(self):
        return APIClient(base_url=API_URL)

    @pytest.fixture
    def login_api(self, client):
        return LoginApi(client)

    @pytest.fixture
    def r(self):
        conn = redis.Redis(
            host=REDIS_HOST, port=REDIS_PORT,
            decode_responses=True,
            protocol=2,
        )
        yield conn
        # 清理
        for key in conn.keys(LOCK_KEY_PATTERN):
            conn.delete(key)

    def _get_count(self, r):
        keys = r.keys(LOCK_KEY_PATTERN)
        if not keys:
            return 0
        return int(r.get(keys[0]) or 0)

    @allure.title("[BUG-002] 错误 3 次后正确登录，计数应清零")
    @pytest.mark.xfail(
        reason="BUG-002: 登录成功后不清除密码错误计数，详见 BUGS.md",
        strict=False,
    )
    def test_counter_reset_after_success_login(self, login_api, r):
        # 清 Redis
        for key in r.keys(LOCK_KEY_PATTERN):
            r.delete(key)

        # 错 3 次
        for i in range(3):
            login_api.admin_login(ADMIN["username"], f"wrong_{i}")

        count_after_fail = self._get_count(r)
        assert count_after_fail == 3, f"错 3 次后 count 应=3，实际 {count_after_fail}"

        # 正确登录
        resp = login_api.admin_login(ADMIN["username"], ADMIN["password"])
        assert resp.json()["success"] is True

        # 期望：count 清零
        count_after_success = self._get_count(r)
        assert count_after_success == 0, \
            f"登录成功后 count 应清零，实际 {count_after_success}（BUG-002）"

    @allure.title("[BUG-002] 计数不清零会导致用户被误锁")
    @pytest.mark.xfail(
        reason="BUG-002: 计数累计导致正常用户被误锁",
        strict=False,
    )
    def test_counter_accumulation_causes_lockout(self, login_api, r):
        # 清 Redis
        for key in r.keys(LOCK_KEY_PATTERN):
            r.delete(key)

        # 错 6 次
        for i in range(6):
            login_api.admin_login(ADMIN["username"], f"wrong_{i}")

        # 正确登录（应清零）
        resp = login_api.admin_login(ADMIN["username"], ADMIN["password"])
        assert resp.json()["success"] is True

        # 再错 6 次
        for i in range(6):
            login_api.admin_login(ADMIN["username"], f"wrong_again_{i}")

        # 因为计数没清零，此时 count=12，超过阈值 10，第 13 次应被锁
        resp = login_api.admin_login(ADMIN["username"], ADMIN["password"])
        assert resp.json()["success"] is True, \
            f"登录成功后再错 6 次不应被锁（BUG-002），实际: {resp.json()}"