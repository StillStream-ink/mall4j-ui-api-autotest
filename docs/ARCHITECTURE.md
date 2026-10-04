# 架构设计文档

## 1. 分层架构

    config/       全局配置（URL、账号、DB、超时）
    common/       日志、DB 连接、请求工具
    pages/        UI 页面对象（POM）
    api/          接口封装
    schemas/      JSON Schema 契约定义
    testcases/    用例（只做断言）

**核心原则**：用例层不碰页面元素，页面层不碰 HTTP 请求。

---

## 2. UI + API 双轨设计

**为什么不是两个独立项目？**

- 共用配置：URL、账号一处修改全局生效
- 共用工具：日志、报告、通知
- 互相配合：接口造数据 → UI 验证界面

**物理隔离**：

    pytest -m ui      # 只跑 UI
    pytest -m api     # 只跑接口

---

## 3. 数据工厂

订单状态机测试需要不同状态的订单，但数据库只有"已完成"和"失败"。

**解决方案**：fixture 临时改 DB 状态，测完自动恢复。

    @pytest.fixture
    def order_with_status(db):
        original = []
        def _set(order_number, status):
            row = db.query_one("SELECT status FROM tz_order WHERE order_number=%s", (order_number,))
            original.append((order_number, dict(row)))
            db.execute("UPDATE tz_order SET status=%s WHERE order_number=%s", (status, order_number))
        yield _set
        for order_number, row in original:
            db.execute("UPDATE tz_order SET status=%s WHERE order_number=%s", (row["status"], order_number))

**关键点**：
- 不依赖手工造数据
- 每条用例自建自清
- 失败时也能恢复（fixture teardown）

---

## 4. 接口 + DB 双重断言

**接口返回成功 ≠ 数据真的落库。**

本项目：

    assert resp.json()["code"] == "00000"
    row = db.query_one("SELECT status, dvy_time FROM tz_order WHERE order_number=%s", (order_number,))
    assert row["status"] == 3
    assert row["dvy_time"] is not None

**踩坑记录**：
- pymysql 默认 `autocommit=False`
- 事务隔离级别 `REPEATABLE READ`
- 首次 SELECT 后，后续查询读到旧快照
- **解决**：`autocommit=True`

---

## 5. 三层验证：数据驱动 + 契约 + 性能

### 数据驱动矩阵

    @pytest.mark.parametrize("username, password, expect_success, case_name", [
        ("admin", "123456", True, "正常登录"),
        ("admin", "wrong_pwd", False, "错误密码"),
        ("", "123456", False, "空用户名"),
        ("admin' OR '1'='1", "123456", False, "SQL 注入"),
        # ...
    ])

一条方法覆盖 10 场景，等价类 + 边界值 + 安全测试。

### JSON Schema 契约测试

后端改字段名会立即失败，比普通断言更早发现问题。

### 性能基线

关键接口响应时间 < 1s 断言。

---

## 6. 专项测试设计

### 弱网测试

Playwright + CDP 模拟网络条件：

    cdp = page.context.new_cdp_session(page)
    cdp.send("Network.emulateNetworkConditions", {
        "offline": False,
        "latency": 400,
        "downloadThroughput": 400 * 1024 / 8,
        "uploadThroughput": 400 * 1024 / 8,
    })

**覆盖**：3G 慢网、断网登录、断网恢复。

**局限**：本地 CDP 不走真实网络，无法复现 TCP 握手超时、丢包重传。

### 兼容性测试

通过 `BROWSER` 环境变量切换引擎：

    $env:BROWSER="chromium"; pytest testcases/test_ui/test_compatibility.py -v
    $env:BROWSER="firefox";  pytest testcases/test_ui/test_compatibility.py -v
    $env:BROWSER="webkit";   pytest testcases/test_ui/test_compatibility.py -v

**WebKit 限制**：Windows 下无法访问 localhost Vite 开发服务器（Playwright 已知问题），用 `@pytest.mark.skipif` 标记。

### RBAC 权限测试

创建受限角色（仅 1 个菜单）→ 创建用户绑定 → 新用户登录 → 验证菜单隔离。

### Redis 缓存测试

验证 token 落 Redis、TTL、key 变更。

**踩坑**：redis-py 5.x 默认 RESP3 协议（HELLO 命令），Redis 5.0 不支持，需 `protocol=2`。

---

## 7. 缺陷管理

### BUG-001：发货接口缺少订单状态校验（P0）

**发现过程**：
1. 设计 6 条状态机用例
2. 4 条失败：待付款 / 已完成 / 失败 / 重复发货全部成功
3. 查看后端源码，定位到 `OrderController.delivery()` 缺少状态校验
4. 用 `@pytest.mark.xfail` 标记对应用例

### BUG-002：登录成功后不清除错误计数（P2）

**发现过程**：
1. 做限流测试，原以为"错误 10 次锁定"
2. 查看 `PasswordCheckManager.java` 发现 `count > 10`，实际第 12 次才锁
3. 进一步发现代码没有"登录成功清除计数"的逻辑

### BUG-003：断网时前端无异常提示（P1）

**发现过程**：
1. 弱网测试探底，CDP 模拟断网
2. 断网点登录，错误提示数量 = 0
3. 查看 `http.js` 响应拦截器：`switch (error.response.status)` 断网时 `error.response` 为 undefined 抛 TypeError

---

## 8. 并行执行的理性决策

**尝试**：`pytest-xdist -n 4`。

**实测**：串行 6.47s → 并行 5.19s，收益 1.28s。

**结论**：
- 接口测试本身很快，并行收益有限
- UI 测试不能简单并行（浏览器上下文冲突）
- 最终方案：接口 4 worker 并行 + UI 串行

---

## 9. 失败处理

- **失败自动截图**：`pytest_runtest_makereport` hook
- **环境信息自动生成**：Allure 报告自动带 `environment.properties`
- **飞书通知**：跑完自动推送卡片
- **xfail 标记**：已知缺陷，开发修复后去掉标记即可回归

---

## 10. 关键设计决策

| 决策 | 方案 A | 方案 B | 最终选择 | 理由 |
|---|---|---|---|---|
| 双轨 vs 两项目 | 两独立仓库 | 同工程双轨 | 双轨 | 共用配置/报告/通知 |
| 并行执行 | 全并行 | 接口并行+UI串行 | 接口并行 | UI 有浏览器状态冲突 |
| 数据准备 | 手工 SQL | Fixture 工厂 | Fixture | 自建自清，不污染环境 |
| 弱网测试 | 全浏览器 | 仅 Chromium | 仅 Chromium | CDP 只在 Chromium 可用 |
| WebKit 兼容 | 报错 | skip | skip | Windows 环境限制 |
| DB 断言 | 只看接口 | 接口+DB双重 | 双重 | 接口成功 ≠ 数据落库 |

---

## 11. 运维脚本设计

项目提供 6 个脚本：

| 脚本 | 平台 | 功能 |
|---|---|---|
| `check_env.sh` | Linux | 环境检查 |
| `check_env.ps1` | Windows | PowerShell 版本 |
| `check_env.py` | 跨平台 | Python 版本 |
| `tail_logs.sh` | Linux | 日志实时查看 |
| `clean_test_data.sh` | Linux | 数据清理 |
| `batch_test.sh` | Linux | 批量跑 + 归档 |

详见 [docs/LINUX_OPS.md](./docs/LINUX_OPS.md)。