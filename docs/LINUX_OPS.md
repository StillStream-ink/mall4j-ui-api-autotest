# 测试环境运维文档

> 项目：Mall4j UI + API 自动化测试
> 运维环境：WSL2 Ubuntu + Windows PowerShell
> 更新日期：2026-10-10

---

## 一、运维体系总览

Mall4j 测试环境涉及 4 个服务 + MySQL + Redis，运维体系包含 3 个 Shell 脚本 + 2 套定时方案。

| 脚本 | 位置 | 用途 |
|---|---|---|
| backup_mall4j.sh | scripts/shell/ | 数据库备份，保留 30 天 |
| check_env.sh | scripts/shell/ | 一键巡检 6 项 |
| rotate_logs.sh | scripts/shell/ | 日志轮转 |

| 定时方案 | 位置 | 用途 |
|---|---|---|
| WSL2 crontab | /var/spool/cron/crontabs/root | WSL2 常驻时执行 |
| Windows 任务计划 | Mall4j-DailyBackup | WSL2 关闭时兜底 |

---

## 二、环境健康检查

### 2.1 一键巡检

```
cd /mnt/e/mall4j-ui-api-autotest/scripts/shell
./check_env.sh
```

**检查项（6 项）：**

- 4 个服务端口：8086（买家端 API）/ 8085（管理员端 API）/ 80（买家端 H5）/ 9527（管理员端 Vue）
- MySQL：连接 + 表数量 + 订单总数
- Redis：端口监听状态
- 备份文件：最新备份 + 总数
- JMeter 脚本：是否存在
- 磁盘：E 盘使用率

**巡检输出示例：**

```
==========================================
  Mall4j 环境健康巡检
  时间: 2026-10-10 16:12:51
==========================================

【1. 服务端口检查】
  ✅ 买家端 API      (8086) 正常
  ✅ 管理员端 API    (8085) 正常
  ✅ 买家端 H5       (80) 正常
  ✅ 管理员端 Vue    (9527) 正常

【2. MySQL 数据库检查】
  ✅ MySQL 连接正常
  📊 yami_shops 表数量: 43
  📦 订单总数: 50

【3. Redis 缓存检查】
  ℹ️  Redis 仅监听 127.0.0.1（WSL2 无法直连，符合安全最佳实践）
      验证方式：Windows PowerShell 执行 netstat -ano | findstr :6379

【4. 备份文件检查】
  ✅ 最新备份: yami_shops_20261009_160300.sql (572K)
  📁 备份总数: 2

【5. 磁盘空间检查】
  💾 E 盘使用率: 8% (已用 14G / 共 188G)

==========================================
  巡检完成
==========================================
```

**用到的命令：**

- bash -c "echo > /dev/tcp/HOST/PORT" —— 端口连通性测试
- mysql -h HOST -P PORT -u USER -pPASS -e "SQL" —— 数据库查询
- du -h / df -h —— 磁盘和文件大小
- ls -t —— 按时间排序取最新

---

## 三、数据库备份

### 3.1 手动备份

```
cd /mnt/e/mall4j-ui-api-autotest/scripts/shell
./backup_mall4j.sh
```

备份文件命名：yami_shops_YYYYMMDD_HHMMSS.sql

**备份策略：**

- mysqldump 整库备份
- --single-transaction 保证一致性
- --routines --triggers 包含存储过程和触发器
- 自动保留最近 30 天，超过自动删除

### 3.2 恢复数据库

```
# 从指定备份恢复
mysql -h 192.168.111.60 -P 3307 -u root -pRoot@123456 yami_shops \
    < /mnt/e/mall4j-ui-api-autotest/scripts/shell/db_backup/yami_shops_20261009_160300.sql
```

### 3.3 验证备份可用

```
# 看 SQL 文件头（确认不是空文件）
head -20 db_backup/yami_shops_20261009_160300.sql

# 应该看到：
# -- MySQL dump 10.13  Distrib 8.0.46, for Linux (x86_64)
# -- Host: 192.168.111.60    Database: yami_shops
# /*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
```

### 3.4 备份脚本核心逻辑

