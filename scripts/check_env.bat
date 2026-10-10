@echo off
echo Running Mall4j env check in WSL2...
wsl -d Ubuntu -- bash -c "cd /mnt/e/mall4j-ui-api-autotest/scripts/shell && ./check_env.sh"
pause