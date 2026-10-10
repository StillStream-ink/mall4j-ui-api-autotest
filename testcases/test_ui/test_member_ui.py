# -*- coding: utf-8 -*-
"""Mall4j admin member UI tests"""
import allure
import pytest

from config.settings import ADMIN
from pages.admin.login_dialog_page import LoginDialogPage
from pages.admin.member_page import MemberPage


@pytest.fixture
def member_page(page):
    login = LoginDialogPage(page)
    login.login(ADMIN["username"], ADMIN["password"])
    login.verify_login_success()
    member = MemberPage(page)
    member.open()
    return member


@allure.feature("会员管理")
@pytest.mark.ui
@pytest.mark.smoke
class TestMember:

    @allure.title("打开会员列表")
    def test_open_member_list(self, member_page):
        rows = member_page.get_row_count()
        assert rows > 0, "member list should have data"
        headers = member_page.get_headers()
        assert "用户昵称" in headers
        assert "状态" in headers

    @allure.title("搜索 Leo")
    def test_search_leo(self, member_page):
        member_page.search("Leo")
        member_page.page.wait_for_timeout(1000)
        texts = member_page.get_row_texts()
        assert len(texts) >= 1
        assert any("Leo" in t for t in texts)

    @allure.title("搜索不存在的会员")
    def test_search_not_exist(self, member_page):
        member_page.search("不存在的会员_XYZ_12345")
        member_page.page.wait_for_timeout(1500)
        rows = member_page.get_row_count()
        assert rows == 0, f"expect 0 rows, got {rows}"

    @allure.title("清空搜索恢复列表")
    def test_clear_search(self, member_page):
        member_page.search("Leo")
        member_page.page.wait_for_timeout(1000)
        member_page.clear_search()
        member_page.page.wait_for_timeout(1000)
        rows = member_page.get_row_count()
        assert rows > 0

    @allure.title("点第一行编辑按钮")
    def test_click_edit(self, member_page):
        member_page.click_first_edit()
        member_page.page.wait_for_timeout(2000)
        # 先验证不报错，弹窗结构后面再探
        assert member_page.page.url