# -*- coding: utf-8 -*-
"""买家端首页 Page Object"""
from pages.base_page import BasePage
BASE_URL = "http://127.0.0.1"
class BuyerHomePage(BasePage):
    PRODUCT_CARD = ".prodimg img"
    ADD_TO_CART_BTN = "text=加入购物车"
    # ⚠️ 待确认：购物车角标的选择器，先用常见的 uni-badge
    CART_BADGE = ".uni-badge--error, .uni-badge"
    def open(self):
        self.goto(BASE_URL)
        self.wait_network_idle()
    def click_first_product(self):
        """点第一个商品，进入详情页"""
        self.click(self.PRODUCT_CARD)
        self.wait_network_idle()
    def click_add_to_cart(self):
        """点加入购物车"""
        self.click(self.ADD_TO_CART_BTN)
        self.wait_network_idle()
    def get_cart_badge_count(self) -> int:
        """底部购物车角标数字，找不到返回 0"""
        try:
            text = self.page.locator(".uni-badge").first.inner_text(timeout=2000)
            return int(text.strip()) if text.strip().isdigit() else 0
        except Exception:
            return 0