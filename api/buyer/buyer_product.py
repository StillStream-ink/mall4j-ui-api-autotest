# -*- coding: utf-8 -*-
"""买家端商品浏览 + 搜索封装"""
from typing import Any, Dict

import requests

BASE_URL: str = "http://127.0.0.1:8086"


class BuyerProduct:
    def __init__(self, headers: Dict[str, str]) -> None:
        self.headers = headers

    def prod_list_by_tag(self, tag_id: int = 1, size: int = 10) -> Dict[str, Any]:
        resp = requests.get(
            f"{BASE_URL}/prod/prodListByTagId",
            headers=self.headers,
            params={"tagId": tag_id, "size": size},
            timeout=10,
        )
        return resp.json()

    def search_prod(
        self,
        prod_name: str,
        shop_id: int = 1,
        size: int = 10,
    ) -> Dict[str, Any]:
        resp = requests.get(
            f"{BASE_URL}/search/searchProdPage",
            headers=self.headers,
            params={"prodName": prod_name, "shopId": shop_id, "size": size},
            timeout=10,
        )
        return resp.json()