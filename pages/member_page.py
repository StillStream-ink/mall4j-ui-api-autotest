# -*- coding: utf-8 -*-
"""MemberPage: Mall4j admin member list page"""
from pages.base_page import BasePage
from common.logger import get_logger

logger = get_logger(__name__)


class MemberPage(BasePage):

    PATH = "/user/user"

    INPUT_KEYWORD = "input[placeholder*='用户昵称']"
    SEARCH_BTN = "button:has-text('搜')"
    CLEAR_BTN = "button:has-text('清 空')"
    EDIT_BTN = "button:has-text('编辑')"

    TABLE_ROWS = ".el-table__row"
    TABLE_HEADERS = ".el-table__header th"

    def open(self):
        from config.settings import WEB_URL
        url = WEB_URL + self.PATH
        logger.info(f"Open member page: {url}")
        self.goto(url)
        self.wait_visible(self.TABLE_ROWS)

    def search(self, keyword: str):
        logger.info(f"Search member: {keyword}")
        self.fill(self.INPUT_KEYWORD, keyword)
        self.click(self.SEARCH_BTN)
        self.page.wait_for_timeout(1500)

    def clear_search(self):
        logger.info("Clear search")
        self.click(self.CLEAR_BTN)
        self.page.wait_for_timeout(1500)

    def get_row_count(self) -> int:
        return self.page.locator(self.TABLE_ROWS).count()

    def get_row_texts(self):
        return [r.inner_text().strip() for r in self.page.locator(self.TABLE_ROWS).all()]

    def get_headers(self):
        return [h.inner_text().strip() for h in self.page.locator(self.TABLE_HEADERS).all()]

    def click_first_edit(self):
        logger.info("Click first row edit")
        self.page.locator(self.EDIT_BTN).first.click()