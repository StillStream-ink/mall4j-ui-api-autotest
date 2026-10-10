# -*- coding: utf-8 -*-
"""Mall4j admin member API tests"""
import allure
import pytest

from api.client import APIClient
from api.admin.member_api import MemberApi
from config.settings import API_URL


@allure.feature("后台接口-会员管理")
@pytest.mark.api
class TestMemberApi:

    @pytest.fixture
    def member_api(self, api_session):
        return MemberApi(api_session)

    @allure.title("拉取会员列表")
    def test_get_member_list(self, member_api):
        resp = member_api.page(current=1, size=10)
        body = resp.json()
        assert resp.status_code == 200
        assert body["code"] == "00000"
        data = body["data"]
        assert "records" in data
        assert len(data["records"]) > 0
        assert data["total"] >= 1

    @allure.title("分页 size=1 只返回1条")
    def test_page_size_1(self, member_api):
        resp = member_api.page(current=1, size=1)
        body = resp.json()
        assert body["code"] == "00000"
        records = body["data"]["records"]
        assert len(records) == 1

    @allure.title("搜索 Leo")
    def test_search_leo(self, member_api):
        resp = member_api.page(current=1, size=10, nick_name="Leo")
        body = resp.json()
        assert body["code"] == "00000"
        records = body["data"]["records"]
        assert len(records) >= 1
        assert any("Leo" in (r.get("nickName") or "") for r in records)

    @allure.title("搜索不存在 返回空")
    def test_search_not_exist(self, member_api):
        resp = member_api.page(current=1, size=10, nick_name="不存在的会员_XYZ_12345")
        body = resp.json()
        assert body["code"] == "00000"
        assert len(body["data"]["records"]) == 0

    @allure.title("会员字段完整性")
    def test_member_fields(self, member_api):
        resp = member_api.page(current=1, size=1)
        body = resp.json()
        first = body["data"]["records"][0]
        for field in ("userId", "nickName", "status", "userRegtime"):
            assert field in first, f"missing field {field}"

    @allure.title("查会员详情")
    def test_get_member_info(self, member_api):
        # 先拉列表拿第一条 userId
        list_resp = member_api.page(current=1, size=1)
        first_id = list_resp.json()["data"]["records"][0]["userId"]
        # 再查详情
        resp = member_api.info(first_id)
        body = resp.json()
        assert body["code"] == "00000"
        assert body["data"]["userId"] == first_id

    @allure.title("无 token 访问 应该被拒")
    def test_no_token(self):
        fresh = APIClient(base_url=API_URL)
        member = MemberApi(fresh)
        resp = member.page(current=1, size=10)
        body = resp.json()
        assert body.get("success") is not True
        assert body.get("code") != "00000"