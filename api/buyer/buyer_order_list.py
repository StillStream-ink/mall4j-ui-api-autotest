# -*- coding: utf-8 -*-
"""买家端订单列表 + 详情封装"""
from typing import Any, Dict

import requests

BASE_URL: str = "http://127.0.0.1:8086"


class BuyerOrderList:
    def __init__(self, headers: Dict[str, str]) -> None:
        self.headers = headers

    def my_orders(
        self,
        status: int = 0,
        current: int = 1,
        size: int = 10,
    ) -> Dict[str, Any]:
        resp = requests.get(
            f"{BASE_URL}/p/myOrder/myOrder",
            headers=self.headers,
            params={"current": current, "size": size, "status": status},
            timeout=10,
        )
        return resp.json()

    def order_detail(self, order_number: str) -> Dict[str, Any]:
        resp = requests.get(
            f"{BASE_URL}/p/myOrder/orderDetail",
            headers=self.headers,
            params={"orderNumber": order_number},
            timeout=10,
        )
        return resp.json()