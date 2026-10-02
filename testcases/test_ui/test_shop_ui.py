# -*- coding: utf-8 -*-
"""Shop management UI tests (5 sub-modules)"""
import allure
import pytest

from config.settings import ADMIN
from pages.login_dialog_page import LoginDialogPage
from pages.shop_page import (
    SelfPickupPage, TransportPage, CarouselPage, HotSearchPage, NoticePage,
)


@pytest.fixture
def logged_page(page):
    login = LoginDialogPage(page)
    login.login(ADMIN["username"], ADMIN["password"])
    login.verify_login_success()
    return page


@allure.feature("门店管理-自提点")
@pytest.mark.ui
class TestSelfPickup:

    @allure.title("打开自提点列表")
    def test_open(self, logged_page):
        p = SelfPickupPage(logged_page)
        p.open()
        headers = p.get_headers()
        assert "自提点名称" in headers
        assert "操作" in headers

    @allure.title("搜索不存在 返回空")
    def test_search_not_exist(self, logged_page):
        p = SelfPickupPage(logged_page)
        p.open()
        p.search_keyword("不存在的自提点_XYZ")
        assert p.get_row_count() == 0


@allure.feature("门店管理-运费模板")
@pytest.mark.ui
class TestTransport:

    @allure.title("打开运费模板列表")
    def test_open(self, logged_page):
        p = TransportPage(logged_page)
        p.open()
        assert p.get_row_count() > 0
        assert "模板名称" in p.get_headers()

    @allure.title("搜索'包邮'")
    def test_search_baoyou(self, logged_page):
        p = TransportPage(logged_page)
        p.open()
        p.search_keyword("包邮")
        rows = p.page.locator(p.TABLE_ROWS).all()
        texts = [r.inner_text() for r in rows]
        assert any("包邮" in t for t in texts)

    @allure.title("搜索不存在 返回空")
    def test_search_not_exist(self, logged_page):
        p = TransportPage(logged_page)
        p.open()
        p.search_keyword("不存在XYZ123")
        assert p.get_row_count() == 0

    @allure.title("点第一行修改按钮")
    def test_click_edit(self, logged_page):
        p = TransportPage(logged_page)
        p.open()
        p.click_first_edit()
        assert logged_page.url


@allure.feature("门店管理-轮播图")
@pytest.mark.ui
class TestCarousel:

    @allure.title("打开轮播图列表")
    def test_open(self, logged_page):
        p = CarouselPage(logged_page)
        p.open()
        assert p.get_row_count() > 0
        headers = p.get_headers()
        assert "轮播图片" in headers
        assert "状态" in headers


@allure.feature("门店管理-热搜")
@pytest.mark.ui
class TestHotSearch:

    @allure.title("打开热搜列表")
    def test_open(self, logged_page):
        p = HotSearchPage(logged_page)
        p.open()
        headers = p.get_headers()
        assert "热搜标题" in headers

    @allure.title("搜索不存在 返回空")
    def test_search_not_exist(self, logged_page):
        p = HotSearchPage(logged_page)
        p.open()
        p.search_keyword("不存在XYZ")
        assert p.get_row_count() == 0


@allure.feature("门店管理-公告")
@pytest.mark.ui
class TestNotice:

    @allure.title("打开公告列表")
    def test_open(self, logged_page):
        p = NoticePage(logged_page)
        p.open()
        assert p.get_row_count() > 0
        assert "公告内容" in p.get_headers()

    @allure.title("搜索'包'")
    def test_search(self, logged_page):
        p = NoticePage(logged_page)
        p.open()
        p.search_keyword("包")
        assert p.get_row_count() >= 1

    @allure.title("搜索不存在 返回空")
    def test_search_not_exist(self, logged_page):
        p = NoticePage(logged_page)
        p.open()
        p.search_keyword("不存在XYZ123")
        assert p.get_row_count() == 0