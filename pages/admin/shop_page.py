# -*- coding: utf-8 -*-
"""Shop management pages (5 sub-modules)"""
from pages.base_page import BasePage
from common.logger import get_logger

logger = get_logger(__name__)


class ShopBasePage(BasePage):
    TABLE_ROWS = ".el-table__row"
    TABLE_HEADERS = ".el-table__header th"
    SEARCH_BTN = "button:has-text('搜')"
    CLEAR_BTN = "button:has-text('清 空')"
    EDIT_BTN = "button:has-text('修改')"
    DELETE_BTN = "button:has-text('删除')"
    ADD_BTN = "button:has-text('新增')"

    def _open(self, path):
        from config.settings import WEB_URL
        logger.info(f"open: {WEB_URL + path}")
        self.goto(WEB_URL + path)
        self.page.wait_for_timeout(2000)

    def get_row_count(self):
        return self.page.locator(self.TABLE_ROWS).count()

    def get_headers(self):
        return [h.inner_text().strip() for h in self.page.locator(self.TABLE_HEADERS).all()]

    def search(self, input_locator, keyword):
        logger.info(f"search {keyword}")
        self.fill(input_locator, keyword)
        self.click(self.SEARCH_BTN)
        self.page.wait_for_timeout(1500)

    def clear_search(self):
        self.click(self.CLEAR_BTN)
        self.page.wait_for_timeout(1500)

    def click_first_edit(self):
        self.page.locator(self.EDIT_BTN).first.click()
        self.page.wait_for_timeout(1500)


class SelfPickupPage(ShopBasePage):
    PATH = "/shop/pickAddr"
    INPUT_KEYWORD = "input[placeholder*='自提点名称']"

    def open(self):
        self._open(self.PATH)

    def search_keyword(self, kw):
        self.search(self.INPUT_KEYWORD, kw)


class TransportPage(ShopBasePage):
    PATH = "/shop/transport"
    INPUT_KEYWORD = "input[placeholder*='模板名称']"

    def open(self):
        self._open(self.PATH)

    def search_keyword(self, kw):
        self.search(self.INPUT_KEYWORD, kw)


class CarouselPage(ShopBasePage):
    PATH = "/admin/indexImg"

    def open(self):
        self._open(self.PATH)


class HotSearchPage(ShopBasePage):
    PATH = "/shop/hotSearch"
    INPUT_KEYWORD = "input[placeholder*='热搜标题']"

    def open(self):
        self._open(self.PATH)

    def search_keyword(self, kw):
        self.search(self.INPUT_KEYWORD, kw)


class NoticePage(ShopBasePage):
    PATH = "/shop/notice"
    INPUT_KEYWORD = "input[placeholder*='公告内容']"

    def open(self):
        self._open(self.PATH)

    def search_keyword(self, kw):
        self.search(self.INPUT_KEYWORD, kw)