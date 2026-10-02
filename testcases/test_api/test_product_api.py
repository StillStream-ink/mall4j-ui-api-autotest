# -*- coding: utf-8 -*-
"""Mall4j 后台 产品管理 接口测试"""
import allure
import pytest

from api.client import APIClient
from api.product_api import ProductApi
from config.settings import API_URL


@allure.feature("后台接口-产品管理")
@pytest.mark.api
class TestProductApi:

    @pytest.fixture
    def product_api(self, api_session):
        return ProductApi(api_session)

    @allure.title("拉取产品列表 第1页")
    def test_get_product_list(self, product_api):
        resp = product_api.page(current=1, size=10)
        body = resp.json()
        assert resp.status_code == 200
        assert body["code"] == "00000"
        data = body["data"]
        assert "records" in data
        assert len(data["records"]) > 0

    @allure.title("分页 size=5 返回5条以内")
    def test_page_size_5(self, product_api):
        resp = product_api.page(current=1, size=5)
        body = resp.json()
        assert body["code"] == "00000"
        records = body["data"]["records"]
        assert len(records) <= 5

    @allure.title("搜索 iPhone 命中")
    def test_search_product(self, product_api):
        resp = product_api.page(current=1, size=10, prod_name="iPhone")
        body = resp.json()
        assert body["code"] == "00000"
        records = body["data"]["records"]
        assert len(records) >= 1
        assert any("iPhone" in r.get("prodName", "") for r in records)

    @allure.title("搜索不存在 返回空")
    def test_search_not_exist(self, product_api):
        resp = product_api.page(current=1, size=10, prod_name="不存在的产品_XYZ_12345")
        body = resp.json()
        assert body["code"] == "00000"
        assert len(body["data"]["records"]) == 0

    @allure.title("无 token 访问 应该被拒")
    def test_no_token(self):
        # 独立创建一个不带 token 的 client
        fresh_client = APIClient(base_url=API_URL)
        product = ProductApi(fresh_client)
        resp = product.page(current=1, size=10)
        body = resp.json()
        assert body.get("success") is not True, f"无 token 竟然成功了: {body}"
        assert body.get("code") != "00000", f"无 token 竟然返回成功码: {body}"
        assert body.get("msg") == "Unauthorized" or "auth" in str(body).lower()

    @allure.title("产品字段完整性")
    def test_product_fields(self, product_api):
        resp = product_api.page(current=1, size=1)
        body = resp.json()
        first = body["data"]["records"][0]
        for field in ("prodId", "prodName", "price", "oriPrice", "status"):
            assert field in first, f"缺少字段 {field}"