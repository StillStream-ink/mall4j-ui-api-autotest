#!/bin/bash
# Mall4j 日志轮转脚本
# 用途：压缩 7 天前日志，删除 30 天前归档

LOG_DIRS=(
    "/mnt/e/mall4j-ui-api-autotest/logs"
    "/mnt/e/mall4j-ui-api-autotest/reports"
)

echo "=========================================="
echo "  Mall4j 日志轮转"
echo "  时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="

for LOG_DIR in "${LOG_DIRS[@]}"; do
    if [ ! -d "${LOG_DIR}" ]; then
        echo "⚠️  目录不存在，跳过: ${LOG_DIR}"
        continue
    fi

    echo ""
    echo "📂 处理目录: ${LOG_DIR}"

    # 1. 压缩 7 天以上的 .log 文件
    COMPRESSED=0
    while IFS= read -r logfile; do
        gzip "${logfile}"
        COMPRESSED=$((COMPRESSED + 1))
    done < <(find "${LOG_DIR}" -name "*.log" -mtime +7 -type f 2>/dev/null)
    echo "  🗜️  压缩 7 天前日志: ${COMPRESSED} 个"

    # 2. 删除 30 天以上的 .gz 文件
    DELETED=$(find "${LOG_DIR}" -name "*.gz" -mtime +30 -type f -delete -print 2>/dev/null | wc -l)
    echo "  🗑️  删除 30 天前归档: ${DELETED} 个"

    # 3. 统计当前占用
    if [ -d "${LOG_DIR}" ]; then
        SIZE=$(du -sh "${LOG_DIR}" 2>/dev/null | cut -f1)
        echo "  💾 当前占用: ${SIZE}"
    fi
done

echo ""
echo "=========================================="
echo "  轮转完成"
echo "=========================================="