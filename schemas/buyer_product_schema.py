# -*- coding: utf-8 -*-
"""买家商品接口 JSON Schema 契约"""

PROD_ITEM_SCHEMA = {
    "type": "object",
    "required": ["prodId", "prodName", "price"],
    "properties": {
        "prodId": {"type": "integer"},
        "prodName": {"type": "string", "minLength": 1},
        "price": {"type": "number"},
        "oriPrice": {"type": ["number", "null"]},
        "pic": {"type": ["string", "null"]},
        "brief": {"type": ["string", "null"]}
    }
}

PROD_LIST_SCHEMA = {
    "type": "object",
    "required": ["code", "success", "fail"],
    "properties": {
        "code": {"type": "string"},
        "success": {"type": "boolean"},
        "fail": {"type": "boolean"},
        "msg": {"type": ["string", "null"]},
        "data": {
            "type": ["array", "null"],
            "items": PROD_ITEM_SCHEMA
        }
    }
}

SEARCH_PAGE_SCHEMA = {
    "type": "object",
    "required": ["code", "success", "fail"],
    "properties": {
        "code": {"type": "string"},
        "success": {"type": "boolean"},
        "fail": {"type": "boolean"},
        "msg": {"type": ["string", "null"]},
        "data": {
            "type": ["object", "null"],
            "properties": {
                "records": {"type": "array", "items": PROD_ITEM_SCHEMA},
                "total": {"type": "integer"},
                "size": {"type": "integer"},
                "current": {"type": "integer"}
            }
        }
    }
}