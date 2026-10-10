# -*- coding: utf-8 -*-
"""买家订单列表 + 详情 JSON Schema 契约"""

ORDER_LIST_ITEM_SCHEMA = {
    "type": "object",
    "required": ["orderNumber", "status", "actualTotal"],
    "properties": {
        "orderNumber": {"type": "string", "minLength": 10},
        "status": {"type": "integer"},
        "actualTotal": {"type": "number"},
        "total": {"type": ["number", "null"]},
        "createTime": {"type": ["string", "null"]},
        "prodName": {"type": ["string", "null"]}
    }
}

ORDER_LIST_SCHEMA = {
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
                "records": {"type": "array", "items": ORDER_LIST_ITEM_SCHEMA},
                "total": {"type": "integer"},
                "size": {"type": "integer"},
                "current": {"type": "integer"}
            }
        }
    }
}

# 注意：订单详情接口不返回 orderNumber，required 只校验 status 和 total
ORDER_DETAIL_SCHEMA = {
    "type": "object",
    "required": ["code", "success", "fail"],
    "properties": {
        "code": {"type": "string"},
        "success": {"type": "boolean"},
        "fail": {"type": "boolean"},
        "msg": {"type": ["string", "null"]},
        "data": {
            "type": ["object", "null"],
            "required": ["status", "total"],
            "properties": {
                "status": {"type": "integer"},
                "total": {"type": ["number", "null"]},
                "actualTotal": {"type": ["number", "null"]},
                "remarks": {"type": ["string", "null"]}
            }
        }
    }
}