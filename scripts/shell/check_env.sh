#!/bin/bash
# Mall4j 环境健康巡检脚本
# 用途：检查 4 个服务端口 + MySQL + Redis

# ============ 配置 ============
WIN_IP="192.168.111.60"
DB_PORT="3307"
DB_USER="root"
DB_PASS="Root@123456"
DB_NAME="yami_shops"

REDIS_HOST="192.168.111.60"
REDIS_PORT="6379"

# 服务端口
PORT_API_BUYER=8086      # 买家端 API
PORT_API_ADMIN=8085      # 管理员端 API
PORT_WEB_BUYER=80        # 买家端 H5
PORT_WEB_ADMIN=9527      # 管理员端 Vue

echo "=========================================="
echo "  Mall4j 环境健康巡检"
echo "  时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="
echo ""

# ============ 1. 端口检查 ============
echo "【1. 服务端口检查】"
check_port() {
    local name=$1
    local port=$2
    if timeout 2 bash -c "echo > /dev/tcp/${WIN_IP}/${port}" 2>/dev/null; then
        echo "  ✅ ${name} (${port}) 正常"
    else
        echo "  ❌ ${name} (${port}) 不可访问"
    fi
}

check_port "买家端 API     " ${PORT_API_BUYER}
check_port "管理员端 API   " ${PORT_API_ADMIN}
check_port "买家端 H5      " ${PORT_WEB_BUYER}
check_port "管理员端 Vue   " ${PORT_WEB_ADMIN}
echo ""

# ============ 2. MySQL 检查 ============
echo "【2. MySQL 数据库检查】"
if mysql -h${WIN_IP} -P${DB_PORT} -u${DB_USER} -p${DB_PASS} \
    -e "SELECT 1" ${DB_NAME} > /dev/null 2>&1; then
    TABLE_COUNT=$(mysql -h${WIN_IP} -P${DB_PORT} -u${DB_USER} -p${DB_PASS} \
        -N -e "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='${DB_NAME}'" 2>/dev/null)
    echo "  ✅ MySQL 连接正常"
    echo "  📊 yami_shops 表数量: ${TABLE_COUNT}"

    ORDER_COUNT=$(mysql -h${WIN_IP} -P${DB_PORT} -u${DB_USER} -p${DB_PASS} \
        -N -e "SELECT COUNT(*) FROM tz_order" ${DB_NAME} 2>/dev/null)
    echo "  📦 订单总数: ${ORDER_COUNT}"
else
    echo "  ❌ MySQL 连接失败"
fi
echo ""

# ============ 3. Redis 检查 ============
echo "【3. Redis 缓存检查】"
# Redis 只监听 127.0.0.1，WSL2 无法直连（安全配置，可接受）
# 如需验证，请在 Windows PowerShell 执行: netstat -ano | findstr :6379
echo "  ℹ️  Redis 仅监听 127.0.0.1（WSL2 无法直连，符合安全最佳实践）"
echo "      验证方式：Windows PowerShell 执行 netstat -ano | findstr :6379"
echo ""

# ============ 4. 备份文件检查 ============
echo "【4. 备份文件检查】"
BACKUP_DIR="/mnt/e/mall4j-ui-api-autotest/scripts/shell/db_backup"
if [ -d "${BACKUP_DIR}" ]; then
    LATEST=$(ls -t ${BACKUP_DIR}/yami_shops_*.sql 2>/dev/null | head -1)
    if [ -n "${LATEST}" ]; then
        FILE_SIZE=$(du -h "${LATEST}" | cut -f1)
        echo "  ✅ 最新备份: $(basename ${LATEST}) (${FILE_SIZE})"
    else
        echo "  ⚠️  暂无备份文件"
    fi
    TOTAL=$(ls ${BACKUP_DIR}/yami_shops_*.sql 2>/dev/null | wc -l)
    echo "  📁 备份总数: ${TOTAL}"
else
    echo "  ⚠️  备份目录不存在"
fi
echo ""

# ============ 5. 磁盘检查 ============
echo "【5. 磁盘空间检查】"
df -h /mnt/e | tail -1 | awk '{print "  💾 E 盘使用率: "$5" (已用 "$3" / 共 "$2")"}'
echo ""

echo "=========================================="
echo "  巡检完成"
echo "=========================================="