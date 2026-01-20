# Export PyTorch model to ONNX format

$ErrorActionPreference = "Stop"

Write-Host "=== Export Model to ONNX ===" -ForegroundColor Cyan

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

# Check if best.pt exists
$ModelPath = "models\best.pt"
if (-not (Test-Path $ModelPath)) {
    Write-Host "✗ PyTorch model not found: $ModelPath" -ForegroundColor Red
    Write-Host ""
    Write-Host "Run first: .\scripts\download_model.ps1" -ForegroundColor Gray
    exit 1
}

Write-Host ""
Write-Host "✓ Found PyTorch model: $ModelPath" -ForegroundColor Green

# Activate backend venv
$VenvPath = "src\backend\autofactoryscope_api\.venv\Scripts\Activate.ps1"
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& $VenvPath

# Install ultralytics if needed
Write-Host ""
Write-Host "Checking for ultralytics..." -ForegroundColor Yellow

$HasUltralytics = python -c "import ultralytics; print('OK')" 2>&1
if ($HasUltralytics -notmatch "OK") {
    Write-Host "Installing ultralytics..." -ForegroundColor Yellow
    pip install ultralytics -q
}

Write-Host "✓ Ultralytics available" -ForegroundColor Green

# Export to ONNX using Python script
Write-Host ""
Write-Host "Exporting to ONNX..." -ForegroundColor Yellow

$ExportScript = @"
from ultralytics import YOLO
from pathlib import Path

# Load PyTorch model
model_path = Path('models/best.pt')
model = YOLO(model_path)

print(f'Loaded model: {model_path}')

# Export to ONNX
onnx_path = model.export(
    format='onnx',
    imgsz=512,
    dynamic=False,
    simplify=True,
    opset=12,
)

print(f'ONNX export complete: {onnx_path}')

# Rename to expected name
final_path = Path('models/robot_detector.onnx')
Path(onnx_path).rename(final_path)

print(f'Final model: {final_path}')
print(f'File size: {final_path.stat().st_size / 1024 / 1024:.2f} MB')
print('✓ Export successful!')
"@

$ExportScript | python

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║            ✓ ONNX EXPORT COMPLETE!                   ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Write-Host "Model ready for production:" -ForegroundColor Cyan
Write-Host "  $RepoRoot\models\robot_detector.onnx" -ForegroundColor Gray
Write-Host ""

Write-Host "Next: Test the API" -ForegroundColor Cyan
Write-Host "  1. Start backend: .\scripts\start_backend.ps1" -ForegroundColor Gray
Write-Host "  2. Start frontend: .\scripts\start_frontend.ps1" -ForegroundColor Gray
Write-Host "  3. Open: http://localhost:5173" -ForegroundColor Gray
Write-Host ""

deactivate
