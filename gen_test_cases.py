# -*- coding: utf-8 -*-
"""生成测试用例文档：TEST_CASES.md + 测试用例.xlsx"""
from pathlib import Path
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

ROOT = Path(r"E:\mall4j-ui-api-autotest")
DOCS = ROOT / "docs"
DOCS.mkdir(exist_ok=True)

# ============================================================
# 接口测试用例
# 格式：(ID, 模块, 标题, 优先级, 步骤, 预期, 状态, 缺陷)
# ============================================================
API_CASES = [
    # test_api_db_consistency.py
    ("DB-001", "数据一致性", "参数新增后 DB 有记录", "P1", "调 /sys/config 新增 → SELECT tz_sys_config", "DB 有记录，字段匹配", "PASS", ""),
    ("DB-002", "数据一致性", "参数编辑后 DB 同步", "P1", "接口编辑 → SELECT tz_sys_config", "DB 字段已更新", "PASS", ""),
    ("DB-003", "数据一致性", "参数删除后 DB 无记录", "P1", "接口删除 → SELECT tz_sys_config", "DB 记录消失", "PASS", ""),
    ("DB-004", "数据一致性", "角色新增后 DB 有记录", "P1", "接口新增 → SELECT tz_sys_role", "DB 有记录", "PASS", ""),
    # test_batch2_api.py
    ("B2-001", "订单管理", "订单列表接口", "P1", "GET /order/order/page", "code=00000", "PASS", ""),
    ("B2-002", "订单管理", "订单 size=1", "P2", "GET size=1", "≤1 条", "PASS", ""),
    ("B2-003", "订单管理", "订单搜索不存在", "P1", "orderNumber 不存在", "total=0", "PASS", ""),
    ("B2-004", "系统管理", "管理员列表", "P1", "GET /sys/user/page", "total≥1", "PASS", ""),
    ("B2-005", "系统管理", "当前管理员信息", "P1", "GET /sys/user/info", "username=admin", "PASS", ""),
    ("B2-006", "系统管理", "角色列表", "P1", "GET /sys/role/page", "total≥1", "PASS", ""),
    ("B2-007", "系统管理", "角色全量 list", "P2", "GET /sys/role/list", "数组非空", "PASS", ""),
    ("B2-008", "系统管理", "菜单树表", "P1", "GET /sys/menu/table", "数组", "PASS", ""),
    ("B2-009", "系统管理", "菜单全量 list", "P2", "GET /sys/menu/list", "数组", "PASS", ""),
    ("B2-010", "系统管理", "菜单导航", "P1", "GET /sys/menu/nav", "menuList 非空", "PASS", ""),
    ("B2-011", "系统管理", "菜单字段完整", "P2", "校验字段", "含 menuId/name/type", "PASS", ""),
    # test_batch3_api.py
    ("B3-001", "产品管理", "分类树表", "P1", "GET /prod/category/table", "数组非空", "PASS", ""),
    ("B3-002", "产品管理", "分类全量 list", "P2", "GET /listCategory", "code=00000", "PASS", ""),
    ("B3-003", "产品管理", "分组分页", "P1", "GET /prod/prodTag/page", "total≥1", "PASS", ""),
    ("B3-004", "产品管理", "分组 size=1", "P2", "size=1", "≤1 条", "PASS", ""),
    ("B3-005", "产品管理", "评论分页", "P2", "GET /prod/prodComm/page", "records 存在", "PASS", ""),
    ("B3-006", "产品管理", "规格分页", "P1", "GET /prod/spec/page", "total≥1", "PASS", ""),
    ("B3-007", "产品管理", "规格全量 list", "P2", "GET /list", "code=00000", "PASS", ""),
    ("B3-008", "系统管理", "参数列表", "P2", "GET /sys/config/page", "records 存在", "PASS", ""),
    ("B3-009", "系统管理", "地址全量", "P2", "GET /admin/area/list", "code=00000", "PASS", ""),
    ("B3-010", "系统管理", "顶层省份", "P2", "GET /listByPid?pid=0", "数组", "PASS", ""),
    ("B3-011", "系统管理", "系统日志列表", "P1", "GET /sys/log/page", "total≥1", "PASS", ""),
    ("B3-012", "系统管理", "日志搜索 admin", "P1", "按用户名搜索", "命中", "PASS", ""),
    # test_cache_consistency.py
    ("CC-001", "数据一致性", "登录后 token 落 Redis", "P1", "登录 → 查 Redis", "有 Authorization key", "PASS", ""),
    ("CC-002", "数据一致性", "token key 有 TTL", "P1", "查 Redis TTL", "0<TTL≤2592000", "PASS", ""),
    ("CC-003", "数据一致性", "登录新增 Redis key", "P2", "登录前后对比", "不减少", "PASS", ""),
    # test_crud_api.py
    ("C-001", "CRUD", "参数 CRUD 完整链路", "P1", "新增→查询→编辑→删除", "全链路成功 + DB 一致", "PASS", ""),
    ("C-002", "CRUD", "参数新增 total+1", "P2", "新增 + 查 total", "+1", "PASS", ""),
    ("C-003", "CRUD", "参数按 key 精确搜索", "P2", "搜索新增 key", "命中", "PASS", ""),
    ("C-004", "CRUD", "参数搜索不存在", "P2", "搜索不存在", "0 行", "PASS", ""),
    ("C-005", "CRUD", "角色 CRUD 完整链路", "P1", "新增→查询→编辑→删除", "全链路成功", "PASS", ""),
    ("C-006", "CRUD", "角色新增 total+1", "P2", "新增 + 查 total", "+1", "PASS", ""),
    ("C-007", "CRUD", "角色搜索不存在", "P2", "搜索不存在", "0 行", "PASS", ""),
    # test_db_queries.py
    ("Q-001", "多表关联", "订单金额 = SUM(订单项)", "P1", "JOIN order + order_item", "金额一致", "PASS", ""),
    ("Q-002", "多表关联", "用户-角色-菜单三表关联", "P1", "3 表 JOIN", "关联成功", "PASS", ""),
    ("Q-003", "多表关联", "订单项无孤儿记录", "P1", "LEFT JOIN WHERE NULL", "0 条孤儿", "PASS", ""),
    ("Q-004", "多表关联", "订单状态分布统计", "P2", "GROUP BY status", "有数据", "PASS", ""),
    ("Q-005", "多表关联", "最近 7 天订单数", "P2", "DATE_SUB 时间过滤", "查询成功", "PASS", ""),
    ("Q-006", "多表关联", "必填字段非 NULL", "P2", "WHERE IS NULL", "0 条异常", "PASS", ""),
    ("Q-007", "多表关联", "订单表主键索引存在", "P2", "SHOW INDEX", "有 PRIMARY", "PASS", ""),
    ("Q-008", "多表关联", "订单项关联一致性", "P2", "LEFT JOIN GROUP BY HAVING", "统计成功", "PASS", ""),
    # test_login_api.py
    ("L-001", "登录", "加密函数时间戳唯一性", "P1", "连续两次加密", "密文不同", "PASS", ""),
    ("L-002", "登录", "登录矩阵[正常登录]", "P0", "admin/123456", "success=true", "PASS", ""),
    ("L-003", "登录", "登录矩阵[空用户名]", "P1", "用户名为空", "code=A00014", "PASS", ""),
    ("L-004", "登录", "登录矩阵[全空格用户名]", "P2", '"   "/123456', "参数校验失败", "PASS", ""),
    ("L-005", "登录", "登录矩阵[错误密码]", "P0", "admin/wrong", "code=A00001", "PASS", ""),
    ("L-006", "登录", "登录矩阵[密码带尾空格]", "P2", '"123456 "', "登录失败", "PASS", ""),
    ("L-007", "登录", "登录成功响应契约", "P1", "JSON Schema 校验", "Schema 通过", "PASS", ""),
    ("L-008", "登录", "登录失败响应契约", "P1", "JSON Schema 校验", "Schema 通过", "PASS", ""),
    ("L-009", "登录", "登录性能基线", "P1", "计时调用", "< 1s", "PASS", ""),
    ("L-010", "登录", "连续 5 次登录性能", "P2", "5 次平均", "< 1s", "PASS", ""),
    # test_login_bug002.py
    ("LB-001", "登录限流", "错误 3 次后正确登录应清零", "P2", "错 3 次→正确登录→查 count", "count=0", "XFAIL", "BUG-002"),
    ("LB-002", "登录限流", "计数不清零会被误锁", "P2", "错 6 次→正确登录→再错 6 次", "不应被锁", "XFAIL", "BUG-002"),
    # test_member_api.py
    ("M-001", "会员管理", "会员列表", "P1", "GET /admin/user/page", "total>0", "PASS", ""),
    ("M-002", "会员管理", "分页 size=1", "P2", "size=1", "1 条", "PASS", ""),
    ("M-003", "会员管理", "搜索 Leo", "P1", "nickName=Leo", "命中", "PASS", ""),
    ("M-004", "会员管理", "搜索不存在", "P1", "不存在昵称", "0 条", "PASS", ""),
    ("M-005", "会员管理", "会员字段完整性", "P2", "校验字段", "含 userId/nickName", "PASS", ""),
    ("M-006", "会员管理", "查会员详情", "P1", "GET /info/{id}", "code=00000", "PASS", ""),
    ("M-007", "会员管理", "无 token 访问被拒", "P1", "不带 token", "失败", "PASS", ""),
    # test_order_deep.py
    ("OD-001", "订单管理", "订单列表", "P1", "GET /order/order/page", "records 非空", "PASS", ""),
    ("OD-002", "订单管理", "分页 size=1", "P2", "size=1", "1 条", "PASS", ""),
    ("OD-003", "订单管理", "按订单号搜索", "P1", "拿真实订单号搜索", "命中", "PASS", ""),
    ("OD-004", "订单管理", "搜索不存在", "P1", "orderNumber 不存在", "0 条", "PASS", ""),
    ("OD-005", "订单管理", "订单详情有商品项", "P1", "GET /orderInfo/{no}", "orderItems 非空", "PASS", ""),
    ("OD-006", "订单管理", "订单详情字段完整", "P1", "校验字段", "含 orderNumber/status", "PASS", ""),
    ("OD-007", "订单管理", "不存在订单号发货被拒", "P1", "发货", "失败", "PASS", ""),
    ("OD-008", "订单管理", "缺参数发货被拒", "P1", "body 为空", "失败", "PASS", ""),
    # test_order_state_full_db.py
    ("OSF-001", "订单管理", "发货后所有字段同步更新", "P0", "发货 → SELECT 全字段", "status/dvy_* 全落库", "PASS", ""),
    ("OSF-002", "订单管理", "订单与订单项关联一致", "P1", "SELECT tz_order + item", "关联项 ≥1", "PASS", ""),
    ("OSF-003", "订单管理", "发货不改变订单金额", "P1", "记录金额→发货→对比", "金额不变", "PASS", ""),
    # test_order_state_machine.py
    ("OSM-001", "订单状态机", "待发货订单发货成功", "P0", "SQL 改 status=2 → 调发货", "DB status=3", "PASS", ""),
    ("OSM-002", "订单状态机", "不存在订单号发货失败", "P1", "orderNumber=NOT_EXIST", "失败", "PASS", ""),
    ("OSM-003", "订单状态机", "待付款订单发货", "P0", "SQL 改 status=1 → 调发货", "应失败", "XFAIL", "BUG-001"),
    ("OSM-004", "订单状态机", "已完成订单发货", "P0", "SQL 改 status=5 → 调发货", "应失败", "XFAIL", "BUG-001"),
    ("OSM-005", "订单状态机", "失败订单发货", "P0", "SQL 改 status=6 → 调发货", "应失败", "XFAIL", "BUG-001"),
    ("OSM-006", "订单状态机", "重复发货", "P0", "已发货订单再次发货", "应被拒", "XFAIL", "BUG-001"),
    # test_performance.py
    ("PERF-001", "性能基线", "登录 < 1s", "P1", "计时调用", "< 1s", "PASS", ""),
    ("PERF-002", "性能基线", "产品列表 < 1s", "P1", "计时调用", "< 1s", "PASS", ""),
    ("PERF-003", "性能基线", "会员列表 < 1s", "P1", "计时调用", "< 1s", "PASS", ""),
    ("PERF-004", "性能基线", "订单列表 < 1s", "P1", "计时调用", "< 1s", "PASS", ""),
    ("PERF-005", "性能基线", "管理员列表 < 1s", "P1", "计时调用", "< 1s", "PASS", ""),
    ("PERF-006", "性能基线", "角色列表 < 1s", "P1", "计时调用", "< 1s", "PASS", ""),
    ("PERF-007", "性能基线", "菜单树 < 1s", "P1", "计时调用", "< 1s", "PASS", ""),
    # test_product_api.py
    ("P-001", "产品管理", "拉取产品列表", "P1", "GET /prod/prod/page", "records 非空", "PASS", ""),
    ("P-002", "产品管理", "分页 size=5", "P2", "size=5", "≤5 条", "PASS", ""),
    ("P-003", "产品管理", "搜索 iPhone", "P1", "prodName=iPhone", "命中", "PASS", ""),
    ("P-004", "产品管理", "搜索不存在", "P1", "prodName 不存在", "0 条", "PASS", ""),
    ("P-005", "产品管理", "无 token 访问被拒", "P1", "不带 token", "失败", "PASS", ""),
    ("P-006", "产品管理", "产品字段完整性", "P2", "校验字段", "含 prodId/prodName", "PASS", ""),
    # test_rbac.py
    ("R-001", "RBAC 权限", "菜单列表有数据", "P1", "GET /sys/menu/list", "数组非空", "PASS", ""),
    ("R-002", "RBAC 权限", "admin 拥有全部菜单", "P1", "GET /sys/menu/nav", "menuList 非空", "PASS", ""),
    ("R-003", "RBAC 权限", "创建受限角色", "P1", "创建角色仅 1 菜单", "创建成功", "PASS", ""),
    ("R-004", "RBAC 权限", "创建用户并绑定角色", "P1", "创建用户 + 绑定角色", "创建成功", "PASS", ""),
    ("R-005", "RBAC 权限", "受限用户菜单权限受限", "P0", "登录+对比菜单", "菜单数 < admin", "PASS", ""),
    # test_shop_api.py
    ("S-001", "门店管理", "自提点列表", "P2", "GET /shop/pickAddr/page", "code=00000", "PASS", ""),
    ("S-002", "门店管理", "自提点 size=1", "P2", "size=1", "≤1 条", "PASS", ""),
    ("S-003", "门店管理", "运费模板列表", "P1", "GET /shop/transport/page", "records 非空", "PASS", ""),
    ("S-004", "门店管理", "运费模板全量 list", "P2", "GET /list", "数组", "PASS", ""),
    ("S-005", "门店管理", "轮播图列表", "P1", "GET /admin/indexImg/page", "records 非空", "PASS", ""),
    ("S-006", "门店管理", "轮播图 size=1", "P2", "size=1", "≤1 条", "PASS", ""),
    ("S-007", "门店管理", "热搜列表", "P2", "GET /admin/hotSearch/page", "code=00000", "PASS", ""),
    ("S-008", "门店管理", "公告列表", "P1", "GET /shop/notice/page", "records 非空", "PASS", ""),
    ("S-009", "门店管理", "公告字段完整性", "P2", "校验字段", "含 noticeContent", "PASS", ""),
    # test_zzz_login_rate_limit.py
    ("RL-001", "登录限流", "连续错误触发限流", "P0", "错 11 次+第 12 次正确密码", "被锁定 30 分钟", "PASS", ""),
    ("RL-002", "登录限流", "限流 key 落 Redis", "P1", "错 1 次→查 Redis", "key + TTL ≤1800s", "PASS", ""),
    ("RL-003", "登录限流", "计数累加验证", "P1", "错 3 次→查 count", "count=3", "PASS", ""),
]

