# Mall4j UI + API 自动化测试

> 168 条通过用例只是结果，工程化能力才是项目本身。

![Tests](https://img.shields.io/badge/tests-168%20passed-brightgreen)
![Bugs](https://img.shields.io/badge/bugs-3%20found-red)
![Python](https://img.shields.io/badge/python-3.11-blue)
![Playwright](https://img.shields.io/badge/playwright-1.63-green)
![Pytest](https://img.shields.io/badge/pytest-9.1-orange)

---

## 为什么做这个项目

很多自动化项目止步于"用例能跑通"。

我想验证的是：当测试对象从简单 B2C 升级到企业级系统后，自动化该如何从"脚本堆叠"演进为"质量保障体系"。

于是有了这个项目：

- UI 与 API 双轨架构，共用配置、日志、报告、通知
- 数据驱动 + 契约 + 性能三重验证，一条方法覆盖 10 场景
- 接口 + 数据库双重断言，穿透到数据层验证一致性
- 数据工厂自建自清，不依赖手工造数据，不污染环境
- 弱网 + 兼容性 + RBAC + 缓存一致性专项测试
- 最终通过订单状态机 + 限流 + 弱网测试发现 3 个真实缺陷

168 条通过用例只是结果，工程化能力才是项目本身。

---

## 核心亮点

### 1. UI + API 双轨架构
同一工程内两条独立测试轨道，共用配置、日志、报告、通知。

    pytest -m ui             # 只跑 UI
    pytest -m api            # 只跑接口
    pytest -m weaknetwork    # 只跑弱网
    pytest -m compatibility  # 只跑兼容性
    pytest -m performance    # 只跑性能基线
    pytest testcases/        # 全跑

### 2. 三层验证：数据驱动 + 契约 + 性能

- 数据驱动矩阵：1 条方法覆盖 10 个场景（正常/错误/空值/超长/空格/大小写/SQL 注入）
- JSON Schema 契约测试：后端改字段名会立刻失败
- 性能基线：登录/产品/会员/订单/管理员 6 个接口响应 < 1s

### 3. AES 加密复现
分析前端 JS 加密逻辑，用 Python 完整复现 AES/ECB/Pkcs7，真实模拟客户端登录，不绕过安全机制。

### 4. 数据工厂
基于 pytest fixture 自动构建/恢复测试数据，不依赖手工准备，不污染环境。

### 5. 接口 + DB 双重断言
不只校验接口返回，直连 MySQL 验证数据真的落库。

    assert resp.json()["code"] == "00000"        # 接口层
    row = db.query_one("SELECT status FROM tz_order WHERE order_number=%s", (no,))
    assert row["status"] == 3                    # 数据库层

### 6. 专项测试全覆盖
- 弱网：Playwright + CDP 模拟 3G / 2G / 断网
- 兼容性：Chromium / Firefox / WebKit 三引擎 + 3 种分辨率
- RBAC 权限：创建受限角色 + 新用户，验证菜单权限隔离
- Redis 缓存：token 落 Redis、TTL、key 变更
- 数据一致性：CRUD 后直连 DB 验证、订单发货全字段一致

### 7. 发现 3 个真实缺陷
- BUG-001（P0）：发货接口缺少订单状态校验
- BUG-002（P2）：登录成功后不清除密码错误计数
- BUG-003（P1）：断网时前端无网络异常提示

详见 BUGS.md。

---

## 测试覆盖

| 轨道 | 模块 | 用例数 |
|---|---|---|
| UI | 登录 / 产品 / 会员 / 门店 / 订单 / 系统管理 | 54 |
| UI | 弱网测试 | 6 |
| UI | 兼容性测试 | 15 |
| API | 登录数据驱动 + 契约 + 性能 | 15 |
| API | 订单状态机 | 6 |
| API | 登录限流 | 3 |
| API | CRUD 完整链路 | 7 |
| API | RBAC 权限 | 5 |
| API | 接口 + DB 强一致 | 4 |
| API | Redis 缓存机制 | 3 |
| API | 订单全字段一致性 | 3 |
| API | 基础功能 | 30 |
| 合计 | 6 大模块 + 25 子功能 | 约 175 |

---

## 已发现缺陷

| ID | 描述 | 严重程度 | 状态 |
|---|---|---|---|
| BUG-001 | 发货接口缺少订单状态校验 | P0 | 待修复 |
| BUG-002 | 登录成功后不清除密码错误计数 | P2 | 待修复 |
| BUG-003 | 断网时前端无网络异常提示 | P1 | 待修复 |

缺陷密度约 2%。

---

## 技术栈

| 工具 | 用途 |
|---|---|
| Python 3.11 | 编程语言 |
| Playwright | UI 自动化 + CDP 弱网模拟 |
| Pytest + pytest-xdist | 测试框架 + 并行执行 |
| Requests | 接口测试 |
| PyMySQL | 数据库直连断言 |
| PyCryptodome | AES 加密复现 |
| jsonschema | 契约测试 |
| Redis-py | 限流 + 缓存机制测试 |
| Allure | 测试报告 |

---

## 项目结构

    mall4j-ui-api-autotest/
    ├── config/              # 全局配置
    ├── common/              # 日志 / DB / 请求封装
    ├── pages/               # UI 页面对象（POM）
    ├── api/                 # 接口封装
    ├── schemas/             # JSON Schema 契约
    ├── testcases/
    │   ├── test_ui/         # UI 用例
    │   └── test_api/        # 接口用例
    ├── conftest.py          # 全局 Fixture
    ├── pytest.ini           # Pytest 配置
    ├── send_feishu.py       # 飞书通知
    ├── run_all_tests.bat    # 一键运行
    ├── BUGS.md              # 缺陷记录
    ├── TEST_CASES.md        # 用例总表
    ├── ARCHITECTURE.md      # 架构文档
    └── requirements.txt

---

## 快速开始

前置条件：
1. 本地部署 Mall4j（MySQL 3307 + Redis 6379 + 后端 8085/8086 + 前端 9527）
2. Python 3.11+
3. Allure 命令行工具

安装：

    git clone https://github.com/StillStream-ink/mall4j-ui-api-autotest.git
    cd mall4j-ui-api-autotest
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    playwright install chromium firefox

配置 .env：

    FEISHU_WEBHOOK=https://open.feishu.cn/open-apis/bot/v2/hook/你的地址

运行：

    pytest testcases/ -v                              # 全部
    pytest testcases/test_api/ -v -n 4                # 只接口并行
    pytest testcases/test_ui/ -v                      # 只 UI
    pytest -m weaknetwork -v                          # 只弱网
    pytest testcases/ --alluredir=reports/allure-results
    allure serve reports/allure-results               # 看报告
    run_all_tests.bat                                 # 一键跑 + 通知

---

## 测试设计方法

| 方法 | 应用场景 |
|---|---|
| 等价类划分 | 登录用户名/密码 |
| 边界值分析 | 密码长度、分页 size |
| 场景法 | 订单状态机流转 |
| 错误推测 | SQL 注入、超长字符串 |
| 数据驱动 | 登录场景矩阵 10 组 |
| 契约测试 | JSON Schema 校验 |
| 性能基线 | 关键接口响应时间 |
| 弱网模拟 | CDP 模拟 3G/2G/断网 |
| 兼容性矩阵 | 3 引擎 × 3 分辨率 |
| 数据一致性 | 接口 + DB 双重断言 |

---

## 面试要点

能讲清的 6 个技术点：

1. 如何设计测试用例矩阵？→ 数据驱动 + 等价类 + 边界值
2. 为什么要做接口 + DB 双重断言？→ 接口返回成功不等于数据落库
3. 如何定位前端 bug 还是后端 bug？→ 抓包 + 日志 + DB 三步定位
4. 自动化测试发现过什么缺陷？→ BUG-001 P0 缺陷的完整过程
5. 为什么 UI 和接口放同一个项目？→ 双轨共用配置 + 互相配合
6. 弱网测试的局限在哪？→ 本地模拟 vs 真实网络差异

能展示的工程能力：

- POM 三层架构设计
- 数据工厂 fixture 生命周期管理
- pytest-xdist 并行决策
- Redis 限流 + 缓存一致性测试
- CDP 弱网模拟
- 契约测试 + 性能基线
- RBAC 权限隔离验证

---

## 我理解的自动化测试

> 数据驱动 > 脚本堆叠
> 契约验证 > 字段猜测
> 接口 + DB 双重断言 > 只看返回码
> 数据工厂 > 手工造数据
> 测试设计 > 代码堆砌
>
> 工具会迭代，工程原则不会。

---

## Let's Connect

- GitHub: [@StillStream-ink](https://github.com/StillStream-ink)

