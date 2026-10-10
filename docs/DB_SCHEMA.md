# 数据库结构文档

> 库名：`yami_shops`（MySQL 8.0，端口 3307）
> 项目：Mall4j 电商系统

---

## 一、核心表清单

| 表名 | 用途 | 测试引用 |
|---|---|---|
| `tz_sys_user` | 管理员 | RBAC、CRUD |
| `tz_sys_role` | 角色 | RBAC、CRUD |
| `tz_sys_user_role` | 用户-角色关联 | RBAC |
| `tz_sys_role_menu` | 角色-菜单关联 | RBAC |
| `tz_sys_menu` | 菜单 | RBAC |
| `tz_sys_config` | 系统参数 | CRUD、DB 断言 |
| `tz_order` | 订单主表 | 状态机、DB 断言 |
| `tz_order_item` | 订单明细 | 多表关联 |
| `tz_user` | 会员 | 会员模块 |
| `tz_prod` | 商品 | 产品模块 |

---

## 二、关键表结构

### 2.1 tz_order（订单主表）

| 字段 | 类型 | 说明 |
|---|---|---|
| order_id | bigint | 主键 |
| order_number | varchar | 业务订单号 |
| status | tinyint | 1待付款 2待发货 3待收货 4待评价 5已完成 6失败 |
| total | decimal | 商品总额 |
| actual_total | decimal | 实付金额 |
| dvy_id | bigint | 快递公司 ID |
| dvy_flow_id | varchar | 快递单号 |
| dvy_time | datetime | 发货时间 |
| create_time | datetime | 下单时间 |

### 2.2 tz_order_item（订单项）

| 字段 | 类型 | 说明 |
|---|---|---|
| order_item_id | bigint | 主键 |
| order_number | varchar | 关联订单 |
| prod_id | bigint | 商品 ID |
| price | decimal | 单价 |
| prod_count | int | 数量 |

关联：`tz_order_item.order_number` → `tz_order.order_number`

### 2.3 tz_sys_config（系统参数）

| 字段 | 类型 | 说明 |
|---|---|---|
| id | bigint | 主键 |
| param_key | varchar | 参数键 |
| param_value | varchar | 参数值 |
| remark | varchar | 备注 |

测试约定：`autotest_` 前缀，测完自动清理。

### 2.4 tz_basket（购物车）

| 字段 | 类型 | 说明 |
|---|---|---|
| basket_id | bigint | 主键 |
| shop_id | bigint | 店铺 ID |
| prod_id | bigint | 商品 ID |
| sku_id | bigint | SKU ID |
| user_id | varchar | 买家 ID |
| basket_count | int | 数量（**注意：不是 prod_count**） |
| basket_date | datetime | 加入时间 |

### 2.5 tz_user_addr（收货地址）

| 字段 | 类型 | 说明 |
|---|---|---|
| addr_id | bigint | 主键 |
| user_id | varchar | 买家 ID |
| receiver | varchar | 收货人 |
| mobile | varchar | 手机号 |
| detail_address | varchar | 详细地址 |

---

### 2.6 库存分两层说明

Mall4j 的库存分两层，**改库存时两张表都要改**：

| 表 | 字段 | 用途 |
|---|---|---|
| `tz_prod` | `total_stocks` | **下单校验用**（真正决定能否下单） |
| `tz_sku` | `stocks` | SKU 总库存（展示用） |
| `tz_sku` | `actual_stocks` | SKU 实际可售库存 |

---

## 三、多表关联关系
tz_sys_user --< tz_sys_user_role >-- tz_sys_role --< tz_sys_role_menu >-- tz_sys_menu

tz_order --< tz_order_item
| |
| +-- prod_id -> tz_prod
|
+-- order_number（业务主键）


---

## 四、测试数据约定

| 前缀 | 用途 | 清理 |
|---|---|---|
| `autotest_` | 参数、角色 | scripts/clean_test_data.sh |
| `au_` | 管理员 | 同上 |
| 无前缀 | 系统内置数据 | 绝不修改 |

---

## 五、面试可讲点

1. **接口 + DB 双重断言**：接口返回成功 ≠ 数据落库
2. **多表关联校验**：订单金额 = SUM(订单项)，用户权限 = 多表 JOIN
3. **孤儿记录巡检**：LEFT JOIN + WHERE IS NULL
4. **测试数据隔离**：autotest_ 前缀 + 自动清理
5. **事务陷阱**：pymysql autocommit=False 导致 REPEATABLE READ 快照，改 autocommit=True