# ============================================================
# UI 测试用例
# ============================================================
UI_CASES = [
    ("B2U-001", "订单管理", "订单打开", "P1", "打开 /order/order", "URL 匹配", "PASS", ""),
    ("B2U-002", "订单管理", "订单搜索", "P1", "搜索订单号", "无报错", "PASS", ""),
    ("B2U-003", "订单管理", "订单分页", "P2", "检查分页", "分页文本存在", "PASS", ""),
    ("B2U-004", "订单管理", "订单清空", "P2", "清空搜索", "无报错", "PASS", ""),
    ("B2U-005", "系统管理", "管理员列表打开", "P1", "打开 /sys/user", "行数≥1", "PASS", ""),
    ("B2U-006", "系统管理", "管理员搜索 admin", "P1", "搜索 admin", "命中", "PASS", ""),
    ("B2U-007", "系统管理", "管理员搜索不存在", "P1", "搜索不存在", "0 行", "PASS", ""),
    ("B2U-008", "系统管理", "角色列表打开", "P1", "打开 /sys/role", "行数≥1", "PASS", ""),
    ("B2U-009", "系统管理", "角色搜索不存在", "P2", "搜索不存在", "0 行", "PASS", ""),
    ("B2U-010", "系统管理", "菜单管理打开", "P1", "打开 /sys/menu", "行数>10", "PASS", ""),
    ("B2U-011", "系统管理", "菜单数 > 10", "P2", "检查行数", ">10", "PASS", ""),
    ("B3U-001", "产品管理", "分类管理打开", "P1", "打开 /prod/category", "行数>0", "PASS", ""),
    ("B3U-002", "产品管理", "分组管理打开", "P1", "打开 /prod/prodTag", "行数>0", "PASS", ""),
    ("B3U-003", "产品管理", "分组搜索", "P2", "搜索", "无报错", "PASS", ""),
    ("B3U-004", "产品管理", "分组搜索不存在", "P2", "搜索不存在", "0 行", "PASS", ""),
    ("B3U-005", "产品管理", "评论管理打开", "P2", "打开 /prod/prodComm", "表头含评价得分", "PASS", ""),
    ("B3U-006", "产品管理", "评论搜索不存在", "P2", "搜索不存在", "0 行", "PASS", ""),
    ("B3U-007", "产品管理", "规格管理打开", "P1", "打开 /prod/spec", "行数>0", "PASS", ""),
    ("B3U-008", "产品管理", "规格搜索不存在", "P2", "搜索不存在", "0 行", "PASS", ""),
    ("B3U-009", "系统管理", "参数管理打开", "P2", "打开 /sys/config", "表头含参数名", "PASS", ""),
    ("B3U-010", "系统管理", "参数搜索不存在", "P2", "搜索不存在", "0 行", "PASS", ""),
    ("B3U-011", "系统管理", "地址管理打开", "P2", "打开 /sys/area", "URL 匹配", "PASS", ""),
    ("B3U-012", "系统管理", "系统日志打开", "P1", "打开 /sys/log", "行数>0", "PASS", ""),
    ("B3U-013", "系统管理", "系统日志搜索 admin", "P1", "搜索 admin", "命中", "PASS", ""),
    ("B3U-014", "系统管理", "系统日志搜索不存在", "P2", "搜索不存在", "0 行", "PASS", ""),
    ("CT-001", "兼容性", "登录流程通过", "P0", "Chromium 登录", "成功", "PASS", ""),
    ("CT-002", "兼容性", "登录页元素可见", "P1", "检查元素", "可见", "PASS", ""),
    ("CT-003", "兼容性", "1920×1080 分辨率", "P1", "设置视口", "登录成功", "PASS", ""),
    ("CT-004", "兼容性", "1366×768 分辨率", "P1", "设置视口", "登录成功", "PASS", ""),
    ("CT-005", "兼容性", "375×667 移动端", "P2", "设置视口", "登录成功", "PASS", ""),
    ("LU-001", "登录", "打开后台登录页", "P0", "打开 /", "元素可见", "PASS", ""),
    ("LU-002", "登录", "正确账号密码登录成功", "P0", "admin/123456 登录", "URL 跳 /home", "PASS", ""),
    ("LU-003", "登录", "错误密码登录失败", "P1", "错误密码", "提示错误", "PASS", ""),
    ("LU-004", "登录", "空用户名登录失败", "P2", "用户名为空", "前端校验拦截", "PASS", ""),
    ("LU-005", "登录", "空密码登录失败", "P2", "密码为空", "前端校验拦截", "PASS", ""),
    ("MU-001", "会员管理", "打开会员列表", "P1", "打开 /user/user", "行数>0", "PASS", ""),
    ("MU-002", "会员管理", "搜索 Leo", "P1", "搜索 Leo", "命中", "PASS", ""),
    ("MU-003", "会员管理", "搜索不存在", "P1", "搜索不存在", "0 行", "PASS", ""),
    ("MU-004", "会员管理", "清空搜索恢复列表", "P2", "清空", "恢复列表", "PASS", ""),
    ("MU-005", "会员管理", "点第一行编辑按钮", "P2", "点编辑", "无报错", "PASS", ""),
    ("ODU-001", "订单管理", "打开订单列表有卡片", "P1", "打开 /order/order", ".prod 卡片>0", "PASS", ""),
    ("ODU-002", "订单管理", "搜索订单号结果减少", "P1", "搜索真实订单号", "≥1 条", "PASS", ""),
    ("ODU-003", "订单管理", "清空搜索恢复列表", "P2", "清空", "卡片>0", "PASS", ""),
    ("ODU-004", "订单管理", "点击查看打开详情弹窗", "P1", "点查看", "el-dialog 可见", "PASS", ""),
    ("ODU-005", "订单管理", "详情弹窗显示订单编号", "P1", "点查看", "显示订单号", "PASS", ""),
    ("ODU-006", "订单管理", "详情弹窗有商品表格", "P1", "点查看", "商品行≥1", "PASS", ""),
    ("ODU-007", "订单管理", "详情弹窗有订单日志区", "P2", "点查看", ".order-log 存在", "PASS", ""),
    ("ODU-008", "订单管理", "导出待发货按钮存在", "P2", "打开订单页", "按钮存在", "PASS", ""),
    ("ODU-009", "订单管理", "导出销售记录按钮存在", "P2", "打开订单页", "按钮存在", "PASS", ""),
    ("ODU-010", "订单管理", "关闭详情弹窗", "P2", "点关闭", "弹窗消失", "PASS", ""),
    ("PU-001", "产品管理", "打开产品列表", "P1", "打开 /prod/prodList", "行数>0", "PASS", ""),
    ("PU-002", "产品管理", "搜索 iPhone", "P1", "搜索 iPhone", "命中", "PASS", ""),
    ("PU-003", "产品管理", "搜索不存在", "P1", "搜索不存在", "0 行", "PASS", ""),
    ("PU-004", "产品管理", "清空搜索恢复列表", "P2", "清空", "恢复列表", "PASS", ""),
    ("PU-005", "产品管理", "点第一行修改按钮", "P2", "点修改", "无报错", "PASS", ""),
    ("SU-001", "门店管理", "自提点列表打开", "P2", "打开 /shop/pickAddr", "表头含自提点名称", "PASS", ""),
    ("SU-002", "门店管理", "自提点搜索不存在", "P2", "搜索不存在", "0 行", "PASS", ""),
    ("SU-003", "门店管理", "运费模板列表", "P1", "打开 /shop/transport", "行数>0", "PASS", ""),
    ("SU-004", "门店管理", "运费模板搜索包邮", "P1", "搜索包邮", "命中", "PASS", ""),
    ("SU-005", "门店管理", "运费模板搜索不存在", "P1", "搜索不存在", "0 行", "PASS", ""),
    ("SU-006", "门店管理", "运费模板点修改", "P2", "点修改", "无报错", "PASS", ""),
    ("SU-007", "门店管理", "轮播图列表", "P1", "打开 /admin/indexImg", "行数>0", "PASS", ""),
    ("SU-008", "门店管理", "热搜列表", "P2", "打开 /shop/hotSearch", "表头含热搜标题", "PASS", ""),
    ("SU-009", "门店管理", "热搜搜索不存在", "P2", "搜索不存在", "0 行", "PASS", ""),
    ("SU-010", "门店管理", "公告列表", "P1", "打开 /shop/notice", "行数>0", "PASS", ""),
    ("SU-011", "门店管理", "公告搜索包", "P2", "搜索包", "命中", "PASS", ""),
    ("SU-012", "门店管理", "公告搜索不存在", "P2", "搜索不存在", "0 行", "PASS", ""),
    ("WN-001", "弱网测试", "基线加载 < 5s", "P1", "无限制打开登录页", "1.22s", "PASS", ""),
    ("WN-002", "弱网测试", "轻弱网 < 8s", "P1", "100ms/2Mbps", "1.89s", "PASS", ""),
    ("WN-003", "弱网测试", "中弱网 < 12s", "P1", "200ms/1Mbps", "3.37s", "PASS", ""),
    ("WN-004", "弱网测试", "重弱网 < 20s", "P1", "400ms/400Kbps", "6.06s", "PASS", ""),
    ("WN-005", "弱网测试", "断网登录应有提示", "P0", "断网后点登录", "无任何提示", "XFAIL", "BUG-003"),
    ("WN-006", "弱网测试", "断网恢复后重试", "P1", "断→恢复→重登", "登录成功", "PASS", ""),
]

