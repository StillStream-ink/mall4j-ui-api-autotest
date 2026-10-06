# -*- coding: utf-8 -*-
"""Batch2 APIs: order + sys user/role/menu"""
class OrderApi:
    def __init__(self, client):
        self.client = client

    def page(self, current=1, size=10, order_number=None):
        params = {"current": current, "size": size}
        if order_number:
            params["orderNumber"] = order_number
        return self.client.get("/order/order/page", params=params)

    def info(self, order_number):
        return self.client.get(f"/order/order/orderInfo/{order_number}")


class SysUserApi:
    def __init__(self, client):
        self.client = client

    def page(self, current=1, size=10, username=None):
        params = {"current": current, "size": size}
        if username:
            params["username"] = username
        return self.client.get("/sys/user/page", params=params)

    def info(self):
        return self.client.get("/sys/user/info")


class SysRoleApi:
    def __init__(self, client):
        self.client = client

    def page(self, current=1, size=10):
        return self.client.get("/sys/role/page",
                               params={"current": current, "size": size})

    def list_all(self):
        return self.client.get("/sys/role/list")


class SysMenuApi:
    def __init__(self, client):
        self.client = client

    def table(self):
        return self.client.get("/sys/menu/table")

    def list_all(self):
        return self.client.get("/sys/menu/list")

    def nav(self):
        return self.client.get("/sys/menu/nav")