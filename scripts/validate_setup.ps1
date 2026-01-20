# AutoFactoryScope Setup Validation Script
# Checks if environment is correctly configured

$ErrorActionPreference = "Continue"

Write-Host "=== AutoFactoryScope Setup Validation ===" -ForegroundColor Cyan
Write-Host ""

$RepoRoot = Split-Path -Parent $PSScriptRoot
$AllGood = $true

# Check 1: Python version
Write-Host "[1/10] Checking Python version..." -ForegroundColor Yellow
$PythonVersion = python --version 2>&1
if ($PythonVersion -match "3\.1[1-9]") {
    Write-Host "  ✓ Python: $PythonVersion" -ForegroundColor Green
} else {
    Write-Host "  ✗ Python 3.11+ required (found: $PythonVersion)" -ForegroundColor Red
    $AllGood = $false
}

# Check 2: Node version
Write-Host "[2/10] Checking Node.js version..." -ForegroundColor Yellow
$NodeVersion = node --version 2>&1
if ($NodeVersion -match "v2[0-9]") {
    Write-Host "  ✓ Node.js: $NodeVersion" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Node.js 20+ recommended (found: $NodeVersion)" -ForegroundColor Yellow
}

# Check 3: Backend venv
Write-Host "[3/10] Checking backend virtual environment..." -ForegroundColor Yellow
$BackendVenv = Join-Path $RepoRoot "src\backend\autofactoryscope_api\.venv\Scripts\python.exe"
if (Test-Path $BackendVenv) {
    Write-Host "  ✓ Backend venv exists" -ForegroundColor Green
} else {
    Write-Host "  ✗ Backend venv not found. Run: .\scripts\setup_env.ps1" -ForegroundColor Red
    $AllGood = $false
}

# Check 4: Backend dependencies
Write-Host "[4/10] Checking backend dependencies..." -ForegroundColor Yellow
$BackendPath = Join-Path $RepoRoot "src\backend\autofactoryscope_api"
Set-Location $BackendPath
& .\.venv\Scripts\Activate.ps1 2>$null
$HasONNX = python -c "import onnxruntime; print('OK')" 2>&1
if ($HasONNX -match "OK") {
    Write-Host "  ✓ ONNX Runtime installed" -ForegroundColor Green
} else {
    Write-Host "  ✗ ONNX Runtime not found. Run: pip install -r requirements.txt" -ForegroundColor Red
    $AllGood = $false
}
deactivate 2>$null
Set-Location $RepoRoot

# Check 5: Frontend dependencies
Write-Host "[5/10] Checking frontend dependencies..." -ForegroundColor Yellow
$FrontendNodeModules = Join-Path $RepoRoot "src\frontend\autofactoryscope-web\node_modules"
if (Test-Path $FrontendNodeModules) {
    Write-Host "  ✓ Frontend node_modules exists" -ForegroundColor Green
} else {
    Write-Host "  ✗ Frontend dependencies not installed. Run: npm install" -ForegroundColor Red
    $AllGood = $false
}

# Check 6: Datasets
Write-Host "[6/10] Checking datasets..." -ForegroundColor Yellow
$DatasetsPath = Join-Path $RepoRoot "datasets"
$V1Path = Join-Path $DatasetsPath "v1_roboflow_export"
$V2Path = Join-Path $DatasetsPath "v2_roboflow_export"

if ((Test-Path $V1Path) -and (Test-Path $V2Path)) {
    $V1Count = (Get-ChildItem "$V1Path\**\*.jpg" -Recurse).Count
    $V2Count = (Get-ChildItem "$V2Path\**\*.jpg" -Recurse).Count
    Write-Host "  ✓ Datasets exist (v1: $V1Count images, v2: $V2Count images)" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Datasets not found. Extract from Downloads folder." -ForegroundColor Yellow
}

# Check 7: Model file
Write-Host "[7/10] Checking ONNX model..." -ForegroundColor Yellow
$ModelPath = Join-Path $RepoRoot "models\robot_detector.onnx"
if (Test-Path $ModelPath) {
    $ModelSize = (Get-Item $ModelPath).Length / 1MB
    Write-Host "  ✓ Model found ($('{0:N2}' -f $ModelSize) MB)" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Model not found. Train model first (see QUICKSTART.md)" -ForegroundColor Yellow
}

# Check 8: .gitignore
Write-Host "[8/10] Checking .gitignore..." -ForegroundColor Yellow
$GitignorePath = Join-Path $RepoRoot ".gitignore"
$GitignoreContent = Get-Content $GitignorePath -Raw
if ($GitignoreContent -match "datasets/") {
    Write-Host "  ✓ .gitignore configured (datasets/ excluded)" -ForegroundColor Green
} else {
    Write-Host "  ✗ .gitignore missing datasets/ entry" -ForegroundColor Red
    $AllGood = $false
}

# Check 9: Documentation
Write-Host "[9/10] Checking documentation..." -ForegroundColor Yellow
$RequiredDocs = @(
    "QUICKSTART.md",
    "docs\IMPLEMENTATION_PLAN.md",
    "docs\LICENSING.md",
    "docs\ANNOTATION_TOOLS.md",
    "docs\RUNBOOK.md",
    "datasets\DATA_README.md"
)

$MissingDocs = @()
foreach ($doc in $RequiredDocs) {
    if (-not (Test-Path (Join-Path $RepoRoot $doc))) {
        $MissingDocs += $doc
    }
}

if ($MissingDocs.Count -eq 0) {
    Write-Host "  ✓ All documentation present" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Missing docs: $($MissingDocs -join ', ')" -ForegroundColor Yellow
}

# Check 10: Notebooks
Write-Host "[10/10] Checking training notebooks..." -ForegroundColor Yellow
$NotebooksPath = Join-Path $RepoRoot "notebooks"
$Notebook1 = Join-Path $NotebooksPath "01_train_yolo11.ipynb"
$Notebook2 = Join-Path $NotebooksPath "02_export_onnx.ipynb"

if ((Test-Path $Notebook1) -and (Test-Path $Notebook2)) {
    Write-Host "  ✓ Training notebooks present" -ForegroundColor Green
} else {
    Write-Host "  ✗ Notebooks missing" -ForegroundColor Red
    $AllGood = $false
}

# Summary
Write-Host ""
Write-Host "=== Validation Complete ===" -ForegroundColor Cyan

if ($AllGood) {
    Write-Host "✅ Setup is complete! Ready to train model." -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Gray
    Write-Host "  1. Backup datasets: .\scripts\backup_dataset.ps1" -ForegroundColor Gray
    Write-Host "  2. Train model in Colab (see QUICKSTART.md)" -ForegroundColor Gray
    Write-Host "  3. Export to ONNX" -ForegroundColor Gray
    Write-Host "  4. Start backend: uvicorn autofactoryscope_api.main:app --reload" -ForegroundColor Gray
} else {
    Write-Host "❌ Setup incomplete. Fix errors above." -ForegroundColor Red
    Write-Host ""
    Write-Host "Run setup script: .\scripts\setup_env.ps1" -ForegroundColor Gray
}

Write-Host ""
