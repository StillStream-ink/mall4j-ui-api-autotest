# -*- coding: utf-8 -*-
"""登录限流机制专项测试

Mall4j 限流逻辑（见 PasswordCheckManager.java）：
- 阈值：count > 10，即第 12 次尝试才触发
- 时间窗口：30 分钟
- 登录成功不清除计数（设计缺陷）
- key 格式：{sysType}checkUserInputErrorPassword_{IP}{USERNAME}
"""
import allure
import pytest
import redis

from config.settings import API_URL, REDIS_HOST, REDIS_PORT, REDIS_DB
from api.client import APIClient
from api.admin.login_api import LoginApi

LOCK_KEY_PATTERN = "*checkUserInputErrorPassword*"
MAX_TRIES_BEFORE_LOCK = 11


@allure.feature("后台接口-登录限流")
@pytest.mark.api
class TestLoginRateLimit:

    @classmethod
    def teardown_class(cls):
        """整个类跑完后清 Redis，防止污染后续测试"""
        import redis
        conn = redis.Redis(
            host="127.0.0.1", port=6379,
            decode_responses=True, protocol=2,
        )
        for key in conn.keys("*checkUserInputErrorPassword*"):
            conn.delete(key)
        print("\n[TEARDOWN] 限流测试结束，已清 Redis 限流 key")

    @pytest.fixture
    def client(self):
        return APIClient(base_url=API_URL)

    @pytest.fixture
    def login_api(self, client):
        return LoginApi(client)

    @pytest.fixture
    def r(self):
        conn = redis.Redis(
            host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB,
            decode_responses=True, protocol=2,
        )
        yield conn
        for key in conn.keys(LOCK_KEY_PATTERN):
            conn.delete(key)

    @allure.title(f"[安全] 连续错误 {MAX_TRIES_BEFORE_LOCK}+1 次触发限流")
    def test_rate_limit_triggered(self, login_api, r):
        # 先清空
        for key in r.keys(LOCK_KEY_PATTERN):
            r.delete(key)

        # 错 11 次（count 从 0 递增到 11）
        for i in range(MAX_TRIES_BEFORE_LOCK):
            body = login_api.admin_login("admin", f"wrong_{i}").json()
            assert body["success"] is False
            # 前 11 次都是"账号或密码不正确"
            assert "账号或密码" in body["msg"], f"第 {i+1} 次错误信息异常: {body}"

        # 第 12 次即使密码正确也被锁
        body = login_api.admin_login("admin", "123456").json()
        assert body["success"] is False, f"触发限流后应拒绝登录: {body}"
        assert "限制" in body["msg"] or "锁定" in body["msg"], \
            f"错误信息应包含限流提示，实际: {body['msg']}"
        allure.attach(body["msg"], name="限流提示")

    @allure.title("[安全] 限流 key 落 Redis 且带 TTL")
    def test_rate_limit_key_exists(self, login_api, r):
        for key in r.keys(LOCK_KEY_PATTERN):
            r.delete(key)

        # 错 1 次
        login_api.admin_login("admin", "wrong_once")

        keys = r.keys(LOCK_KEY_PATTERN)
        assert len(keys) >= 1, "密码错误后应生成限流 key"

        key = keys[0]
        ttl = r.ttl(key)
        count = r.get(key)
        allure.attach(f"key={key}\ncount={count}\nttl={ttl}s", name="Redis 限流数据")

        assert 0 < ttl <= 1800, f"TTL 应为 30 分钟(1800s)以内，实际 {ttl}"

    @allure.title("[安全] 计数累计验证：每次错误+1")
    def test_rate_limit_counter_increments(self, login_api, r):
        for key in r.keys(LOCK_KEY_PATTERN):
            r.delete(key)

        # 错 3 次
        for _ in range(3):
            login_api.admin_login("admin", "wrong")

        keys = r.keys(LOCK_KEY_PATTERN)
        assert len(keys) == 1
        count = int(r.get(keys[0]))
        assert count == 3, f"错 3 次后 count 应为 3，实际 {count}"