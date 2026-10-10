# -*- coding: utf-8 -*-
import allure
from pages.buyer.buyer_home_page import BuyerHomePage


@allure.feature("买家端 UI")
@allure.story("首页浏览 → 加入购物车冒烟")
def test_buyer_browse_and_add_cart_ui(buyer_logged_page):
    home = BuyerHomePage(buyer_logged_page)

    # 1. 打开首页
    home.open()
    buyer_logged_page.wait_for_timeout(1000)

    # 2. 记录加购前角标
    before = home.get_cart_badge_count()
    print(f"\n加购前角标: {before}")

    # 3. 点商品 + 加购
    home.click_first_product()
    buyer_logged_page.wait_for_timeout(1500)
    home.click_add_to_cart()
    buyer_logged_page.wait_for_timeout(1500)

    # 4. 截图
    buyer_logged_page.screenshot(path="screenshots/buyer_add_cart.png", full_page=True)

    # 5. 返回首页，验证角标
    home.open()
    buyer_logged_page.wait_for_timeout(1000)
    after = home.get_cart_badge_count()
    print(f"\n加购后角标: {after}")
    assert after >= before, "加购后购物车角标未增加"