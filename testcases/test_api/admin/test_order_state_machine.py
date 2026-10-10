# -*- coding: utf-8 -*-
"""订单状态机测试：接口 + DB 双重断言
发现缺陷：
- BUG-001: 发货接口缺少订单状态校验
  待付款/已完成/失败单/重复发货 都能成功发货
  详见 BUGS.md
"""
import allure
import pytest

from api.admin.order_api import OrderApi


STATUS_WAIT_PAY = 1
STATUS_WAIT_SEND = 2
STATUS_WAIT_RECV = 3
STATUS_WAIT_COMMENT = 4
STATUS_SUCCESS = 5
STATUS_FAIL = 6

ORDER_NUMBER = "1145634946149388288"       # 原始 status=5
ORDER_NUMBER_FAIL = "1146346112622399488"  # 原始 status=6

# 已知缺陷：发货接口缺少状态校验。开发修好后，去掉 xfail 标记即可
KNOWN_BUG = pytest.mark.xfail(
    reason="BUG-001: 发货接口缺少订单状态校验，详见 BUGS.md",
    strict=False,
)


@allure.feature("订单状态机")
@pytest.mark.api
class TestOrderStateMachine:

    @pytest.fixture
    def api(self, api_session):
        return OrderApi(api_session)

    @pytest.fixture
    def order_with_status(self, db):
        original_records = []

        def _set(order_number, status):
            row = db.query_one(
                "SELECT status, dvy_time, dvy_id, dvy_flow_id FROM tz_order WHERE order_number=%s",
                (order_number,),
            )
            assert row is not None, f"订单 {order_number} 不存在"
            original_records.append((order_number, dict(row)))
            db.execute(
                "UPDATE tz_order SET status=%s, dvy_time=NULL, dvy_id=NULL, dvy_flow_id=NULL WHERE order_number=%s",
                (status, order_number),
            )
            return order_number

        yield _set

        for order_number, row in original_records:
            db.execute(
                "UPDATE tz_order SET status=%s, dvy_time=%s, dvy_id=%s, dvy_flow_id=%s WHERE order_number=%s",
                (row["status"], row["dvy_time"], row["dvy_id"], row["dvy_flow_id"], order_number),
            )

    def _get_db_status(self, db, order_number):
        row = db.query_one("SELECT status FROM tz_order WHERE order_number=%s", (order_number,))
        return row["status"] if row else None

    # ==================== 正向：应通过 ====================
    @allure.title("待发货订单 → 发货成功 → DB status 变 3")
    def test_wait_send_delivery_success(self, api, db, valid_dvy, order_with_status):
        order_with_status(ORDER_NUMBER, STATUS_WAIT_SEND)
        assert self._get_db_status(db, ORDER_NUMBER) == STATUS_WAIT_SEND

        resp = api.delivery(
            order_number=ORDER_NUMBER,
            dvy_id=valid_dvy["dvyId"],
            dvy_flow_id="SF_AUTOTEST_0001",
        )
        body = resp.json()
        assert body["code"] == "00000", f"发货失败: {body}"

        row = db.query_one(
            "SELECT status, dvy_time, dvy_id, dvy_flow_id FROM tz_order WHERE order_number=%s",
            (ORDER_NUMBER,),
        )
        assert row["status"] == STATUS_WAIT_RECV
        assert row["dvy_time"] is not None
        assert row["dvy_id"] == valid_dvy["dvyId"]
        assert row["dvy_flow_id"] == "SF_AUTOTEST_0001"

    @allure.title("不存在的订单号 → 发货失败")
    def test_nonexist_order_delivery_fail(self, api, db, valid_dvy):
        resp = api.delivery("NOT_EXIST_99999999999", valid_dvy["dvyId"], "SF_AUTOTEST_0005")
        body = resp.json()
        assert body["code"] != "00000" or body.get("fail") is True

    # ==================== 反向：暴露 BUG ====================
    @KNOWN_BUG
    @allure.title("[BUG-001] 待付款订单 → 不应能发货")
    def test_wait_pay_delivery_fail(self, api, db, valid_dvy, order_with_status):
        order_with_status(ORDER_NUMBER, STATUS_WAIT_PAY)
        resp = api.delivery(ORDER_NUMBER, valid_dvy["dvyId"], "SF_AUTOTEST_0002")
        body = resp.json()
        assert body["code"] != "00000" or body.get("fail") is True, \
            f"待付款订单不应发货成功: {body}"

    @KNOWN_BUG
    @allure.title("[BUG-001] 已完成订单 → 不应能发货")
    def test_success_order_delivery_fail(self, api, db, valid_dvy, order_with_status):
        order_with_status(ORDER_NUMBER, STATUS_SUCCESS)
        resp = api.delivery(ORDER_NUMBER, valid_dvy["dvyId"], "SF_AUTOTEST_0003")
        body = resp.json()
        assert body["code"] != "00000" or body.get("fail") is True

    @KNOWN_BUG
    @allure.title("[BUG-001] 失败订单 → 不应能发货")
    def test_fail_order_delivery_fail(self, api, db, valid_dvy):
        resp = api.delivery(ORDER_NUMBER_FAIL, valid_dvy["dvyId"], "SF_AUTOTEST_0004")
        body = resp.json()
        assert body["code"] != "00000" or body.get("fail") is True

    @KNOWN_BUG
    @allure.title("[BUG-001] 重复发货 → 应被拒绝")
    def test_duplicate_delivery_fail(self, api, db, valid_dvy, order_with_status):
        order_with_status(ORDER_NUMBER, STATUS_WAIT_SEND)
        r1 = api.delivery(ORDER_NUMBER, valid_dvy["dvyId"], "SF_AUTOTEST_0006")
        assert r1.json()["code"] == "00000"

        r2 = api.delivery(ORDER_NUMBER, valid_dvy["dvyId"], "SF_AUTOTEST_0007")
        body = r2.json()
        assert body["code"] != "00000" or body.get("fail") is True, \
            "已发货订单不应重复发货"
      
        row = db.query_one(
            "SELECT status, dvy_flow_id FROM tz_order WHERE order_number=%s",
            (ORDER_NUMBER,),
        )
        assert row["status"] == STATUS_WAIT_RECV, \
            f"DB status 应保持 {STATUS_WAIT_RECV}，实际 {row['status']}"
        assert row["dvy_flow_id"] == "SF_AUTOTEST_0006", \
            f"dvy_flow_id 不应被第 2 次请求覆盖，实际 {row['dvy_flow_id']}"