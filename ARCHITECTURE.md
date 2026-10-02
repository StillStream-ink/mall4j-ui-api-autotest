# 架构设计文档

## 1. 分层架构

    config/       全局配置
    common/       日志、DB、请求工具
    pages/        UI 页面对象（POM）
    api/          接口封装
    schemas/      JSON Schema 契约
    testcases/    用例（只做断言）

核心原则：用例层不碰页面元素，页面层不碰 HTTP 请求。

## 2. UI + API 双轨设计

为什么不是两个独立项目？
- 共用配置：URL、账号一处修改全局生效
- 共用工具：日志、报告、通知
- 互相配合：接口造数据 -> UI 验证界面

## 3. 数据工厂

订单状态机测试需要不同状态的订单，数据库只有已完成和失败。
解决方案：fixture 临时改 DB 状态，测完自动恢复。

关键点：
- 不依赖手工造数据
- 每条用例自建自清
- 失败时也能恢复

## 4. 接口 + DB 双重断言

接口返回成功不等于数据真的落库。

踩坑记录：
- pymysql 默认 autocommit=False
- 事务隔离级别 REPEATABLE READ
- 首次 SELECT 后，后续查询读到旧快照
- 解决：autocommit=True

## 5. 三层验证：数据驱动 + 契约 + 性能

数据驱动矩阵：一条方法覆盖 10 场景，等价类 + 边界值 + 安全测试。
JSON Schema 契约：后端改字段名会立即失败。
性能基线：从能跑通升级到性能达标。

## 6. 专项测试设计

### 弱网测试
通过 Playwright + CDP 模拟网络条件。
覆盖：3G 慢网加载、断网登录提示、断网恢复重试。
局限：本地 CDP 不走真实网络，定位为"前端网络异常处理测试"。

### 兼容性测试
通过 BROWSER 环境变量切换 Chromium / Firefox / WebKit。
WebKit 在 Windows 下无法访问 localhost，用 skipif 标记。

### RBAC 权限测试
创建受限角色 -> 创建用户绑定 -> 新用户登录 -> 验证菜单隔离。

### Redis 缓存测试
验证 token 落 Redis、TTL、key 变更。
踩坑：redis-py 5.x 默认 RESP3，Redis 5.0 不支持，需 protocol=2。

## 7. 缺陷管理

### BUG-001 发货接口缺少订单状态校验（P0）
6 条状态机用例，4 条失败。查看 OrderController.delivery() 缺少状态校验。

### BUG-002 登录成功后不清除错误计数（P2）
PasswordCheckManager 中 count > 10 实际第 12 次才锁，且登录成功不清计数。

### BUG-003 断网无提示（P1）
http.js 响应拦截器 error.response 可能为 undefined 抛 TypeError。

## 8. 并行执行的理性决策

实测：串行 6.47s，并行 5.19s，收益 1.28s。
结论：接口测试本身很快，UI 测试不能简单并行。
最终方案：接口 4 worker 并行 + UI 串行。

## 9. 失败处理

- 失败自动截图
- Allure 环境信息自动生成
- 飞书通知
- xfail 标记已知缺陷

## 10. 关键设计决策记录

| 决策 | 最终选择 | 理由 |
|---|---|---|
| 双轨 vs 两项目 | 双轨 | 共用配置/报告/通知 |
| 并行执行 | 接口并行+UI串行 | UI 有浏览器状态冲突 |
| 数据准备 | Fixture 工厂 | 自建自清 |
| 弱网测试 | 仅 Chromium | CDP 只在 Chromium |
| WebKit 兼容 | skip | Windows 环境限制 |
| DB 断言 | 接口+DB双重 | 接口成功不等于落库 |
