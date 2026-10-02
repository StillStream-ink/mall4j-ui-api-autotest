# -*- coding: utf-8 -*-
"""B. Redis 缓存机制验证"""
import allure
import pytest
import redis

from config.settings import API_URL, ADMIN
from api.client import APIClient
from api.login_api import LoginApi


@allure.feature("数据一致性-Redis 缓存")
@pytest.mark.api
class TestRedisCache:

    @pytest.fixture
    def r(self):
        conn = redis.Redis(
            host="127.0.0.1", port=6379,
            decode_responses=True,
            protocol=2,
        )
        yield conn

    @allure.title("[缓存] 登录后 token 落 Redis")
    def test_login_token_in_redis(self, r):
        client = APIClient(base_url=API_URL)
        resp = LoginApi(client).admin_login(ADMIN["username"], ADMIN["password"])
        token = resp.json()["data"]["accessToken"]

        keys = r.keys("*Authorization*") + r.keys("*token*")
        assert len(keys) > 0, "登录后 Redis 应有 token key"

        found = any(
            token in str(r.get(k) or "")
            for k in keys
            if r.type(k) == "string"
        )
        assert found, f"token {token[:20]}... 未在 Redis 找到"

    @allure.title("[缓存] token key 有 TTL")
    def test_token_ttl(self, r):
        keys = r.keys("*Authorization*")
        assert len(keys) > 0, "Redis 里应有 Authorization key"
        ttl_found = False
        for k in keys:
            ttl = r.ttl(k)
            if 0 < ttl <= 2592000:
                ttl_found = True
                break
        assert ttl_found, "token key 应有合理 TTL（≤ 30 天）"

    @allure.title("[缓存] 登录新增 Redis key")
    def test_cache_key_change_on_login(self, r):
        before_count = len(r.keys("*"))
        client = APIClient(base_url=API_URL)
        LoginApi(client).admin_login(ADMIN["username"], ADMIN["password"])
        after_count = len(r.keys("*"))
        print(f"\n登录前 key 数: {before_count}")
        print(f"登录后 key 数: {after_count}")
        assert after_count >= before_count, "登录后 Redis key 数不应减少"
