# -*- coding: utf-8 -*-
"""CRUD 完整链路测试：参数管理 + 角色管理

安全策略：
- 所有测试数据加 `autotest_` 前缀 + uuid 后缀
- fixture 测完自动清理
- 绝不碰现有数据
"""
import logging

import allure
import pytest
import uuid

from api.crud_api import SysConfigCrudApi, SysRoleCrudApi

logger = logging.getLogger(__name__)


def unique_key(prefix="autotest"):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


@allure.feature("CRUD-参数管理")
@pytest.mark.api
class TestSysConfigCrud:

    @pytest.fixture
    def api(self, api_session):
        return SysConfigCrudApi(api_session)

    @pytest.fixture(autouse=True)
    def cleanup(self, api):
        """测试前后清理所有 autotest_ 前缀的残留数据"""
        def _clean():
            try:
                body = api.page(param_key="autotest_").json()
                records = body.get("data", {}).get("records", [])
                ids = [
                    r["id"] for r in records
                    if str(r.get("paramKey", "")).startswith("autotest_")
                ]
                if ids:
                    api.delete(ids)
            except Exception as e:
                logger.warning(f"cleanup config failed: {e}")

        _clean()
        yield
        _clean()

    @allure.title("参数 CRUD 完整链路：新增→查询→编辑→删除")
    def test_full_crud(self, api):
        key = unique_key()
        value1 = "test_value_1"
        value2 = "test_value_2_updated"

        # 1. 新增
        resp = api.create(key, value1, remark="autotest create")
        assert resp.json()["code"] == "00000", f"新增失败: {resp.json()}"

        # 2. 查询验证
        found = api.find_by_key(key)
        assert found is not None, f"新增后应查到 {key}"
        assert found["paramKey"] == key
        assert found["paramValue"] == value1
        config_id = found["id"]

        # 3. 编辑
        resp = api.update(config_id, key, value2, remark="autotest update")
        assert resp.json()["code"] == "00000", f"编辑失败: {resp.json()}"

        detail = api.info(config_id).json()
        assert detail["code"] == "00000"
        assert detail["data"]["paramValue"] == value2

        # 4. 删除
        resp = api.delete([config_id])
        assert resp.json()["code"] == "00000", f"删除失败: {resp.json()}"

        found = api.find_by_key(key)
        assert found is None, "删除后不应再查到"

    @allure.title("新增参数后列表 total+1")
    def test_create_increases_total(self, api):
        before = api.page().json()["data"]["total"]
        key = unique_key()
        api.create(key, "v1")
        after = api.page().json()["data"]["total"]
        assert after == before + 1, f"新增后 total 应 +1，{before} → {after}"

    @allure.title("按 paramKey 精确搜索")
    def test_search_by_key(self, api):
        key = unique_key("autotest_search")
        api.create(key, "search_value")
        found = api.find_by_key(key)
        assert found is not None
        assert found["paramKey"] == key

    @allure.title("搜索不存在的 paramKey 返回空")
    def test_search_not_exist(self, api):
        body = api.page(param_key="autotest_no_such_key_9999").json()
        assert body["code"] == "00000"
        assert len(body["data"]["records"]) == 0


@allure.feature("CRUD-角色管理")
@pytest.mark.api
class TestSysRoleCrud:

    @pytest.fixture
    def api(self, api_session):
        return SysRoleCrudApi(api_session)

    @pytest.fixture(autouse=True)
    def cleanup(self, api):
        def _clean():
            try:
                body = api.page(role_name="autotest_").json()
                records = body.get("data", {}).get("records", [])
                ids = [
                    r["roleId"] for r in records
                    if str(r.get("roleName", "")).startswith("autotest_")
                ]
                if ids:
                    api.delete(ids)
            except Exception as e:
                logger.warning(f"cleanup role failed: {e}")

        _clean()
        yield
        _clean()

    @allure.title("角色 CRUD 完整链路：新增→查询→编辑→删除")
    def test_full_crud(self, api):
        name = unique_key("autotest_role")

        resp = api.create(name, remark="autotest 角色")
        assert resp.json()["code"] == "00000", f"新增失败: {resp.json()}"

        found = api.find_by_name(name)
        assert found is not None
        assert found["roleName"] == name
        role_id = found["roleId"]

        new_name = name + "_upd"
        resp = api.update(role_id, new_name, remark="autotest 更新")
        assert resp.json()["code"] == "00000", f"编辑失败: {resp.json()}"

        detail = api.info(role_id).json()
        assert detail["code"] == "00000"
        assert detail["data"]["roleName"] == new_name

        resp = api.delete([role_id])
        assert resp.json()["code"] == "00000"

        found = api.find_by_name(new_name)
        assert found is None

    @allure.title("新增角色后列表 total+1")
    def test_create_increases_total(self, api):
        before = api.page().json()["data"]["total"]
        api.create(unique_key("autotest_role"), remark="")
        after = api.page().json()["data"]["total"]
        assert after == before + 1

    @allure.title("搜索不存在的角色名 返回空")
    def test_search_not_exist(self, api):
        body = api.page(role_name="autotest_no_such_role_9999").json()
        assert body["code"] == "00000"
        assert len(body["data"]["records"]) == 0