#!/bin/bash
# ============================================================
# Mall4j 环境健康检查脚本（Linux 生产环境）
#
# ⚠️ 本脚本为 Linux 设计，Windows Git Bash 兼容性有限
#    Windows 本地开发请用: check_env.ps1
#
# 用法: bash check_env.sh
# ============================================================

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "============================================================"
echo "  Mall4j 环境健康检查"
echo "  时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "============================================================"

FAIL=0

# ---------- 1. 端口检查 ----------
echo ""
echo "[1/5] 端口检查"
for port in 6379 8085 8086 9527; do
    if netstat -tunlp 2>/dev/null | grep -q ":$port " || netstat -ano 2>/dev/null | grep -q ":$port "; then
        echo -e "  ${GREEN}[OK]${NC}   Port $port 已监听"
    else
        echo -e "  ${RED}[FAIL]${NC} Port $port 未监听"
        FAIL=$((FAIL+1))
    fi
done

# ---------- 2. MySQL 连通 ----------
echo ""
echo "[2/5] MySQL 连通性"
export MYSQL_PWD="Root@123456"
if mysql -h127.0.0.1 -P3307 -uroot -e "USE yami_shops; SELECT 1;" >/dev/null 2>&1; then
    COUNT=$(mysql -h127.0.0.1 -P3307 -uroot -N -e "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='yami_shops';" 2>/dev/null)
    echo -e "  ${GREEN}[OK]${NC}   MySQL 连通，yami_shops 有 $COUNT 张表"
else
    echo -e "  ${RED}[FAIL]${NC} MySQL 连接失败"
    FAIL=$((FAIL+1))
fi
unset MYSQL_PWD

# ---------- 3. Redis 连通 ----------
echo ""
echo "[3/5] Redis 连通性"
REDIS_CLI=""
for candidate in redis-cli /e/redis/redis-cli.exe "E:/redis/redis-cli.exe" "E:\\redis\\redis-cli.exe"; do
    if command -v "$candidate" >/dev/null 2>&1 || [ -f "$candidate" ]; then
        REDIS_CLI="$candidate"
        break
    fi
done

if [ -n "$REDIS_CLI" ]; then
    PONG=$($REDIS_CLI -h 127.0.0.1 -p 6379 ping 2>/dev/null | tr -d '\r')
    if [ "$PONG" = "PONG" ]; then
        KEYS=$($REDIS_CLI -h 127.0.0.1 -p 6379 dbsize 2>/dev/null | tr -d '\r')
        echo -e "  ${GREEN}[OK]${NC}   Redis 连通，当前 $KEYS 个 key"
    else
        echo -e "  ${RED}[FAIL]${NC} Redis 无响应"
        FAIL=$((FAIL+1))
    fi
else
    echo -e "  ${YELLOW}[SKIP]${NC} redis-cli 未找到（尝试过 redis-cli / E:/redis/redis-cli.exe）"
fi

# ---------- 4. 磁盘空间 ----------
echo ""
echo "[4/5] 磁盘空间"
if df -h / >/dev/null 2>&1; then
    df -h / | tail -1 | awk '{print "  根分区使用率: "$5}'
else
    # Windows Git Bash 用 C 盘
    df -h /c 2>/dev/null | tail -1 | awk '{print "  C 盘使用率: "$5}'
fi

# ---------- 5. 内存 ----------
echo ""
echo "[5/5] 内存"
if command -v free >/dev/null 2>&1; then
    free -h | awk 'NR<=2'
else
    echo "  [SKIP] free 命令不可用（Windows 环境）"
fi

# ---------- 汇总 ----------
echo ""
echo "============================================================"
if [ $FAIL -eq 0 ]; then
    echo -e "  ${GREEN}全部通过${NC}"
else
    echo -e "  ${RED}发现 $FAIL 个问题${NC}"
fi
echo "============================================================"
exit $FAIL
