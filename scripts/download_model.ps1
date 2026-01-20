# Download trained model from Google Drive to local repo

$ErrorActionPreference = "Stop"

Write-Host "=== Download Trained Model from Drive ===" -ForegroundColor Cyan

$RepoRoot = Split-Path -Parent $PSScriptRoot

# Source: Google Drive
$SourcePath = "G:\My Drive\AutoFactoryScope\models\best.pt"

# Destination: Local repo
$DestPath = Join-Path $RepoRoot "models\best.pt"

Write-Host ""
Write-Host "Source: $SourcePath" -ForegroundColor Gray
Write-Host "Dest:   $DestPath" -ForegroundColor Gray
Write-Host ""

# Check if source exists
if (-not (Test-Path $SourcePath)) {
    Write-Host "✗ Model not found in Google Drive!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Expected location: $SourcePath" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Possible issues:" -ForegroundColor Yellow
    Write-Host "  1. Training not completed yet" -ForegroundColor Gray
    Write-Host "  2. Model saved to different location" -ForegroundColor Gray
    Write-Host "  3. Google Drive not mounted at G:\My Drive\" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Check training notebook output for actual save location." -ForegroundColor Gray
    exit 1
}

# Get file size
$FileSize = (Get-Item $SourcePath).Length / 1MB

Write-Host "Found model file: $('{0:N2}' -f $FileSize) MB" -ForegroundColor Green

# Copy to local
Write-Host ""
Write-Host "Copying to local repo..." -ForegroundColor Yellow

Copy-Item $SourcePath -Destination $DestPath -Force

Write-Host "✓ Model downloaded successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next step: Export to ONNX" -ForegroundColor Cyan
Write-Host "  Run: .\scripts\export_onnx.ps1" -ForegroundColor Gray
Write-Host ""