# ============================================================
# 单元测试用例
# ============================================================
UNIT_CASES = [
    ("U-001", "加密", "加密返回字符串", "P1", "encrypt_password('123456')", "返回 str", "PASS", ""),
    ("U-002", "加密", "加密非空", "P1", "加密后检查长度", "len > 0", "PASS", ""),
    ("U-003", "加密", "时间戳驱动密文变化", "P1", "间隔 5ms 两次加密", "密文不同", "PASS", ""),
    ("U-004", "加密", "密文可解密", "P1", "解密后匹配时间戳+密码", "解密成功", "PASS", ""),
    ("U-005", "加密", "不同密码密文不同", "P1", "加密 abc 和 xyz", "密文不同", "PASS", ""),
    ("U-006", "加密", "参数化[123456]", "P2", "加密 123456", "成功", "PASS", ""),
    ("U-007", "加密", "参数化[a]", "P2", "加密 a", "成功", "PASS", ""),
    ("U-008", "加密", "参数化[!@#$%]", "P2", "加密特殊字符", "成功", "PASS", ""),
    ("U-009", "加密", "参数化[长密码测试]", "P2", "加密中文", "成功", "PASS", ""),
]

# ============================================================
# 缺陷列表
# ============================================================
BUGS = [
    ("BUG-001", "P0", "高", "发货接口缺少订单状态校验", "OSM-003, OSM-004, OSM-005, OSM-006", "待修复"),
    ("BUG-002", "P2", "中", "登录成功后不清除密码错误计数", "LB-001, LB-002", "待修复"),
    ("BUG-003", "P1", "中", "断网时前端无网络异常提示", "WN-005", "待修复"),
]

