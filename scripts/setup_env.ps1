# AutoFactoryScope Development Environment Setup
# Windows PowerShell Script

param(
    [switch]$SkipFrontend,
    [switch]$SkipBackend,
    [string]$PythonVersion = "3.11"
)

$ErrorActionPreference = "Stop"

Write-Host "=== AutoFactoryScope Environment Setup ===" -ForegroundColor Cyan

# Repo root
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

# 1. BACKEND SETUP
if (-not $SkipBackend) {
    Write-Host "`n[1/2] Setting up Python backend..." -ForegroundColor Yellow

    $BackendPath = Join-Path $RepoRoot "src\backend\autofactoryscope_api"

    if (-not (Test-Path $BackendPath)) {
        Write-Error "Backend path not found: $BackendPath"
        exit 1
    }

    Set-Location $BackendPath

    # Check Python version
    $CurrentPython = python --version 2>&1
    Write-Host "  Python version: $CurrentPython" -ForegroundColor Gray

    # Create virtual environment
    if (-not (Test-Path ".venv")) {
        Write-Host "  Creating virtual environment..." -ForegroundColor Gray
        python -m venv .venv
    } else {
        Write-Host "  Virtual environment already exists" -ForegroundColor Gray
    }

    # Activate venv
    .\.venv\Scripts\Activate.ps1

    # Upgrade pip
    Write-Host "  Upgrading pip..." -ForegroundColor Gray
    python -m pip install --upgrade pip -q

    # Install dependencies
    Write-Host "  Installing dependencies..." -ForegroundColor Gray
    pip install -r requirements.txt -q

    # Install training dependencies (optional)
    Write-Host "  Installing training dependencies (ultralytics, PaddleOCR)..." -ForegroundColor Gray
    pip install ultralytics paddleocr -q

    Write-Host "  ✓ Backend setup complete" -ForegroundColor Green

    # Deactivate venv
    deactivate

    Set-Location $RepoRoot
}

# 2. FRONTEND SETUP
if (-not $SkipFrontend) {
    Write-Host "`n[2/2] Setting up TypeScript/React frontend..." -ForegroundColor Yellow

    $FrontendPath = Join-Path $RepoRoot "src\frontend\autofactoryscope-web"

    if (-not (Test-Path $FrontendPath)) {
        Write-Error "Frontend path not found: $FrontendPath"
        exit 1
    }

    Set-Location $FrontendPath

    # Check Node version
    $NodeVersion = node --version 2>&1
    Write-Host "  Node version: $NodeVersion" -ForegroundColor Gray

    if ($NodeVersion -notmatch "v20") {
        Write-Warning "  Node.js 20+ recommended (current: $NodeVersion)"
    }

    # Install dependencies
    Write-Host "  Installing npm dependencies..." -ForegroundColor Gray
    npm install

    Write-Host "  ✓ Frontend setup complete" -ForegroundColor Green

    Set-Location $RepoRoot
}

# 3. CREATE MODELS DIRECTORY
Write-Host "`nCreating models directory..." -ForegroundColor Yellow
$ModelsPath = Join-Path $RepoRoot "models"
if (-not (Test-Path $ModelsPath)) {
    New-Item -ItemType Directory -Path $ModelsPath | Out-Null
    New-Item -ItemType File -Path (Join-Path $ModelsPath ".gitkeep") | Out-Null
}

Write-Host "`n=== Setup Complete ===" -ForegroundColor Cyan
Write-Host "`nNext Steps:" -ForegroundColor Gray
Write-Host "  1. Train model (see notebooks/01_train_yolo11.ipynb)"
Write-Host "  2. Export to ONNX (see notebooks/02_export_onnx.ipynb)"
Write-Host "  3. Place robot_detector.onnx in models/"
Write-Host "  4. Start backend: cd src\backend\autofactoryscope_api && .\.venv\Scripts\Activate.ps1 && uvicorn autofactoryscope_api.main:app --reload"
Write-Host "  5. Start frontend: cd src\frontend\autofactoryscope-web && npm run dev"
