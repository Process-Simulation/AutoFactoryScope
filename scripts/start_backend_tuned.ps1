# Start AutoFactoryScope Backend with Tuned Detection Parameters
# Uses lower thresholds to detect more robots

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$BackendDir = Join-Path $RepoRoot "src\backend"
$ApiPath = Join-Path $BackendDir "autofactoryscope_api"

Write-Host "=== Starting AutoFactoryScope Backend (Tuned Detection) ===" -ForegroundColor Cyan
Write-Host ""

# Set environment variables for tuned detection
$env:AFS_CONFIDENCE_THRESHOLD = "0.20"  # Lower from 0.25 to catch more robots
$env:AFS_NMS_IOU_THRESHOLD = "0.40"     # Lower from 0.50 to avoid merging close robots

Write-Host "Detection Parameters:" -ForegroundColor Yellow
Write-Host "  Confidence Threshold: $env:AFS_CONFIDENCE_THRESHOLD (default: 0.25)" -ForegroundColor Gray
Write-Host "  NMS IoU Threshold: $env:AFS_NMS_IOU_THRESHOLD (default: 0.50)" -ForegroundColor Gray
Write-Host ""
Write-Host "These lower thresholds should detect more robots!" -ForegroundColor Green
Write-Host ""

# Check if model exists
$ModelPath = Join-Path $RepoRoot "models\robot_detector.onnx"
if (-not (Test-Path $ModelPath)) {
    Write-Host "⚠ WARNING: ONNX model not found!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  API will start but /detect endpoint will fail." -ForegroundColor Yellow
    Write-Host "  Train model first (see TRAIN_NOW.md)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Press any key to continue anyway..." -ForegroundColor Gray
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# Change to backend directory (parent of autofactoryscope_api)
Set-Location $BackendDir

# Activate venv
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\autofactoryscope_api\.venv\Scripts\Activate.ps1

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║      AutoFactoryScope API Starting (Tuned)...        ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Write-Host "API will be available at:" -ForegroundColor Cyan
Write-Host "  http://localhost:8000" -ForegroundColor White
Write-Host "  http://localhost:8000/docs (Swagger UI)" -ForegroundColor White
Write-Host ""

Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Start uvicorn
uvicorn autofactoryscope_api.main:app --reload
