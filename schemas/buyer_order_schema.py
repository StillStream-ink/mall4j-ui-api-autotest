# -*- coding: utf-8 -*-
"""买家订单接口 JSON Schema 契约"""

# 通用响应骨架
COMMON_RESPONSE = {
    "type": "object",
    "required": ["code", "success", "fail"],
    "properties": {
        "code": {"type": "string"},
        "success": {"type": "boolean"},
        "fail": {"type": "boolean"},
        "msg": {"type": ["string", "null"]}
    }
}

# 购物车列表响应
CART_INFO_SCHEMA = {
    **COMMON_RESPONSE,
    "properties": {
        **COMMON_RESPONSE["properties"],
        "data": {
            "type": ["array", "null"],
            "items": {
                "type": "object",
                "required": ["shopId", "shopName", "shopCartItemDiscounts"],
                "properties": {
                    "shopId": {"type": "integer"},
                    "shopName": {"type": "string"},
                    "shopCartItemDiscounts": {"type": "array"}
                }
            }
        }
    }
}

# 提交订单响应
ORDER_SUBMIT_SCHEMA = {
    **COMMON_RESPONSE,
    "properties": {
        **COMMON_RESPONSE["properties"],
        "data": {
            "type": ["object", "null"],
            "required": ["orderNumbers"],
            "properties": {
                "orderNumbers": {"type": "string", "minLength": 10}
            }
        }
    }
}