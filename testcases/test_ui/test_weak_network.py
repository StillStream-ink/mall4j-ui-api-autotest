import os
import time
import allure
import pytest

from config.settings import WEB_URL, ADMIN
from pages.admin.login_dialog_page import LoginDialogPage
from playwright.sync_api import expect

pytestmark = [
    pytest.mark.ui,
    pytest.mark.weaknetwork,
    pytest.mark.skipif(
        os.getenv("BROWSER", "chromium") != "chromium",
        reason="CDP (弱网模拟) 只在 Chromium 可用",
    ),
]


def set_network(cdp, latency=0, kbps=0, offline=False):
    cdp.send("Network.emulateNetworkConditions", {
        "offline": offline,
        "latency": latency,
        "downloadThroughput": kbps * 1024 if kbps else -1,
        "uploadThroughput": kbps * 1024 if kbps else -1,
    })

@allure.feature("弱网测试")
@pytest.mark.ui
class TestWeakNetwork:

    @allure.title("[弱网-基线] 无限制下加载登录页 < 5s")
    def test_baseline_load(self, page):
        start = time.time()
        page.goto(WEB_URL, wait_until="domcontentloaded", timeout=60000)
        page.locator(".login .el-input input").first.wait_for(state="visible", timeout=60000)
        elapsed = time.time() - start
        allure.attach(f"{elapsed:.2f}s", name="加载耗时")
        assert elapsed < 5, f"基线加载 {elapsed:.2f}s 超过 5s"

    @allure.title("[弱网-轻] 2Mbps 下加载登录页 < 8s")
    def test_light_weak_load(self, page):
        cdp = page.context.new_cdp_session(page)
        set_network(cdp, latency=100, kbps=2048)
        start = time.time()
        page.goto(WEB_URL, wait_until="domcontentloaded", timeout=60000)
        page.locator(".login .el-input input").first.wait_for(state="visible", timeout=60000)
        elapsed = time.time() - start
        allure.attach(f"{elapsed:.2f}s", name="加载耗时")
        assert elapsed < 8, f"轻弱网加载 {elapsed:.2f}s 超过 8s"

    @allure.title("[弱网-中] 1Mbps 下加载登录页 < 12s")
    def test_medium_weak_load(self, page):
        cdp = page.context.new_cdp_session(page)
        set_network(cdp, latency=200, kbps=1024)
        start = time.time()
        page.goto(WEB_URL, wait_until="domcontentloaded", timeout=60000)
        page.locator(".login .el-input input").first.wait_for(state="visible", timeout=60000)
        elapsed = time.time() - start
        allure.attach(f"{elapsed:.2f}s", name="加载耗时")
        assert elapsed < 12, f"中弱网加载 {elapsed:.2f}s 超过 12s"

    @allure.title("[弱网-重] 400Kbps 下加载登录页 < 20s")
    def test_heavy_weak_load(self, page):
        cdp = page.context.new_cdp_session(page)
        set_network(cdp, latency=400, kbps=400)
        start = time.time()
        page.goto(WEB_URL, wait_until="domcontentloaded", timeout=60000)
        page.locator(".login .el-input input").first.wait_for(state="visible", timeout=60000)
        elapsed = time.time() - start
        allure.attach(f"{elapsed:.2f}s", name="加载耗时")
        assert elapsed < 20, f"重弱网加载 {elapsed:.2f}s 超过 20s"

    @allure.title("[BUG-003] 断网登录应显示网络异常提示")
    @pytest.mark.xfail(
        reason="BUG-003: 断网时前端无提示，详见 BUGS.md",
        strict=False,
    )
    def test_offline_login_shows_error(self, page):
        # 先正常加载
        page.goto(WEB_URL, wait_until="domcontentloaded", timeout=60000)
        page.locator(".login .el-input input").first.wait_for(state="visible")

        login = LoginDialogPage(page)
        login.fill_credentials(ADMIN["username"], ADMIN["password"])

        # 断网
        page.context.set_offline(True)
        page.wait_for_timeout(500)

        # 点登录
        login.click_login()

        # 期望：有错误提示（显式等待，不用固定等待）
        expect(page.locator(".el-message, .el-notification, .el-message-box").first).to_be_visible(timeout=8000)


    @allure.title("[弱网] 断网恢复后重试登录成功")
    def test_recover_after_offline(self, page):
        page.goto(WEB_URL, wait_until="domcontentloaded", timeout=60000)
        page.locator(".login .el-input input").first.wait_for(state="visible")

        login = LoginDialogPage(page)
        login.fill_credentials(ADMIN["username"], ADMIN["password"])

        # 断网 → 点登录（失败）
        page.context.set_offline(True)
        page.wait_for_timeout(500)
        login.click_login()
        page.wait_for_timeout(2000)   # 给失败请求一点响应时间

        # 恢复网络 → 重新登录
        page.context.set_offline(False)
        page.wait_for_timeout(500)   # 给网络恢复一点时间

        # 重新填账号密码（断网失败后表单可能被清空）
        if page.locator(".login .el-input input").first.is_visible():
            login.fill_credentials(ADMIN["username"], ADMIN["password"])
        login.click_login()

        # 断言：登录成功跳转 /home
        page.wait_for_url("**/home", timeout=15000)