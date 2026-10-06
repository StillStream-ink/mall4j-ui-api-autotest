# 缺陷记录

> 项目：Mall4j UI + API 自动化测试
> 发现缺陷：3 个（P0 × 1，P1 × 1，P2 × 1）
> 更新日期：2026-10-02

---

## BUG-001: 发货接口缺少订单状态校验

### 基本信息
| 项 | 内容 |
|---|---|
| 严重程度 | 高 |
| 优先级 | P0 |
| 发现时间 | 2026-10-01 |
| 发现方式 | 订单状态机测试 |
| 状态 | 待修复 |

### 问题描述
后台"订单发货"接口（PUT /order/order/delivery）只校验了 shopId 权限，没有校验订单状态，导致任意状态的订单都能被"发货"。

### 复现步骤
1. 通过 SQL 把任意订单改成非"待发货"状态（如待付款 status=1）
2. 调用发货接口 PUT /order/order/delivery，body 为 {"orderNumber": "...", "dvyId": 1, "dvyFlowId": "SF_TEST_001"}
3. 接口返回 code=00000 成功
4. DB 里该订单 status 被改成 3（待收货）

### 期望行为
只有 status=2（待发货）的订单能被发货，其他状态应返回业务错误。

### 影响范围
- 数据一致性风险：待付款订单被发货，用户没付钱就收到货
- 状态机约束失效：订单状态可被任意跨越
- 重复发货：已发货订单可再次"发货"，覆盖快递单号
- 失败订单复活：已失败/已取消订单可被发货

### 代码位置
yami-shop-admin/src/main/java/com/yami/shop/admin/controller/OrderController.java

delivery 方法只校验了 shopId，缺少如下校验：

    if (!Objects.equal(order.getStatus(), OrderStatus.PAYED.value())) {
        throw new YamiShopBindException("当前订单状态不允许发货");
    }

### 修复建议
在 shopId 校验后补上订单状态校验。

### 验证方式
pytest testcases/test_api/test_order_state_machine.py -v
所有 [BUG-001] 标记的用例应从 XFAIL 变为 PASSED。

---

## BUG-002: 登录成功后不清除密码错误计数

### 基本信息
| 项 | 内容 |
|---|---|
| 严重程度 | 中 |
| 优先级 | P2 |
| 发现时间 | 2026-10-02 |
| 发现方式 | 登录限流测试 |
| 状态 | 待修复 |

### 问题描述
PasswordCheckManager.checkPassword() 中，用户密码错误时 count 递增，但登录成功后没有清除 count。导致用户正常登录后再有几次失误，就会被误锁。

### 代码位置
yami-shop-security-common/.../PasswordCheckManager.java

    public void checkPassword(...) {
        int count = ...;
        if (count > TIMES_CHECK_INPUT_PASSWORD_NUM) {  // 阈值 10
            throw new YamiShopBindException("密码输入错误十次，已限制登录30分钟");
        }
        RedisUtil.set(checkPrefix + userNameOrMobile, count, 1800);

        // 密码错误时 count++
        if (StrUtil.isBlank(encodedPassword) || !passwordEncoder.matches(rawPassword, encodedPassword)) {
            count++;
            RedisUtil.set(checkPrefix + userNameOrMobile, count, 1800);
            throw new YamiShopBindException("账号或密码不正确");
        }
        // 缺失：登录成功应清除计数
        // RedisUtil.delete(checkPrefix + userNameOrMobile);
    }

### 复现步骤
1. 30 分钟内连续输错密码 5 次（count=5）
2. 正常登录（密码正确）-> 登录成功，但 count 仍为 5
3. 再输错 6 次密码
4. 第 12 次尝试（即使密码正确）-> 被锁定 30 分钟

### 期望行为
用户登录成功后，应清除失败计数：

    // 密码验证通过后加一行
    RedisUtil.delete(checkPrefix + userNameOrMobile);

### 影响范围
- 用户被误锁：历史错误累计到阈值即锁
- 客服成本增加：用户频繁来电"为什么我密码正确却被锁"
- 安全体验下降：多次输入错误后即使成功登录，计数不清零

### 附带发现
注释写"密码输入错误十次，已限制登录"，但实际是 count > 10，即第 12 次尝试才触发锁，代码与注释不一致。

### 验证方式
pytest testcases/test_api/test_login_bug002.py -v
所有 [BUG-002] 标记的用例应从 XFAIL 变为 PASSED。

---

## BUG-003: 断网时前端无网络异常提示

### 基本信息
| 项 | 内容 |
|---|---|
| 严重程度 | 中 |
| 优先级 | P1 |
| 发现时间 | 2026-10-02 |
| 发现方式 | 弱网测试 - CDP 模拟断网 |
| 状态 | 待修复 |

### 问题描述
断网状态下点击登录按钮，前端无任何错误提示，用户点击后界面无反馈，无法感知网络异常。

### 复现步骤
1. 打开登录页 http://localhost:9527/
2. 填入 admin / 123456
3. 断开网络
4. 点击登录按钮
5. 观察 8 秒

