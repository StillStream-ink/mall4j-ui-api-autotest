# -*- coding: utf-8 -*-
"""C. 订单状态流转 - DB 全字段一致性"""
import allure
import pytest

from api.admin.order_api import OrderApi


ORDER_NUMBER = "1145634946149388288"


@allure.feature("数据一致性-订单状态流转")
@pytest.mark.api
class TestOrderStateFullDb:

    @pytest.fixture
    def api(self, api_session):
        return OrderApi(api_session)

    @pytest.fixture
    def restore_order(self, db):
        original = db.query_one(
            "SELECT status, dvy_time, dvy_id, dvy_flow_id FROM tz_order WHERE order_number=%s",
            (ORDER_NUMBER,),
        )
        yield
        db.execute(
            "UPDATE tz_order SET status=%s, dvy_time=%s, dvy_id=%s, dvy_flow_id=%s WHERE order_number=%s",
            (
                original["status"], original["dvy_time"],
                original["dvy_id"], original["dvy_flow_id"],
                ORDER_NUMBER,
            ),
        )

    @allure.title("[订单DB一致] 发货后所有相关字段同步更新")
    def test_delivery_all_fields_updated(self, api, db, valid_dvy, restore_order):
        db.execute(
            "UPDATE tz_order SET status=2, dvy_time=NULL, dvy_id=NULL, dvy_flow_id=NULL WHERE order_number=%s",
            (ORDER_NUMBER,),
        )

        flow_id = "SF_CONSISTENCY_001"
        resp = api.delivery(ORDER_NUMBER, valid_dvy["dvyId"], flow_id)
        assert resp.json()["code"] == "00000"

        row = db.query_one(
            "SELECT status, dvy_time, dvy_id, dvy_flow_id FROM tz_order WHERE order_number=%s",
            (ORDER_NUMBER,),
        )
        assert row["status"] == 3, f"status 应为 3，实际 {row['status']}"
        assert row["dvy_time"] is not None, "dvy_time 应非空"
        assert row["dvy_id"] == valid_dvy["dvyId"]
        assert row["dvy_flow_id"] == flow_id

    @allure.title("[订单DB一致] 订单与订单项关联一致")
    def test_order_item_consistency(self, db):
        order = db.query_one(
            "SELECT order_id FROM tz_order WHERE order_number=%s",
            (ORDER_NUMBER,),
        )
        assert order is not None

        items = db.query_all(
            "SELECT * FROM tz_order_item WHERE order_number=%s",
            (ORDER_NUMBER,),
        )
        assert len(items) > 0, f"订单 {ORDER_NUMBER} 应有订单项"

    @allure.title("[订单DB一致] 发货不改变订单金额")
    def test_delivery_does_not_change_amount(self, api, db, valid_dvy, restore_order):
        before = db.query_one(
            "SELECT actual_total, total FROM tz_order WHERE order_number=%s",
            (ORDER_NUMBER,),
        )
        db.execute(
            "UPDATE tz_order SET status=2 WHERE order_number=%s",
            (ORDER_NUMBER,),
        )
        api.delivery(ORDER_NUMBER, valid_dvy["dvyId"], "SF_AMOUNT_001")

        after = db.query_one(
            "SELECT actual_total, total FROM tz_order WHERE order_number=%s",
            (ORDER_NUMBER,),
        )
        assert before["actual_total"] == after["actual_total"]
        assert before["total"] == after["total"]
