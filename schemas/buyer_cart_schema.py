# -*- coding: utf-8 -*-
"""买家购物车接口 JSON Schema 契约"""

CART_ITEM_SCHEMA = {
    "type": "object",
    "required": ["basketId", "prodId", "skuId", "prodCount", "price"],
    "properties": {
        "basketId": {"type": "integer"},
        "prodId": {"type": "integer"},
        "skuId": {"type": "integer"},
        "prodCount": {"type": "integer", "minimum": 1},
        "price": {"type": "number", "minimum": 0},
        "prodName": {"type": "string"},
        "oriPrice": {"type": ["number", "null"]},
        "pic": {"type": ["string", "null"]}
    }
}

CART_GROUP_SCHEMA = {
    "type": "object",
    "required": ["shopId", "shopName", "shopCartItemDiscounts"],
    "properties": {
        "shopId": {"type": "integer"},
        "shopName": {"type": "string"},
        "shopCartItemDiscounts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "shopCartItems": {
                        "type": "array",
                        "items": CART_ITEM_SCHEMA
                    }
                }
            }
        }
    }
}

CART_INFO_SCHEMA = {
    "type": "object",
    "required": ["code", "success", "fail"],
    "properties": {
        "code": {"type": "string"},
        "success": {"type": "boolean"},
        "fail": {"type": "boolean"},
        "msg": {"type": ["string", "null"]},
        "data": {
            "type": ["array", "null"],
            "items": CART_GROUP_SCHEMA
        }
    }
}

COMMON_SUCCESS_SCHEMA = {
    "type": "object",
    "required": ["code", "success", "fail"],
    "properties": {
        "code": {"type": "string"},
        "success": {"type": "boolean"},
        "fail": {"type": "boolean"},
        "msg": {"type": ["string", "null"]}
    }
}