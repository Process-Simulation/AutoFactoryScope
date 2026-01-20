# Install PyTorch with CUDA support for Quadro P4000

$ErrorActionPreference = "Stop"

Write-Host "╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║     Installing PyTorch with CUDA Support            ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

# Activate venv
Write-Host "[1/3] Activating virtual environment..." -ForegroundColor Yellow
$VenvPath = "src\backend\autofactoryscope_api\.venv\Scripts\Activate.ps1"
& $VenvPath
Write-Host "  ✓ Virtual environment activated" -ForegroundColor Green

# Uninstall CPU-only torch
Write-Host "`n[2/3] Removing CPU-only PyTorch..." -ForegroundColor Yellow
pip uninstall -y torch torchvision torchaudio 2>$null
Write-Host "  ✓ CPU version removed" -ForegroundColor Green

# Install CUDA version (CUDA 12.4 compatible)
Write-Host "`n[3/3] Installing PyTorch with CUDA 12.4 support..." -ForegroundColor Yellow
Write-Host "  (This will download ~2GB, please wait...)" -ForegroundColor Gray
Write-Host ""

pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║         ✓ PyTorch with CUDA Installed!              ║" -ForegroundColor Green
Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

# Verify CUDA
Write-Host "Verifying CUDA availability..." -ForegroundColor Yellow
Write-Host ""

$VerifyScript = @"
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA version: {torch.version.cuda}')
    print(f'GPU count: {torch.cuda.device_count()}')
    print(f'GPU name: {torch.cuda.get_device_name(0)}')
    print(f'GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB')
else:
    print('WARNING: CUDA not available!')
    print('Check NVIDIA drivers are installed.')
"@

$VerifyScript | python

Write-Host ""
Write-Host "Next: Run training again" -ForegroundColor Cyan
Write-Host "  .\scripts\train_local.ps1" -ForegroundColor Gray
Write-Host ""

deactivate
