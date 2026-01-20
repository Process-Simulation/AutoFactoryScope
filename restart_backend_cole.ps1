# Restart Backend with Cole's Model
# Ensures clean start with default thresholds

$ErrorActionPreference = "Stop"

Write-Host "╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     Restarting Backend with Cole's Model             ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Clear any environment variable overrides
$env:AFS_CONFIDENCE_THRESHOLD = $null
$env:AFS_NMS_IOU_THRESHOLD = $null

Write-Host "Using default config.py settings:" -ForegroundColor Yellow
Write-Host "  confidence_threshold: 0.27" -ForegroundColor Gray
Write-Host "  nms_iou_threshold: 0.40" -ForegroundColor Gray
Write-Host ""

Write-Host "Model: Cole's YOLOv8s (43MB)" -ForegroundColor Yellow
Write-Host "  Location: models/robot_detector.onnx" -ForegroundColor Gray
Write-Host ""

Write-Host "Starting backend..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host ""

Set-Location "$PSScriptRoot\src\backend"

# Activate venv and start
& .\autofactoryscope_api\.venv\Scripts\Activate.ps1
uvicorn autofactoryscope_api.main:app --reload
