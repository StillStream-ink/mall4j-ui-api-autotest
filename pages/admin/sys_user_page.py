# -*- coding: utf-8 -*-
"""Sys user (admin) page"""
from pages.base_page import BasePage
class SysUserPage(BasePage):
    PATH = "/sys/user"

    INPUT_KEYWORD = "input[placeholder*='用户名']"
    SEARCH_BTN = "button:has-text('搜')"
    CLEAR_BTN = "button:has-text('清 空')"
    ADD_BTN = "button:has-text('新增')"
    EDIT_BTN = "button:has-text('编辑')"
    DELETE_BTN = "button:has-text('删除')"

    TABLE_ROWS = ".el-table__row"
    TABLE_HEADERS = ".el-table__header th"

    def open(self):
        from config.settings import WEB_URL
        self.goto(WEB_URL + self.PATH)
        self.page.wait_for_timeout(2000)

    def search(self, kw):
        self.fill(self.INPUT_KEYWORD, kw)
        self.click(self.SEARCH_BTN)
        self.page.wait_for_timeout(1500)

    def get_row_count(self):
        return self.page.locator(self.TABLE_ROWS).count()

    def get_headers(self):
        return [h.inner_text().strip() for h in self.page.locator(self.TABLE_HEADERS).all()]

    def click_first_edit(self):
        self.page.locator(self.EDIT_BTN).first.click()
        self.page.wait_for_timeout(1500)