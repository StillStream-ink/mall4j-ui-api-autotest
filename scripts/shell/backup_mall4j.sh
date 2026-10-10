#!/bin/bash
# Mall4j 数据库自动备份脚本
# 用途：每日备份 yami_shops 数据库，保留最近 30 天

set -e

# ============ 配置 ============
DB_HOST="192.168.111.60"
DB_PORT="3307"
DB_USER="root"
DB_PASS="Root@123456"
DB_NAME="yami_shops"

BACKUP_DIR="/mnt/e/mall4j-ui-api-autotest/scripts/shell/db_backup"
LOG_FILE="/mnt/e/mall4j-ui-api-autotest/scripts/shell/backup_run.log"

# ============ 初始化 ============
[ ! -d "${BACKUP_DIR}" ] && mkdir -p "${BACKUP_DIR}"

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/yami_shops_${DATE}.sql"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 开始备份 ${DB_NAME} ..." >> "${LOG_FILE}"

# ============ 执行备份 ============
if mysqldump -h${DB_HOST} -P${DB_PORT} -u${DB_USER} -p${DB_PASS} \
    --single-transaction --routines --triggers \
    ${DB_NAME} > "${BACKUP_FILE}" 2>/dev/null; then

    FILE_SIZE=$(du -h "${BACKUP_FILE}" | cut -f1)
    echo "✅ 备份成功：${BACKUP_FILE} (${FILE_SIZE})" | tee -a "${LOG_FILE}"
else
    echo "❌ 备份失败" | tee -a "${LOG_FILE}"
    exit 1
fi

# ============ 清理 30 天前的备份 ============
DELETED=$(find "${BACKUP_DIR}" -name "yami_shops_*.sql" -mtime +30 -print -delete | wc -l)
if [ "${DELETED}" -gt 0 ]; then
    echo "🗑️ 清理了 ${DELETED} 个过期备份" | tee -a "${LOG_FILE}"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] 备份任务完成" >> "${LOG_FILE}"
echo "---" >> "${LOG_FILE}"