```
#!/bin/bash
DB_HOST="192.168.111.60"
DB_PORT="3307"
DB_USER="root"
DB_PASS="Root@123456"
DB_NAME="yami_shops"

BACKUP_DIR="/mnt/e/mall4j-ui-api-autotest/scripts/shell/db_backup"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/yami_shops_${DATE}.sql"

[ ! -d "${BACKUP_DIR}" ] && mkdir -p "${BACKUP_DIR}"

mysqldump -h${DB_HOST} -P${DB_PORT} -u${DB_USER} -p${DB_PASS} \
    --single-transaction --routines --triggers \
    ${DB_NAME} > "${BACKUP_FILE}"

# 自动清理 30 天前的备份
find "${BACKUP_DIR}" -name "yami_shops_*.sql" -mtime +30 -delete
```

---

## 四、日志轮转

```
cd /mnt/e/mall4j-ui-api-autotest/scripts/shell
./rotate_logs.sh
```

**处理目录：**

- /mnt/e/mall4j-ui-api-autotest/logs（应用日志）
- /mnt/e/mall4j-ui-api-autotest/reports（测试报告）

**策略：**

- 7 天前的 .log 文件自动 gzip 压缩
- 30 天前的 .gz 文件自动删除
- 输出当前目录占用

**输出示例：**

```
📂 处理目录: /mnt/e/mall4j-ui-api-autotest/logs
  🗜️  压缩 7 天前日志: 0 个
  🗑️  删除 30 天前归档: 0 个
  💾 当前占用: 28M
```

---

## 五、定时任务

### 5.1 WSL2 crontab

```
# 编辑
crontab -e

# 查看
crontab -l
```

**配置内容：**

```
# ============ Mall4j 定时任务 ============

# 每天凌晨 2 点备份数据库
0 2 * * * /mnt/e/mall4j-ui-api-autotest/scripts/shell/backup_mall4j.sh >> /mnt/e/mall4j-ui-api-autotest/scripts/shell/backup_run.log 2>&1

# 每周日凌晨 3 点日志轮转
0 3 * * 0 /mnt/e/mall4j-ui-api-autotest/scripts/shell/rotate_logs.sh >> /mnt/e/mall4j-ui-api-autotest/scripts/shell/rotate_run.log 2>&1

# 每天早 9 点环境巡检
0 9 * * * /mnt/e/mall4j-ui-api-autotest/scripts/shell/check_env.sh >> /mnt/e/mall4j-ui-api-autotest/scripts/shell/check_run.log 2>&1
```

**实测：** 加一条 * * * * * 测试任务，连续 3 分钟写入 3 条时间戳，验证 crontab 正常工作。

### 5.2 Windows 任务计划程序

**为什么需要：** WSL2 关闭后 crontab 不跑，生产环境必须用 Windows 兜底。

**创建任务（管理员 PowerShell）：**

```
$action = New-ScheduledTaskAction `
    -Execute "wsl.exe" `
    -Argument "-d Ubuntu -- bash -c '/mnt/e/mall4j-ui-api-autotest/scripts/shell/backup_mall4j.sh'"

$trigger = New-ScheduledTaskTrigger -Daily -At 2am

Register-ScheduledTask `
    -TaskName "Mall4j-DailyBackup" `
    -Action $action `
    -Trigger $trigger `
    -Description "Mall4j 每日数据库备份"
```

**验证：**

```
Get-ScheduledTask -TaskName "Mall4j-DailyBackup"
Start-ScheduledTask -TaskName "Mall4j-DailyBackup"
Start-Sleep -Seconds 30
Get-Content E:\mall4j-ui-api-autotest\scripts\shell\backup_run.log -Tail 5
```

**实测：** 手动触发后 30 秒内生成 572K 备份文件。

---

## 六、一键快捷脚本（Windows）

双击即可执行：

| 文件 | 用途 |
|---|---|
| scripts\check_env.bat | 一键巡检（调 WSL2 脚本） |
| scripts\backup_db.bat | 一键备份（调 WSL2 脚本） |
| scripts\start_all.ps1 | 一键启动 4 个服务 |
| scripts\stop_all.ps1 | 一键关闭所有服务 |

**check_env.bat 内容：**

```
@echo off
chcp 65001 > nul
echo Running Mall4j env check in WSL2...
wsl -d Ubuntu -- bash -c "cd /mnt/e/mall4j-ui-api-autotest/scripts/shell && ./check_env.sh"
pause
```

---

