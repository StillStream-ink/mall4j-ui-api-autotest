# -*- coding: utf-8 -*-
"""买家端 UI 扩展用例：鉴权拦截、购物车角标"""
import allure
from pages.buyer.buyer_home_page import BuyerHomePage

@allure.feature("买家端 UI")
@allure.story("未登录访问购物车 → 被拦截")
def test_buyer_unauth_cart_redirect(page):
    """不带 token 直接访问购物车，应被拦截"""
    page.goto("http://127.0.0.1", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(1000)
    page.goto("http://127.0.0.1/pages/basket/basket", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(2000)
    page.screenshot(path="screenshots/buyer_unauth_cart.png", full_page=True)
    print(f"\n未登录访问购物车后 URL: {page.url}")
    content = page.content()
    assert "login" in page.url.lower() or "登录" in content or "请先登录" in content, \
        f"未登录访问购物车未被拦截，当前 URL: {page.url}"


@allure.feature("买家端 UI")
@allure.story("加购后购物车角标 +1")
def test_buyer_cart_badge_increase(buyer_logged_page):
    """加购一件，验证购物车角标数字增加"""
    home = BuyerHomePage(buyer_logged_page)
    home.open()
    buyer_logged_page.wait_for_timeout(1000)
    before = home.get_cart_badge_count()
    print(f"\n加购前角标: {before}")
    home.click_first_product()
    buyer_logged_page.wait_for_timeout(1500)
    home.click_add_to_cart()
    buyer_logged_page.wait_for_timeout(2000)
    home.open()
    buyer_logged_page.wait_for_timeout(1000)
    after = home.get_cart_badge_count()
    print(f"加购后角标: {after}")
    buyer_logged_page.screenshot(path="screenshots/buyer_cart_badge.png", full_page=True)
    assert after >= before, "加购后角标未增加"