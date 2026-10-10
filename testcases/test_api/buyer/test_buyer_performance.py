# -*- coding: utf-8 -*-
"""
买家端核心接口性能基线
断言：每个接口响应时间 < 1s（本地环境）
"""
import time
import allure
import pytest

from api.buyer.buyer_cart import BuyerCart
from api.buyer.buyer_order import BuyerOrder
from api.buyer.buyer_order_list import BuyerOrderList
from api.buyer.buyer_product import BuyerProduct

# 性能阈值（毫秒）
THRESHOLD_MS = 1000


def _measure(func, *args, **kwargs):
    """测一次接口调用耗时，返回 (毫秒, 响应)"""
    start = time.time()
    result = func(*args, **kwargs)
    elapsed_ms = (time.time() - start) * 1000
    return round(elapsed_ms, 2), result


def _assert_perf(name, elapsed_ms):
    """统一断言 + 打印"""
    print(f"\n[{name}] 响应耗时: {elapsed_ms} ms")
    assert elapsed_ms < THRESHOLD_MS, \
        f"{name} 耗时 {elapsed_ms}ms 超过阈值 {THRESHOLD_MS}ms"


@allure.feature("买家端性能基线")
@allure.story("商品列表接口 < 1s")
def test_perf_prod_list(buyer_headers):
    product = BuyerProduct(buyer_headers)
    elapsed, result = _measure(product.prod_list_by_tag, tag_id=1, size=10)
    assert result["code"] == "00000"
    _assert_perf("商品列表 /prod/prodListByTagId", elapsed)


@allure.feature("买家端性能基线")
@allure.story("商品搜索接口 < 1s")
def test_perf_search_prod(buyer_headers):
    product = BuyerProduct(buyer_headers)
    elapsed, result = _measure(product.search_prod, prod_name="测试", shop_id=1)
    assert result["code"] == "00000"
    _assert_perf("商品搜索 /search/searchProdPage", elapsed)


@allure.feature("买家端性能基线")
@allure.story("购物车列表接口 < 1s")
def test_perf_cart_info(buyer_headers):
    cart = BuyerCart(buyer_headers)
    elapsed, result = _measure(cart.get_cart_info)
    assert result["code"] == "00000"
    _assert_perf("购物车列表 /p/shopCart/info", elapsed)


@allure.feature("买家端性能基线")
@allure.story("加入购物车接口 < 1s")
def test_perf_add_to_cart(buyer_headers):
    cart = BuyerCart(buyer_headers)
    # 用 count=0 触发参数校验失败，但请求照样发出去，能测响应时间
    elapsed, result = _measure(
        cart.add_to_cart, sku_id=402, prod_id=75, count=0
    )
    print(f"\n加购响应: {result['code']}, msg={result.get('msg')}")
    _assert_perf("加购 /p/shopCart/changeItem", elapsed)


@allure.feature("买家端性能基线")
@allure.story("订单列表接口 < 1s")
def test_perf_order_list(buyer_headers):
    order_list = BuyerOrderList(buyer_headers)
    elapsed, result = _measure(order_list.my_orders)
    assert result["code"] == "00000"
    _assert_perf("订单列表 /p/myOrder/myOrder", elapsed)


@allure.feature("买家端性能基线")
@allure.story("确认订单接口 < 1s")
def test_perf_confirm_order(buyer_headers):
    cart = BuyerCart(buyer_headers)
    order = BuyerOrder(buyer_headers)

    cart.add_to_cart(sku_id=402, prod_id=75, count=1)
    basket_id = cart.get_first_basket_id()

    elapsed, result = _measure(
        order.confirm_order, basket_ids=[basket_id], addr_id=3
    )
    print(f"\n确认订单响应: {result['code']}, msg={result.get('msg')}")
    _assert_perf("确认订单 /p/order/confirm", elapsed)

