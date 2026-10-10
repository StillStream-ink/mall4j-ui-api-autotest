# -*- coding: utf-8 -*-
"""买家端购物车封装"""
from typing import Any, Dict, List

import requests

BASE_URL: str = "http://127.0.0.1:8086"


class BuyerCart:
    def __init__(self, headers: Dict[str, str]) -> None:
        self.headers = headers

    def add_to_cart(
        self,
        sku_id: int,
        prod_id: int,
        shop_id: int = 1,
        count: int = 1,
    ) -> Dict[str, Any]:
        resp = requests.post(
            f"{BASE_URL}/p/shopCart/changeItem",
            headers=self.headers,
            json={
                "shopId": shop_id,
                "prodId": prod_id,
                "skuId": sku_id,
                "count": count,
            },
            timeout=10,
        )
        return resp.json()

    def get_cart_info(self) -> Dict[str, Any]:
        resp = requests.post(
            f"{BASE_URL}/p/shopCart/info",
            headers=self.headers,
            json={},
            timeout=10,
        )
        return resp.json()

    def get_prod_count(self) -> Dict[str, Any]:
        resp = requests.post(
            f"{BASE_URL}/p/shopCart/prodCount",
            headers=self.headers,
            json={},
            timeout=10,
        )
        return resp.json()

    def get_first_basket_id(self) -> int | None:
        info = self.get_cart_info()
        if info["code"] != "00000" or not info["data"]:
            return None
        items = info["data"][0]["shopCartItemDiscounts"][0]["shopCartItems"]
        return items[0]["basketId"] if items else None

    def update_count(
        self,
        sku_id: int,
        prod_id: int,
        count: int,
        shop_id: int = 1,
    ) -> Dict[str, Any]:
        resp = requests.post(
            f"{BASE_URL}/p/shopCart/changeItem",
            headers=self.headers,
            json={
                "shopId": shop_id,
                "prodId": prod_id,
                "skuId": sku_id,
                "count": count,
            },
            timeout=10,
        )
        return resp.json()

    def delete_item(self, basket_ids: List[int]) -> Dict[str, Any]:
        resp = requests.delete(
            f"{BASE_URL}/p/shopCart/deleteItem",
            headers=self.headers,
            json=basket_ids,
            timeout=10,
        )
        return resp.json()

    def delete_all(self) -> None:
        info = self.get_cart_info()
        if info["code"] != "00000" or not info["data"]:
            return
        basket_ids: List[int] = []
        for group in info["data"]:
            for discount in group["shopCartItemDiscounts"]:
                for item in discount["shopCartItems"]:
                    basket_ids.append(item["basketId"])
        if basket_ids:
            self.delete_item(basket_ids)