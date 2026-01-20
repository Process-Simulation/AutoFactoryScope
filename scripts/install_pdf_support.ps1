# Install PDF Processing Support
# Adds pdf2image and PyMuPDF for PDF to PNG conversion

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$VenvPath = Join-Path $RepoRoot "src\backend\autofactoryscope_api\.venv\Scripts\Activate.ps1"

Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "  Installing PDF Processing Support" -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host ""

# Activate venv
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& $VenvPath

Write-Host ""
Write-Host "Installing PDF libraries..." -ForegroundColor Yellow
Write-Host "  - pdf2image: PDF page rendering" -ForegroundColor Gray
Write-Host "  - PyMuPDF (fitz): PDF processing" -ForegroundColor Gray
Write-Host ""

pip install pdf2image PyMuPDF

Write-Host ""
Write-Host "===========================================================" -ForegroundColor Green
Write-Host "  PDF Support Installed Successfully!" -ForegroundColor Green
Write-Host "===========================================================" -ForegroundColor Green
Write-Host ""

Write-Host "You can now upload PDF files to the /detect endpoint!" -ForegroundColor Cyan
Write-Host "Restart the backend for changes to take effect:" -ForegroundColor Gray
Write-Host "  .\scripts\start_backend.ps1" -ForegroundColor White
Write-Host ""

deactivate
