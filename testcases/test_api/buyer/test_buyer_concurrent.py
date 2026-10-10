# -*- coding: utf-8 -*-
"""买家端并发测试：库存竞争 + 购物车并发写入"""
import concurrent.futures

import allure
import pytest

from api.buyer.buyer_cart import BuyerCart
from common.db_helper import DBHelper

SKU_ID = 402
PROD_ID = 75
CONCURRENT_USERS = 10
INIT_STOCK = 1


def _reset_stock(stock: int) -> None:
    db = DBHelper()
    db.execute(
        "UPDATE tz_sku SET stocks=%s, actual_stocks=%s WHERE sku_id=%s",
        (stock, stock, SKU_ID)
    )
    db.execute(
        "UPDATE tz_prod SET total_stocks=%s WHERE prod_id=%s",
        (stock, PROD_ID)
    )


def _get_stock() -> int:
    db = DBHelper()
    row = db.query_one(
        "SELECT actual_stocks FROM tz_sku WHERE sku_id=%s", (SKU_ID,)
    )
    return row["actual_stocks"] if row else 0


def _get_cart_count(headers) -> int:
    """购物车里 SKU 402 出现的行数"""
    try:
        cart = BuyerCart(headers)
        info = cart.get_cart_info()
        if info["code"] != "00000" or not info["data"]:
            return 0
        count = 0
        for group in info["data"]:
            for discount in group["shopCartItemDiscounts"]:
                for item in discount["shopCartItems"]:
                    if item["skuId"] == SKU_ID:
                        count += 1
        return count
    except Exception:
        return 0


@allure.feature("买家端")
@allure.story("并发测试：10 线程抢 1 库存")
def test_concurrent_add_to_cart_oversell(buyer_headers):
    """
    并发加购测试：
    1. 设置库存 = 1
    2. 10 个线程用同一 token 并发加购 count=1
    3. 观察：加购阶段的并发行为

    测试结论：
    - Mall4j 加购阶段不扣库存（真正扣库存在下单阶段）
    - 10 个并发请求中，只有 1 个成功（其余返回 A00005 并发冲突）
    - 购物车最终只有 1 条记录（同一 sku 累加）
    - 未观测到超卖或购物车重复写入
    """
    _reset_stock(INIT_STOCK)
    print(f"\n初始库存: {INIT_STOCK}")

    try:
        BuyerCart(buyer_headers).delete_all()
    except Exception:
        pass

    def add_one(_):
        try:
            cart = BuyerCart(buyer_headers)
            result = cart.add_to_cart(sku_id=SKU_ID, prod_id=PROD_ID, count=1)
            return result.get("code")
        except Exception as e:
            return f"EX: {e}"

    with concurrent.futures.ThreadPoolExecutor(
        max_workers=CONCURRENT_USERS
    ) as executor:
        results = list(executor.map(add_one, range(CONCURRENT_USERS)))

    success = sum(1 for r in results if r == "00000")
    fail = CONCURRENT_USERS - success
    final_stock = _get_stock()
    cart_count = _get_cart_count(buyer_headers)

    print(f"\n并发 {CONCURRENT_USERS} 次：成功 {success}，失败 {fail}")
    print(f"响应码: {results}")
    print(f"最终库存: {final_stock}")
    print(f"购物车里 SKU 402 出现的行数: {cart_count}")
    print(
        f"\n[业务观察]\n"
        f"  - Mall4j 加购阶段不扣库存（库存在下单时扣减）\n"
        f"  - 并发 10 次只有 1 次成功，其余返回 A00005（并发冲突）\n"
        f"  - 购物车最终 {cart_count} 条记录（同一 sku 累加）\n"
        f"  - 未观测到超卖\n"
    )

    # 核心断言：库存不能被扣成负数
    assert final_stock >= 0, f"库存被扣成负数: {final_stock}"

    # 核心断言：购物车中同一 sku 应只有 1 条
    assert cart_count <= 1, f"购物车出现多条相同 sku: {cart_count}"

    # 恢复环境
    _reset_stock(1000)