@echo off
echo Running Mall4j backup in WSL2...
wsl -d Ubuntu -- bash -c "cd /mnt/e/mall4j-ui-api-autotest/scripts/shell && ./backup_mall4j.sh"
pause