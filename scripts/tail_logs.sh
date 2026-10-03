# -*- coding: utf-8 -*-
"""写入 tail_logs.sh"""
from pathlib import Path

content = '''#!/bin/bash
# Mall4j 日志查看脚本
LOG_DIR="${LOG_DIR:-/var/log/mall4j}"

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
        grep -h "ERROR" "$LOG_DIR"/*.log | tail -50
        ;;
    *)
        echo "用法:"
        echo "  bash tail_logs.sh api"
        echo "  bash tail_logs.sh admin"
        echo "  bash tail_logs.sh error"
        echo "  bash tail_logs.sh grep <keyword>"
        echo "  bash tail_logs.sh last-error"
        ;;
esac
'''

path = Path(r"E:\\mall4j-ui-api-autotest") / "scripts" / "tail_logs.sh"
path.write_text(content, encoding="utf-8", newline="\\n")
print(f"[OK] {path}  ({len(content)} bytes)")