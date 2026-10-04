@echo off
chcp 65001 >nul
cd /d E:\mall4j-ui-api-autotest
call venv\Scripts\activate.bat
python -m pytest testcases/test_ui/ -v --alluredir=reports/allure-results
pause