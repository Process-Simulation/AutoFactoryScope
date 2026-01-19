"""
Post-processing module for detection results.

Handles coordinate merging from tiles and Non-Maximum Suppression (NMS).
"""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


@dataclass
class Detection:
    """A single object detection."""

    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float
    class_id: int
    class_name: str = "robot"

    @property
    def bbox(self) -> tuple[float, float, float, float]:
        """Return bounding box as (x1, y1, x2, y2)."""
        return (self.x1, self.y1, self.x2, self.y2)

    @property
    def width(self) -> float:
        """Width of bounding box."""
        return self.x2 - self.x1

    @property
    def height(self) -> float:
        """Height of bounding box."""
        return self.y2 - self.y1

    @property
    def area(self) -> float:
        """Area of bounding box."""
        return self.width * self.height

    @property
    def center(self) -> tuple[float, float]:
        """Center point of bounding box."""
        return ((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "bbox": [self.x1, self.y1, self.x2, self.y2],
            "confidence": round(self.confidence, 4),
            "class": self.class_name,
        }


def compute_iou(box1: tuple[float, ...], box2: tuple[float, ...]) -> float:
    """
    Compute Intersection over Union (IoU) between two bounding boxes.

    Args:
        box1: (x1, y1, x2, y2) first bounding box
        box2: (x1, y1, x2, y2) second bounding box

    Returns:
        IoU value between 0 and 1
    """
    x1_1, y1_1, x2_1, y2_1 = box1
    x1_2, y1_2, x2_2, y2_2 = box2

    # Intersection coordinates
    xi1 = max(x1_1, x1_2)
    yi1 = max(y1_1, y1_2)
    xi2 = min(x2_1, x2_2)
    yi2 = min(y2_1, y2_2)

    # No intersection
    if xi2 <= xi1 or yi2 <= yi1:
        return 0.0

    # Intersection area
    intersection = (xi2 - xi1) * (yi2 - yi1)

    # Union area
    area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
    area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
    union = area1 + area2 - intersection

    if union <= 0:
        return 0.0

    return intersection / union


def nms(
    detections: list[Detection],
    iou_threshold: float = 0.5,
) -> list[Detection]:
    """
    Apply Non-Maximum Suppression to remove duplicate detections.

    Args:
        detections: List of Detection objects
        iou_threshold: IoU threshold for suppression

    Returns:
        Filtered list of detections
    """
    if not detections:
        return []

    # Sort by confidence (descending)
    sorted_dets = sorted(detections, key=lambda d: d.confidence, reverse=True)

    keep: list[Detection] = []

    while sorted_dets:
        # Take the highest confidence detection
        best = sorted_dets.pop(0)
        keep.append(best)

        # Remove detections with high IoU overlap
        remaining: list[Detection] = []
        for det in sorted_dets:
            iou = compute_iou(best.bbox, det.bbox)
            if iou < iou_threshold:
                remaining.append(det)

        sorted_dets = remaining

    return keep


def nms_numpy(
    boxes: NDArray[np.float64],
    scores: NDArray[np.float64],
    iou_threshold: float = 0.5,
) -> NDArray[np.intp]:
    """
    Vectorized NMS implementation using numpy.

    Args:
        boxes: (N, 4) array of bounding boxes [x1, y1, x2, y2]
        scores: (N,) array of confidence scores
        iou_threshold: IoU threshold for suppression

    Returns:
        Indices of kept detections
    """
    if len(boxes) == 0:
        return np.array([], dtype=np.intp)

    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]

    areas = (x2 - x1) * (y2 - y1)
    order = scores.argsort()[::-1]

    keep: list[int] = []

    while order.size > 0:
        i = order[0]
        keep.append(int(i))

        if order.size == 1:
            break

        # Compute IoU with remaining boxes
        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])

        w = np.maximum(0.0, xx2 - xx1)
        h = np.maximum(0.0, yy2 - yy1)
        intersection = w * h

        iou = intersection / (areas[i] + areas[order[1:]] - intersection)

        # Keep boxes with IoU below threshold
        mask = iou < iou_threshold
        order = order[1:][mask]

    return np.array(keep, dtype=np.intp)


def filter_by_confidence(
    detections: list[Detection],
    threshold: float = 0.25,
) -> list[Detection]:
    """
    Filter detections by confidence threshold.

    Args:
        detections: List of Detection objects
        threshold: Minimum confidence to keep

    Returns:
        Filtered list of detections
    """
    return [d for d in detections if d.confidence >= threshold]


def merge_tile_detections(
    all_detections: list[list[Detection]],
    iou_threshold: float = 0.5,
) -> list[Detection]:
    """
    Merge detections from multiple tiles and apply NMS.

    This is useful when detections from overlapping tiles may contain
    duplicates of the same object.

    Args:
        all_detections: List of detection lists (one per tile)
        iou_threshold: IoU threshold for NMS

    Returns:
        Merged and deduplicated detections
    """
    # Flatten all detections
    flat: list[Detection] = []
    for tile_dets in all_detections:
        flat.extend(tile_dets)

    # Apply NMS to remove duplicates from overlapping regions
    return nms(flat, iou_threshold)
