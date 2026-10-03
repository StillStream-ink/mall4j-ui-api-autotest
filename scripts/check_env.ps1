# Mall4j 环境检查
Write-Host "=== Mall4j 环境检查 ==="

Write-Host ""
Write-Host "[1/5] 端口"
foreach ($port in @(6379, 8085, 8086, 9527)) {
    $r = Test-NetConnection 127.0.0.1 -Port $port -WarningAction SilentlyContinue
    if ($r.TcpTestSucceeded) {
        Write-Host "  OK   $port"
    } else {
        Write-Host "  FAIL $port"
    }
}

Write-Host ""
Write-Host "[2/5] MySQL 服务"
$mysql = Get-Service MySQL80 -ErrorAction SilentlyContinue
if ($mysql -and $mysql.Status -eq "Running") {
    Write-Host "  OK   Running"
} else {
    Write-Host "  FAIL Not Running"
}

Write-Host ""
Write-Host "[3/5] Redis 进程"
$redis = Get-Process redis-server -ErrorAction SilentlyContinue
if ($redis) {
    Write-Host "  OK   Running"
} else {
    Write-Host "  FAIL Not Running"
}

Write-Host ""
Write-Host "[4/5] Java 进程"
$java = Get-Process java -ErrorAction SilentlyContinue
if ($java) {
    $n = @($java).Count
} else {
    $n = 0
}
Write-Host "  Count: $n"

Write-Host ""
Write-Host "[5/5] 磁盘"
$disk = Get-PSDrive E -ErrorAction SilentlyContinue
if ($disk) {
    $total = $disk.Used + $disk.Free
    $pct = [math]::Round(100 * $disk.Used / $total, 0)
    Write-Host "  Usage: $pct"
}

Write-Host ""
Write-Host "=== Done ==="