# -*- coding: utf-8 -*-
import allure

from api.buyer.buyer_product import BuyerProduct


@allure.feature("买家端")
@allure.story("商品浏览：按标签查询")
def test_buyer_page_product(buyer_headers):
    """商品列表：按标签 tagId=1 查，应返回商品数据"""
    product = BuyerProduct(buyer_headers)
    result = product.prod_list_by_tag(tag_id=1, size=10)

    assert result["code"] == "00000", f"商品列表查询失败: {result['msg']}"

    # data 可能是 list，也可能是 dict 里包着 list
    records = result["data"]
    if isinstance(records, dict):
        records = records.get("records") or records.get("list") or []
    assert isinstance(records, list) and len(records) > 0, f"商品列表为空: {records}"

    first = records[0]
    print(f"\n首条商品: prodId={first.get('prodId')}, name={first.get('prodName')}, price={first.get('price')}")
    assert first.get("prodId"), "商品 prodId 缺失"
    assert first.get("prodName"), "商品 prodName 缺失"


@allure.feature("买家端")
@allure.story("商品搜索：关键词匹配")
def test_buyer_search_product(buyer_headers):
    """搜索'测试'，应返回匹配结果"""
    product = BuyerProduct(buyer_headers)
    result = product.search_prod(prod_name="测试", shop_id=1)

    assert result["code"] == "00000", f"商品搜索失败: {result['msg']}"
    records = result["data"]
    if isinstance(records, dict):
        records = records.get("records") or records.get("list") or []
    print(f"\n搜索'测试'命中: {len(records)} 条")
    assert len(records) > 0, "搜索无结果"