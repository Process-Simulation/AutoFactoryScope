"""
Tests for inference module.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from autofactoryscope_api.inference import ModelWrapper
from autofactoryscope_api.postprocess import Detection


@pytest.fixture
def mock_onnx_session():
    with patch("onnxruntime.InferenceSession") as mock:
        session = MagicMock()
        mock.return_value = session

        # Mock inputs/outputs
        input_meta = MagicMock()
        input_meta.name = "images"
        session.get_inputs.return_value = [input_meta]

        output_meta = MagicMock()
        output_meta.name = "output0"
        session.get_outputs.return_value = [output_meta]

        yield session


def test_model_wrapper_initialization():
    """Test model wrapper init."""
    model = ModelWrapper("dummy.onnx", confidence_threshold=0.5)
    assert model.confidence_threshold == 0.5
    assert not model.is_loaded


def test_preprocess():
    """Test image preprocessing."""
    model = ModelWrapper("dummy.onnx", input_size=512)

    # random 100x100 image
    img = np.zeros((100, 100, 3), dtype=np.uint8)

    tensor = model.preprocess(img)

    # Should be (1, 3, 512, 512)
    assert tensor.shape == (1, 3, 512, 512)
    assert tensor.dtype == np.float32

    # Should be normalized to [0, 1]
    assert tensor.max() <= 1.0
    assert tensor.min() >= 0.0


def test_postprocess_detections():
    """Test output parsing."""
    model = ModelWrapper("dummy.onnx", confidence_threshold=0.5)

    # Mock output: (1, 5, 2) -> (1, 5, 6) to satisfy transpose check (channels < predictions)
    # Pred 1: Center 10, 10, size 10, 10, score 0.9 (Good)
    # Pred 2-6: Dummy bad predictions
    output = np.array([
        [
            [10, 50, 0, 0, 0, 0],  # x
            [10, 50, 0, 0, 0, 0],  # y
            [10, 10, 0, 0, 0, 0],  # w
            [10, 10, 0, 0, 0, 0],  # h
            [0.9, 0.1, 0, 0, 0, 0] # score
        ]
    ], dtype=np.float32)

    detections = model.postprocess([output])

    assert len(detections) == 1
    det = detections[0]
    assert det.confidence == pytest.approx(0.9)
    # Center 10,10, size 10,10 -> x1=5, y1=5, x2=15, y2=15
    assert det.bbox == pytest.approx((5.0, 5.0, 15.0, 15.0))
