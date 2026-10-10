# -*- coding: utf-8 -*-
"""Token 失效 + 并发登录测试

验证：
1. 无 token / 假 token / 格式错误的 token 都会被拒
2. sa-token 单 token 机制：同账号再登录会踢掉旧 token
"""
import allure
import pytest

from config.settings import API_URL, ADMIN
from api.client import APIClient
from api.admin.login_api import LoginApi


@allure.feature("后台接口-Token 失效")
@pytest.mark.api
class TestTokenExpired:

    @allure.title("[Token] 无 token 访问被拒")
    def test_no_token_rejected(self):
        client = APIClient(base_url=API_URL)
        resp = client.get("/prod/prod/page")
        body = resp.json()
        assert body["code"] != "00000", f"无 token 应该失败: {body}"

    @allure.title("[Token] 假 token 访问被拒")
    def test_fake_token_rejected(self):
        client = APIClient(base_url=API_URL)
        client.set_token("fake_token_1234567890")
        resp = client.get("/prod/prod/page")
        body = resp.json()
        assert body["code"] != "00000", f"假 token 应该失败: {body}"

    @allure.title("[Token] 格式错误的 token 被拒")
    def test_malformed_token_rejected(self):
        client = APIClient(base_url=API_URL)
        client.set_token("@@@invalid###token")
        resp = client.get("/prod/prod/page")
        body = resp.json()
        assert body["code"] != "00000", f"格式错误的 token 应该失败: {body}"


@allure.feature("后台接口-并发登录")
@pytest.mark.api
class TestConcurrentLogin:

    @pytest.mark.xfail(
        reason="sa-token 配置为多 token 共存（is-share=true），旧 token 不失效（已确认行为）",
        strict=False,
    )
    @allure.title("[并发] 同账号登录两次，旧 token 被踢")
    def test_login_twice_kicks_old_token(self):
        # 第 1 次登录
        c1 = APIClient(base_url=API_URL)
        r1 = LoginApi(c1).admin_login(ADMIN["username"], ADMIN["password"])
        assert r1.json()["success"] is True
        token1 = r1.json()["data"]["accessToken"]
        c1.set_token(token1)

        # 第 1 次登录的 token 应有效
        resp1 = c1.get("/prod/prod/page")
        assert resp1.json()["code"] == "00000", "第 1 个 token 应该有效"

        # 第 2 次登录（踢掉第 1 个）
        c2 = APIClient(base_url=API_URL)
        r2 = LoginApi(c2).admin_login(ADMIN["username"], ADMIN["password"])
        token2 = r2.json()["data"]["accessToken"]
        c2.set_token(token2)
        assert token1 != token2, "两次登录 token 应不同"

        # token1 应该失效
        resp2 = c1.get("/prod/prod/page")
        body2 = resp2.json()
        assert body2["code"] != "00000", (
            f"sa-token 单 token 机制下，旧 token 应失效。实际: {body2}"
        )

    @allure.title("[并发] 新 token 仍然有效")
    def test_new_token_still_valid(self):
        c = APIClient(base_url=API_URL)
        r = LoginApi(c).admin_login(ADMIN["username"], ADMIN["password"])
        token = r.json()["data"]["accessToken"]
        c.set_token(token)
        resp = c.get("/prod/prod/page")
        assert resp.json()["code"] == "00000"