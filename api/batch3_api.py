# -*- coding: utf-8 -*-
"""Batch3 APIs"""
from common.logger import get_logger

logger = get_logger(__name__)


class CategoryApi:
    def __init__(self, client):
        self.client = client

    def table(self):
        return self.client.get("/prod/category/table")

    def list_category(self):
        return self.client.get("/prod/category/listCategory")


class ProdTagApi:
    def __init__(self, client):
        self.client = client

    def page(self, current=1, size=10, title=None):
        params = {"current": current, "size": size}
        if title:
            params["title"] = title
        return self.client.get("/prod/prodTag/page", params=params)

    def list_all(self):
        return self.client.get("/prod/prodTag/listTagList")


class ProdCommApi:
    def __init__(self, client):
        self.client = client

    def page(self, current=1, size=10):
        return self.client.get("/prod/prodComm/page",
                               params={"current": current, "size": size})


class SpecApi:
    def __init__(self, client):
        self.client = client

    def page(self, current=1, size=10):
        return self.client.get("/prod/spec/page",
                               params={"current": current, "size": size})

    def list_all(self):
        return self.client.get("/prod/spec/list")


class SysConfigApi:
    def __init__(self, client):
        self.client = client

    def page(self, current=1, size=10):
        return self.client.get("/sys/config/page",
                               params={"current": current, "size": size})


class AreaApi:
    def __init__(self, client):
        self.client = client

    def list_all(self):
        return self.client.get("/admin/area/list")

    def list_by_pid(self, pid=0):
        return self.client.get("/admin/area/listByPid", params={"pid": pid})


class SysLogApi:
    def __init__(self, client):
        self.client = client

    def page(self, current=1, size=10, username=None):
        params = {"current": current, "size": size}
        if username:
            params["username"] = username
        return self.client.get("/sys/log/page", params=params)