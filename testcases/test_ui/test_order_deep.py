# -*- coding: utf-8 -*-
"""Order deep UI tests"""
import allure
import pytest

from config.settings import ADMIN
from pages.login_dialog_page import LoginDialogPage
from pages.order_detail_page import OrderDetailPage


@pytest.fixture
def order_page(page):
    login = LoginDialogPage(page)
    login.login(ADMIN["username"], ADMIN["password"])
    login.verify_login_success()
    p = OrderDetailPage(page)
    p.open()
    return p


@allure.feature("订单-深度")
@pytest.mark.ui
class TestOrderDeep:

    @allure.title("打开订单列表 有订单卡片")
    def test_list_has_cards(self, order_page):
        assert order_page.get_card_count() > 0, "订单列表应有卡片"

    @allure.title("搜索订单号 结果减少")
    def test_search_by_order_no(self, order_page):
        # 先记录总数
        total_before = order_page.get_card_count()
        # 取第一张卡片里的订单号
        card_text = order_page.page.locator(order_page.ORDER_CARD).first.inner_text()
        # 订单编号: xxxxx
        import re
        m = re.search(r"订单编号：(\d+)", card_text)
        assert m, f"未能从卡片中提取订单号: {card_text[:100]}"
        order_no = m.group(1)
        # 搜索
        order_page.search_order_no(order_no)
        after = order_page.get_card_count()
        assert after >= 1, "搜索订单号后应至少 1 条"
        # 再搜不存在的
        order_page.clear_search()
        order_page.search_order_no("NOT_EXIST_999999999999")
        assert order_page.get_card_count() == 0

    @allure.title("清空搜索恢复列表")
    def test_clear_search(self, order_page):
        # 先确认初始有数据
        assert order_page.get_card_count() > 0, "初始应有数据"
        # 搜不存在的订单号
        order_page.search_order_no("NOT_EXIST_99999999")
        assert order_page.get_card_count() == 0
        # 清空（内部会自动重载或重新查询）
        order_page.clear_search()
        # 允许等更长时间
        order_page.page.wait_for_timeout(1500)
        assert order_page.get_card_count() > 0, "清空后应恢复列表"

    @allure.title("点击查看 打开订单详情弹窗")
    def test_open_detail_dialog(self, order_page):
        order_page.click_first_view()
        assert order_page.is_detail_dialog_visible(), "详情弹窗应可见"

    @allure.title("详情弹窗显示订单编号")
    def test_detail_has_order_no(self, order_page):
        order_page.click_first_view()
        assert order_page.is_detail_dialog_visible()
        no = order_page.get_detail_order_no()
        assert no, f"详情应显示订单编号，实际: {no!r}"
        assert len(no) > 5

    @allure.title("详情弹窗有商品表格")
    def test_detail_has_items(self, order_page):
        order_page.click_first_view()
        rows = order_page.get_detail_item_rows()
        assert rows >= 1, "详情应有商品行"

    @allure.title("详情弹窗有订单日志区")
    def test_detail_has_log(self, order_page):
        order_page.click_first_view()
        # 订单日志标题
        log = order_page.page.locator(".el-dialog .order-log")
        assert log.count() > 0

    @allure.title("导出待发货订单按钮存在")
    def test_export_waiting_btn_exists(self, order_page):
        assert order_page.page.locator(order_page.EXPORT_WAITING_BTN).count() > 0

    @allure.title("导出销售记录按钮存在")
    def test_export_sold_btn_exists(self, order_page):
        assert order_page.page.locator(order_page.EXPORT_SOLD_BTN).count() > 0

    @allure.title("关闭详情弹窗")
    def test_close_detail(self, order_page):
        order_page.click_first_view()
        assert order_page.is_detail_dialog_visible()
        order_page.close_dialog()
        order_page.page.wait_for_timeout(1000)
        # 关闭后 el-dialog 应该是隐藏的（不是删除）
        visible = order_page.page.locator(order_page.DIALOG).first.is_visible()
        assert not visible, "弹窗关闭后不应可见"