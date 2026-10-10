# -*- coding: utf-8 -*-
import allure
import pytest

from api.buyer.buyer_cart import BuyerCart

SKU_ID = 402
PROD_ID = 75


@pytest.fixture
def clean_cart_after(buyer_headers):
    """异常用例跑完自动清空购物车，防止 999999 污染后续用例"""
    yield
    try:
        BuyerCart(buyer_headers).delete_all()
        print("\n[清理] 购物车已清空")
    except Exception as e:
        print(f"\n[清理警告] {e}")


@allure.feature("买家端")
@allure.story("异常场景：加购数量超过库存应被拦截")
def test_buyer_add_to_cart_out_of_stock(buyer_headers, clean_cart_after):
    """
    业务发现：Mall4j 库存校验发生在【加购】阶段，
    用超大数量触发库存不足，不改数据库、不污染环境。
    """
    cart = BuyerCart(buyer_headers)

    result = cart.add_to_cart(sku_id=SKU_ID, prod_id=PROD_ID, count=999999)
    print(f"\n加购响应: {result['code']}, msg={result['msg']}")

    assert result["code"] != "00000", "超大数量加购居然成功了，库存校验缺失"
    assert "库存不足" in result["msg"], f"错误提示不是库存不足: {result['msg']}"


@allure.feature("买家端")
@allure.story("异常场景：未登录访问购物车应被拦截")
def test_buyer_cart_without_token():
    """不带 token 访问购物车接口，应返回未授权"""
    cart = BuyerCart(headers={"Content-Type": "application/json"})
    result = cart.get_cart_info()
    assert result["code"] != "00000", "未登录居然能查购物车，鉴权缺失"
    print(f"\n未登录响应: {result['msg']}")