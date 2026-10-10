# -*- coding: utf-8 -*-
"""买家端订单封装"""
from typing import Any, Dict, List

import requests

BASE_URL: str = "http://127.0.0.1:8086"


class BuyerOrder:
    def __init__(self, headers: Dict[str, str]) -> None:
        self.headers = headers

    def confirm_order(
        self,
        basket_ids: List[int],
        addr_id: int,
    ) -> Dict[str, Any]:
        resp = requests.post(
            f"{BASE_URL}/p/order/confirm",
            headers=self.headers,
            json={
                "addrId": addr_id,
                "basketIds": basket_ids,
                "couponIds": [],
                "userChangeCoupon": 1,
            },
            timeout=10,
        )
        return resp.json()

    def submit_order(
        self,
        shop_id: int = 1,
        remarks: str = "",
    ) -> Dict[str, Any]:
        resp = requests.post(
            f"{BASE_URL}/p/order/submit",
            headers=self.headers,
            json={"orderShopParam": [{"remarks": remarks, "shopId": shop_id}]},
            timeout=10,
        )
        return resp.json()