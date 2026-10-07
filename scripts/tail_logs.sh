#!/bin/bash
# Mall4j 日志查看脚本
LOG_DIR="${LOG_DIR:-/var/log/mall4j}"

if [ ! -d "$LOG_DIR" ]; then
    LOG_DIR="E:/mall4j-master/logs"
fi

case "$1" in
    api)
        echo "查看 API 日志 (Ctrl+C 退出)"
        tail -f "$LOG_DIR/api.log"
        ;;
    admin)
        echo "查看 Admin 日志 (Ctrl+C 退出)"
        tail -f "$LOG_DIR/admin.log"
        ;;
    error)
        echo "实时过滤 ERROR / Exception"
        tail -f "$LOG_DIR"/*.log | grep -E "ERROR|Exception|Caused by" --color=auto
        ;;
    grep)
        if [ -z "$2" ]; then
            echo "用法: bash tail_logs.sh grep <keyword>"
            exit 1
        fi
        tail -f "$LOG_DIR"/*.log | grep --color=auto "$2"
        ;;
    last-error)
        echo "最近 50 条错误日志"
        grep -h "ERROR" "$LOG_DIR"/*.log 2>/dev/null | tail -50
        ;;
    *)
        echo "用法: bash tail_logs.sh {api|admin|error|grep <kw>|last-error}"
        ;;
esac