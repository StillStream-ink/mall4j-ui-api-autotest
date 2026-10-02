# -*- coding: utf-8 -*-
"""Mall4j shop management APIs (5 sub-modules)"""
from common.logger import get_logger

logger = get_logger(__name__)


class ShopApi:
    def __init__(self, client):
        self.client = client

    # 自提点
    def pick_addr_page(self, current=1, size=10):
        return self.client.get("/shop/pickAddr/page",
                               params={"current": current, "size": size})

    # 运费模板
    def transport_page(self, current=1, size=10):
        return self.client.get("/shop/transport/page",
                               params={"current": current, "size": size})

    def transport_list(self):
        return self.client.get("/shop/transport/list")

    # 轮播图
    def carousel_page(self, current=1, size=10):
        return self.client.get("/admin/indexImg/page",
                               params={"current": current, "size": size})

    # 热搜
    def hot_search_page(self, current=1, size=10):
        return self.client.get("/admin/hotSearch/page",
                               params={"current": current, "size": size})

    # 公告
    def notice_page(self, current=1, size=10):
        return self.client.get("/shop/notice/page",
                               params={"current": current, "size": size})