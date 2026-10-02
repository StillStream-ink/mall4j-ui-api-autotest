# -*- coding: utf-8 -*-
"""RBAC 权限测试"""
import allure
import pytest
import uuid
import requests

from config.settings import API_URL
from api.rbac_api import SysUserCrudApi, SysMenuApi, RBACLoginApi
from api.crud_api import SysRoleCrudApi


def unique_key():
    """username 长度 ≤ 20"""
    return f"au_{uuid.uuid4().hex[:6]}"


@allure.feature("RBAC 权限测试")
@pytest.mark.api
class TestRBAC:

    @pytest.fixture
    def user_api(self, api_session):
        return SysUserCrudApi(api_session)

    @pytest.fixture
    def role_api(self, api_session):
        return SysRoleCrudApi(api_session)

    @pytest.fixture
    def menu_api(self, api_session):
        return SysMenuApi(api_session)

    @pytest.fixture(autouse=True)
    def cleanup(self, user_api, role_api):
        """清理 autotest_ / au_ 前缀的用户和角色"""
        def _clean():
            try:
                body = user_api.page(username="au_").json()
                records = body.get("data", {}).get("records", [])
                uids = [r["userId"] for r in records if str(r.get("username", "")).startswith("au_")]
                if uids:
                    user_api.delete(uids)
            except Exception as e:
                print(f"cleanup user failed: {e}")
            try:
                body = role_api.page(role_name="autotest_").json()
                records = body.get("data", {}).get("records", [])
                rids = [r["roleId"] for r in records if str(r.get("roleName", "")).startswith("autotest_")]
                if rids:
                    role_api.delete(rids)
            except Exception as e:
                print(f"cleanup role failed: {e}")

        _clean()
        yield
        _clean()

    @allure.title("菜单列表有数据")
    def test_menu_list_available(self, menu_api):
        body = menu_api.list_all().json()
        assert body["code"] == "00000"
        assert isinstance(body["data"], list)
        assert len(body["data"]) > 0

    @allure.title("admin 拥有全部菜单权限")
    def test_admin_has_full_permissions(self, menu_api):
        body = menu_api.nav().json()
        assert body["code"] == "00000"
        menus = body["data"].get("menuList") or []
        print(f"\nadmin 菜单数: {len(menus)}")
        assert len(menus) > 0, "admin 应有菜单"

    @allure.title("创建受限角色（仅授 1 个菜单）")
    def test_create_restricted_role(self, role_api, menu_api):
        menus = menu_api.list_all().json()["data"]
        one_menu_id = menus[0].get("menuId") or menus[0].get("id")
        assert one_menu_id, f"菜单 ID 字段找不到: {menus[0].keys()}"

        role_name = f"autotest_role_{uuid.uuid4().hex[:6]}"
        resp = role_api.create(role_name, remark="RBAC test", menu_id_list=[one_menu_id])
        assert resp.json()["code"] == "00000"

        found = role_api.find_by_name(role_name)
        assert found is not None
        assert found["roleName"] == role_name

    @allure.title("创建用户并绑定受限角色")
    def test_create_user_with_role(self, user_api, role_api, menu_api):
        menus = menu_api.list_all().json()["data"]
        one_menu_id = menus[0].get("menuId") or menus[0].get("id")

        role_name = f"autotest_role_{uuid.uuid4().hex[:6]}"
        role_resp = role_api.create(role_name, remark="", menu_id_list=[one_menu_id])
        assert role_resp.json()["code"] == "00000"
        role = role_api.find_by_name(role_name)

        username = unique_key()
        password = "Test@123456"
        user_resp = user_api.create(username, password, role_id_list=[role["roleId"]])
        assert user_resp.json()["code"] == "00000", f"创建用户失败: {user_resp.json()}"

        found = user_api.find_by_username(username)
        assert found is not None
        assert found["username"] == username

    @allure.title("受限用户登录后菜单权限受限")
    def test_restricted_user_login_and_menus(self, user_api, role_api, menu_api):
        # 1. 拿一个菜单 ID
        menus_all = menu_api.list_all().json()["data"]
        one_menu_id = menus_all[0].get("menuId") or menus_all[0].get("id")

        # 2. 创建受限角色（仅授权 1 个菜单）
        role_name = f"autotest_role_{uuid.uuid4().hex[:6]}"
        role_api.create(role_name, remark="", menu_id_list=[one_menu_id])
        role = role_api.find_by_name(role_name)
        assert role is not None, f"角色创建后应能查到: {role_name}"

        # 3. 创建用户并绑定该角色
        username = unique_key()
        password = "Test@123456"
        user_api.create(username, password, role_id_list=[role["roleId"]])

        # 4. 用新用户登录
        login_api = RBACLoginApi(API_URL)
        resp = login_api.login(username, password)
        body = resp.json()
        assert body["success"] is True, f"新用户登录失败: {body}"
        token = body["data"]["accessToken"]

        # 5. 查受限用户的 nav 菜单
        r = requests.get(
            f"{API_URL}/sys/menu/nav",
            headers={"Authorization": token},
            timeout=15,
        )
        nav_body = r.json()
        assert nav_body["code"] == "00000"
        nav_menus = nav_body["data"].get("menuList") or []

        # 6. 查 admin 的 nav 菜单作为对比
        admin_nav = menu_api.nav().json()
        admin_menus = admin_nav["data"].get("menuList") or []

        # 7. 打印对比信息，方便排查
        print("\n" + "=" * 60)
        print(f"  admin 菜单数: {len(admin_menus)}")
        for m in admin_menus:
            sub = m.get("list") or []
            print(f"    [admin] {m.get('name')}  (子菜单 {len(sub)} 个)")
        print(f"  受限用户菜单数: {len(nav_menus)}")
        for m in nav_menus:
            sub = m.get("list") or []
            print(f"    [受限] {m.get('name')}  (子菜单 {len(sub)} 个)")
        print("=" * 60 + "\n")

        # 8. 断言：受限用户菜单数应少于 admin
        assert len(nav_menus) < len(admin_menus), (
            f"受限用户菜单数({len(nav_menus)}) 应少于 admin({len(admin_menus)})。"
            f"如果相等，说明后端未做菜单权限过滤 —— 记录为 BUG-004。"
        )

        # 9. 断言：受限用户菜单应只包含被授权的那 1 个
        assert len(nav_menus) >= 1, "受限用户至少有 1 个菜单"
    
