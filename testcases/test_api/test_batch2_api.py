# -*- coding: utf-8 -*-
"""Batch2 API tests"""
import allure
import pytest

from api.batch2_api import OrderApi, SysUserApi, SysRoleApi, SysMenuApi


@allure.feature("后台接口-订单")
@pytest.mark.api
class TestOrderApi:

    @pytest.fixture
    def api(self, api_session):
        return OrderApi(api_session)

    @allure.title("订单列表 有数据")
    def test_list(self, api):
        body = api.page().json()
        assert body["code"] == "00000"
        assert body["data"]["total"] > 0

    @allure.title("订单 size=1")
    def test_size(self, api):
        body = api.page(size=1).json()
        assert body["code"] == "00000"
        assert len(body["data"]["records"]) <= 1

    @allure.title("搜索不存在的订单号")
    def test_search_not_exist(self, api):
        body = api.page(order_number="NOT_EXIST_9999").json()
        assert body["code"] == "00000"
        assert body["data"]["total"] == 0


@allure.feature("后台接口-管理员")
@pytest.mark.api
class TestSysUserApi:

    @pytest.fixture
    def api(self, api_session):
        return SysUserApi(api_session)

    @allure.title("管理员列表")
    def test_list(self, api):
        body = api.page().json()
        assert body["code"] == "00000"
        assert body["data"]["total"] >= 1

    @allure.title("当前管理员信息")
    def test_info(self, api):
        body = api.info().json()
        assert body["code"] == "00000"
        assert body["data"]["username"] == "admin"


@allure.feature("后台接口-角色")
@pytest.mark.api
class TestSysRoleApi:

    @pytest.fixture
    def api(self, api_session):
        return SysRoleApi(api_session)

    @allure.title("角色列表")
    def test_page(self, api):
        body = api.page().json()
        assert body["code"] == "00000"
        assert body["data"]["total"] >= 1

    @allure.title("角色全量list")
    def test_list_all(self, api):
        body = api.list_all().json()
        assert body["code"] == "00000"
        assert isinstance(body["data"], list)
        assert len(body["data"]) >= 1


@allure.feature("后台接口-菜单")
@pytest.mark.api
class TestSysMenuApi:

    @pytest.fixture
    def api(self, api_session):
        return SysMenuApi(api_session)

    @allure.title("菜单树表")
    def test_table(self, api):
        body = api.table().json()
        assert body["code"] == "00000"
        assert isinstance(body["data"], list)
        assert len(body["data"]) > 0

    @allure.title("菜单全量list")
    def test_list_all(self, api):
        body = api.list_all().json()
        assert body["code"] == "00000"
        assert isinstance(body["data"], list)

    @allure.title("菜单导航")
    def test_nav(self, api):
        body = api.nav().json()
        assert body["code"] == "00000"