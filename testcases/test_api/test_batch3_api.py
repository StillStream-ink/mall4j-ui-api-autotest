# -*- coding: utf-8 -*-
"""Batch3 API tests"""
import allure
import pytest

from api.batch3_api import (
    CategoryApi, ProdTagApi, ProdCommApi, SpecApi,
    SysConfigApi, AreaApi, SysLogApi,
)


@allure.feature("接口-分类管理")
@pytest.mark.api
class TestCategoryApi:

    @pytest.fixture
    def api(self, api_session):
        return CategoryApi(api_session)

    @allure.title("分类树表 有数据")
    def test_table(self, api):
        body = api.table().json()
        assert body["code"] == "00000"
        assert isinstance(body["data"], list)
        assert len(body["data"]) > 0

    @allure.title("分类全量list")
    def test_list(self, api):
        body = api.list_category().json()
        assert body["code"] == "00000"


@allure.feature("接口-分组管理")
@pytest.mark.api
class TestProdTagApi:

    @pytest.fixture
    def api(self, api_session):
        return ProdTagApi(api_session)

    @allure.title("分组分页列表 有数据")
    def test_page(self, api):
        body = api.page().json()
        assert body["code"] == "00000"
        assert body["data"]["total"] >= 1

    @allure.title("分组 size=1")
    def test_size(self, api):
        body = api.page(size=1).json()
        assert body["code"] == "00000"
        assert len(body["data"]["records"]) <= 1


@allure.feature("接口-评论管理")
@pytest.mark.api
class TestProdCommApi:

    @pytest.fixture
    def api(self, api_session):
        return ProdCommApi(api_session)

    @allure.title("评论分页列表")
    def test_page(self, api):
        body = api.page().json()
        assert body["code"] == "00000"
        assert "records" in body["data"]


@allure.feature("接口-规格管理")
@pytest.mark.api
class TestSpecApi:

    @pytest.fixture
    def api(self, api_session):
        return SpecApi(api_session)

    @allure.title("规格分页 有数据")
    def test_page(self, api):
        body = api.page().json()
        assert body["code"] == "00000"
        assert body["data"]["total"] >= 1

    @allure.title("规格全量list")
    def test_list_all(self, api):
        body = api.list_all().json()
        assert body["code"] == "00000"


@allure.feature("接口-参数管理")
@pytest.mark.api
class TestSysConfigApi:

    @pytest.fixture
    def api(self, api_session):
        return SysConfigApi(api_session)

    @allure.title("参数列表")
    def test_page(self, api):
        body = api.page().json()
        assert body["code"] == "00000"
        assert "records" in body["data"]


@allure.feature("接口-地址管理")
@pytest.mark.api
class TestAreaApi:

    @pytest.fixture
    def api(self, api_session):
        return AreaApi(api_session)

    @allure.title("全量地址")
    def test_list(self, api):
        body = api.list_all().json()
        assert body["code"] == "00000"

    @allure.title("顶层省份")
    def test_list_by_pid(self, api):
        body = api.list_by_pid(0).json()
        assert body["code"] == "00000"
        assert isinstance(body["data"], list)


@allure.feature("接口-系统日志")
@pytest.mark.api
class TestSysLogApi:

    @pytest.fixture
    def api(self, api_session):
        return SysLogApi(api_session)

    @allure.title("日志列表 有数据")
    def test_page(self, api):
        body = api.page().json()
        assert body["code"] == "00000"
        assert body["data"]["total"] >= 1

    @allure.title("搜索 admin 的日志")
    def test_search_admin(self, api):
        body = api.page(username="admin").json()
        assert body["code"] == "00000"