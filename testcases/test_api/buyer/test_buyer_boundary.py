# -*- coding: utf-8 -*-
"""买家端边界值/异常输入测试"""
import allure
import pytest

from api.buyer.buyer_cart import BuyerCart
from api.buyer.buyer_product import BuyerProduct


@pytest.mark.parametrize("keyword, desc", [
    ("A" * 500,                    "超长文本 500 字符"),
    ("  test  ",                   "前后带空格"),
    ("admin' OR '1'='1",           "SQL 注入"),
    ("<script>alert(1)</script>",  "XSS 脚本"),
    ("!@#$%^&*()",                 "特殊字符"),
])
@allure.feature("买家端")
@allure.story("边界值：搜索关键词异常输入")
def test_search_with_invalid_keyword(buyer_headers, keyword, desc):
    """搜索异常输入，后端不应返回 500"""
    product = BuyerProduct(buyer_headers)
    result = product.search_prod(prod_name=keyword)

    assert result["code"] != "A00005", f"[{desc}] 返回服务器异常: {result}"
    raw = str(result)
    assert "<script>alert(1)</script>" not in raw, f"[{desc}] XSS payload 未转义"
    print(f"\n[{desc}] code={result['code']}, msg={result.get('msg')}")


@allure.feature("买家端")
@allure.story("边界值：Emoji 输入（BUG-004）")
@pytest.mark.xfail(
    reason="BUG-004: 搜索接口对 Emoji 输入返回 A00005 服务器异常",
    strict=False,
)
def test_search_with_emoji_should_not_crash(buyer_headers):
    """
    BUG-004: 搜索接口传入 Emoji 表情时，后端返回 A00005 服务器异常。
    预期：应正常处理（返回空结果或明确参数错误），而非 500。
    等开发修复后，此用例应从 XFAIL 变为 PASSED。
    """
    product = BuyerProduct(buyer_headers)
    result = product.search_prod(prod_name="😀😂🤔")
    print(f"\nEmoji 搜索响应: {result['code']}, msg={result.get('msg')}")

    assert result["code"] != "A00005", f"Emoji 输入导致服务器异常: {result}"


@pytest.mark.parametrize("count, desc", [
    (0,      "数量为 0"),
    (-1,     "数量为负"),
])
@allure.feature("买家端")
@allure.story("边界值：加购数量异常")
def test_add_to_cart_invalid_count(buyer_headers, count, desc):
    """加购异常数量，后端应拦截或正确处理"""
    cart = BuyerCart(buyer_headers)
    result = cart.add_to_cart(sku_id=402, prod_id=75, count=count)

    assert result["code"] != "A00005", f"[{desc}] 返回服务器异常: {result}"
    print(f"\n[{desc}] code={result['code']}, msg={result.get('msg')}")