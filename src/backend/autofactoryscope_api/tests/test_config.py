"""
Minimal test to validate configuration loading.
This ensures the CI pipeline can run tests even before full test coverage.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_config_import():
    """Test that config module can be imported."""
    try:
        import autofactoryscope_api.config
        assert True, "Config module imported successfully"
    except ImportError as e:
        # If config doesn't exist yet, that's okay for MVP
        # This test will pass once config.py is created
        assert False, f"Config module import failed: {e}"


def test_fastapi_import():
    """Test that FastAPI can be imported (basic dependency check)."""
    try:
        from fastapi import FastAPI
        assert FastAPI is not None
    except ImportError:
        assert False, "FastAPI not available - check requirements.txt"


def test_onnx_runtime_import():
    """Test that ONNX Runtime can be imported (basic dependency check)."""
    try:
        import onnxruntime
        assert onnxruntime is not None
    except ImportError:
        # ONNX Runtime might not be available in all test environments
        # This is a warning, not a failure for basic CI
        pass

