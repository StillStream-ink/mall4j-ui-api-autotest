# Mall4j - Start all services
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Mall4j - Start all services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Path config
$API_DIR   = "E:\mall4j-master\yami-shop-api"
$ADMIN_DIR = "E:\mall4j-master\yami-shop-admin"
$UNI_DIR   = "E:\mall4j-master\mall4uni"
$VUE_DIR   = "E:\mall4j-master\front-end\mall4v"

Write-Host ""
Write-Host "Starting Buyer API (8086)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$API_DIR'; mvn spring-boot:run"
Start-Sleep -Seconds 2

Write-Host "Starting Admin API (8085)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ADMIN_DIR'; mvn spring-boot:run"
Start-Sleep -Seconds 2

Write-Host "Starting Buyer H5 (80)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$UNI_DIR'; pnpm run dev:h5"
Start-Sleep -Seconds 2

Write-Host "Starting Admin Vue (9527)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$VUE_DIR'; pnpm run dev"

Write-Host ""
Write-Host "4 services launched. Waiting 30 seconds..." -ForegroundColor Green
Start-Sleep -Seconds 30

Write-Host ""
Write-Host "Port check:" -ForegroundColor Cyan

$ok = 0
$ports = @(8086, 8085, 80, 9527)
foreach ($p in $ports) {
    $result = netstat -ano | Select-String ":$p .*LISTENING"
    if ($result) {
        Write-Host "  [OK] Port $p running" -ForegroundColor Green
        $ok = $ok + 1
    } else {
        Write-Host "  [X]  Port $p NOT running" -ForegroundColor Red
    }
}

Write-Host ""
if ($ok -eq 4) {
    Write-Host "All services up. Ready to test!" -ForegroundColor Green
} else {
    Write-Host "Some services failed. Check the windows above." -ForegroundColor Yellow
}