# -*- coding: utf-8 -*-
"""性能基线测试：关键接口响应时间 < 1s"""
import time
import allure
import pytest

from api.client import APIClient
from api.login_api import LoginApi
from api.product_api import ProductApi
from api.member_api import MemberApi
from api.order_api import OrderApi
from api.batch2_api import SysUserApi, SysRoleApi, SysMenuApi
from config.settings import API_URL, ADMIN


@allure.feature("性能基线")
@pytest.mark.api
@pytest.mark.performance
class TestPerformance:

    @pytest.fixture
    def login_api(self):
        return LoginApi(APIClient(base_url=API_URL))

    @pytest.fixture
    def product_api(self, api_session):
        return ProductApi(api_session)

    @pytest.fixture
    def member_api(self, api_session):
        return MemberApi(api_session)

    @pytest.fixture
    def order_api(self, api_session):
        return OrderApi(api_session)

    @pytest.fixture
    def sys_user_api(self, api_session):
        return SysUserApi(api_session)

    @pytest.fixture
    def sys_role_api(self, api_session):
        return SysRoleApi(api_session)

    @pytest.fixture
    def sys_menu_api(self, api_session):
        return SysMenuApi(api_session)

    def _check_time(self, func, name, baseline=1.0):
        start = time.time()
        resp = func()
        elapsed = time.time() - start
        allure.attach(f"{elapsed:.3f}s", name=f"{name} 响应时间")
        body = resp.json()
        assert body.get("code") == "00000", f"{name} 接口返回异常: {body}"
        assert elapsed < baseline, f"{name} 响应 {elapsed:.3f}s 超过 {baseline}s 基线"
        return elapsed

    @allure.title("[性能] 登录 < 1s")
    def test_login_perf(self, login_api):
        self._check_time(
            lambda: login_api.admin_login(ADMIN["username"], ADMIN["password"]),
            "登录", 1.0,
        )

    @allure.title("[性能] 产品列表 < 1s")
    def test_product_list_perf(self, product_api):
        self._check_time(lambda: product_api.page(size=10), "产品列表", 1.0)

    @allure.title("[性能] 会员列表 < 1s")
    def test_member_list_perf(self, member_api):
        self._check_time(lambda: member_api.page(size=10), "会员列表", 1.0)

    @allure.title("[性能] 订单列表 < 1s")
    def test_order_list_perf(self, order_api):
        self._check_time(lambda: order_api.page(size=10), "订单列表", 1.0)

    @allure.title("[性能] 管理员列表 < 1s")
    def test_sys_user_list_perf(self, sys_user_api):
        self._check_time(lambda: sys_user_api.page(size=10), "管理员列表", 1.0)

    @allure.title("[性能] 角色列表 < 1s")
    def test_sys_role_list_perf(self, sys_role_api):
        self._check_time(lambda: sys_role_api.page(size=10), "角色列表", 1.0)

    @allure.title("[性能] 菜单树 < 1s")
    def test_sys_menu_perf(self, sys_menu_api):
        self._check_time(lambda: sys_menu_api.table(), "菜单树", 1.0)