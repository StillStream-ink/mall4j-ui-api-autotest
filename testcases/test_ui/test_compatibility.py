# -*- coding: utf-8 -*-
"""兼容性测试：多浏览器 + 多分辨率
通过 BROWSER 环境变量切换引擎：
  $env:BROWSER="chromium"; pytest testcases/test_ui/test_compatibility.py -v
  $env:BROWSER="firefox";  pytest testcases/test_ui/test_compatibility.py -v
  $env:BROWSER="webkit";   pytest testcases/test_ui/test_compatibility.py -v
"""
import os
import allure
import pytest

from config.settings import ADMIN, BROWSER
from pages.login_dialog_page import LoginDialogPage

pytestmark = [
    pytest.mark.ui,
    pytest.mark.compatibility,
    pytest.mark.skipif(
        os.getenv("BROWSER", "chromium") == "webkit",
        reason="WebKit on Windows cannot access localhost",
    ),
]

@allure.feature(f"兼容性测试-{BROWSER}")
@pytest.mark.ui
class TestCompatibility:

    @allure.title(f"[{BROWSER}] 登录流程通过")
    def test_login_on_browser(self, page):
        """当前浏览器下登录成功"""
        login = LoginDialogPage(page)
        login.login(ADMIN["username"], ADMIN["password"])
        login.verify_login_success()

    @allure.title(f"[{BROWSER}] 登录页元素布局正确")
    def test_login_page_elements(self, page):
        """登录页关键元素可见 + 可点击"""
        login = LoginDialogPage(page)
        login.open_login_page()
        login.expect_visible(login.INPUT_USERNAME)
        login.expect_visible(login.INPUT_PASSWORD)
        login.expect_visible(login.LOGIN_BTN)

    @allure.title(f"[{BROWSER}] 1920×1080 分辨率登录")
    def test_viewport_1920x1080(self, page):
        page.set_viewport_size({"width": 1920, "height": 1080})
        login = LoginDialogPage(page)
        login.login(ADMIN["username"], ADMIN["password"])
        login.verify_login_success()

    @allure.title(f"[{BROWSER}] 1366×768 分辨率登录")
    def test_viewport_1366x768(self, page):
        page.set_viewport_size({"width": 1366, "height": 768})
        login = LoginDialogPage(page)
        login.login(ADMIN["username"], ADMIN["password"])
        login.verify_login_success()

    @allure.title(f"[{BROWSER}] 375×667 移动端分辨率登录")
    def test_viewport_375x667(self, page):
        page.set_viewport_size({"width": 375, "height": 667})
        login = LoginDialogPage(page)
        login.login(ADMIN["username"], ADMIN["password"])
        login.verify_login_success()