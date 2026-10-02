# -*- coding: utf-8 -*-
"""LoginPage: Mall4j 后台管理系统登录页（本地环境）"""
from pages.base_page import BasePage
from common.logger import get_logger

logger = get_logger(__name__)


class LoginDialogPage(BasePage):
    """本地 Mall4j 后台登录页

    登录页地址：http://localhost:9527/
    登录后跳转：/home
    无验证码（已改前端 + 后端跳过校验）
    """

    # ---------- 登录页元素 ----------
    # 用户名输入框（Element Plus，placeholder="账号"）
    INPUT_USERNAME = ".login .el-input input"
    # 密码输入框
    INPUT_PASSWORD = "input[type='password']"
    # 登录按钮（原生 input）
    LOGIN_BTN = ".item-btn input[type='button']"

    # ---------- 登录成功后标志 ----------
    # 登录后跳到 /home，右上角显示 admin
    HOME_FLAG = "text=admin"

    # ---------- 错误提示 ----------
    TOAST_ERROR = ".el-message--error, .el-message"

    # ---------- 行为 ----------
    def open_login_page(self):
        """打开登录页"""
        from config.settings import WEB_URL
        logger.info(f"打开登录页: {WEB_URL}")
        self.goto(WEB_URL)
        self.wait_visible(self.INPUT_USERNAME)

    def fill_credentials(self, username: str, password: str):
        """填写账号密码"""
        logger.info(f"填写账号: {username}")
        self.fill(self.INPUT_USERNAME, username)
        self.fill(self.INPUT_PASSWORD, password)

    def click_login(self):
        """点击登录按钮"""
        logger.info("点击登录按钮")
        self.click(self.LOGIN_BTN)

    def login(self, username: str, password: str):
        """完整登录：打开页面 → 填账号密码 → 点登录"""
        self.open_login_page()
        self.fill_credentials(username, password)
        self.click_login()

    # ---------- 断言 ----------
    def verify_login_success(self, timeout: int = 10000):
        """登录成功：URL 变成 /home，或者页面出现 admin"""
        logger.info("校验登录成功")
        self.page.wait_for_url("**/home", timeout=timeout)

    def verify_login_failed(self, timeout: int = 8000):
        """登录失败：出现错误提示"""
        self.expect_visible(self.TOAST_ERROR, timeout=timeout)

    def verify_still_on_login(self, timeout: int = 3000):
        """校验仍停留在登录页"""
        self.expect_visible(self.INPUT_USERNAME, timeout=timeout)