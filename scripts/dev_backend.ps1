# Development script for AutoFactoryScope backend
# Windows PowerShell script to set up and run the FastAPI backend

$ErrorActionPreference = "Stop"

$BackendDir = Join-Path $PSScriptRoot "..\src\backend\autofactoryscope_api"
$BackendDir = Resolve-Path $BackendDir -ErrorAction SilentlyContinue

if (-not $BackendDir) {
    Write-Error "Backend directory not found: $BackendDir"
    Write-Error "Expected path: src/backend/autofactoryscope_api"
    exit 1
}

Set-Location $BackendDir

# Check for Python
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Error "Python not found. Please install Python 3.11 or later."
    exit 1
}

# Check Python version
$pythonVersion = python --version 2>&1
Write-Host "Using: $pythonVersion"

# Check for SkipInstall flag
$skipInstall = $args -contains "--SkipInstall"

# Create virtual environment if it doesn't exist
$venvPath = Join-Path $BackendDir ".venv"
if (-not (Test-Path $venvPath) -and -not $skipInstall) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to create virtual environment"
        exit 1
    }
}

# Activate virtual environment
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    Write-Host "Activating virtual environment..."
    & $activateScript
} else {
    Write-Warning "Virtual environment activation script not found. Continuing anyway..."
}

# Install requirements if not skipping
if (-not $skipInstall) {
    Write-Host "Installing requirements..."
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install requirements"
        exit 1
    }
}

# Check if uvicorn is available
$uvicornCmd = Get-Command uvicorn -ErrorAction SilentlyContinue
if (-not $uvicornCmd) {
    Write-Error "uvicorn not found. Install it with: pip install uvicorn"
    exit 1
}

# Check for model file
$modelPath = Join-Path $PSScriptRoot "..\models\robot_detector.onnx"
$modelPath = Resolve-Path $modelPath -ErrorAction SilentlyContinue
if (-not $modelPath) {
    Write-Warning "Model file not found at models/robot_detector.onnx"
    Write-Warning "Backend may fail to start without the model file."
}

Write-Host ""
Write-Host "Starting FastAPI backend..."
Write-Host "API docs will be available at: http://localhost:8000/docs"
Write-Host "Press Ctrl+C to stop"
Write-Host ""

# Run uvicorn
uvicorn autofactoryscope_api.main:app --reload --host 0.0.0.0 --port 8000

