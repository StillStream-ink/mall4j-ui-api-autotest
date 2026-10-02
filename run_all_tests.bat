@echo off
chcp 65001 >nul
cd /d E:\mall4j-ui-api-autotest

echo ============================================================
echo   Mall4j UI + API 自动化测试
echo ============================================================
echo.

call venv\Scripts\activate.bat

set BROWSER=chromium
set HEADLESS=true
set SLOW_MO=0

echo [1/4] 清理旧报告 + Redis 限流 key...
if exist reports\allure-results rmdir /s /q reports\allure-results
mkdir reports\allure-results

cd /d E:\redis
redis-cli.exe del "1checkUserInputErrorPassword_0:0:0:0:0:0:0:1admin" 2>nul
redis-cli.exe del "1checkUserInputErrorPassword_0:0:0:0:0:0:0:1ADMIN" 2>nul
cd /d E:\mall4j-ui-api-autotest

echo.
echo [2/4] 接口测试（不含限流测试，串行）...
python -m pytest testcases\test_api\ -v --alluredir=reports\allure-results ^
  --ignore=testcases\test_api\test_zzz_login_rate_limit.py

echo.
echo [3/4] UI 测试（串行）...
python -m pytest testcases\test_ui\ -v --alluredir=reports\allure-results

echo.
echo [4/4] 限流测试（独立跑，跑完自动清 Redis）...
python -m pytest testcases\test_api\test_zzz_login_rate_limit.py -v --alluredir=reports\allure-results

cd /d E:\redis
redis-cli.exe del "1checkUserInputErrorPassword_0:0:0:0:0:0:0:1admin" 2>nul
redis-cli.exe del "1checkUserInputErrorPassword_0:0:0:0:0:0:0:1ADMIN" 2>nul
cd /d E:\mall4j-ui-api-autotest

echo.
echo ============================================================
echo   完成！查看报告： allure serve reports\allure-results
echo ============================================================
pause
