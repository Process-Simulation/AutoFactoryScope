#!/bin/bash
# Development script for AutoFactoryScope frontend
# Linux/macOS bash script to build and run the TypeScript/React web application

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$SCRIPT_DIR/../src/frontend/autofactoryscope-web"

if [ ! -d "$FRONTEND_DIR" ]; then
    echo "Error: Frontend directory not found: $FRONTEND_DIR" >&2
    echo "Expected path: src/frontend/autofactoryscope-web" >&2
    exit 1
fi

cd "$FRONTEND_DIR"

# Check for Node.js
if ! command -v node &> /dev/null; then
    echo "Error: Node.js not found. Please install Node.js 18 or later." >&2
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node --version)
echo "Using Node.js: $NODE_VERSION"

# Check for npm
if ! command -v npm &> /dev/null; then
    echo "Error: npm not found. Please install npm (comes with Node.js)." >&2
    exit 1
fi

# Check for package.json
if [ ! -f "package.json" ]; then
    echo "Error: package.json not found in $FRONTEND_DIR" >&2
    echo "This doesn't appear to be a valid Node.js project." >&2
    exit 1
fi

# Check for SkipInstall flag
SKIP_INSTALL=false
SHOULD_BUILD=false
for arg in "$@"; do
    if [ "$arg" = "--SkipInstall" ]; then
        SKIP_INSTALL=true
    fi
    if [ "$arg" = "--build" ]; then
        SHOULD_BUILD=true
    fi
done

# Install dependencies if not skipping
if [ "$SKIP_INSTALL" = false ]; then
    echo "Installing dependencies..."
    npm install
fi

# Build if requested
if [ "$SHOULD_BUILD" = true ]; then
    echo "Building project..."
    npm run build
    echo "Build successful!"
    exit 0
fi

# Default: run development server
echo "Starting development server..."
echo "Frontend will be available at http://localhost:5173 (or next available port)"
echo "Press Ctrl+C to stop"
echo ""

npm run dev
