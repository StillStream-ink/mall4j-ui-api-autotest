# -*- coding: utf-8 -*-
"""生成面试速查手册"""
from pathlib import Path

ROOT = Path(r"E:\mall4j-ui-api-autotest")
DOC = ROOT / "docs" / "INTERVIEW_GUIDE.md"
DOC.parent.mkdir(exist_ok=True)

CONTENT = """# 面试速查手册

> 项目：Mall4j UI + API 自动化测试
> 用途：面试前 30 分钟速览，面试中快速定位

---

## 一、项目全景图
Mall4j 自动化测试项目
├── 双轨架构
│ ├── UI 轨道：pages/ (11 个) + testcases/test_ui/ (73 条)
│ └── API 轨道：api/ (11 个) + testcases/test_api/ (110 条)
├── 核心设计
│ ├── conftest.py：browser/page/api_client/api_session/db/valid_dvy fixture
│ ├── 数据工厂：order_with_status 临时改 DB 状态，测完恢复
│ └── 接口+DB 双重断言：db_helper.py + autocommit=True
├── 专项测试
│ ├── 弱网：CDP 模拟 3G/2G/断网
│ ├── 兼容性：Chromium/Firefox/WebKit
│ ├── RBAC：受限角色+用户+菜单隔离
│ ├── 限流：连续错 11 次触发
│ └── 多表关联：订单金额=SUM(订单项)
├── 缺陷发现
│ ├── BUG-001 (P0)：发货接口缺状态校验
│ ├── BUG-002 (P2)：登录计数不清零
│ └── BUG-003 (P1)：断网无提示
└── 运维脚本
├── check_env.sh/.ps1/.py
├── tail_logs.sh
├── clean_test_data.sh
└── batch_test.sh

---

## 二、10 个高频问题 + 标准答案

### Q1. 介绍一下这个项目

**答**：
> Mall4j 是一个电商系统，我给它做了 UI + API 双轨自动化测试，183 条用例，发现 3 个真实缺陷。
>
> UI 用 Playwright + POM 分层，API 用 Requests + PyMySQL，实现了接口 + 数据库双重断言。
>
> 还做了弱网、兼容性、RBAC 权限、限流机制、多表关联等专项测试。

### Q2. 为什么用 UI + API 双轨架构

**答**：
> 三点原因：
> 1. **共用配置**：URL、账号、DB 一处修改全局生效
> 2. **共用工具**：日志、报告、通知
> 3. **互相配合**：接口造数据，UI 验证界面
>
> 物理隔离：`pytest -m ui` / `pytest -m api` 可以独立跑。

### Q3. 遇到过最难的问题是什么

**答**：
> 做登录数据驱动测试时，跑了 10 组错误密码，触发了后端限流，把 admin 锁了 30 分钟，**后续 37 条测试全失败**。
>
> 排查发现两个问题：
> 1. **限流副作用**：登录矩阵测试连续错密码触发限流
> 2. **sa-token 单 token 机制**：每次成功登录生成新 token，把旧 token 踢掉
>
> 修复：
> - `api_session` 从 session scope 改为 function scope（每条测试前重新登录）
> - 限流测试用 `--ignore` 隔离，单独跑，跑完清 Redis
> - 写 `clean_test_data.sh` 脚本自动化清理

### Q4. 发现了什么缺陷

**答**：
> **BUG-001（P0）**：订单发货接口只校验 shopId 权限，**没校验订单状态**。
>
> 我设计 6 条状态机用例，发现待付款、已完成、失败订单都能被"发货"——严重的数据一致性风险，可能导致"用户没付钱就收到货"。
>
> 复现步骤：
> 1. SQL 把订单状态改成 1（待付款）
> 2. 调发货接口
> 3. 接口返回成功，DB 状态变 3
>
> 修复建议：在 shopId 校验后加订单状态校验。

### Q5. 怎么定位是前端 bug 还是后端 bug

**答**：
> 三步定位：
> 1. **抓包**：F12 / Charles 看请求参数和响应
> 2. **查日志**：`tail -f api.log | grep ERROR` 看后端日志
> 3. **直连 DB**：`SELECT` 看数据是否真的落库
>
> 如果请求参数对、后端日志正常、DB 数据对 → 前端展示问题。
> 如果请求参数对、后端返回错误 → 后端问题。

### Q6. 接口 + DB 双重断言怎么做的

**答**：
> 用 `pymysql` 直连 MySQL，封装 `common/db_helper.py`。
>
> 踩过一个坑：默认 `autocommit=False`，事务隔离级别 `REPEATABLE READ`，第一次 SELECT 后，后续查询读到**旧快照**。改成 `autocommit=True` 才正常。
>
> 用例里先断言接口返回码，再 `SELECT` 验证数据落库。比如订单发货：
> ```python
> assert resp.json()["code"] == "00000"          # 接口层
> row = db.query_one("SELECT status FROM tz_order WHERE order_number=%s", (no,))
> assert row["status"] == 3                      # 数据库层
> ```

### Q7. 弱网测试怎么做的

**答**：
> 用 Playwright + CDP（Chrome DevTools Protocol）：
> ```python
> cdp = page.context.new_cdp_session(page)
> cdp.send("Network.emulateNetworkConditions", {
>     "offline": False, "latency": 400,
>     "downloadThroughput": 400 * 1024 / 8,
>     "uploadThroughput": 400 * 1024 / 8,
> })
> ```
>
> 覆盖 4 个网络梯度 + 断网场景。发现 BUG-003：断网登录前端无提示。
>
> **局限**：只模拟浏览器层，不走真实网络，无法复现 TCP 握手超时、丢包重传。定位为"前端网络异常处理测试"。

### Q8. 测试数据怎么准备

**答**：
> 用数据工厂（fixture）自动构建和恢复：
> ```python
> @pytest.fixture
> def order_with_status(db):
>     original = []
>     def _set(order_number, status):
>         row = db.query_one("SELECT status FROM tz_order WHERE ...")
>         original.append((order_number, dict(row)))
>         db.execute("UPDATE tz_order SET status=%s WHERE ...")
>     yield _set
>     for order_number, row in original:  # teardown 恢复
>         db.execute("UPDATE tz_order SET status=%s WHERE ...")
> ```
>
> 好处：不依赖手工造数据、每条用例自建自清、失败时也能恢复。
>
> 测试数据统一用 `autotest_` / `au_` 前缀，测完自动清理。

### Q9. 测试效率怎么提升的

**答**：
> 三个措施：
> 1. **接口并行**：`pytest-xdist -n 4`，串行 6.47s → 并行 5.19s
> 2. **UI 串行**：多浏览器上下文冲突，不适合并行
> 3. **分类运行**：`-m ui` / `-m api` / `-m weaknetwork` 按需跑
>
> 实测收益有限，**并行要基于瓶颈分析，不是盲目加参数**。

### Q10. 后续想改进什么

**答**：
> 4 个方向：
> 1. **CI/CD**：GitHub Actions 每次 push 自动跑接口测试
> 2. **契约测试扩展**：所有核心接口加 JSON Schema
> 3. **性能趋势**：Allure 趋势图展示接口响应时间变化
> 4. **WebKit 测试**：迁移到 macOS runner

---

## 三、代码速查表

| 想找什么 | 文件路径 |
|---|---|
| 登录 AES 加密 | `api/login_api.py` |
| DB 连接工具 | `common/db_helper.py` |
| Fixture 定义 | `conftest.py` |
| HTTP 封装 | `api/client.py` |
| 订单状态机测试 | `testcases/test_api/test_order_state_machine.py` |
| 弱网 CDP 测试 | `testcases/test_ui/test_weak_network.py` |
| RBAC 权限测试 | `testcases/test_api/test_rbac.py` |
| 多表关联测试 | `testcases/test_api/test_db_queries.py` |
| 数据驱动登录 | `testcases/test_api/test_login_api.py` |
| 缺陷报告 | `BUGS.md` |
| 用例总表 | `TEST_CASES.md` |
| 架构文档 | `ARCHITECTURE.md` |

---

## 四、必背的 5 个代码片段

### 1. AES 加密（api/login_api.py）

```python
def encrypt_password(password: str) -> str:
    ts = str(int(time.time() * 1000))
    plain = (ts + password).encode("utf-8")
    cipher = AES.new(b"-mall4j-password", AES.MODE_ECB)
    return base64.b64encode(cipher.encrypt(pad(plain, AES.block_size))).decode("utf-8")
···
关键点：AES/ECB/Pkcs7，密钥 -mall4j-password，明文 = 时间戳 + 密码。



