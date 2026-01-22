#!/bin/bash
# Run backend development server
cd "$(dirname "$0")/../src/backend/autofactoryscope_api"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run the API
uvicorn main:app --reload --host 0.0.0.0 --port 8000
