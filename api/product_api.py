# -*- coding: utf-8 -*-
"""Mall4j admin product API wrapper"""
from common.logger import get_logger

logger = get_logger(__name__)


class ProductApi:
    def __init__(self, client):
        self.client = client

    def page(self, current=1, size=10, prod_name=None):
        params = {"current": current, "size": size}
        if prod_name:
            params["prodName"] = prod_name
        return self.client.get("/prod/prod/page", params=params)

    def info(self, prod_id):
        return self.client.get(f"/prod/prod/info/{prod_id}")