- 实际结果：无任何提示，停留在登录页
- 期望结果：弹出"网络异常，请检查网络连接"提示

### 代码位置
mall4v/src/utils/http.js 第 39 行起的响应拦截器，error 分支直接访问 error.response.status，但断网时 error.response 为 undefined，抛 TypeError 导致拦截器崩溃。

### 修复建议
在 error 分支开头加：

    if (!error.response) {
        ElMessage({
            message: '网络异常，请检查网络连接',
            type: 'error',
            duration: 2000,
        })
        return Promise.reject(error)
    }

### 验证方式
pytest testcases/test_ui/test_weak_network.py::TestWeakNetwork::test_offline_login_shows_error -v
应从 XFAIL 变为 PASSED。

---

## 缺陷统计

| 严重程度 | 数量 |
|---|---|
| P0（严重） | 1 |
| P1（高） | 1 |
| P2（中） | 1 |
| 合计 | 3 |

**缺陷分布**：
- 后端逻辑缺陷：2（BUG-001、BUG-002）
- 前端逻辑缺陷：1（BUG-003）

**测试有效性**：约 150 条用例发现 3 个缺陷，缺陷密度约 2%。

---

## 附录：其他发现与注意事项

以下问题不算严格意义上的产品缺陷，但在测试过程中被发现，值得记录：

### 观察-001：用户名大小写不敏感

**现象**：用 `ADMIN` 大写登录也能成功，与 `admin` 视为同一账号。

**性质**：潜在安全问题（多数系统接受此行为）

**处理方式**：测试用例改为断言"大小写不敏感（已确认行为）"，不作为缺陷。

**风险**：如果系统未来允许多账号共存，`Admin` 和 `admin` 会冲突。

---

### 观察-002：限流阈值注释与代码不一致

**位置**：`PasswordCheckManager.java`

**现象**：注释写"密码输入错误十次，已限制登录30分钟"，但代码是 `if (count > TIMES_CHECK_INPUT_PASSWORD_NUM)`，实际是**第 12 次尝试**才触发锁。

**性质**：代码与注释不一致（已在 BUG-002 中附带提及）

**建议**：改为 `count >= TIMES_CHECK_INPUT_PASSWORD_NUM`，让行为与注释一致。

---

### 观察-003：WebKit 在 Windows 下无法访问本地服务

**现象**：Playwright WebKit 引擎在 Windows 下访问 `http://localhost:9527` 超时。

**性质**：**环境限制，非代码问题**（Playwright 已知问题）

**处理方式**：用 `@pytest.mark.skipif` 标记，跳过 WebKit 测试。

**生产方案**：CI 环境用 macOS runner 跑 WebKit，或部署到正式域名后再测。

---

### 观察-004：pytest-xdist 并行导致数据冲突

**现象**：4 个 worker 并行跑接口测试时，登录限流、CRUD、RBAC 测试互相干扰，37 条测试失败。

**性质**：**测试框架问题，非产品缺陷**

**根因**：
1. 限流测试锁定 admin 账号，导致其他 worker 拿不到 token
2. CRUD 测试使用共享数据，多 worker 同时增删造成冲突

**处理方式**：
1. `api_session` 从 session scope 改为 function scope，每条测试前重新登录
2. 限流测试单独跑，不参与全量并行
3. 有副作用的测试用 `--ignore` 隔离

**结论**：并行不是银弹，**有状态依赖的测试必须串行**。

---

### 观察-005：sa-token 单账号单 token 机制

**现象**：登录矩阵测试每成功一次，旧 token 被新 token 踢掉，导致共享 `api_session` 的后续测试全部 `Unauthorized`。

**性质**：**配置特性，非缺陷**（sa-token `is-share: false`）

**处理方式**：`api_session` 改为 function scope，每条测试前重新登录。

**价值**：这一条体现了"**测试隔离要隔离会话状态**"，不只是数据。



---

## 观察-006：sa-token 允许多 token 共存

### 基本信息
| 项 | 内容 |
|---|---|
| 严重程度 | 低 |
| 优先级 | P3 |
| 发现时间 | 2026-10-06 |
| 发现方式 | 并发登录测试 |
| 状态 | 已确认行为 |

### 问题描述
同账号多次登录，**旧 token 不会失效**——多个 token 可同时访问接口。

### 复现步骤
1. 第 1 次登录，拿 token1
2. 第 2 次登录，拿 token2
3. 用 token1 访问 `/prod/prod/page` → 仍然成功（code=00000）

### 影响范围
- **安全风险**：token 泄露后，即使重新登录也无法使旧 token 失效
- **用户困惑**：用户以为"重新登录 = 踢掉旧设备"，实际旧设备仍在线

### 根因
sa-token 配置 `is-share = true` 或未开启"同端互斥登录"。

### 修复建议
如需踢掉旧 token，配置：

```yaml
sa-token:
  is-concurrent: false    # 禁止同一账号并发登录
  is-share: false         # 不共用 token