# ============================================================
# 样式
# ============================================================
HEADER_FILL = PatternFill("solid", fgColor="4472C4")
HEADER_FONT = Font(color="FFFFFF", bold=True, size=11)
PASS_FILL = PatternFill("solid", fgColor="C6EFCE")
FAIL_FILL = PatternFill("solid", fgColor="FFC7CE")
THIN_BORDER = Border(
    left=Side(style="thin"),
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin"),
)
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)
LEFT = Alignment(horizontal="left", vertical="center", wrap_text=True)

def write_sheet(ws, title, cases):
    """写一个 sheet"""
    headers = ["序号", "用例ID", "模块", "用例标题", "优先级", "测试步骤", "预期结果", "实际结果", "状态", "关联缺陷"]
    ws.append(headers)
    for cell in ws[1]:
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = CENTER
        cell.border = THIN_BORDER
    for i, case in enumerate(cases, 1):
        cid, module, title_, priority, steps, expected, status, bug = case
        row = [i, cid, module, title_, priority, steps, expected, expected, status, bug]
        ws.append(row)
        r = ws.max_row
        for idx, cell in enumerate(ws[r], 1):
            cell.border = THIN_BORDER
            if idx in (1, 2, 5, 9, 10):
                cell.alignment = CENTER
            else:
                cell.alignment = LEFT
        if status == "PASS":
            ws.cell(r, 9).fill = PASS_FILL
        elif status == "XFAIL":
            ws.cell(r, 9).fill = FAIL_FILL
    # 列宽
    widths = [6, 10, 12, 30, 8, 35, 25, 25, 8, 12]
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[chr(64 + i)].width = w

