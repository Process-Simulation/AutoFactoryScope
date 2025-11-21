#!/bin/bash
# Development script for AutoFactoryScope frontend
# Linux/macOS bash script to build the WPF desktop application
# Note: WPF is Windows-only, this script only handles restore/build for CI-like environments

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$SCRIPT_DIR/../src/frontend/AutoFactoryScope.Desktop"

if [ ! -d "$FRONTEND_DIR" ]; then
    echo "Error: Frontend directory not found: $FRONTEND_DIR" >&2
    echo "Expected path: src/frontend/AutoFactoryScope.Desktop" >&2
    exit 1
fi

cd "$FRONTEND_DIR"

# Check for .NET SDK
if ! command -v dotnet &> /dev/null; then
    echo "Error: .NET SDK not found. Please install .NET 8 SDK or later." >&2
    exit 1
fi

# Check .NET version
DOTNET_VERSION=$(dotnet --version)
echo "Using .NET SDK: $DOTNET_VERSION"

# Check for solution or project file
PROJECT_FILE=$(find . -maxdepth 1 -name "*.csproj" | head -n 1)
SOLUTION_FILE=$(find . -maxdepth 1 -name "*.sln" | head -n 1)

if [ -z "$PROJECT_FILE" ] && [ -z "$SOLUTION_FILE" ]; then
    echo "Error: No .csproj or .sln file found in $FRONTEND_DIR" >&2
    exit 1
fi

# Note: WPF is Windows-only
echo "Note: WPF is Windows-only. This script will only restore and build."
echo "For running the application, use Windows with Visual Studio or the PowerShell script."
echo ""

# Restore dependencies
echo "Restoring dependencies..."
if [ -n "$SOLUTION_FILE" ]; then
    dotnet restore "$SOLUTION_FILE"
else
    dotnet restore
fi

# Build
echo "Building project (Debug configuration)..."
if [ -n "$SOLUTION_FILE" ]; then
    dotnet build "$SOLUTION_FILE" --configuration Debug
else
    dotnet build --configuration Debug
fi

echo "Build successful!"
echo ""
echo "Note: To run the WPF application, use Windows and run:"
echo "  scripts/dev_frontend.ps1 --run"

