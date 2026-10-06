# -*- coding: utf-8 -*-
"""JSON Schema: Mall4j API contracts

用途：
- 校验接口返回结构是否符合契约
- 后端改字段名/类型时，Schema 校验会立即失败
"""

# 通用响应外壳（所有接口都套这一层）
BASE_RESPONSE = {
    "type": "object",
    "required": ["code", "success"],
    "properties": {
        "code": {"type": "string"},
        "success": {"type": "boolean"},
        "fail": {"type": ["boolean", "null"]},
        "msg": {"type": ["string", "null"]},
        "data": {"type": ["object", "null"]},   # object 或 null
    },
}

# 登录成功响应
LOGIN_SUCCESS_SCHEMA = {
    "type": "object",
    "required": ["code", "data", "success"],
    "properties": {
        "code": {"const": "00000"},
        "success": {"const": True},
        "data": {
            "type": "object",
            "required": ["accessToken", "expiresIn", "refreshToken"],
            "properties": {
                "accessToken": {"type": "string", "minLength": 10},
                "refreshToken": {"type": "string", "minLength": 10},
                "expiresIn": {"type": "integer", "minimum": 0},
            },
        },
    },
}

# 登录失败响应
LOGIN_FAIL_SCHEMA = {
    "type": "object",
    "required": ["code", "fail", "success", "msg"],
    "properties": {
        "code": {"type": "string"},
        "fail": {"const": True},
        "success": {"const": False},
        "msg": {"type": "string", "minLength": 1},
        "data": {"type": "null"},
    },
}

# 分页响应（适用于所有分页查询接口）
PAGE_SCHEMA = {
    "type": "object",
    "required": ["code", "data", "success"],
    "properties": {
        "code": {"const": "00000"},
        "success": {"const": True},
        "data": {
            "type": "object",
            "required": ["records", "total", "size", "current"],
            "properties": {
                "records": {"type": "array"},
                "total": {"type": "integer", "minimum": 0},
                "size": {"type": "integer", "minimum": 1},
                "current": {"type": "integer", "minimum": 1},
            },
        },
    },
}