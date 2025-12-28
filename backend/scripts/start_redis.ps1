# PowerShell script to help start Redis on Windows
# This script provides multiple options for starting Redis

Write-Host "=== Redis Setup for Herfa ===" -ForegroundColor Cyan
Write-Host ""

# Check if Redis is already running
try {
    $response = Test-NetConnection -ComputerName localhost -Port 6379 -InformationLevel Quiet -WarningAction SilentlyContinue
    if ($response) {
        Write-Host "✓ Redis is already running on port 6379" -ForegroundColor Green
        exit 0
    }
} catch {
    # Continue to setup options
}

Write-Host "Redis is not running. Choose an option:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Option 1: Use Docker (if installed)" -ForegroundColor White
Write-Host "  docker run -d -p 6379:6379 --name redis redis" -ForegroundColor Gray
Write-Host ""
Write-Host "Option 2: Install Redis for Windows" -ForegroundColor White
Write-Host "  Download from: https://github.com/microsoftarchive/redis/releases" -ForegroundColor Gray
Write-Host "  Or use WSL2: wsl sudo apt-get install redis-server" -ForegroundColor Gray
Write-Host ""
Write-Host "Option 3: Use Redis Cloud (Free tier)" -ForegroundColor White
Write-Host "  Sign up at: https://redis.com/try-free/" -ForegroundColor Gray
Write-Host "  Update CELERY_BROKER_URL in settings.py" -ForegroundColor Gray
Write-Host ""
Write-Host "Option 4: Use Memurai (Redis-compatible for Windows)" -ForegroundColor White
Write-Host "  Download from: https://www.memurai.com/get-memurai" -ForegroundColor Gray
Write-Host ""

# Check if WSL is available
$wslAvailable = Get-Command wsl -ErrorAction SilentlyContinue
if ($wslAvailable) {
    Write-Host "WSL detected. You can install Redis in WSL:" -ForegroundColor Cyan
    Write-Host "  wsl sudo apt-get update" -ForegroundColor Gray
    Write-Host "  wsl sudo apt-get install redis-server" -ForegroundColor Gray
    Write-Host "  wsl sudo service redis-server start" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "For development, you can also:" -ForegroundColor Yellow
Write-Host "  1. Comment out Celery tasks temporarily" -ForegroundColor Gray
Write-Host "  2. Use a cloud Redis service (free tier available)" -ForegroundColor Gray
Write-Host ""

