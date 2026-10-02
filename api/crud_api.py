# -*- coding: utf-8 -*-
"""CRUD APIs: sys config + sys role"""
from common.logger import get_logger

logger = get_logger(__name__)


class SysConfigCrudApi:
    """系统-参数管理 CRUD"""
    def __init__(self, client):
        self.client = client

    def page(self, current=1, size=100, param_key=None):
        params = {"current": current, "size": size}
        if param_key:
            params["paramKey"] = param_key
        return self.client.get("/sys/config/page", params=params)

    def info(self, config_id):
        return self.client.get(f"/sys/config/info/{config_id}")

    def create(self, param_key, param_value, remark=""):
        return self.client.post("/sys/config", json={
            "paramKey": param_key,
            "paramValue": param_value,
            "remark": remark,
        })

    def update(self, config_id, param_key, param_value, remark=""):
        return self.client.put("/sys/config", json={
            "id": config_id,
            "paramKey": param_key,
            "paramValue": param_value,
            "remark": remark,
        })

    def delete(self, config_ids):
        """DELETE 用 JSON body（后端设计如此）"""
        return self.client.session.request(
            "DELETE",
            f"{self.client.base_url}/sys/config",
            json=config_ids,
            timeout=self.client.timeout,
        )

    def find_by_key(self, param_key):
        body = self.page(param_key=param_key).json()
        records = body.get("data", {}).get("records", [])
        return records[0] if records else None


class SysRoleCrudApi:
    """系统-角色管理 CRUD"""
    def __init__(self, client):
        self.client = client

    def page(self, current=1, size=100, role_name=None):
        params = {"current": current, "size": size}
        if role_name:
            params["roleName"] = role_name
        return self.client.get("/sys/role/page", params=params)

    def info(self, role_id):
        return self.client.get(f"/sys/role/info/{role_id}")

    def create(self, role_name, remark="", menu_id_list=None):
        return self.client.post("/sys/role", json={
            "roleName": role_name,
            "remark": remark,
            "menuIdList": menu_id_list or [],
        })

    def update(self, role_id, role_name, remark="", menu_id_list=None):
        return self.client.put("/sys/role", json={
            "roleId": role_id,
            "roleName": role_name,
            "remark": remark,
            "menuIdList": menu_id_list or [],
        })

    def delete(self, role_ids):
        return self.client.session.request(
            "DELETE",
            f"{self.client.base_url}/sys/role",
            json=role_ids,
            timeout=self.client.timeout,
        )

    def find_by_name(self, role_name):
        body = self.page(role_name=role_name).json()
        records = body.get("data", {}).get("records", [])
        return records[0] if records else None