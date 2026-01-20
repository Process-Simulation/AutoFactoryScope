# AutoFactoryScope: Smart Training Launcher
# Detects GPU and chooses best training method

$ErrorActionPreference = "Stop"

Write-Host "╔══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   AutoFactoryScope - Smart Training Launcher        ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Check for NVIDIA GPU
Write-Host "Detecting hardware..." -ForegroundColor Yellow
$HasGPU = $false
$GPUName = ""

try {
    $GPUInfo = nvidia-smi --query-gpu=name --format=csv,noheader 2>&1
    if ($GPUInfo -and $GPUInfo -notmatch "not found" -and $GPUInfo -notmatch "Unable") {
        $HasGPU = $true
        $GPUName = $GPUInfo.Trim()
    }
} catch {
    $HasGPU = $false
}

Write-Host ""

if ($HasGPU) {
    Write-Host "╔══════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║          ✓ NVIDIA GPU DETECTED!                      ║" -ForegroundColor Green
    Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "  GPU: $GPUName" -ForegroundColor White
    Write-Host ""
    Write-Host "🚀 RECOMMENDATION: Train locally on your GPU!" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Benefits:" -ForegroundColor Yellow
    Write-Host "  ✓ Faster training (20-30 min vs 60 min on Colab)" -ForegroundColor Gray
    Write-Host "  ✓ No network/browser issues" -ForegroundColor Gray
    Write-Host "  ✓ Complete privacy (data stays local)" -ForegroundColor Gray
    Write-Host "  ✓ No session limits" -ForegroundColor Gray
    Write-Host ""

    # Offer choice
    Write-Host "Choose training method:" -ForegroundColor Cyan
    Write-Host "  [1] Train locally on GPU (Recommended)" -ForegroundColor White
    Write-Host "  [2] Train on Google Colab (slower, requires browser)" -ForegroundColor Gray
    Write-Host "  [Q] Quit" -ForegroundColor Gray
    Write-Host ""

    $Choice = Read-Host "Enter choice"

    if ($Choice -eq "1") {
        Write-Host ""
        Write-Host "Starting local GPU training..." -ForegroundColor Green
        Write-Host ""
        & ".\scripts\train_local.ps1"
    } elseif ($Choice -eq "2") {
        Write-Host ""
        Write-Host "Setting up for Colab training..." -ForegroundColor Yellow
        & ".\START_HERE.ps1"
    } else {
        Write-Host "Exiting..." -ForegroundColor Gray
        exit 0
    }

} else {
    Write-Host "╔══════════════════════════════════════════════════════╗" -ForegroundColor Yellow
    Write-Host "║          ⚠ NO NVIDIA GPU DETECTED                   ║" -ForegroundColor Yellow
    Write-Host "╚══════════════════════════════════════════════════════╝" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "🌐 RECOMMENDATION: Use Google Colab (free GPU)" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Training on CPU would take several hours." -ForegroundColor Gray
    Write-Host "Colab provides free T4 GPU (~60 min training)." -ForegroundColor Gray
    Write-Host ""

    # Offer choice
    Write-Host "Choose training method:" -ForegroundColor Cyan
    Write-Host "  [1] Use Google Colab (Recommended)" -ForegroundColor White
    Write-Host "  [2] Train on CPU anyway (slow)" -ForegroundColor Gray
    Write-Host "  [Q] Quit" -ForegroundColor Gray
    Write-Host ""

    $Choice = Read-Host "Enter choice"

    if ($Choice -eq "1") {
        Write-Host ""
        Write-Host "Setting up for Colab training..." -ForegroundColor Green
        Write-Host ""
        & ".\START_HERE.ps1"
    } elseif ($Choice -eq "2") {
        Write-Host ""
        Write-Host "⚠ WARNING: CPU training will be VERY slow!" -ForegroundColor Red
        Write-Host "Expected time: 3-6 hours" -ForegroundColor Yellow
        Write-Host ""
        $Confirm = Read-Host "Are you sure? (yes/no)"
        if ($Confirm -eq "yes") {
            & ".\scripts\train_local.ps1"
        } else {
            Write-Host "Cancelled." -ForegroundColor Gray
            exit 0
        }
    } else {
        Write-Host "Exiting..." -ForegroundColor Gray
        exit 0
    }
}
