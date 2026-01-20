# Complete Testing and Finalization Script
# Tests detection with optimal threshold and updates configuration

$ErrorActionPreference = "Stop"

Write-Host "╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  AutoFactoryScope - Final Testing & Configuration   ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Write-Host "This script will:" -ForegroundColor Yellow
Write-Host "  1. Test detection with threshold 0.23" -ForegroundColor Gray
Write-Host "  2. Verify we get 23 robots (floor-mounted only)" -ForegroundColor Gray
Write-Host "  3. Update config.py if successful" -ForegroundColor Gray
Write-Host ""

# Check if backend is running
Write-Host "Checking backend status..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 3
    Write-Host "  Backend is running" -ForegroundColor Green
    Write-Host "  Current model loaded: $($health.model_loaded)" -ForegroundColor Gray
} catch {
    Write-Host "  ERROR: Backend not responding!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please start the backend with:" -ForegroundColor Yellow
    Write-Host '  $env:AFS_CONFIDENCE_THRESHOLD="0.23"' -ForegroundColor White
    Write-Host '  $env:AFS_NMS_IOU_THRESHOLD="0.40"' -ForegroundColor White
    Write-Host '  .\scripts\start_backend.ps1' -ForegroundColor White
    Write-Host ""
    Write-Host "Then run this script again." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Running detection test..." -ForegroundColor Yellow

# Run Python test script
python test_models_comparison.py

Write-Host ""
$response = Read-Host "Did the test show exactly 23 detections? (yes/no)"

if ($response -eq "yes") {
    Write-Host ""
    Write-Host "Updating default configuration..." -ForegroundColor Green

    # Update config.py
    $configPath = "src\backend\autofactoryscope_api\config.py"
    $config = Get-Content $configPath -Raw

    # Update confidence threshold
    $config = $config -replace 'confidence_threshold: float = 0\.25', 'confidence_threshold: float = 0.23'

    # Update NMS threshold
    $config = $config -replace 'nms_iou_threshold: float = 0\.5', 'nms_iou_threshold: float = 0.40'

    Set-Content $configPath -Value $config

    Write-Host "  ✓ Updated confidence_threshold to 0.23" -ForegroundColor Green
    Write-Host "  ✓ Updated nms_iou_threshold to 0.40" -ForegroundColor Green
    Write-Host ""
    Write-Host "Configuration finalized!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Restart backend normally: .\scripts\start_backend.ps1" -ForegroundColor Gray
    Write-Host "  2. Test on other PDFs to validate" -ForegroundColor Gray
    Write-Host "  3. Consider retraining with track robots for 24/24 detection" -ForegroundColor Gray

} elseif ($response -eq "no") {
    Write-Host ""
    Write-Host "Optimization needed. Current detection count is not 23." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Actions to try:" -ForegroundColor Cyan
    Write-Host "  - If TOO MANY (>23): Raise threshold to 0.24 or 0.25" -ForegroundColor Gray
    Write-Host "  - If TOO FEW (<23): Lower threshold to 0.22 or 0.21" -ForegroundColor Gray
    Write-Host ""
    Write-Host "To test different threshold:" -ForegroundColor Yellow
    Write-Host '  1. Stop backend (Ctrl+C)' -ForegroundColor Gray
    Write-Host '  2. $env:AFS_CONFIDENCE_THRESHOLD="0.XX"' -ForegroundColor Gray
    Write-Host '  3. .\scripts\start_backend.ps1' -ForegroundColor Gray
    Write-Host '  4. Run this script again' -ForegroundColor Gray

} else {
    Write-Host ""
    Write-Host "Please restart and answer 'yes' or 'no'" -ForegroundColor Yellow
}

Write-Host ""
