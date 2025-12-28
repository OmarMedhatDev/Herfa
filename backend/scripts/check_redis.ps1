# Quick script to check if Redis is running
Write-Host "Checking Redis connection..." -ForegroundColor Cyan

try {
    $connection = Test-NetConnection -ComputerName localhost -Port 6379 -InformationLevel Quiet -WarningAction SilentlyContinue
    if ($connection) {
        Write-Host "[OK] Redis is running on localhost:6379" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Redis is NOT running on localhost:6379" -ForegroundColor Red
        Write-Host ""
        Write-Host "To start Redis, choose one of these options:" -ForegroundColor Yellow
        Write-Host "  1. Use Docker: docker run -d -p 6379:6379 redis" -ForegroundColor Gray
        Write-Host "  2. Install Redis for Windows from GitHub" -ForegroundColor Gray
        Write-Host "  3. Use WSL: wsl sudo service redis-server start" -ForegroundColor Gray
        Write-Host "  4. Use Redis Cloud (free tier): https://redis.com/try-free/" -ForegroundColor Gray
        Write-Host ""
        Write-Host "Run: .\backend\scripts\start_redis.ps1 for more options" -ForegroundColor Cyan
    }
} catch {
    Write-Host "[ERROR] Cannot check Redis connection" -ForegroundColor Red
    Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Gray
}
