# -*- coding: utf-8 -*-
"""CRUD APIs: sys config + sys role"""
from api.client import APIClient
from common.logger import get_logger

logger = get_logger(__name__)


class SysConfigCrudApi:
    """系统-参数管理 CRUD"""

    def __init__(self, client: APIClient):
        self.client = client

    def page(self, current: int = 1, size: int = 100, param_key: str = None):
        params = {"current": current, "size": size}
        if param_key:
            params["paramKey"] = param_key
        return self.client.get("/sys/config/page", params=params)

    def info(self, config_id: int):
        return self.client.get(f"/sys/config/info/{config_id}")

    def create(self, param_key: str, param_value: str, remark: str = ""):
        return self.client.post("/sys/config", json={
            "paramKey": param_key,
            "paramValue": param_value,
            "remark": remark,
        })

    def update(self, config_id: int, param_key: str, param_value: str, remark: str = ""):
        return self.client.put("/sys/config", json={
            "id": config_id,
            "paramKey": param_key,
            "paramValue": param_value,
            "remark": remark,
        })

    def delete(self, config_ids: list):
        return self.client.delete_json("/sys/config", config_ids)

    def find_by_key(self, param_key: str):
        body = self.page(param_key=param_key).json()
        records = body.get("data", {}).get("records", [])
        return records[0] if records else None


class SysRoleCrudApi:
    """系统-角色管理 CRUD"""

    def __init__(self, client: APIClient):
        self.client = client

    def page(self, current: int = 1, size: int = 100, role_name: str = None):
        params = {"current": current, "size": size}
        if role_name:
            params["roleName"] = role_name
        return self.client.get("/sys/role/page", params=params)

    def info(self, role_id: int):
        return self.client.get(f"/sys/role/info/{role_id}")

    def create(self, role_name: str, remark: str = "", menu_id_list: list = None):
        return self.client.post("/sys/role", json={
            "roleName": role_name,
            "remark": remark,
            "menuIdList": menu_id_list or [],
        })

    def update(self, role_id: int, role_name: str, remark: str = "", menu_id_list: list = None):
        return self.client.put("/sys/role", json={
            "roleId": role_id,
            "roleName": role_name,
            "remark": remark,
            "menuIdList": menu_id_list or [],
        })

    def delete(self, role_ids: list):
        return self.client.delete_json("/sys/role", role_ids)

    def find_by_name(self, role_name: str):
        body = self.page(role_name=role_name).json()
        records = body.get("data", {}).get("records", [])
        return records[0] if records else None