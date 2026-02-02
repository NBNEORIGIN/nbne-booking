# Quick start script for NBNE Booking (PowerShell)

Write-Host "Starting NBNE Booking..." -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Host "✓ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "Error: Docker is not running. Please start Docker Desktop first." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Start containers
Write-Host "Starting containers..." -ForegroundColor Cyan
docker-compose up -d

Write-Host ""
Write-Host "Waiting for services to be ready..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

# Check health
Write-Host ""
Write-Host "Checking API health..." -ForegroundColor Cyan

$maxAttempts = 30
$attempt = 0
$healthy = $false

while ($attempt -lt $maxAttempts) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 2
        if ($response.StatusCode -eq 200) {
            $healthy = $true
            break
        }
    } catch {
        # Continue trying
    }
    $attempt++
    Start-Sleep -Seconds 2
}

if ($healthy) {
    Write-Host "✓ API is healthy!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Services running:" -ForegroundColor Cyan
    Write-Host "  - API: http://localhost:8000"
    Write-Host "  - API Docs: http://localhost:8000/docs"
    Write-Host "  - Health: http://localhost:8000/health"
    Write-Host ""
    Write-Host "View logs: docker-compose logs -f" -ForegroundColor Yellow
    exit 0
} else {
    Write-Host "✗ API health check timed out. Check logs with: docker-compose logs" -ForegroundColor Red
    exit 1
}
