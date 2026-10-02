# -*- coding: utf-8 -*-
"""Order detail + delivery dialog"""
from pages.base_page import BasePage
from common.logger import get_logger

logger = get_logger(__name__)


class OrderDetailPage(BasePage):
    PATH = "/order/order"

    # 列表页
    INPUT_ORDER_NO = "input[placeholder='订单编号']"
    QUERY_BTN = "button:has-text('查询')"
    CLEAR_BTN = "button:has-text('清空')"
    EXPORT_WAITING_BTN = "button:has-text('导出待发货订单')"
    EXPORT_SOLD_BTN = "button:has-text('导出销售记录')"

    # 卡片
    ORDER_CARD = ".prod"
    VIEW_BTN = "button:has-text('查看')"

    # 详情弹窗
    DIALOG = ".el-dialog"
    DIALOG_TITLE = ".el-dialog__title"
    DETAIL_ORDER_NO = ".el-dialog .order-number .text"
    DETAIL_ITEM_TABLE = ".el-dialog .item-list .el-table__row"
    DELIVERY_BTN = ".el-dialog button:has-text('发货')"

    # 发货弹窗
    DEVY_DIALOG = ".el-dialog:has-text('选择发货地址')"
    DEVY_SELECT = ".el-dialog .el-select"
    DEVY_INPUT = ".el-dialog input:not([readonly])"
    DEVY_CONFIRM = ".el-dialog button:has-text('确定')"
    DEVY_CANCEL = ".el-dialog button:has-text('取消')"

    def open(self):
        from config.settings import WEB_URL
        self.goto(WEB_URL + self.PATH)
        self.page.wait_for_timeout(2500)

    def get_card_count(self):
        return self.page.locator(self.ORDER_CARD).count()

    def search_order_no(self, order_no):
        self.fill(self.INPUT_ORDER_NO, order_no)
        self.click(self.QUERY_BTN)
        self.page.wait_for_timeout(2000)

    def clear_search(self):
        self.click(self.CLEAR_BTN)
        self.page.wait_for_timeout(2000)
        # 如果清空后没数据，说明清空按钮只清了表单没重新加载，再点一次查询
        if self.get_card_count() == 0:
            self.click(self.QUERY_BTN)
            self.page.wait_for_timeout(2000)

    def click_first_view(self):
        logger.info("click first view button")
        self.page.locator(self.VIEW_BTN).first.click()
        self.page.wait_for_timeout(2500)

    def is_detail_dialog_visible(self):
        loc = self.page.locator(self.DIALOG)
        if loc.count() == 0:
            return False
        try:
            return loc.first.is_visible()
        except Exception:
            return False

    def get_detail_order_no(self):
        loc = self.page.locator(self.DETAIL_ORDER_NO)
        if loc.count() == 0:
            return ""
        return loc.first.inner_text().strip()

    def get_detail_item_rows(self):
        return self.page.locator(self.DETAIL_ITEM_TABLE).count()

    def has_delivery_button(self):
        return self.page.locator(self.DELIVERY_BTN).count() > 0

    def close_dialog(self):
        # 点 X 按钮
        x = self.page.locator(".el-dialog__headerbtn").first
        if x.count() > 0 or x.is_visible():
            x.click()
            self.page.wait_for_timeout(1000)