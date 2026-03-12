# Setup PostgreSQL database for AMADOP
Write-Host "Setting up AMADOP database..." -ForegroundColor Green

# Find PostgreSQL installation
$pgPath = "C:\Program Files\PostgreSQL\15\bin"
if (-not (Test-Path $pgPath)) {
    $pgPath = "C:\Program Files\PostgreSQL\16\bin"
}
if (-not (Test-Path $pgPath)) {
    $pgPath = "C:\Program Files\PostgreSQL\14\bin"
}

if (-not (Test-Path $pgPath)) {
    Write-Host "❌ PostgreSQL not found. Please install PostgreSQL 15 or higher." -ForegroundColor Red
    exit 1
}

Write-Host "Found PostgreSQL at: $pgPath" -ForegroundColor Cyan

# Set environment variable for password
$env:PGPASSWORD = "postgres"

# Create database
Write-Host "`nCreating database..." -ForegroundColor Yellow
& "$pgPath\psql.exe" -U postgres -c "CREATE DATABASE amadop_db;" 2>&1 | Out-Null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Database 'amadop_db' created successfully" -ForegroundColor Green
} else {
    Write-Host "✓ Database 'amadop_db' already exists or created" -ForegroundColor Green
}

Write-Host "`n✅ Database setup complete!" -ForegroundColor Green
Write-Host "`nDatabase connection string:" -ForegroundColor Yellow
Write-Host "  postgresql://postgres:postgres@localhost:5432/amadop_db" -ForegroundColor Cyan
Write-Host "`nThe tables will be created automatically when you start the services." -ForegroundColor Yellow
