# AMADOP Blogging Platform - Run All Services
Write-Host "Starting all AMADOP services..." -ForegroundColor Green

# Set environment variables
$env:DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/amadop_db"
$env:SECRET_KEY = "your-secret-key-change-this-in-production-min-32-chars"
$env:ALGORITHM = "HS256"
$env:ACCESS_TOKEN_EXPIRE_MINUTES = "30"
$env:CORS_ORIGINS = "http://localhost:5173"
$env:AUTH_SERVICE_URL = "http://localhost:8001"
$env:POST_SERVICE_URL = "http://localhost:8002"
$env:COMMENT_SERVICE_URL = "http://localhost:8003"
$env:NOTIFICATION_SERVICE_URL = "http://localhost:8004"

Write-Host "`nStarting services in background..." -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow

# Start Auth Service
Write-Host "`n[1/5] Starting Auth Service on port 8001..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend\auth_service'; .\venv\Scripts\Activate.ps1; `$env:DATABASE_URL='$env:DATABASE_URL'; `$env:SECRET_KEY='$env:SECRET_KEY'; uvicorn main:app --host 0.0.0.0 --port 8001 --reload"

Start-Sleep -Seconds 2

# Start Post Service
Write-Host "[2/5] Starting Post Service on port 8002..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend\post_service'; .\venv\Scripts\Activate.ps1; `$env:DATABASE_URL='$env:DATABASE_URL'; `$env:AUTH_SERVICE_URL='$env:AUTH_SERVICE_URL'; uvicorn main:app --host 0.0.0.0 --port 8002 --reload"

Start-Sleep -Seconds 2

# Start Comment Service
Write-Host "[3/5] Starting Comment Service on port 8003..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend\comment_service'; .\venv\Scripts\Activate.ps1; `$env:DATABASE_URL='$env:DATABASE_URL'; `$env:AUTH_SERVICE_URL='$env:AUTH_SERVICE_URL'; `$env:NOTIFICATION_SERVICE_URL='$env:NOTIFICATION_SERVICE_URL'; uvicorn main:app --host 0.0.0.0 --port 8003 --reload"

Start-Sleep -Seconds 2

# Start Notification Service
Write-Host "[4/5] Starting Notification Service on port 8004..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend\notification_service'; .\venv\Scripts\Activate.ps1; `$env:DATABASE_URL='$env:DATABASE_URL'; uvicorn main:app --host 0.0.0.0 --port 8004 --reload"

Start-Sleep -Seconds 2

# Start Frontend
Write-Host "[5/5] Starting Frontend on port 5173..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; npm run dev"

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "All services started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`nServices are running at:" -ForegroundColor Yellow
Write-Host "  Frontend:     http://localhost:5173" -ForegroundColor Cyan
Write-Host "  Auth API:     http://localhost:8001" -ForegroundColor Cyan
Write-Host "  Post API:     http://localhost:8002" -ForegroundColor Cyan
Write-Host "  Comment API:  http://localhost:8003" -ForegroundColor Cyan
Write-Host "  Notification: http://localhost:8004" -ForegroundColor Cyan
Write-Host "`nHealth checks:" -ForegroundColor Yellow
Write-Host "  http://localhost:8001/health" -ForegroundColor Cyan
Write-Host "  http://localhost:8002/health" -ForegroundColor Cyan
Write-Host "  http://localhost:8003/health" -ForegroundColor Cyan
Write-Host "  http://localhost:8004/health" -ForegroundColor Cyan
Write-Host "`nPress any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
