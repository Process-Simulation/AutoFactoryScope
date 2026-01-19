"""
Tests for post-processing module.
"""

import numpy as np
import pytest

from autofactoryscope_api.postprocess import Detection, compute_iou, nms, nms_numpy

# Fixtures
@pytest.fixture
def box_a():
    return (0.0, 0.0, 10.0, 10.0)

@pytest.fixture
def box_b_overlap():
    # 50% overlap approx (5x10 intersection = 50 area. Union = 100+100-50=150. IoU = 1/3)
    return (5.0, 0.0, 15.0, 10.0)

@pytest.fixture
def box_c_separate():
    return (20.0, 20.0, 30.0, 30.0)


def test_detection_properties():
    """Test Detection dataclass properties."""
    d = Detection(x1=0, y1=0, x2=10, y2=20, confidence=0.9, class_id=0)
    assert d.width == 10
    assert d.height == 20
    assert d.area == 200
    assert d.center == (5, 10)
    assert d.bbox == (0, 0, 10, 20)


def test_compute_iou(box_a):
    """Test IoU computation."""
    # Self IoU should be 1.0
    assert compute_iou(box_a, box_a) == 1.0

    # No overlap
    assert compute_iou(box_a, (20, 20, 30, 30)) == 0.0

    # Half overlap
    # Box 1: 0,0 to 10,10 (Area 100)
    # Box 2: 5,0 to 15,10 (Area 100)
    # Intersection: 5,0 to 10,10 (Area 50)
    # Union: 100 + 100 - 50 = 150
    # IoU: 50 / 150 = 0.333...
    iou = compute_iou((0, 0, 10, 10), (5, 0, 15, 10))
    assert 0.33 < iou < 0.34


def test_nms_basic():
    """Test NMS with list of detections."""
    d1 = Detection(0, 0, 10, 10, 0.9, 0)
    d2 = Detection(0, 0, 10, 10, 0.8, 0)  # Duplicate of d1 (lower conf)
    d3 = Detection(20, 20, 30, 30, 0.7, 0)  # Separate object

    filtered = nms([d1, d2, d3], iou_threshold=0.5)

    assert len(filtered) == 2
    assert d1 in filtered
    assert d3 in filtered
    assert d2 not in filtered


def test_nms_numpy():
    """Test vectorized NMS."""
    boxes = np.array([
        [0, 0, 10, 10],
        [0, 0, 10, 10],
        [20, 20, 30, 30]
    ], dtype=np.float64)

    scores = np.array([0.9, 0.8, 0.7], dtype=np.float64)

    keep_indices = nms_numpy(boxes, scores, iou_threshold=0.5)

    assert len(keep_indices) == 2
    assert 0 in keep_indices  # Highest score kept
    assert 2 in keep_indices  # Separate object kept
    assert 1 not in keep_indices  # Duplicate removed
