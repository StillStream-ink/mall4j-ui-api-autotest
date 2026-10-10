# -*- coding: utf-8 -*-
"""Batch2 UI: order + sys user/role/menu"""
import allure
import pytest

from config.settings import ADMIN
from pages.admin.login_dialog_page import LoginDialogPage
from pages.admin.order_page import OrderPage
from pages.admin.sys_user_page import SysUserPage
from pages.admin.sys_role_page import SysRolePage
from pages.admin.sys_menu_page import SysMenuPage


@pytest.fixture
def logged_page(page):
    login = LoginDialogPage(page)
    login.login(ADMIN["username"], ADMIN["password"])
    login.verify_login_success()
    return page


@allure.feature("订单管理")
@pytest.mark.ui
class TestOrder:

    @allure.title("打开订单管理页")
    def test_open(self, logged_page):
        p = OrderPage(logged_page)
        p.open()
        assert "/order/order" in logged_page.url

    @allure.title("搜索订单号")
    def test_search_order(self, logged_page):
        p = OrderPage(logged_page)
        p.open()
        p.search_order_no("114634")
        assert "/order/order" in logged_page.url

    @allure.title("分页显示总条数")
    def test_pagination(self, logged_page):
        p = OrderPage(logged_page)
        p.open()
        txt = p.get_pagination_text()
        assert "共" in txt or txt == ""

    @allure.title("清空搜索")
    def test_clear(self, logged_page):
        p = OrderPage(logged_page)
        p.open()
        p.search_order_no("114634")
        p.click(p.CLEAR_BTN)
        p.page.wait_for_timeout(1500)


@allure.feature("系统管理-管理员")
@pytest.mark.ui
class TestSysUser:

    @allure.title("打开管理员列表")
    def test_open(self, logged_page):
        p = SysUserPage(logged_page)
        p.open()
        assert p.get_row_count() >= 1
        headers = p.get_headers()
        assert "用户名" in headers

    @allure.title("搜索 admin")
    def test_search_admin(self, logged_page):
        p = SysUserPage(logged_page)
        p.open()
        p.search("admin")
        assert p.get_row_count() >= 1

    @allure.title("搜索不存在 返回空")
    def test_search_not_exist(self, logged_page):
        p = SysUserPage(logged_page)
        p.open()
        p.search("no_such_admin_xyz")
        assert p.get_row_count() == 0


@allure.feature("系统管理-角色")
@pytest.mark.ui
class TestSysRole:

    @allure.title("打开角色列表")
    def test_open(self, logged_page):
        p = SysRolePage(logged_page)
        p.open()
        assert p.get_row_count() >= 1
        headers = p.get_headers()
        assert "角色名称" in headers

    @allure.title("搜索不存在 返回空")
    def test_search_not_exist(self, logged_page):
        p = SysRolePage(logged_page)
        p.open()
        p.search("no_such_role_xyz")
        assert p.get_row_count() == 0


@allure.feature("系统管理-菜单")
@pytest.mark.ui
class TestSysMenu:

    @allure.title("打开菜单管理")
    def test_open(self, logged_page):
        p = SysMenuPage(logged_page)
        p.open()
        assert p.get_row_count() > 0
        headers = p.get_headers()
        assert "名称" in headers
        assert "类型" in headers

    @allure.title("菜单数据量大于 10")
    def test_menu_count(self, logged_page):
        p = SysMenuPage(logged_page)
        p.open()
        assert p.get_row_count() > 10