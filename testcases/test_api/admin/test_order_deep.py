# -*- coding: utf-8 -*-
"""Order deep API tests"""
import allure
import pytest

from api.admin.order_api import OrderApi


@allure.feature("后台接口-订单深度")
@pytest.mark.api
class TestOrderDeep:

    @pytest.fixture
    def api(self, api_session):
        return OrderApi(api_session)

    @allure.title("订单列表 有数据")
    def test_list(self, api):
        body = api.page().json()
        assert body["code"] == "00000"
        assert body["data"]["total"] > 0

    @allure.title("订单列表分页 size=1")
    def test_page_size_1(self, api):
        body = api.page(size=1).json()
        assert body["code"] == "00000"
        assert len(body["data"]["records"]) == 1

    @allure.title("按订单号搜索")
    def test_search_by_order_number(self, api):
        # 先拿一个真实订单号
        list_body = api.page(size=1).json()
        first = list_body["data"]["records"][0]
        order_no = first.get("orderNumber")
        assert order_no, "列表应返回 orderNumber"
        # 搜索它
        body = api.page(order_number=order_no).json()
        assert body["code"] == "00000"
        assert body["data"]["total"] >= 1
        assert any(r["orderNumber"] == order_no for r in body["data"]["records"])

    @allure.title("搜索不存在的订单号 返回空")
    def test_search_not_exist(self, api):
        body = api.page(order_number="NOT_EXIST_999999999").json()
        assert body["code"] == "00000"
        assert body["data"]["total"] == 0

    @allure.title("订单详情 有商品项")
    def test_order_detail(self, api):
        list_body = api.page(size=1).json()
        order_no = list_body["data"]["records"][0]["orderNumber"]
        body = api.info(order_no).json()
        assert body["code"] == "00000"
        assert body["data"]["orderNumber"] == order_no
        assert "orderItems" in body["data"]
        assert len(body["data"]["orderItems"]) >= 1

    @allure.title("订单详情字段完整")
    def test_order_detail_fields(self, api):
        list_body = api.page(size=1).json()
        order_no = list_body["data"]["records"][0]["orderNumber"]
        data = api.info(order_no).json()["data"]
        for f in ("orderNumber", "status", "actualTotal", "createTime", "orderItems"):
            assert f in data, f"缺少字段 {f}"

    @allure.title("发货接口 不存在的订单号 应该报错")
    def test_delivery_nonexist_order(self, api):
        """危险操作保护：用不存在的订单号测，不应污染数据"""
        resp = api.delivery(
            order_number="NOT_EXIST_ORDER_999999999",
            dvy_id=1,
            dvy_flow_id="SF9999999999",
        )
        body = resp.json()
        # 应该返回错误（订单不存在 / 无权限）
        assert body["code"] != "00000" or body.get("fail") is True, \
            f"不存在的订单不应发货成功: {body}"

    @allure.title("发货接口 缺参数 应被拒")
    def test_delivery_missing_params(self, api):
        # 直接空 body
        resp = api.delivery(order_number="", dvy_id=None, dvy_flow_id="")
        body = resp.json()
        assert body.get("success") is not True or body["code"] != "00000"