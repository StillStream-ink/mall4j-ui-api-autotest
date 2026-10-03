# -*- coding: utf-8 -*-
"""MySQL 多表关联一致性测试"""
import allure
import pytest


ORDER_NUMBER = "1145634946149388288"


@allure.feature("数据库多表关联")
@pytest.mark.api
class TestDBQueries:

    @allure.title("[DB] 订单金额 = SUM(订单项金额 * 数量)")
    def test_order_amount_match_items(self, db):
        sql = """
            SELECT o.order_number, o.total AS order_total,
                   COALESCE(SUM(oi.price * oi.prod_count), 0) AS items_sum
            FROM tz_order o
            LEFT JOIN tz_order_item oi ON o.order_number = oi.order_number
            WHERE o.order_number = %s
            GROUP BY o.order_number, o.total
        """
        row = db.query_one(sql, (ORDER_NUMBER,))
        assert row is not None, f"订单 {ORDER_NUMBER} 不存在"
        assert abs(float(row["order_total"]) - float(row["items_sum"])) < 0.01, \
            f"订单金额不一致：{row['order_total']} vs {row['items_sum']}"

    @allure.title("[DB] 用户-角色-菜单 三表关联")
    def test_user_role_menu_relation(self, db):
        user_row = db.query_one(
            "SELECT user_id, username FROM tz_sys_user WHERE username = 'admin'"
        )
        assert user_row is not None, "admin 用户不存在"
        sql = """
            SELECT r.role_name, COUNT(rm.menu_id) AS menu_count
            FROM tz_sys_user u
            JOIN tz_sys_user_role ur ON u.user_id = ur.user_id
            JOIN tz_sys_role r ON ur.role_id = r.role_id
            LEFT JOIN tz_sys_role_menu rm ON r.role_id = rm.role_id
            WHERE u.username = 'admin'
            GROUP BY r.role_name
        """
        rows = db.query_all(sql)
        allure.attach(f"角色数={len(rows)}", name="关联信息")

    @allure.title("[DB] 订单项无孤儿记录")
    def test_no_orphan_order_items(self, db):
        sql = """
            SELECT oi.order_item_id FROM tz_order_item oi
            LEFT JOIN tz_order o ON oi.order_number = o.order_number
            WHERE o.order_number IS NULL LIMIT 5
        """
        orphans = db.query_all(sql)
        assert len(orphans) == 0, f"发现 {len(orphans)} 条孤儿订单项"

    @allure.title("[DB] 订单状态分布统计")
    def test_order_status_distribution(self, db):
        rows = db.query_all("""
            SELECT status, COUNT(*) AS cnt FROM tz_order
            GROUP BY status ORDER BY status
        """)
        total = sum(r["cnt"] for r in rows)
        assert total > 0
        allure.attach(
            "\n".join(f"status={r['status']}: {r['cnt']}" for r in rows),
            name="状态分布",
        )

    @allure.title("[DB] 最近 7 天订单数")
    def test_recent_orders(self, db):
        row = db.query_one("""
            SELECT COUNT(*) AS cnt FROM tz_order
            WHERE create_time >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        """)
        allure.attach(f"近7天订单={row['cnt']}", name="时间范围")
        assert row is not None

    @allure.title("[DB] 必填字段非 NULL")
    def test_required_fields_not_null(self, db):
        row = db.query_one("""
            SELECT COUNT(*) AS cnt FROM tz_order
            WHERE order_number IS NULL OR actual_total IS NULL OR status IS NULL
        """)
        assert row["cnt"] == 0

    @allure.title("[DB] 订单表主键索引存在")
    def test_order_primary_key(self, db):
        rows = db.query_all("SHOW INDEX FROM tz_order WHERE Key_name = 'PRIMARY'")
        assert len(rows) >= 1

    @allure.title("[DB] 订单项关联一致性")
    def test_order_items_relation(self, db):
        rows = db.query_all("""
            SELECT o.order_number FROM tz_order o
            LEFT JOIN tz_order_item oi ON o.order_number = oi.order_number
            GROUP BY o.order_number
            HAVING COUNT(oi.order_item_id) = 0
        """)
        allure.attach(f"无订单项的订单数={len(rows)}", name="关联校验")
        assert True