## 七、常用命令速查

### 7.1 进程 / 端口

```
# WSL2 查端口（通过 Windows IP）
timeout 2 bash -c "echo > /dev/tcp/192.168.111.60/8086" && echo "OK"

# Windows 查端口
netstat -ano | findstr :8086

# 查 Java 进程（Windows）
jps -l
```

### 7.2 MySQL

```
# WSL2 连 Windows MySQL
mysql -h 192.168.111.60 -P 3307 -u root -pRoot@123456

# 查表字符集
SELECT TABLE_NAME, TABLE_COLLATION FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'yami_shops';

# 查订单数
SELECT COUNT(*) FROM tz_order;
```

### 7.3 Redis

```
# WSL2 清 Redis（用 Python）
python -c "import redis; redis.Redis(host='192.168.111.60', port=6379, db=0, protocol=2).flushdb()"

# Windows 查 Redis
netstat -ano | findstr :6379
```

### 7.4 日志

```
# 实时看
tail -f /mnt/e/mall4j-ui-api-autotest/logs/autotest.log

# 看最后 100 行
tail -100 autotest.log

# 过滤 ERROR
grep -n "ERROR" autotest.log

# 统计错误数
grep -c "ERROR" autotest.log
```

### 7.5 磁盘

```
df -h /mnt/e           # E 盘使用率
du -sh /mnt/e/mall4j-ui-api-autotest/logs  # 日志目录大小
```

---

## 八、常见问题排查

| 问题 | 原因 | 解决 |
|---|---|---|
| WSL2 无法连 MySQL | Host 'xxx' is not allowed | MySQL 里 UPDATE mysql.user SET host='%' WHERE user='root' |
| WSL2 无法连 MySQL | 防火墙拦截 | 管理员 PowerShell New-NetFirewallRule -LocalPort 3307 ... |
| Redis 巡检失败 | 只监听 127.0.0.1 | 不改（安全配置），脚本里输出说明而非报错 |
| crontab 不自动执行 | WSL2 未启用 systemd | /etc/wsl.conf 加 [boot] + systemd=true |
| crontab 关闭 WSL2 后不跑 | WSL2 已知限制 | 配 Windows 任务计划程序兜底 |
| E 盘 /mnt/e 丢失 | WSL2 挂载失效 | wsl --shutdown 后重进；或 sudo mount -t drvfs E: /mnt/e |

---

## 九、踩坑记录

| 坑 | 问题 | 根因 | 解决 |
|---|---|---|---|
| 坑 1 | WSL2 无法连通宿主机 MySQL | WSL2 回环地址指向子系统自身 | 用 Windows 局域网 IP 192.168.111.60 |
| 坑 2 | MySQL 报 Host is not allowed | MySQL 权限表只有 root@localhost | UPDATE mysql.user SET host='%' WHERE user='root' |
| 坑 3 | crontab 不自动执行 | 旧版 WSL2 无 systemd | /etc/wsl.conf 加 [boot] + systemd=true |
| 坑 4 | WSL2 关闭后定时任务不跑 | WSL2 已知限制 | Windows 任务计划程序兜底 |
| 坑 5 | E 盘挂载丢失 | WSL2 重启后挂载失效 | wsl --shutdown 或手动 mount -t drvfs |
| 坑 6 | MySQL 表存不了 Emoji | 表级字符集 utf8mb3 | 建议 ALTER TABLE ... CONVERT TO utf8mb4（未执行，保留 BUG-004 现场） |

---

## 十、与 OpenCart 项目的运维差异

| 维度 | OpenCart 项目 | Mall4j 项目 |
|---|---|---|
| 部署方式 | XAMPP（Apache + MariaDB 单服务） | 4 个独立服务（8085/8086/80/9527） |
| 数据库 | MariaDB | MySQL 8.0（端口 3307） |
| 运维脚本环境 | WSL2 Ubuntu | WSL2 Ubuntu |
| 巡检对象 | Apache + MySQL + 备份 | 4 个端口 + MySQL + Redis + 备份 + JMeter + 磁盘 |
| 定时方案 | crontab | crontab + Windows 任务计划程序（双方案） |

**核心差异：** Mall4j 是分布式部署（前后端分离 + 双端），巡检需覆盖 4 个端口，比 OpenCart 单体架构复杂。