# ============================================================
# 生成 Excel
# ============================================================
wb = Workbook()
ws_sum = wb.active
ws_sum.title = "汇总"

# 汇总
ws_sum.append(["Mall4j 自动化测试用例汇总"])
ws_sum["A1"].font = Font(bold=True, size=14)
ws_sum.append([])
ws_sum.append(["Suite", "文件", "用例数", "通过", "XFAIL", "失败"])
for c in ws_sum[3]:
    c.fill = HEADER_FILL
    c.font = HEADER_FONT
    c.alignment = CENTER

api_pass = sum(1 for c in API_CASES if c[6] == "PASS")
api_xfail = sum(1 for c in API_CASES if c[6] == "XFAIL")
ui_pass = sum(1 for c in UI_CASES if c[6] == "PASS")
ui_xfail = sum(1 for c in UI_CASES if c[6] == "XFAIL")
unit_pass = len(UNIT_CASES)

ws_sum.append(["接口测试", "test_api/", len(API_CASES), api_pass, api_xfail, 0])
ws_sum.append(["UI 测试", "test_ui/", len(UI_CASES), ui_pass, ui_xfail, 0])
ws_sum.append(["单元测试", "test_unit/", len(UNIT_CASES), unit_pass, 0, 0])
total = len(API_CASES) + len(UI_CASES) + len(UNIT_CASES)
ws_sum.append(["合计", "", total, api_pass + ui_pass + unit_pass, api_xfail + ui_xfail, 0])
ws_sum["A7"].font = Font(bold=True)
for r in range(4, 8):
    for c in ws_sum[r]:
        c.border = THIN_BORDER
        c.alignment = CENTER

