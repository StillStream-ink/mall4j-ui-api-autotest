# -*- coding: utf-8 -*-
"""Batch3 pages: product sub-modules + system sub-modules"""
from pages.base_page import BasePage
class _Base(BasePage):
    TABLE_ROWS = ".el-table__row"
    TABLE_HEADERS = ".el-table__header th"
    SEARCH_BTN = "button:has-text('搜')"
    CLEAR_BTN = "button:has-text('清 空')"
    ADD_BTN = "button:has-text('新增')"

    def _open(self, path):
        from config.settings import WEB_URL
        self.goto(WEB_URL + path)
        self.page.wait_for_timeout(2500)

    def get_row_count(self):
        return self.page.locator(self.TABLE_ROWS).count()

    def get_headers(self):
        return [h.inner_text().strip() for h in self.page.locator(self.TABLE_HEADERS).all()]

    def search(self, locator, kw):
        self.fill(locator, kw)
        self.click(self.SEARCH_BTN)
        self.page.wait_for_timeout(1500)


class CategoryPage(_Base):
    PATH = "/prod/category"

    def open(self):
        self._open(self.PATH)


class ProdTagPage(_Base):
    PATH = "/prod/prodTag"
    INPUT = "input[placeholder*='标签名称']"

    def open(self):
        self._open(self.PATH)

    def search_tag(self, kw):
        self.search(self.INPUT, kw)


class ProdCommPage(_Base):
    PATH = "/prod/prodComm"
    INPUT = "input[placeholder*='商品名']"

    def open(self):
        self._open(self.PATH)

    def search_prod(self, kw):
        self.search(self.INPUT, kw)


class SpecPage(_Base):
    PATH = "/prod/spec"
    INPUT = "input[placeholder*='属性名称']"

    def open(self):
        self._open(self.PATH)

    def search_spec(self, kw):
        self.search(self.INPUT, kw)


class SysConfigPage(_Base):
    PATH = "/sys/config"
    INPUT = "input[placeholder*='参数名']"

    def open(self):
        self._open(self.PATH)

    def search_config(self, kw):
        self.search(self.INPUT, kw)


class AreaPage(_Base):
    PATH = "/sys/area"
    INPUT = "input[placeholder*='地区关键词']"

    def open(self):
        self._open(self.PATH)


class SysLogPage(_Base):
    PATH = "/sys/log"
    INPUT_USER = "input[placeholder*='用户名']"

    def open(self):
        self._open(self.PATH)

    def search_user(self, kw):
        self.search(self.INPUT_USER, kw)