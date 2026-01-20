# AutoFactoryScope: One-Click Training Setup
# This script prepares everything for Colab training

$ErrorActionPreference = "Stop"

Write-Host "╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   AutoFactoryScope - Training Setup Assistant       ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$RepoRoot = $PSScriptRoot

# Step 1: Copy notebook to Drive
Write-Host "[1/5] Copying training notebook to Google Drive..." -ForegroundColor Yellow

$NotebookSource = Join-Path $RepoRoot "notebooks\01_train_yolo11_drive.ipynb"
$NotebookDest = "G:\My Drive\AutoFactoryScope\01_train_yolo11_drive.ipynb"

if (Test-Path "G:\My Drive\AutoFactoryScope") {
    Copy-Item $NotebookSource -Destination $NotebookDest -Force
    Write-Host "  ✓ Notebook copied to Google Drive" -ForegroundColor Green
} else {
    Write-Host "  ✗ Google Drive not found at G:\My Drive\" -ForegroundColor Red
    Write-Host "    Please map Google Drive or copy manually." -ForegroundColor Gray
}

# Step 2: Verify dataset location
Write-Host "`n[2/5] Verifying dataset location..." -ForegroundColor Yellow

$DatasetPath = "G:\My Drive\AutoFactoryScope\robot_detection_layouts.v2i.yolov8 (1)"
if (Test-Path $DatasetPath) {
    $ImageCount = (Get-ChildItem "$DatasetPath\**\*.jpg" -Recurse -ErrorAction SilentlyContinue).Count
    Write-Host "  ✓ Dataset found: $ImageCount images" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Dataset not found in Drive" -ForegroundColor Yellow
    Write-Host "    Expected: $DatasetPath" -ForegroundColor Gray
}

# Step 3: Create models directory
Write-Host "`n[3/5] Preparing models directory..." -ForegroundColor Yellow

$ModelsDir = Join-Path $RepoRoot "models"
if (-not (Test-Path $ModelsDir)) {
    New-Item -ItemType Directory -Path $ModelsDir -Force | Out-Null
}
New-Item -ItemType File -Path "$ModelsDir\.gitkeep" -Force | Out-Null

Write-Host "  ✓ Models directory ready: $ModelsDir" -ForegroundColor Green

# Step 4: Create Drive models folder
Write-Host "`n[4/5] Creating models folder in Google Drive..." -ForegroundColor Yellow

$DriveModelsDir = "G:\My Drive\AutoFactoryScope\models"
if (Test-Path "G:\My Drive\AutoFactoryScope") {
    if (-not (Test-Path $DriveModelsDir)) {
        New-Item -ItemType Directory -Path $DriveModelsDir -Force | Out-Null
    }
    Write-Host "  ✓ Drive models folder ready" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Skipped (Drive not mounted)" -ForegroundColor Yellow
}

# Step 5: Open browser to Drive
Write-Host "`n[5/5] Opening Google Drive in browser..." -ForegroundColor Yellow

Start-Process "https://drive.google.com/drive/folders/my-drive"
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              ✓ SETUP COMPLETE!                       ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

Write-Host "📋 NEXT STEPS:" -ForegroundColor Cyan
Write-Host ""
Write-Host "  1. In Google Drive (browser just opened):" -ForegroundColor White
Write-Host "     - Navigate to: AutoFactoryScope/" -ForegroundColor Gray
Write-Host "     - Find: 01_train_yolo11_drive.ipynb" -ForegroundColor Gray
Write-Host "     - Right-click → Open with → Google Colaboratory" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. In Google Colab:" -ForegroundColor White
Write-Host "     - Runtime → Change runtime type → T4 GPU → Save" -ForegroundColor Gray
Write-Host "     - Runtime → Run all (Ctrl+F9)" -ForegroundColor Gray
Write-Host "     - Approve Drive mount when prompted" -ForegroundColor Gray
Write-Host ""
Write-Host "  3. Wait ~60 minutes for training to complete" -ForegroundColor White
Write-Host ""
Write-Host "  4. After training:" -ForegroundColor White
Write-Host "     - Run: .\scripts\download_model.ps1" -ForegroundColor Gray
Write-Host "     - Then: .\scripts\export_onnx.ps1" -ForegroundColor Gray
Write-Host ""

Write-Host "📚 Documentation: See TRAIN_NOW.md for details" -ForegroundColor Cyan
Write-Host ""

# Pause so user can read
Write-Host "Press any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
