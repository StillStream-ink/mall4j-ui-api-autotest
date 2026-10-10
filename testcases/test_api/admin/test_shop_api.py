# -*- coding: utf-8 -*-
"""Shop management API tests (5 sub-modules)"""
import allure
import pytest

from api.client import APIClient
from api.admin.shop_api import ShopApi
from config.settings import API_URL


@allure.feature("后台接口-门店管理")
@pytest.mark.api
class TestShopApi:

    @pytest.fixture
    def shop_api(self, api_session):
        return ShopApi(api_session)

    # ==================== 自提点 ====================
    @allure.title("自提点列表")
    def test_pick_addr_list(self, shop_api):
        body = shop_api.pick_addr_page().json()
        assert body["code"] == "00000"
        assert "records" in body["data"]

    @allure.title("自提点 分页 size=1")
    def test_pick_addr_size(self, shop_api):
        body = shop_api.pick_addr_page(size=1).json()
        assert body["code"] == "00000"
        assert len(body["data"]["records"]) <= 1

    # ==================== 运费模板 ====================
    @allure.title("运费模板列表 有数据")
    def test_transport_list(self, shop_api):
        body = shop_api.transport_page().json()
        assert body["code"] == "00000"
        assert len(body["data"]["records"]) > 0

    @allure.title("运费模板 全量list")
    def test_transport_list_all(self, shop_api):
        body = shop_api.transport_list().json()
        assert body["code"] == "00000"
        assert isinstance(body["data"], list)

    # ==================== 轮播图 ====================
    @allure.title("轮播图列表 有数据")
    def test_carousel_list(self, shop_api):
        body = shop_api.carousel_page().json()
        assert body["code"] == "00000"
        records = body["data"]["records"]
        assert len(records) > 0
        assert "imgUrl" in records[0] or "pic" in records[0] or "imgId" in records[0]

    @allure.title("轮播图 size=1")
    def test_carousel_size(self, shop_api):
        body = shop_api.carousel_page(size=1).json()
        assert body["code"] == "00000"
        assert len(body["data"]["records"]) <= 1

    # ==================== 热搜 ====================
    @allure.title("热搜列表")
    def test_hot_search_list(self, shop_api):
        body = shop_api.hot_search_page().json()
        assert body["code"] == "00000"
        assert "records" in body["data"]

    # ==================== 公告 ====================
    @allure.title("公告列表 有数据")
    def test_notice_list(self, shop_api):
        body = shop_api.notice_page().json()
        assert body["code"] == "00000"
        records = body["data"]["records"]
        assert len(records) > 0

    @allure.title("公告 字段完整性")
    def test_notice_fields(self, shop_api):
        body = shop_api.notice_page(size=1).json()
        first = body["data"]["records"][0]
        assert "noticeContent" in first or "content" in first