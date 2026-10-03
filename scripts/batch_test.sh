#!/bin/bash
# ============================================================
# Mall4j 批量跑测试 + 归档
# 用法:
#   bash batch_test.sh            跑全部
#   bash batch_test.sh api        只跑接口
#   bash batch_test.sh ui         只跑 UI
# ============================================================

PROJECT_DIR="E:/mall4j-ui-api-autotest"
cd "$PROJECT_DIR" || exit 1

DATE=$(date +%Y%m%d_%H%M%S)
REPORT_DIR="reports/allure-results"

echo "============================================================"
echo "  Mall4j 批量测试 ($DATE)"
echo "============================================================"

# 前置清理
bash scripts/clean_test_data.sh

case "${1:-all}" in
    api)
        echo ""
        echo ">>> 只跑接口测试"
        python -m pytest testcases/test_api/ -q \
            --ignore=testcases/test_api/test_zzz_login_rate_limit.py \
            --alluredir=$REPORT_DIR
        ;;
    ui)
        echo ""
        echo ">>> 只跑 UI 测试"
        python -m pytest testcases/test_ui/ -q --alluredir=$REPORT_DIR
        ;;
    all)
        echo ""
        echo ">>> 接口测试"
        python -m pytest testcases/test_api/ -q \
            --ignore=testcases/test_api/test_zzz_login_rate_limit.py \
            --alluredir=$REPORT_DIR

        echo ""
        echo ">>> UI 测试"
        python -m pytest testcases/test_ui/ -q --alluredir=$REPORT_DIR

        echo ""
        echo ">>> 限流测试（独立跑）"
        python -m pytest testcases/test_api/test_zzz_login_rate_limit.py -q \
            --alluredir=$REPORT_DIR
        ;;
    *)
        echo "用法: bash batch_test.sh {api|ui|all}"
        exit 1
        ;;
esac

# 归档
echo ""
echo ">>> 归档报告"
mkdir -p reports/archive
tar -czf reports/archive/run_$DATE.tar.gz $REPORT_DIR 2>/dev/null
echo "  归档: reports/archive/run_$DATE.tar.gz"

# 清理 7 天前的归档
find reports/archive -name "run_*.tar.gz" -mtime +7 -delete 2>/dev/null
echo "  已清理 7 天前的归档"

echo ""
echo "============================================================"
echo "  完成！查看报告: allure serve $REPORT_DIR"
echo "============================================================"