# -*- coding: utf-8 -*-
"""A. 接口 → DB 强一致：CRUD 后验证数据真的落库"""
import allure
import pytest
import uuid

from api.crud_api import SysConfigCrudApi, SysRoleCrudApi


def unique_key(prefix="autotest"):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


@allure.feature("数据一致性-接口与DB")
@pytest.mark.api
class TestApiDbConsistency:

    @pytest.fixture
    def config_api(self, api_session):
        return SysConfigCrudApi(api_session)

    @pytest.fixture
    def role_api(self, api_session):
        return SysRoleCrudApi(api_session)

    @pytest.fixture(autouse=True)
    def cleanup(self, config_api, role_api):
        def _clean():
            try:
                body = config_api.page(param_key="autotest_").json()
                records = body.get("data", {}).get("records", [])
                ids = [r["id"] for r in records if str(r.get("paramKey", "")).startswith("autotest_")]
                if ids:
                    config_api.delete(ids)
            except Exception:
                pass
            try:
                body = role_api.page(role_name="autotest_").json()
                records = body.get("data", {}).get("records", [])
                ids = [r["roleId"] for r in records if str(r.get("roleName", "")).startswith("autotest_")]
                if ids:
                    role_api.delete(ids)
            except Exception:
                pass
        _clean()
        yield
        _clean()

    @allure.title("[DB一致] 参数新增后 DB 有记录")
    def test_config_create_in_db(self, config_api, db):
        key = unique_key()
        resp = config_api.create(key, "db_value", remark="db_check")
        assert resp.json()["code"] == "00000"

        row = db.query_one(
            "SELECT * FROM tz_sys_config WHERE param_key = %s", (key,)
        )
        assert row is not None, f"接口返回成功但 DB 查不到 {key}"
        assert row["param_value"] == "db_value"
        assert row["remark"] == "db_check"

    @allure.title("[DB一致] 参数编辑后 DB 同步")
    def test_config_update_in_db(self, config_api, db):
        key = unique_key()
        config_api.create(key, "v1")
        row = db.query_one("SELECT id FROM tz_sys_config WHERE param_key = %s", (key,))
        config_id = row["id"]

        config_api.update(config_id, key, "v2_updated")

        row = db.query_one("SELECT param_value FROM tz_sys_config WHERE id = %s", (config_id,))
        assert row["param_value"] == "v2_updated"

    @allure.title("[DB一致] 参数删除后 DB 无记录")
    def test_config_delete_in_db(self, config_api, db):
        key = unique_key()
        config_api.create(key, "to_delete")
        row = db.query_one("SELECT id FROM tz_sys_config WHERE param_key = %s", (key,))
        config_id = row["id"]

        config_api.delete([config_id])

        row = db.query_one("SELECT * FROM tz_sys_config WHERE id = %s", (config_id,))
        assert row is None, "接口删除成功但 DB 还有记录"

    @allure.title("[DB一致] 角色新增后 DB 有记录")
    def test_role_create_in_db(self, role_api, db):
        name = unique_key("autotest_role")
        resp = role_api.create(name, remark="db_check")
        assert resp.json()["code"] == "00000"

        row = db.query_one("SELECT * FROM tz_sys_role WHERE role_name = %s", (name,))
        assert row is not None
        assert row["role_name"] == name
