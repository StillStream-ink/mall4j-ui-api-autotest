# -*- coding: utf-8 -*-
"""
BasePage：所有页面对象的基类，封装公共操作
"""
from playwright.sync_api import Page, expect
from common.logger import get_logger

logger = get_logger(__name__)


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    # ---------- 导航 ----------
    def goto(self, url: str, wait_until: str = "domcontentloaded"):
        logger.info(f"打开页面: {url}")
        self.page.goto(url, wait_until=wait_until)

    # ---------- 点击（带重试） ----------
    def click(self, locator: str, retry: int = 2, timeout: int = 10000):
        last_err = None
        for i in range(retry + 1):
            try:
                self.page.locator(locator).first.click(timeout=timeout)
                return
            except Exception as e:
                last_err = e
                logger.warning(f"点击失败 [{i+1}/{retry+1}] locator={locator} err={e}")
        raise last_err

    # ---------- 输入 ----------
    def fill(self, locator: str, value: str, timeout: int = 10000):
        self.page.locator(locator).first.fill(value, timeout=timeout)

    # ---------- 等待 ----------
    def wait_visible(self, locator: str, timeout: int = 10000):
        self.page.locator(locator).first.wait_for(state="visible", timeout=timeout)

    def wait_hidden(self, locator: str, timeout: int = 10000):
        self.page.locator(locator).first.wait_for(state="hidden", timeout=timeout)

    def wait_network_idle(self, timeout: int = 15000):
        try:
            self.page.wait_for_load_state("networkidle", timeout=timeout)
        except Exception:
            pass

    # ---------- 文本 / 属性 ----------
    def text(self, locator: str) -> str:
        return self.page.locator(locator).first.inner_text()

    def is_visible(self, locator: str) -> bool:
        """检查元素是否可见

        只在"元素不存在 / 超时"时返回 False，
        其他异常（网络错误、浏览器崩溃）往上抛，避免掩盖真实问题。
        """
        try:
            return self.page.locator(locator).first.is_visible()
        except Exception as e:
            err_msg = str(e).lower()
            if "timeout" in err_msg or "not found" in err_msg or "no element" in err_msg:
                return False
            raise

    # ---------- 断言 ----------
    def expect_visible(self, locator: str, timeout: int = 10000):
        expect(self.page.locator(locator).first).to_be_visible(timeout=timeout)

    def expect_hidden(self, locator: str, timeout: int = 10000):
        expect(self.page.locator(locator).first).to_be_hidden(timeout=timeout)

    def expect_text_contains(self, locator: str, expected: str, timeout: int = 10000):
        expect(self.page.locator(locator).first).to_contain_text(expected, timeout=timeout)

    # ---------- 滚动 ----------
    def scroll_to_bottom(self):
        self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")