# -*- coding: utf-8 -*-
"""Batch3 UI tests"""
import allure
import pytest

from config.settings import ADMIN
from pages.login_dialog_page import LoginDialogPage
from pages.batch3_page import (
    CategoryPage, ProdTagPage, ProdCommPage, SpecPage,
    SysConfigPage, AreaPage, SysLogPage,
)


@pytest.fixture
def logged_page(page):
    login = LoginDialogPage(page)
    login.login(ADMIN["username"], ADMIN["password"])
    login.verify_login_success()
    return page


@allure.feature("产品-分类管理")
@pytest.mark.ui
class TestCategory:

    @allure.title("打开分类管理 有数据")
    def test_open(self, logged_page):
        p = CategoryPage(logged_page)
        p.open()
        assert p.get_row_count() > 0
        headers = p.get_headers()
        assert "分类名称" in headers
        assert "操作" in headers


@allure.feature("产品-分组管理")
@pytest.mark.ui
class TestProdTag:

    @allure.title("打开分组管理 有数据")
    def test_open(self, logged_page):
        p = ProdTagPage(logged_page)
        p.open()
        assert p.get_row_count() > 0
        assert "标签名称" in p.get_headers()

    @allure.title("搜索标签名")
    def test_search(self, logged_page):
        p = ProdTagPage(logged_page)
        p.open()
        p.search_tag("测试")
        # 不强断言具体条数

    @allure.title("搜索不存在 返回空")
    def test_search_not_exist(self, logged_page):
        p = ProdTagPage(logged_page)
        p.open()
        p.search_tag("不存在XYZ123")
        assert p.get_row_count() == 0


@allure.feature("产品-评论管理")
@pytest.mark.ui
class TestProdComm:

    @allure.title("打开评论管理页")
    def test_open(self, logged_page):
        p = ProdCommPage(logged_page)
        p.open()
        headers = p.get_headers()
        assert "商品名" in headers
        assert "评价得分" in headers

    @allure.title("搜索不存在的商品评论")
    def test_search_not_exist(self, logged_page):
        p = ProdCommPage(logged_page)
        p.open()
        p.search_prod("不存在XYZ999")
        assert p.get_row_count() == 0


@allure.feature("产品-规格管理")
@pytest.mark.ui
class TestSpec:

    @allure.title("打开规格管理 有数据")
    def test_open(self, logged_page):
        p = SpecPage(logged_page)
        p.open()
        assert p.get_row_count() > 0
        assert "属性名称" in p.get_headers()

    @allure.title("搜索不存在 返回空")
    def test_search_not_exist(self, logged_page):
        p = SpecPage(logged_page)
        p.open()
        p.search_spec("不存在XYZ999")
        assert p.get_row_count() == 0


@allure.feature("系统-参数管理")
@pytest.mark.ui
class TestSysConfig:

    @allure.title("打开参数管理")
    def test_open(self, logged_page):
        p = SysConfigPage(logged_page)
        p.open()
        headers = p.get_headers()
        assert "参数名" in headers

    @allure.title("搜索不存在 返回空")
    def test_search_not_exist(self, logged_page):
        p = SysConfigPage(logged_page)
        p.open()
        p.search_config("不存在XYZ999")
        assert p.get_row_count() == 0


@allure.feature("系统-地址管理")
@pytest.mark.ui
class TestArea:

    @allure.title("打开地址管理页")
    def test_open(self, logged_page):
        p = AreaPage(logged_page)
        p.open()
        # 地址是树形，只验证 URL 和搜索框
        assert "/sys/area" in logged_page.url
        assert logged_page.locator(p.INPUT).count() > 0


@allure.feature("系统-系统日志")
@pytest.mark.ui
class TestSysLog:

    @allure.title("打开系统日志 有数据")
    def test_open(self, logged_page):
        p = SysLogPage(logged_page)
        p.open()
        assert p.get_row_count() > 0
        headers = p.get_headers()
        assert "用户名" in headers
        assert "请求方法" in headers

    @allure.title("搜索 admin")
    def test_search_admin(self, logged_page):
        p = SysLogPage(logged_page)
        p.open()
        p.search_user("admin")
        assert p.get_row_count() >= 1

    @allure.title("搜索不存在 返回空")
    def test_search_not_exist(self, logged_page):
        p = SysLogPage(logged_page)
        p.open()
        p.search_user("no_such_user_xyz999")
        assert p.get_row_count() == 0