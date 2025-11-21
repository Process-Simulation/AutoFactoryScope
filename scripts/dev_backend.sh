#!/bin/bash
# Development script for AutoFactoryScope backend
# Linux/macOS bash script to set up and run the FastAPI backend

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/../src/backend/autofactoryscope_api"

if [ ! -d "$BACKEND_DIR" ]; then
    echo "Error: Backend directory not found: $BACKEND_DIR" >&2
    echo "Expected path: src/backend/autofactoryscope_api" >&2
    exit 1
fi

cd "$BACKEND_DIR"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 not found. Please install Python 3.11 or later." >&2
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1)
echo "Using: $PYTHON_VERSION"

# Check for SkipInstall flag
SKIP_INSTALL=false
for arg in "$@"; do
    if [ "$arg" = "--SkipInstall" ]; then
        SKIP_INSTALL=true
        break
    fi
done

# Create virtual environment if it doesn't exist
VENV_PATH="$BACKEND_DIR/.venv"
if [ ! -d "$VENV_PATH" ] && [ "$SKIP_INSTALL" = false ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
if [ -f "$VENV_PATH/bin/activate" ]; then
    echo "Activating virtual environment..."
    source "$VENV_PATH/bin/activate"
else
    echo "Warning: Virtual environment activation script not found. Continuing anyway..." >&2
fi

# Install requirements if not skipping
if [ "$SKIP_INSTALL" = false ]; then
    echo "Installing requirements..."
    pip install -r requirements.txt
fi

# Check if uvicorn is available
if ! command -v uvicorn &> /dev/null; then
    echo "Error: uvicorn not found. Install it with: pip install uvicorn" >&2
    exit 1
fi

# Check for model file
MODEL_PATH="$SCRIPT_DIR/../models/robot_detector.onnx"
if [ ! -f "$MODEL_PATH" ]; then
    echo "Warning: Model file not found at models/robot_detector.onnx" >&2
    echo "Warning: Backend may fail to start without the model file." >&2
fi

echo ""
echo "Starting FastAPI backend..."
echo "API docs will be available at: http://localhost:8000/docs"
echo "Press Ctrl+C to stop"
echo ""

# Run uvicorn
uvicorn autofactoryscope_api.main:app --reload --host 0.0.0.0 --port 8000

