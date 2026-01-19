"""
Integration tests for FastAPI application.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from autofactoryscope_api.main import app
from autofactoryscope_api.schemas import DetectionResponse

client = TestClient(app)


def test_health_check():
    """Test /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "version" in data


def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["name"] == "AutoFactoryScope API"


@patch("autofactoryscope_api.main.get_model")
def test_detect_endpoint_mocked(mock_get_model):
    """Test /detect endpoint with mocked model."""
    # Setup mock model
    mock_model = MagicMock()
    mock_model.is_loaded = True
    
    # Mock return value of predict_tiles
    from autofactoryscope_api.postprocess import Detection
    mock_model.predict_tiles.return_value = [
        Detection(0, 0, 10, 10, 0.9, 0)
    ]
    
    # Configure get_model to return our mock
    mock_get_model.return_value = mock_model

    # Create dummy image file
    from io import BytesIO
    from PIL import Image
    
    img = Image.new("RGB", (100, 100), color="red")
    img_byte_arr = BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)

    # Send request
    response = client.post(
        "/detect",
        files={"file": ("test.png", img_byte_arr, "image/png")}
    )

    assert response.status_code == 200
    data = response.json()
    
    # Validate response schema
    assert data["robot_count"] == 1
    assert len(data["detections"]) == 1
    assert "request_id" in data
    assert data["image_size"] == [100, 100]


def test_detect_invalid_file():
    """Test upload of invalid file type."""
    response = client.post(
        "/detect",
        files={"file": ("test.txt", b"plain text content", "text/plain")}
    )
    
    assert response.status_code == 400
    data = response.json()
    assert data["error"]["code"] == "INVALID_FILE_TYPE"
