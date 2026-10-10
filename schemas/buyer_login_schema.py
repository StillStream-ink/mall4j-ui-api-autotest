# -*- coding: utf-8 -*-
"""买家登录接口 JSON Schema 契约"""

BUYER_LOGIN_SCHEMA = {
    "type": "object",
    "required": ["code", "success", "fail"],
    "properties": {
        "code": {"type": "string"},
        "success": {"type": "boolean"},
        "fail": {"type": "boolean"},
        "msg": {"type": ["string", "null"]},
        "data": {
            "type": ["object", "null"],
            "required": ["accessToken", "expiresIn", "refreshToken"],
            "properties": {
                "accessToken": {"type": "string", "minLength": 10},
                "expiresIn": {"type": "integer"},
                "refreshToken": {"type": "string", "minLength": 10}
            }
        }
    }
}