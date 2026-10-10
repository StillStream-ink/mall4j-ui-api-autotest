# -*- coding: utf-8 -*-
"""Mall4j 后台登录 UI 测试"""
import allure
import pytest

from config.settings import WEB_URL, ADMIN
from pages.admin.login_dialog_page import LoginDialogPage


@allure.feature("后台登录")
@pytest.mark.ui
@pytest.mark.smoke
class TestAdminLogin:

    @allure.title("打开后台登录页")
    def test_open_login_page(self, page):
        login = LoginDialogPage(page)
        login.open_login_page()
        login.expect_visible(login.INPUT_USERNAME)
        login.expect_visible(login.INPUT_PASSWORD)
        login.expect_visible(login.LOGIN_BTN)

    @allure.title("正确账号密码登录成功")
    def test_login_success(self, page):
        login = LoginDialogPage(page)
        login.login(ADMIN["username"], ADMIN["password"])
        login.verify_login_success()

    @allure.title("错误密码登录失败")
    def test_login_wrong_password(self, page):
        login = LoginDialogPage(page)
        login.login(ADMIN["username"], "wrong_password_xyz")
        login.verify_login_failed()

    @allure.title("空用户名登录失败")
    def test_login_empty_username(self, page):
        login = LoginDialogPage(page)
        login.login("", ADMIN["password"])
        login.verify_still_on_login()

    @allure.title("空密码登录失败")
    def test_login_empty_password(self, page):
        login = LoginDialogPage(page)
        login.login(ADMIN["username"], "")
        login.verify_still_on_login()