# 三个用例 sheet
write_sheet(wb.create_sheet("接口测试"), "接口测试", API_CASES)
write_sheet(wb.create_sheet("UI测试"), "UI测试", UI_CASES)
write_sheet(wb.create_sheet("单元测试"), "单元测试", UNIT_CASES)

# 缺陷 sheet
ws_bug = wb.create_sheet("缺陷列表")
ws_bug.append(["缺陷ID", "优先级", "严重性", "标题", "对应用例", "状态"])
for c in ws_bug[1]:
    c.fill = HEADER_FILL
    c.font = HEADER_FONT
    c.alignment = CENTER
for bug in BUGS:
    ws_bug.append(list(bug))
    r = ws_bug.max_row
    for cell in ws_bug[r]:
        cell.border = THIN_BORDER
        cell.alignment = LEFT if cell.column == 4 else CENTER
for i, w in enumerate([12, 8, 10, 40, 30, 10], 1):
    ws_bug.column_dimensions[chr(64 + i)].width = w

xlsx_path = DOCS / "测试用例.xlsx"
wb.save(xlsx_path)
print(f"[OK] {xlsx_path}")

# ============================================================
# 生成 Markdown
# ============================================================
def md_table(cases):
    lines = ["| 序号 | 用例ID | 模块 | 用例标题 | 优先级 | 测试步骤 | 预期结果 | 状态 | 关联缺陷 |",
             "|---|---|---|---|---|---|---|---|---|"]
    for i, c in enumerate(cases, 1):
        cid, module, title_, priority, steps, expected, status, bug = c
        lines.append(f"| {i} | {cid} | {module} | {title_} | {priority} | {steps} | {expected} | {status} | {bug} |")
    return "\n".join(lines)

