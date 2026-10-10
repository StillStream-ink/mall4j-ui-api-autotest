# -*- coding: utf-8 -*-
"""Order page"""
from pages.base_page import BasePage
from common.logger import get_logger

logger = get_logger(__name__)


class OrderPage(BasePage):
    PATH = "/order/order"

    INPUT_ORDER_NO = "input[placeholder='订单编号']"
    QUERY_BTN = "button:has-text('查询')"
    CLEAR_BTN = "button:has-text('清空')"
    VIEW_BTN = "button:has-text('查看')"
    PAGINATION = ".el-pagination"

    def open(self):
        from config.settings import WEB_URL
        self.goto(WEB_URL + self.PATH)
        self.page.wait_for_timeout(2500)

    def search_order_no(self, order_no):
        logger.info(f"search order {order_no}")
        self.fill(self.INPUT_ORDER_NO, order_no)
        self.click(self.QUERY_BTN)
        self.page.wait_for_timeout(2000)

    def get_pagination_text(self):
        if self.page.locator(self.PAGINATION).count() == 0:
            return ""
        return self.page.locator(self.PAGINATION).first.inner_text().replace("\n", " ")

    def get_view_button_count(self):
        return self.page.locator(self.VIEW_BTN).count()