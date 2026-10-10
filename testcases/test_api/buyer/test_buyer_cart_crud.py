# -*- coding: utf-8 -*-
import allure

from api.buyer.buyer_cart import BuyerCart

SKU_ID = 402
PROD_ID = 75


@allure.feature("买家端")
@allure.story("购物车：修改数量")
def test_buyer_update_cart_count(buyer_headers):
    """加购 count=1 → 改成 count=3 → 验证 prodCount=3"""
    cart = BuyerCart(buyer_headers)

    # 加购 1 件
    cart.add_to_cart(sku_id=SKU_ID, prod_id=PROD_ID, count=1)

    # 找到购物车里对应 sku 的记录
    info = cart.get_cart_info()
    items = info["data"][0]["shopCartItemDiscounts"][0]["shopCartItems"]
    target = next(i for i in items if i["skuId"] == SKU_ID)
    print(f"\n修改前 prodCount = {target['prodCount']}")
    assert target["prodCount"] == 1, "加购后数量不是 1"

    # 改成 3
    result = cart.update_count(sku_id=SKU_ID, prod_id=PROD_ID, count=3)
    print(f"\n修改数量响应: {result}")
    assert result["code"] == "00000", f"修改数量失败: {result['msg']}"

    # 验证
    info = cart.get_cart_info()
    items = info["data"][0]["shopCartItemDiscounts"][0]["shopCartItems"]
    target = next(i for i in items if i["skuId"] == SKU_ID)
    print(f"\n修改后 prodCount = {target['prodCount']}")
    assert target["prodCount"] == 3, "数量未更新为 3"


@allure.feature("买家端")
@allure.story("购物车：删除商品")
def test_buyer_delete_cart_item(buyer_headers):
    """加购后删除，验证商品从购物车消失"""
    cart = BuyerCart(buyer_headers)

    # 加购
    cart.add_to_cart(sku_id=SKU_ID, prod_id=PROD_ID, count=1)
    basket_id = cart.get_first_basket_id()
    assert basket_id, "购物车为空"

    before = cart.get_cart_info()
    before_count = sum(
        len(d["shopCartItems"])
        for g in (before["data"] or [])
        for d in g["shopCartItemDiscounts"]
    )

    # 删除
    result = cart.delete_item([basket_id])
    assert result["code"] == "00000", f"删除失败: {result['msg']}"

    # 验证
    after = cart.get_cart_info()
    after_count = sum(
        len(d["shopCartItems"])
        for g in (after["data"] or [])
        for d in g["shopCartItemDiscounts"]
    )
    print(f"\n删除前 {before_count} 件，删除后 {after_count} 件")
    assert after_count == before_count - 1, "删除后商品数未 -1"

@allure.feature("买家端")
@allure.story("购物车：累加数量")
def test_buyer_update_cart_count(buyer_headers):
    """先清购物车 → 加购 1 → 再累加 2 → 验证 prodCount=3"""
    cart = BuyerCart(buyer_headers)

    # 先清空，保证初始干净
    cart.delete_all()

    # 加购 1 件
    cart.add_to_cart(sku_id=SKU_ID, prod_id=PROD_ID, count=1)

    info = cart.get_cart_info()
    items = info["data"][0]["shopCartItemDiscounts"][0]["shopCartItems"]
    target = next(i for i in items if i["skuId"] == SKU_ID)
    print(f"\n加购后 prodCount = {target['prodCount']}")
    assert target["prodCount"] == 1, "加购后数量不是 1"

    # 再累加 2 件
    result = cart.update_count(sku_id=SKU_ID, prod_id=PROD_ID, count=2)
    assert result["code"] == "00000", f"累加失败: {result['msg']}"

    info = cart.get_cart_info()
    items = info["data"][0]["shopCartItemDiscounts"][0]["shopCartItems"]
    target = next(i for i in items if i["skuId"] == SKU_ID)
    print(f"\n累加后 prodCount = {target['prodCount']}")
    assert target["prodCount"] == 3, "数量应为 1 + 2 = 3"

    # 测完清空
    cart.delete_all()