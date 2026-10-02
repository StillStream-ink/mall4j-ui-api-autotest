# -*- coding: utf-8 -*-
"""ProductPage: Mall4j 后台 产品管理 页面对象"""
from pages.base_page import BasePage
from common.logger import get_logger

logger = get_logger(__name__)


class ProductPage(BasePage):

    # 页面路径
    PATH = "/prod/prodList"

    # ---------- 搜索区 ----------
    INPUT_KEYWORD = "input[placeholder*='产品名字']"
    SEARCH_BTN = "button:has-text('搜')"
    CLEAR_BTN = "button:has-text('清 空')"

    # ---------- 操作按钮 ----------
    ADD_BTN = "button:has-text('新增')"
    EDIT_BTN = "button:has-text('修改')"
    DELETE_BTN = "button:has-text('删除')"
    BATCH_DELETE_BTN = "button:has-text('批量删除')"

    # ---------- 表格 ----------
    TABLE_ROWS = ".el-table__row"
    TABLE_HEADERS = ".el-table__header th"
    PAGINATION = ".el-pagination"
    EMPTY_TEXT = "text=暂无数据"

    # ---------- 行为 ----------
    def open(self):
        """打开产品管理列表页（需要先登录）"""
        from config.settings import WEB_URL
        url = WEB_URL + self.PATH
        logger.info(f"打开产品管理页: {url}")
        self.goto(url)
        self.wait_visible(self.TABLE_ROWS)

    def search(self, keyword: str):
        """输入关键词，点搜索"""
        logger.info(f"搜索关键词: {keyword}")
        self.fill(self.INPUT_KEYWORD, keyword)
        self.click(self.SEARCH_BTN)
        # 等表格刷新
        self.page.wait_for_timeout(1500)

    def clear_search(self):
        """清空搜索条件"""
        logger.info("清空搜索")
        self.click(self.CLEAR_BTN)
        self.page.wait_for_timeout(1500)

    # ---------- 断言/取值 ----------
    def get_row_count(self) -> int:
        return self.page.locator(self.TABLE_ROWS).count()

    def get_row_texts(self) -> list:
        """返回所有行的文本，方便断言包含某个关键词"""
        rows = self.page.locator(self.TABLE_ROWS).all()
        return [r.inner_text().strip() for r in rows]

    def get_headers(self) -> list:
        return [h.inner_text().strip() for h in self.page.locator(self.TABLE_HEADERS).all()]

    def click_first_edit(self):
        logger.info("点击第一行的 修改")
        self.page.locator(self.EDIT_BTN).first.click()

    def click_first_delete(self):
        logger.info("点击第一行的 删除")
        self.page.locator(self.DELETE_BTN).first.click()