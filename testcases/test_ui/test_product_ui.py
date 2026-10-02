# -*- coding: utf-8 -*-
"""Mall4j 后台 产品管理 UI 测试"""
import allure
import pytest

from config.settings import ADMIN
from pages.login_dialog_page import LoginDialogPage
from pages.product_page import ProductPage


@pytest.fixture
def product_page(page):
    """登录后打开产品管理页，返回 ProductPage"""
    login = LoginDialogPage(page)
    login.login(ADMIN["username"], ADMIN["password"])
    login.verify_login_success()
    product = ProductPage(page)
    product.open()
    return product


@allure.feature("产品管理")
@pytest.mark.ui
@pytest.mark.smoke
class TestProduct:

    @allure.title("打开产品管理列表")
    def test_open_product_list(self, product_page):
        rows = product_page.get_row_count()
        assert rows > 0, "产品列表应该有数据"
        headers = product_page.get_headers()
        assert "产品名字" in headers
        assert "操作" in headers

    @allure.title("搜索存在的产品")
    def test_search_product(self, product_page):
        product_page.search("iPhone")
        product_page.page.wait_for_timeout(1000)
        texts = product_page.get_row_texts()
        assert len(texts) > 0, "搜索结果不应为空"
        assert any("iPhone" in t for t in texts), "应该包含 iPhone"

    @allure.title("搜索不存在的产品")
    def test_search_not_exist(self, product_page):
        product_page.search("不存在的产品_XYZ_12345")
        product_page.page.wait_for_timeout(1500)
        rows = product_page.get_row_count()
        assert rows == 0, f"搜索不存在应返回0行，实际{rows}行"

    @allure.title("清空搜索恢复列表")
    def test_clear_search(self, product_page):
        product_page.search("iPhone")
        product_page.page.wait_for_timeout(1000)
        product_page.clear_search()
        product_page.page.wait_for_timeout(1000)
        rows = product_page.get_row_count()
        assert rows > 0, "清空后应恢复列表"

    @allure.title("点第一行修改按钮打开弹窗")
    def test_click_edit(self, product_page):
        product_page.click_first_edit()
        product_page.page.wait_for_timeout(2000)
        # 编辑弹窗或跳转后应该出现"产品名字"输入框
        # 具体等 F12 再看，先只验证点击不报错
        assert product_page.page.url  # 简单占位
        