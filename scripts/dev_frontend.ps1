# Development script for AutoFactoryScope frontend
# Windows PowerShell script to build and run the TypeScript/React web application

$ErrorActionPreference = "Stop"

$FrontendDir = Join-Path $PSScriptRoot "..\src\frontend\autofactoryscope-web"
$FrontendDir = Resolve-Path $FrontendDir -ErrorAction SilentlyContinue

if (-not $FrontendDir) {
    Write-Error "Frontend directory not found: $FrontendDir"
    Write-Error "Expected path: src/frontend/autofactoryscope-web"
    exit 1
}

Set-Location $FrontendDir

# Check for Node.js
$nodeCmd = Get-Command node -ErrorAction SilentlyContinue
if (-not $nodeCmd) {
    Write-Error "Node.js not found. Please install Node.js 18 or later."
    exit 1
}

# Check Node.js version
$nodeVersion = node --version
Write-Host "Using Node.js: $nodeVersion"

# Check for npm
$npmCmd = Get-Command npm -ErrorAction SilentlyContinue
if (-not $npmCmd) {
    Write-Error "npm not found. Please install npm (comes with Node.js)."
    exit 1
}

# Check for package.json
if (-not (Test-Path "package.json")) {
    Write-Error "package.json not found in $FrontendDir"
    Write-Error "This doesn't appear to be a valid Node.js project."
    exit 1
}

# Check for SkipInstall flag
$skipInstall = $args -contains "--SkipInstall"

# Install dependencies if not skipping
if (-not $skipInstall) {
    Write-Host "Installing dependencies..."
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to install dependencies"
        exit 1
    }
}

# Check if --build flag is provided
$shouldBuild = $args -contains "--build"

if ($shouldBuild) {
    Write-Host "Building project..."
    npm run build
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Build failed"
        exit 1
    }
    Write-Host "Build successful!"
    exit 0
}

# Default: run development server
Write-Host "Starting development server..."
Write-Host "Frontend will be available at http://localhost:5173 (or next available port)"
Write-Host "Press Ctrl+C to stop"
Write-Host ""

npm run dev
