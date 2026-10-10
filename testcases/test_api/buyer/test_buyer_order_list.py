# -*- coding: utf-8 -*-
import allure
import jsonschema

from api.buyer.buyer_order_list import BuyerOrderList
from schemas.buyer_order_list_schema import ORDER_LIST_SCHEMA, ORDER_DETAIL_SCHEMA


@allure.feature("买家端")
@allure.story("订单列表：查询我的订单")
def test_buyer_order_list(buyer_headers):
    """查询我的订单列表，应返回列表结构"""
    order_list = BuyerOrderList(buyer_headers)
    result = order_list.my_orders()

    jsonschema.validate(result, ORDER_LIST_SCHEMA)
    assert result["code"] == "00000", f"订单列表查询失败: {result['msg']}"

    data = result["data"]
    records = data.get("records") if isinstance(data, dict) else data
    print(f"\n订单数量: {len(records or [])}")
    assert data is not None, "订单列表返回为空"


@allure.feature("买家端")
@allure.story("订单详情：从列表取一条订单查详情")
def test_buyer_order_detail(buyer_headers):
    """从订单列表取第一条订单，查详情"""
    order_list = BuyerOrderList(buyer_headers)

    list_result = order_list.my_orders()
    assert list_result["code"] == "00000"
    records = (
        list_result["data"].get("records")
        if isinstance(list_result["data"], dict)
        else list_result["data"]
    )
    assert records, "订单列表为空，无法测详情"

    order_number = records[0]["orderNumber"]
    print(f"\n取列表第一条订单号: {order_number}")

    detail = order_list.order_detail(order_number=order_number)
    jsonschema.validate(detail, ORDER_DETAIL_SCHEMA)
    assert detail["code"] == "00000", f"详情查询失败: {detail['msg']}"

    detail_data = detail["data"]
    print(f"\n详情 status: {detail_data.get('status')}, total: {detail_data.get('total')}")
    assert detail_data.get("status") is not None, "详情缺少 status 字段"
    assert detail_data.get("total") is not None, "详情缺少 total 字段"