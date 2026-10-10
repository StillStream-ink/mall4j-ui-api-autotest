import os
import sys
import json
import pytest
import requests
import pymysql
import redis
import allure

from pathlib import Path
from playwright.sync_api import sync_playwright

from config.settings import (
    BROWSER, HEADLESS, SLOW_MO, DEFAULT_TIMEOUT,
    WEB_URL, API_URL, ADMIN,
    REDIS_HOST, REDIS_PORT,
    ALLURE_RESULTS_DIR, SCREENSHOT_DIR,
)
from common.logger import get_logger
from api.client import APIClient
from api.admin.login_api import LoginApi
from api.buyer.buyer_login import BuyerLogin

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
# pytest hook: 记录每阶段结果（供截图 fixture 读取）
# ============================================================
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture(autouse=True)
def capture_screenshot(request):
    """UI 用例失败时自动截图并挂到 Allure 报告（兼容 page / buyer_logged_page）"""
    yield
    rep = getattr(request.node, "rep_call", None)
    if rep is None or not rep.failed:
        return

    # 找 page / buyer_logged_page（二者取其一）
    page_obj = None
    for name in ("page", "buyer_logged_page"):
        if name in request.fixturenames:
            try:
                page_obj = request.getfixturevalue(name)
            except Exception:
                page_obj = None
            if page_obj:
                break
    if not page_obj:
        return

    try:
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        safe_name = request.node.name.replace("/", "_").replace("\\", "_")
        path = SCREENSHOT_DIR / f"FAILED_{safe_name}.png"
        page_obj.screenshot(path=str(path), full_page=True)
        allure.attach.file(
            str(path),
            name=f"失败截图 - {request.node.name}",
            attachment_type=allure.attachment_type.PNG,
        )
    except Exception as e:
        logger.warning(f"失败截图失败: {e}")


# ============================================================
# pytest hook: Allure 环境信息自动生成
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
    from common.db_helper import DBHelper
    helper = DBHelper()
    yield helper
    helper.close()


# ============================================================
# 快递公司 fixture（订单发货需要）
# ============================================================
@pytest.fixture(scope="function")
def valid_dvy(api_session):
    resp = api_session.get("/admin/delivery/list")
    body = resp.json()
    assert body["code"] == "00000", f"获取快递公司失败: {body}"
    if not body["data"]:
        pytest.skip("快递公司列表为空，跳过依赖快递公司的测试")
    return body["data"][0]


# ============================================================
# 买家端 fixture
# ============================================================
@pytest.fixture(scope="session")
def buyer_token():
    """买家登录，整个会话复用 token"""
    return BuyerLogin().login()


@pytest.fixture(scope="session")
def buyer_headers(buyer_token):
    return {
        "Authorization": buyer_token,
        "Content-Type": "application/json"
    }


@pytest.fixture
def buyer_logged_page(page, buyer_token):
    """买家端已登录 page：token 从 API 登录拿，注入 localStorage 跳过 UI 登录"""
    page.goto("http://127.0.0.1")     # ← 改成 127.0.0.1
    page.evaluate(f"localStorage.setItem('Token', '{buyer_token}')")
    page.evaluate(f"localStorage.setItem('hadLogin', 'true')")
    page.reload()
    page.wait_for_load_state("domcontentloaded")
    yield page


@pytest.fixture
def clean_buyer_data():
    """测试结束后软删除本次测试产生的订单"""
    yield
    try:
        from common.db_helper import DBHelper

        DBHelper().execute(
            "UPDATE tz_sku SET stocks = 1000000,actual_stocks = 1000000 WHERE sku_id = 402"
        )
        print("\n[环境准备] sku 402 库存已恢复为 1000000")
    except Exception as e:
        print(f"\n[清理警告] {e}")


@pytest.fixture(scope="session", autouse=True)
def restore_buyer_test_env():
    """每次测试会话开始前：恢复商品/SKU 库存 + 清 Redis"""
    try:
        from common.db_helper import DBHelper
        # 商品总库存（下单校验用）
        DBHelper().execute(
            "UPDATE tz_prod SET total_stocks = 1000 WHERE prod_id = 75"
        )
        DBHelper().execute(
            "UPDATE tz_sku SET stocks = 1000, actual_stocks = 1000 WHERE sku_id = 402"
        )
        print("\n[环境准备] prod 75 / sku 402 库存已恢复为 1000")

        redis.Redis(
            host=REDIS_HOST, port=REDIS_PORT, db=0, protocol=2
        ).flushdb()
        print("[环境准备] Redis 缓存已清空")
    except Exception as e:
        print(f"\n[环境准备失败] {e}")