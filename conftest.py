# -*- coding: utf-8 -*-
"""Global fixtures: UI page + API session + failure screenshot + allure env"""
import json
import sys
from pathlib import Path

import allure
import pytest
from playwright.sync_api import sync_playwright

from common.logger import get_logger
from config.settings import (
    WEB_URL, API_URL, BROWSER, HEADLESS, SLOW_MO,
    DEFAULT_TIMEOUT, ADMIN,
    ALLURE_RESULTS_DIR, SCREENSHOT_DIR, BASE_DIR,
)
from api.client import APIClient
from api.login_api import LoginApi

logger = get_logger(__name__)


# ============================================================
# UI track
# ============================================================
@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        b = getattr(p, BROWSER).launch(headless=HEADLESS, slow_mo=SLOW_MO)
        yield b
        b.close()


@pytest.fixture(scope="function")
def page(browser):
    ctx = browser.new_context()
    pg = ctx.new_page()
    # WebKit 首次启动慢，给它更长超时
    timeout = 60000 if BROWSER == "webkit" else DEFAULT_TIMEOUT
    pg.set_default_timeout(timeout)
    pg.goto(WEB_URL, wait_until="domcontentloaded", timeout=timeout)
    yield pg
    ctx.close()


# ============================================================
# API track
# ============================================================
@pytest.fixture(scope="session")
def api_client():
    client = APIClient(base_url=API_URL)
    yield client
    client.close()


@pytest.fixture(scope="function")
def api_session(api_client):
    """每条测试前重新登录，保证 token 有效"""
    login = LoginApi(api_client)
    resp = login.admin_login(ADMIN["username"], ADMIN["password"])
    body = resp.json()
    assert body.get("success") is True, f"登录失败: {body}"
    token = body["data"]["accessToken"]
    api_client.set_token(token)
    return api_client


# ============================================================
# pytest hooks: 失败自动截图
# ============================================================
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """把每个阶段的执行结果挂到 item 上，供 capture_screenshot 使用"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture(autouse=True)
def capture_screenshot(request):
    """用例失败时自动截图并挂到 Allure 报告"""
    yield
    if "page" not in request.fixturenames:
        return
    rep = getattr(request.node, "rep_call", None)
    if rep is None or not rep.failed:
        return

    # 保护：page fixture 可能已销毁
    try:
        page = request.getfixturevalue("page")
    except Exception:
        return

    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    safe_name = request.node.name.replace("/", "_").replace("\\", "_")
    path = SCREENSHOT_DIR / f"FAILED_{safe_name}.png"
    try:
        page.screenshot(path=str(path), full_page=True)
        allure.attach.file(
            str(path),
            name=f"失败截图 - {request.node.name}",
            attachment_type=allure.attachment_type.PNG,
        )
    except Exception as e:
        logger.warning(f"screenshot failed: {e}")


# ============================================================
# pytest hooks: Allure 环境信息自动生成
# ============================================================
def pytest_sessionfinish(session, exitstatus):
    try:
        ALLURE_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

        env = {
            "Project": "Mall4j UI + API Autotest",
            "Web_URL": WEB_URL,
            "API_URL": API_URL,
            "Browser": BROWSER,
            "Headless": str(HEADLESS),
            "Python": sys.version.split()[0],
        }
        (ALLURE_RESULTS_DIR / "environment.properties").write_text(
            "\n".join(f"{k}={v}" for k, v in env.items()),
            encoding="utf-8",
        )

        executor = {
            "name": "Local",
            "type": "pytest",
            "buildName": "local-run",
        }
        (ALLURE_RESULTS_DIR / "executor.json").write_text(
            json.dumps(executor, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as e:
        logger.warning(f"生成 Allure 环境信息失败: {e}")


# ============================================================
# DB fixture
# ============================================================
@pytest.fixture(scope="session")
def db():
    """数据库直连，用于接口 + DB 双重断言"""
    from common.db_helper import DBHelper
    helper = DBHelper()
    yield helper
    helper.close()


# ============================================================
# 快递公司 fixture（订单发货需要）
# ============================================================
@pytest.fixture(scope="function")
def valid_dvy(api_session):
    """获取一个有效的快递公司（空列表时跳过测试）"""
    resp = api_session.get("/admin/delivery/list")
    body = resp.json()
    assert body["code"] == "00000", f"获取快递公司失败: {body}"
    if not body["data"]:
        pytest.skip("快递公司列表为空，跳过依赖快递公司的测试")
    return body["data"][0]