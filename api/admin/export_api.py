# -*- coding: utf-8 -*-
"""订单导出接口封装"""
import time
from typing import Any

from api.client import APIClient


class ExportApi:
    def __init__(self, client: APIClient) -> None:
        self.client = client

    def export_waiting_consignment(
        self,
        consignment_name: str = "",
        consignment_mobile: str = "",
        consignment_addr: str = "",
    ) -> Any:
        """导出待发货订单，返回 requests.Response（二进制流）"""
        ts = str(int(time.time() * 1000))
        params = {
            "t": ts,
            "consignmentName": consignment_name,
            "consignmentMobile": consignment_mobile,
            "consignmentAddr": consignment_addr,
        }
        return self.client.get("/order/order/waitingConsignmentExcel", params=params)

    def export_sold(self) -> Any:
        """导出销售记录，返回 requests.Response（二进制流）"""
        ts = str(int(time.time() * 1000))
        return self.client.get("/order/order/soldExcel", params={"t": ts})