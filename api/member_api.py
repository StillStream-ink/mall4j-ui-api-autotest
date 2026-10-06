# -*- coding: utf-8 -*-
"""Mall4j admin member API wrapper"""
class MemberApi:
    def __init__(self, client):
        self.client = client

    def page(self, current=1, size=10, nick_name=None, status=None):
        params = {"current": current, "size": size}
        if nick_name:
            params["nickName"] = nick_name
        if status is not None:
            params["status"] = status
        return self.client.get("/admin/user/page", params=params)

    def info(self, user_id):
        return self.client.get(f"/admin/user/info/{user_id}")