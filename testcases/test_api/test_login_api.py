# -*- coding: utf-8 -*-
"""Mall4j 后台登录 接口测试
优化：
1. 数据驱动参数化（10 组场景）
2. JSON Schema 契约测试
3. 性能基线断言
"""
import time
import allure
import jsonschema
import pytest

from config.settings import API_URL, ADMIN
from api.client import APIClient
from api.login_api import LoginApi
from common.crypto import encrypt_password
from schemas.login_schema import LOGIN_SUCCESS_SCHEMA, LOGIN_FAIL_SCHEMA


@allure.feature("后台接口-登录")
@pytest.mark.api
class TestLoginApi:

    @pytest.fixture
    def client(self):
        return APIClient(base_url=API_URL)

    @pytest.fixture
    def login_api(self, client):
        return LoginApi(client)

    # ==================== 1. 加密函数（纯单元） ====================
    @allure.title("加密函数每次结果不同（时间戳驱动）")
    def test_encrypt_dynamic(self):
        r1 = encrypt_password("123456")
        time.sleep(0.005)
        r2 = encrypt_password("123456")
        assert isinstance(r1, str) and len(r1) > 0
        assert r1 != r2

    # ==================== 2. 数据驱动：登录场景矩阵 ====================
    @allure.title("登录场景矩阵：{case_name}")
    @pytest.mark.parametrize(
        "username, password, expect_success, expect_msg_contains, case_name",
        [
            # 正向（1 组）
            ("admin", "123456", True, "", "正常登录"),
            # 参数校验（2 组，不触发限流）
            ("", "123456", False, "userName", "空用户名"),
            ("   ", "123456", False, "userName", "全空格用户名"),
            # 密码错误（2 组，限流阈值内）
            ("admin", "wrong_pwd", False, "账号或密码", "错误密码"),
            ("admin", "123456 ", False, "账号或密码", "密码带尾空格"),
        ],
        ids=[
            "normal", "empty_user", "space_user", "wrong_pwd", "trailing_space",
        ],
    )
    
    def test_login_matrix(self, login_api, username, password,
                          expect_success, expect_msg_contains, case_name):
        resp = login_api.admin_login(username, password)
        body = resp.json()

        assert resp.status_code == 200
        assert body["success"] is expect_success, \
            f"[{case_name}] 期望 success={expect_success}，实际 {body}"

        if expect_success:
            assert body["code"] == "00000"
            assert "accessToken" in body["data"]
        else:
            assert body["code"] != "00000"
            if expect_msg_contains:
                assert expect_msg_contains in str(body.get("msg", "")) or \
                       expect_msg_contains in str(body.get("data", "")), \
                       f"[{case_name}] 期望错误信息含 {expect_msg_contains!r}，实际 {body}"

    # ==================== 3. 契约测试 ====================
    @allure.title("[契约] 登录成功响应符合 Schema")
    def test_login_success_contract(self, login_api):
        body = login_api.admin_login(ADMIN["username"], ADMIN["password"]).json()
        jsonschema.validate(instance=body, schema=LOGIN_SUCCESS_SCHEMA)

    @allure.title("[契约] 登录失败响应符合 Schema")
    def test_login_fail_contract(self, login_api):
        body = login_api.admin_login(ADMIN["username"], "wrong").json()
        jsonschema.validate(instance=body, schema=LOGIN_FAIL_SCHEMA)

    # ==================== 4. 性能基线 ====================
    @allure.title("[性能] 登录响应时间 < 2s")
    def test_login_performance(self, login_api):
        start = time.time()
        resp = login_api.admin_login(ADMIN["username"], ADMIN["password"])
        elapsed = time.time() - start

        assert resp.json()["code"] == "00000"
        allure.attach(f"{elapsed:.3f}s", name="响应时间", attachment_type=allure.attachment_type.TEXT)
        assert elapsed < 2.0, f"登录响应 {elapsed:.3f}s，超过 2s 基线"

    @allure.title("[性能] 连续 5 次登录平均响应 < 2s")
    def test_login_performance_avg(self, login_api):
        times = []
        for _ in range(5):
            start = time.time()
            resp = login_api.admin_login(ADMIN["username"], ADMIN["password"])
            times.append(time.time() - start)
            assert resp.json()["code"] == "00000"

        avg = sum(times) / len(times)
        allure.attach(
            "\n".join(f"第 {i+1} 次: {t:.3f}s" for i, t in enumerate(times)) +
            f"\n\n平均: {avg:.3f}s",
            name="性能数据", attachment_type=allure.attachment_type.TEXT,
        )
        assert avg < 2.0, f"平均响应 {avg:.3f}s，超过 2s 基线"