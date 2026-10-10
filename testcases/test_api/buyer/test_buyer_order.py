# -*- coding: utf-8 -*-
import allure
import jsonschema

from api.buyer.buyer_cart import BuyerCart
from api.buyer.buyer_order import BuyerOrder
from common.db_helper import DBHelper
from schemas.buyer_order_schema import ORDER_SUBMIT_SCHEMA

SKU_ID = 402
PROD_ID = 75
SHOP_ID = 1
ADDR_ID = 3


@allure.feature("买家端")
@allure.story("下单完整链路：加购 → 确认 → 提交 → DB 断言")
def test_buyer_submit_order(buyer_headers, clean_buyer_data):
    cart = BuyerCart(buyer_headers)
    order = BuyerOrder(buyer_headers)

    # 先清空购物车，避免异常用例留下的脏数据
    cart.delete_all()

    # 1. 数据工厂：测试自己加购
    add_result = cart.add_to_cart(sku_id=SKU_ID, prod_id=PROD_ID, count=1)
    assert add_result["code"] == "00000", f"加购失败: {add_result['msg']}"

    basket_id = cart.get_first_basket_id()
    assert basket_id, "购物车为空，无法下单"
    basket_ids = [basket_id]
    print(f"\n使用 basketIds: {basket_ids}")

    # 2. 确认订单
    confirm = order.confirm_order(basket_ids=basket_ids, addr_id=ADDR_ID)
    assert confirm["code"] == "00000", f"确认订单失败: {confirm['msg']}"
    expected_total = confirm["data"]["total"]
    print(f"\n确认订单金额: {expected_total}")

    # 3. 提交订单
    submit = order.submit_order(shop_id=SHOP_ID, remarks="自动化测试下单")
    jsonschema.validate(submit, ORDER_SUBMIT_SCHEMA)
    assert submit["code"] == "00000", f"提交订单失败: {submit['msg']}"

    order_number = submit["data"]["orderNumbers"]
    print(f"\n生成的订单号: {order_number}")

    # 4. DB 双重断言
    db = DBHelper()
    row = db.query_one(
        "SELECT order_number, status, actual_total FROM tz_order WHERE order_number = %s",
        (order_number,)
    )
    assert row is not None, f"数据库找不到订单 {order_number}"
    assert row["order_number"] == order_number

    transfee = confirm["data"]["shopCartOrders"][0]["transfee"]
    expected_db_total = expected_total + transfee
    print(f"\n商品金额: {expected_total}, 运费: {transfee}, 预期实付: {expected_db_total}")
    print(f"DB 实付金额: {row['actual_total']}")
    assert abs(float(row["actual_total"]) - expected_db_total) < 0.01, \
        f"金额不一致：接口 total+运费={expected_db_total}，DB actual_total={row['actual_total']}"