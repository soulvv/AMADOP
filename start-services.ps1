# AMADOP Blogging Platform - Service Startup Script
Write-Host "Starting AMADOP Blogging Platform..." -ForegroundColor Green

# Check if PostgreSQL is running
Write-Host "`nChecking PostgreSQL..." -ForegroundColor Yellow
$pgService = Get-Service -Name "postgresql-x64-15" -ErrorAction SilentlyContinue
if ($pgService -and $pgService.Status -eq "Running") {
    Write-Host "PostgreSQL is running" -ForegroundColor Green
} else {
    Write-Host "Starting PostgreSQL service..." -ForegroundColor Yellow
    Start-Service -Name "postgresql-x64-15" -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 3
}

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

Write-Host "`nInstalling backend dependencies..." -ForegroundColor Yellow

# Install Auth Service dependencies
Write-Host "Setting up Auth Service..." -ForegroundColor Cyan
Set-Location backend/auth_service
if (-not (Test-Path "venv")) {
    python -m venv venv
}
.\venv\Scripts\Activate.ps1
pip install -q -r requirements.txt
deactivate
Set-Location ../..

# Install Post Service dependencies
Write-Host "Setting up Post Service..." -ForegroundColor Cyan
Set-Location backend/post_service
if (-not (Test-Path "venv")) {
    python -m venv venv
}
.\venv\Scripts\Activate.ps1
pip install -q -r requirements.txt
deactivate
Set-Location ../..

# Install Comment Service dependencies
Write-Host "Setting up Comment Service..." -ForegroundColor Cyan
Set-Location backend/comment_service
if (-not (Test-Path "venv")) {
    python -m venv venv
}
.\venv\Scripts\Activate.ps1
pip install -q -r requirements.txt
deactivate
Set-Location ../..

# Install Notification Service dependencies
Write-Host "Setting up Notification Service..." -ForegroundColor Cyan
Set-Location backend/notification_service
if (-not (Test-Path "venv")) {
    python -m venv venv
}
.\venv\Scripts\Activate.ps1
pip install -q -r requirements.txt
deactivate
Set-Location ../..

# Install Frontend dependencies
Write-Host "`nSetting up Frontend..." -ForegroundColor Cyan
Set-Location frontend
if (-not (Test-Path "node_modules")) {
    npm install
}
Set-Location ..

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "`nTo start all services, run:" -ForegroundColor Yellow
Write-Host "  .\run-all-services.ps1" -ForegroundColor Cyan
Write-Host "`nOr start services individually in separate terminals:" -ForegroundColor Yellow
Write-Host "  cd backend/auth_service && .\venv\Scripts\Activate.ps1 && uvicorn main:app --port 8001 --reload" -ForegroundColor Cyan
Write-Host "  cd backend/post_service && .\venv\Scripts\Activate.ps1 && uvicorn main:app --port 8002 --reload" -ForegroundColor Cyan
Write-Host "  cd backend/comment_service && .\venv\Scripts\Activate.ps1 && uvicorn main:app --port 8003 --reload" -ForegroundColor Cyan
Write-Host "  cd backend/notification_service && .\venv\Scripts\Activate.ps1 && uvicorn main:app --port 8004 --reload" -ForegroundColor Cyan
Write-Host "  cd frontend && npm run dev" -ForegroundColor Cyan
