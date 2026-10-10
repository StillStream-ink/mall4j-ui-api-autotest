# -*- coding: utf-8 -*-
import allure
import jsonschema

from api.buyer.buyer_login import BuyerLogin
from api.buyer.buyer_cart import BuyerCart
from schemas.buyer_login_schema import BUYER_LOGIN_SCHEMA
from schemas.buyer_order_schema import CART_INFO_SCHEMA

def _clear_redis():
    """清空 Redis 缓存（仅开发测试环境用）"""
    try:
        import redis
        from config.settings import REDIS_HOST, REDIS_PORT
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
        r.flushdb()
        print("\n[Redis] 已清空缓存")
    except Exception as e:
        print(f"\n[Redis 清理失败] {e}")

@allure.feature("买家端")
@allure.story("买家登录")
def test_buyer_login():
    """登录接口：校验 token 返回 + Schema 契约"""
    buyer = BuyerLogin()
    token = buyer.login()
    assert token, "登录未返回 token"

    # 契约校验：再请求一次拿完整响应体
    import requests
    from common.crypto import encrypt_password
    resp = requests.post(
        f"{BuyerLogin.__module__ and 'http://127.0.0.1:8086'}/login",
        json={"userName": "13000000001", "passWord": encrypt_password("123456")}
    )
    jsonschema.validate(resp.json(), BUYER_LOGIN_SCHEMA)

def _total_prod_count(cart_info):
    """统计购物车里所有商品的总数量（累加 prodCount）"""
    total = 0
    if cart_info["data"]:
        for g in cart_info["data"]:
            for d in g["shopCartItemDiscounts"]:
                for item in d["shopCartItems"]:
                    total += item["prodCount"]
    return total

@allure.feature("买家端")
@allure.story("加入购物车")
def test_buyer_add_to_cart(buyer_headers):
    """加购：加购前记录总数量，加购后断言 +1"""
    cart = BuyerCart(buyer_headers)

    before_info = cart.get_cart_info()
    jsonschema.validate(before_info, CART_INFO_SCHEMA)
    before_count = _total_prod_count(before_info)

    # 加购（skuId=402 测试商品A）
    result = cart.add_to_cart(sku_id=402, prod_id=75, count=1)
    assert result["code"] == "00000", f"加购失败: {result['msg']}"

    after_info = cart.get_cart_info()
    after_count = _total_prod_count(after_info)

    print(f"\n加购前总数 {before_count} 件，加购后总数 {after_count} 件")
    assert after_count == before_count + 1, "加购后总数量未 +1"


@allure.feature("买家端")
@allure.story("购物车列表契约")
def test_buyer_cart_info_contract(buyer_headers):
    """购物车列表：JSON Schema 契约校验"""
    cart = BuyerCart(buyer_headers)
    info = cart.get_cart_info()
    jsonschema.validate(info, CART_INFO_SCHEMA)