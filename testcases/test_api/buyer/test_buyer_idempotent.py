# -*- coding: utf-8 -*-
"""买家端下单幂等性测试"""
import allure
from api.buyer.buyer_cart import BuyerCart
from api.buyer.buyer_order import BuyerOrder
from common.db_helper import DBHelper

SKU_ID = 402
PROD_ID = 75
SHOP_ID = 1
ADDR_ID = 3

@allure.feature("买家端")
@allure.story("幂等性：同一订单重复提交")
def test_submit_order_idempotent(buyer_headers):
    """
    幂等性测试：
    1. 加购 → 确认订单 → 提交订单（第 1 次）
    2. 用同一购物车再提交一次（第 2 次）
    3. 验证：只能创建1个订单，第二次提交被拦截
    """
    cart = BuyerCart(buyer_headers)
    order = BuyerOrder(buyer_headers)
    db = DBHelper()
    # 先清空购物车
    cart.delete_all()
    # 记录下单前的订单数
    before = db.query_one(
        "SELECT COUNT(*) AS cnt FROM tz_order "
        "WHERE user_id = (SELECT user_id FROM tz_user WHERE user_mobile='13000000001')"
    )
    before_count = before["cnt"]
    print(f"\n下单前订单数: {before_count}")
    # 加购 + 确认
    cart.add_to_cart(sku_id=SKU_ID, prod_id=PROD_ID, count=1)
    basket_id = cart.get_first_basket_id()
    confirm = order.confirm_order(basket_ids=[basket_id], addr_id=ADDR_ID)
    assert confirm["code"] == "00000", "确认订单失败"
    # 第 1 次提交
    submit1 = order.submit_order(shop_id=SHOP_ID, remarks="自动化测试下单")
    print(f"\n第 1 次提交: code={submit1['code']}, msg={submit1.get('msg')}")
    order1 = submit1.get("data", {}).get("orderNumbers") if submit1.get("data") else None
    # 第 2 次提交（同一购物车，模拟重复点击）
    submit2 = order.submit_order(shop_id=SHOP_ID, remarks="自动化测试下单")
    print(f"第 2 次提交: code={submit2['code']}, msg={submit2.get('msg')}")
    order2 = submit2.get("data", {}).get("orderNumbers") if submit2.get("data") else None
    # 查下单后的订单数
    after = db.query_one(
        "SELECT COUNT(*) AS cnt FROM tz_order "
        "WHERE user_id = (SELECT user_id FROM tz_user WHERE user_mobile='13000000001')"
    )
    after_count = after["cnt"]
    print(f"\n下单后订单数: {after_count}")
    print(f"新增订单数: {after_count - before_count}")
    print(f"第 1 次订单号: {order1}")
    print(f"第 2 次订单号: {order2}")

    # ========== 替换成截图里的强断言（把原来if观察逻辑删掉 ==========
    # 核心断言: 幂等 — 重复提交只能创建 1 个订单
    new_orders = after_count - before_count
    assert new_orders == 1, \
        f"⚠️ 幂等性缺陷: 重复提交创建了 {new_orders} 个订单, 应该只有 1 个"

    # 断言第2次提交被拒
    assert submit2["code"] != "00000", \
        f"⚠️ 重复提交未被拦截, 返回 {submit2['code']}"
    assert "过期" in (submit2.get("msg") or ""), \
        f"重复提交错误提示不符合预期: {submit2.get('msg')}"

    print(f"\n✅ 幂等性验证通过: 重复提交被正确拦截, 只创建 1 个订单")
    # ================================================================

    # 恢复环境
    try:
        cart.delete_all()
    except Exception:
        pass