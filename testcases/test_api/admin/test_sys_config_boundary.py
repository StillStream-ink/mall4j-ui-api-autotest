# -*- coding: utf-8 -*-
"""系统参数边界值测试：超长、SQL 注入、Emoji"""
import allure
import pytest

from api.admin.crud_api import SysConfigCrudApi


def _cleanup(api: SysConfigCrudApi, key: str) -> None:
    """清理测试数据：按 key 删除"""
    try:
        rec = api.find_by_key(key)
        if rec:
            api.delete([rec["id"]])
    except Exception:
        pass


@allure.feature("系统管理")
@allure.story("边界值：参数值超长 1000 字符")
def test_config_value_too_long(api_session):
    """参数值传 1000 字符，后端不应返回 500"""
    api = SysConfigCrudApi(api_session)
    key = "autotest_long_value"
    _cleanup(api, key)

    long_value = "A" * 1000
    resp = api.create(param_key=key, param_value=long_value)
    body = resp.json()
    print(f"\n超长参数值响应: code={body['code']}, msg={body.get('msg')}")

    assert body["code"] != "A00005", f"超长输入导致服务器异常: {body}"

    _cleanup(api, key)


@allure.feature("系统管理")
@allure.story("边界值：参数键含 SQL 注入")
def test_config_key_sql_injection(api_session):
    """参数键传 SQL 注入 payload，后端不应被注入"""
    api = SysConfigCrudApi(api_session)
    payload = "autotest_sqli' OR '1'='1"
    _cleanup(api, payload)

    resp = api.create(param_key=payload, param_value="test")
    body = resp.json()
    print(f"\nSQL 注入响应: code={body['code']}, msg={body.get('msg')}")

    assert body["code"] != "A00005", f"SQL 注入导致服务器异常: {body}"

    if body["code"] == "00000":
        rec = api.find_by_key(payload)
        print(f"查询到的记录: {rec}")

    _cleanup(api, payload)


@allure.feature("系统管理")
@allure.story("边界值：参数值含 Emoji（BUG-004 旁证）")
@pytest.mark.xfail(
    reason="BUG-004: Mall4j 后端对 Emoji（4 字节 Unicode）处理异常，"
           "搜索接口和系统参数接口均返回 A00005",
    strict=False,
)
def test_config_value_emoji(api_session):
    """
    BUG-004 旁证：系统参数接口传 Emoji 也返回 A00005 服务器异常。
    说明这不是搜索接口单个 bug，而是后端字符编码的系统性问题。
    """
    api = SysConfigCrudApi(api_session)
    key = "autotest_emoji"
    _cleanup(api, key)

    emoji_value = "😀😂🤔🎉"
    resp = api.create(param_key=key, param_value=emoji_value)
    body = resp.json()
    print(f"\nEmoji 参数值响应: code={body['code']}, msg={body.get('msg')}")

    assert body["code"] != "A00005", f"Emoji 输入导致服务器异常: {body}"

    _cleanup(api, key)