# -*- coding: utf-8 -*-
"""买家端安全测试：XSS、Token 失效、越权访问"""
import allure
import pytest

from api.buyer.buyer_cart import BuyerCart
from api.buyer.buyer_order_list import BuyerOrderList
from api.buyer.buyer_product import BuyerProduct


@allure.feature("买家端")
@allure.story("安全测试：XSS 注入")
def test_buyer_xss_in_search(buyer_headers):
    """搜索框输入 XSS payload，后端应正常处理或转义"""
    product = BuyerProduct(buyer_headers)

    payload = "<script>alert(1)</script>"
    result = product.search_prod(prod_name=payload)

    assert result["code"] in ("00000", "A00001"), f"XSS 测试异常响应: {result}"

    if result.get("data"):
        raw = str(result)
        assert "<script>alert(1)</script>" not in raw, "响应中返回了未转义的 XSS payload"
    print(f"\nXSS 测试响应: {result['code']}, msg={result.get('msg')}")


@allure.feature("买家端")
@allure.story("安全测试：Token 失效")
def test_buyer_invalid_token_rejected():
    """使用伪造 token 访问购物车，应被拒绝"""
    fake_headers = {
        "Authorization": "fake_token_1234567890",
        "Content-Type": "application/json",
    }
    cart = BuyerCart(fake_headers)
    result = cart.get_cart_info()

    assert result["code"] != "00000", "伪造 token 居然能访问购物车，鉴权缺失"
    print(f"\n伪造 token 响应: {result['code']}, msg={result.get('msg')}")


@allure.feature("买家端")
@allure.story("安全测试：越权访问他人订单")
def test_buyer_idor_order_detail(buyer_headers):
    """用不存在的订单号查详情，不应返回数据"""
    order_list = BuyerOrderList(buyer_headers)

    fake_order_number = "0000000000000000000"
    result = order_list.order_detail(order_number=fake_order_number)

    if result["code"] == "00000" and result.get("data"):
        pytest.fail(f"越权风险：不存在的订单号居然返回了数据: {result['data']}")
    print(f"\nIDOR 测试响应: {result['code']}, msg={result.get('msg')}")