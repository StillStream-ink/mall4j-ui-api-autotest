# -*- coding: utf-8 -*-
"""Sys menu page"""
from pages.base_page import BasePage
class SysMenuPage(BasePage):
    PATH = "/sys/menu"

    ADD_BTN = "button:has-text('新增')"
    EDIT_BTN = "button:has-text('修改')"
    DELETE_BTN = "button:has-text('删除')"

    TABLE_ROWS = ".el-table__row"
    TABLE_HEADERS = ".el-table__header th"

    def open(self):
        from config.settings import WEB_URL
        self.goto(WEB_URL + self.PATH)
        self.page.wait_for_timeout(2500)

    def get_row_count(self):
        return self.page.locator(self.TABLE_ROWS).count()

    def get_headers(self):
        return [h.inner_text().strip() for h in self.page.locator(self.TABLE_HEADERS).all()]