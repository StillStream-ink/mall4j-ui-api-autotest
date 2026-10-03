#!/bin/bash
# ============================================================
# 清理 Mall4j 测试产生的脏数据
# 清理范围：
#   MySQL: autotest_ 前缀的 config/role，au_ 前缀的 user
#   Redis: 限流 key
# ============================================================

DB_HOST="127.0.0.1"
DB_PORT="3307"
DB_USER="root"
DB_PWD="Root@123456"
DB_NAME="yami_shops"

echo "============================================================"
echo "  Mall4j 测试数据清理"
echo "============================================================"

# ---------- MySQL 清理 ----------
echo ""
echo "[1/2] 清理 MySQL 测试数据"

mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PWD $DB_NAME <<EOF 2>/dev/null
SELECT '待清理 config:' AS msg, COUNT(*) AS cnt FROM tz_sys_config WHERE param_key LIKE 'autotest_%';
SELECT '待清理 role:' AS msg, COUNT(*) AS cnt FROM tz_sys_role WHERE role_name LIKE 'autotest_%';
SELECT '待清理 user:' AS msg, COUNT(*) AS cnt FROM tz_sys_user WHERE username LIKE 'au_%';
EOF

mysql -h$DB_HOST -P$DB_PORT -u$DB_USER -p$DB_PWD $DB_NAME <<EOF 2>/dev/null
DELETE FROM tz_sys_config WHERE param_key LIKE 'autotest_%';
DELETE FROM tz_sys_role WHERE role_name LIKE 'autotest_%';
DELETE FROM tz_sys_user WHERE username LIKE 'au_%';
EOF

if [ $? -eq 0 ]; then
    echo "  [OK] MySQL 清理完成"
else
    echo "  [FAIL] MySQL 清理失败"
fi

# ---------- Redis 清理 ----------
echo ""
echo "[2/2] 清理 Redis 限流 key"

if command -v redis-cli >/dev/null 2>&1; then
    KEYS=$(redis-cli -h 127.0.0.1 -p 6379 keys "*checkUserInputErrorPassword*" 2>/dev/null)
    if [ -n "$KEYS" ]; then
        echo "$KEYS" | while read k; do
            redis-cli -h 127.0.0.1 -p 6379 del "$k" >/dev/null
            echo "  已删除: $k"
        done
    else
        echo "  [OK] 无残留限流 key"
    fi
else
    echo "  [SKIP] redis-cli 未安装"
fi

echo ""
echo "============================================================"
echo "  清理完成"
echo "============================================================"