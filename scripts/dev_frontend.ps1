# Development script for AutoFactoryScope frontend
# Windows PowerShell script to build and run the WPF desktop application

$ErrorActionPreference = "Stop"

$FrontendDir = Join-Path $PSScriptRoot "..\src\frontend\AutoFactoryScope.Desktop"
$FrontendDir = Resolve-Path $FrontendDir -ErrorAction SilentlyContinue

if (-not $FrontendDir) {
    Write-Error "Frontend directory not found: $FrontendDir"
    Write-Error "Expected path: src/frontend/AutoFactoryScope.Desktop"
    exit 1
}

Set-Location $FrontendDir

# Check for .NET SDK
$dotnetCmd = Get-Command dotnet -ErrorAction SilentlyContinue
if (-not $dotnetCmd) {
    Write-Error ".NET SDK not found. Please install .NET 8 SDK or later."
    exit 1
}

# Check .NET version
$dotnetVersion = dotnet --version
Write-Host "Using .NET SDK: $dotnetVersion"

# Check for solution or project file
$projectFile = Get-ChildItem -Filter "*.csproj" -ErrorAction SilentlyContinue
$solutionFile = Get-ChildItem -Filter "*.sln" -ErrorAction SilentlyContinue

if (-not $projectFile -and -not $solutionFile) {
    Write-Error "No .csproj or .sln file found in $FrontendDir"
    exit 1
}

# Restore dependencies
Write-Host "Restoring dependencies..."
if ($solutionFile) {
    dotnet restore $solutionFile.Name
} else {
    dotnet restore
}

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to restore dependencies"
    exit 1
}

# Build
Write-Host "Building project (Debug configuration)..."
if ($solutionFile) {
    dotnet build $solutionFile.Name --configuration Debug
} else {
    dotnet build --configuration Debug
}

if ($LASTEXITCODE -ne 0) {
    Write-Error "Build failed"
    exit 1
}

Write-Host "Build successful!"
Write-Host ""

# Check if --run flag is provided
$shouldRun = $args -contains "--run"

if ($shouldRun) {
    Write-Host "Running application..."
    Write-Host "Press Ctrl+C to stop"
    Write-Host ""
    
    if ($solutionFile) {
        dotnet run --project $projectFile.Name
    } else {
        dotnet run
    }
} else {
    Write-Host "To run the application, use:"
    Write-Host "  .\scripts\dev_frontend.ps1 --run"
    Write-Host ""
    Write-Host "Or manually:"
    if ($solutionFile) {
        Write-Host "  dotnet run --project $($projectFile.Name)"
    } else {
        Write-Host "  dotnet run"
    }
}

