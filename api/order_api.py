# -*- coding: utf-8 -*-
"""Order API wrapper (deep tests)"""
from common.logger import get_logger

logger = get_logger(__name__)


class OrderApi:
    def __init__(self, client):
        self.client = client

    def page(self, current=1, size=10, order_number=None, status=None):
        params = {"current": current, "size": size}
        if order_number:
            params["orderNumber"] = order_number
        if status is not None:
            params["status"] = status
        return self.client.get("/order/order/page", params=params)

    def info(self, order_number):
        """订单详情"""
        return self.client.get(f"/order/order/orderInfo/{order_number}")

    def delivery(self, order_number, dvy_id, dvy_flow_id):
        """发货（PUT）—— 危险操作，测试时用假数据"""
        return self.client.put("/order/order/delivery", json={
            "orderNumber": order_number,
            "dvyId": dvy_id,
            "dvyFlowId": dvy_flow_id,
        })