# Pre-PR validation script
# Runs backend tests and frontend build to validate before opening a PR

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Join-Path $ScriptDir ".."
$RepoRoot = Resolve-Path $RepoRoot

Write-Host "Running pre-PR validation checks..."
Write-Host "Repository root: $RepoRoot"
Write-Host ""

$allPassed = $true

# Backend tests
Write-Host "========================================="
Write-Host "Backend Tests"
Write-Host "========================================="
$BackendDir = Join-Path $RepoRoot "src\backend\autofactoryscope_api"
if (Test-Path $BackendDir) {
    Set-Location $BackendDir
    
    # Check if pytest is available
    $pytestCmd = Get-Command pytest -ErrorAction SilentlyContinue
    if (-not $pytestCmd) {
        Write-Warning "pytest not found. Skipping backend tests."
        Write-Warning "Install with: pip install pytest"
    } else {
        # Check for tests directory
        if (Test-Path "tests") {
            Write-Host "Running pytest..."
            pytest
            if ($LASTEXITCODE -ne 0) {
                Write-Error "Backend tests failed"
                $allPassed = $false
            } else {
                Write-Host "Backend tests passed!" -ForegroundColor Green
            }
        } else {
            Write-Warning "No tests directory found. Skipping backend tests."
            Write-Warning "Create tests/ directory and add test files to enable testing."
        }
    }
} else {
    Write-Warning "Backend directory not found: $BackendDir"
}

Write-Host ""

# Frontend build
Write-Host "========================================="
Write-Host "Frontend Build"
Write-Host "========================================="
$FrontendDir = Join-Path $RepoRoot "src\frontend\autofactoryscope-web"
if (Test-Path $FrontendDir) {
    Set-Location $FrontendDir
    
    # Check for Node.js
    $nodeCmd = Get-Command node -ErrorAction SilentlyContinue
    if (-not $nodeCmd) {
        Write-Error "Node.js not found. Cannot build frontend."
        $allPassed = $false
    } else {
        # Check for npm
        $npmCmd = Get-Command npm -ErrorAction SilentlyContinue
        if (-not $npmCmd) {
            Write-Error "npm not found. Cannot build frontend."
            $allPassed = $false
        } else {
            Write-Host "Installing dependencies..."
            npm ci
            if ($LASTEXITCODE -ne 0) {
                Write-Error "Frontend dependency installation failed"
                $allPassed = $false
            } else {
                Write-Host "Building frontend..."
                npm run build
                if ($LASTEXITCODE -ne 0) {
                    Write-Error "Frontend build failed"
                    $allPassed = $false
                } else {
                    Write-Host "Frontend build passed!" -ForegroundColor Green
                }
            }
        }
    }
} else {
    Write-Warning "Frontend directory not found: $FrontendDir"
}

Write-Host ""
Write-Host "========================================="
if ($allPassed) {
    Write-Host "All checks passed!" -ForegroundColor Green
    exit 0
} else {
    Write-Host "Some checks failed. Please fix issues before opening a PR." -ForegroundColor Red
    exit 1
}

