# Switch to Cole's YOLOv8s Model and Test
# Cole's model: 120 epochs, hyperparameter tuning, better accuracy

$ErrorActionPreference = "Stop"

$RepoRoot = $PSScriptRoot
$ModelsDir = Join-Path $RepoRoot "models"

Write-Host "╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     Switching to Cole's YOLOv8s Model                ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check if Cole's model exists
$ColeModel = Join-Path $ModelsDir "robot_detector_cole.onnx"
if (-not (Test-Path $ColeModel)) {
    Write-Host "ERROR: Cole's model not found!" -ForegroundColor Red
    Write-Host "Expected: $ColeModel" -ForegroundColor Gray
    exit 1
}

Write-Host "Cole's Model Info:" -ForegroundColor Yellow
$coleSize = (Get-Item $ColeModel).Length / 1MB
Write-Host "  Size: $($coleSize.ToString('F2')) MB" -ForegroundColor Gray
Write-Host "  Training: 120 epochs with hyperparameter tuning" -ForegroundColor Gray
Write-Host "  Architecture: YOLOv8s (small)" -ForegroundColor Gray
Write-Host ""

# Backup current model if it exists
$CurrentModel = Join-Path $ModelsDir "robot_detector.onnx"
if (Test-Path $CurrentModel) {
    $BackupModel = Join-Path $ModelsDir "robot_detector_yolov11n_backup.onnx"

    Write-Host "Backing up current model..." -ForegroundColor Yellow
    Copy-Item $CurrentModel $BackupModel -Force
    Write-Host "  ✓ Backup saved: robot_detector_yolov11n_backup.onnx" -ForegroundColor Green
    Write-Host ""
}

# Copy Cole's model
Write-Host "Installing Cole's model as active model..." -ForegroundColor Yellow
Copy-Item $ColeModel $CurrentModel -Force
Write-Host "  ✓ Cole's model installed" -ForegroundColor Green
Write-Host ""

Write-Host "╔══════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║     Model Switch Complete!                           ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Start backend: .\scripts\start_backend.ps1" -ForegroundColor White
Write-Host "  2. Test detection: python test_annotated.py" -ForegroundColor White
Write-Host ""
Write-Host "Note: Cole's model may need different threshold tuning." -ForegroundColor Gray
Write-Host "      Start with default 0.27 and adjust if needed." -ForegroundColor Gray
Write-Host ""

# Ask if user wants to start backend now
$response = Read-Host "Start backend now? (yes/no)"
if ($response -eq "yes") {
    Write-Host ""
    Write-Host "Starting backend with Cole's model..." -ForegroundColor Green
    Write-Host ""

    & "$RepoRoot\scripts\start_backend.ps1"
}
