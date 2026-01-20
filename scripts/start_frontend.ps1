# Start AutoFactoryScope Frontend

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$FrontendPath = Join-Path $RepoRoot "src\frontend\autofactoryscope-web"

Write-Host "=== Starting AutoFactoryScope Frontend ===" -ForegroundColor Cyan
Write-Host ""

Set-Location $FrontendPath

Write-Host "╔══════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║        AutoFactoryScope Frontend Starting...         ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Write-Host "Frontend will be available at:" -ForegroundColor Cyan
Write-Host "  http://localhost:5173" -ForegroundColor White
Write-Host ""

Write-Host "Make sure backend is running:" -ForegroundColor Yellow
Write-Host "  .\scripts\start_backend.ps1" -ForegroundColor Gray
Write-Host ""

Write-Host "Press Ctrl+C to stop the dev server" -ForegroundColor Gray
Write-Host ""

# Start Vite dev server
npm run dev
