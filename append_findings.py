# -*- coding: utf-8 -*-
"""追加"其他发现"章节到 BUGS.md"""
from pathlib import Path

ROOT = Path(r"E:\mall4j-ui-api-autotest")
path = ROOT / "BUGS.md"

APPENDIX = """

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
"""

current = path.read_text(encoding="utf-8")

if "其他发现与注意事项" not in current:
    path.write_text(current + APPENDIX, encoding="utf-8")
    print(f"[OK] BUGS.md 追加'其他发现'章节（5 条观察）")
    print(f"     文件大小: {len(current + APPENDIX)} bytes")
else:
    print("[SKIP] BUGS.md 已含'其他发现'章节")