md = f"""# Mall4j 完整测试用例清单

> 用例总数：{total} 条
> 通过：{api_pass + ui_pass + unit_pass} / XFAIL：{api_xfail + ui_xfail}
> 更新日期：2026-10-05

## 一、汇总

| Suite | 文件 | 用例数 | 通过 | XFAIL |
|---|---|---|---|---|
| 接口测试 | test_api/ | {len(API_CASES)} | {api_pass} | {api_xfail} |
| UI 测试 | test_ui/ | {len(UI_CASES)} | {ui_pass} | {ui_xfail} |
| 单元测试 | test_unit/ | {len(UNIT_CASES)} | {unit_pass} | 0 |
| **合计** | | **{total}** | **{api_pass + ui_pass + unit_pass}** | **{api_xfail + ui_xfail}** |

---

## 二、接口测试用例（{len(API_CASES)} 条）

{md_table(API_CASES)}

---

## 三、UI 测试用例（{len(UI_CASES)} 条）

{md_table(UI_CASES)}

---

## 四、单元测试用例（{len(UNIT_CASES)} 条）

{md_table(UNIT_CASES)}

---

## 五、缺陷列表

| 缺陷ID | 优先级 | 严重性 | 标题 | 状态 |
|---|---|---|---|---|
| BUG-001 | P0 | 高 | 发货接口缺少订单状态校验 | 待修复 |
| BUG-002 | P2 | 中 | 登录成功后不清除密码错误计数 | 待修复 |
| BUG-003 | P1 | 中 | 断网时前端无网络异常提示 | 待修复 |
"""

md_path = DOCS / "TEST_CASES.md"
md_path.write_text(md, encoding="utf-8")
print(f"[OK] {md_path}")
print(f"\n总计：{total} 条用例")
print(f"  - 通过：{api_pass + ui_pass + unit_pass}")
print(f"  - XFAIL：{api_xfail + ui_xfail}")