"""
Post-processing module for AutoFactoryScope.
Handles merging tile detections, coordinate transformation, and Non-Max Suppression (NMS).
"""

def merge_detections(detections):
    """Merges detections from individual tiles into global coordinates."""
    merged = []
    for det in detections:
        tile_x = det.get("tile_x", 0)
        tile_y = det.get("tile_y", 0)
        x1, y1, x2, y2 = det["bbox"]
        merged.append(
            {
                "bbox": [x1 + tile_x, y1 + tile_y, x2 + tile_x, y2 + tile_y],
                "score": det["score"],
                "class_id": det.get("class_id", 0),
                "label": det.get("label"),
            }
        )
    return merged

def apply_nms(detections, iou_threshold=0.45):
    """Applies Non-Max Suppression to filter overlapping boxes."""
    def iou(box_a, box_b):
        ax1, ay1, ax2, ay2 = box_a
        bx1, by1, bx2, by2 = box_b
        inter_x1 = max(ax1, bx1)
        inter_y1 = max(ay1, by1)
        inter_x2 = min(ax2, bx2)
        inter_y2 = min(ay2, by2)
        inter_w = max(0.0, inter_x2 - inter_x1)
        inter_h = max(0.0, inter_y2 - inter_y1)
        inter_area = inter_w * inter_h
        if inter_area == 0:
            return 0.0
        area_a = max(0.0, ax2 - ax1) * max(0.0, ay2 - ay1)
        area_b = max(0.0, bx2 - bx1) * max(0.0, by2 - by1)
        union = area_a + area_b - inter_area
        if union <= 0:
            return 0.0
        return inter_area / union

    kept = []
    detections_sorted = sorted(detections, key=lambda d: d["score"], reverse=True)
    while detections_sorted:
        current = detections_sorted.pop(0)
        kept.append(current)
        remaining = []
        for det in detections_sorted:
            if det.get("class_id") == current.get("class_id"):
                if iou(det["bbox"], current["bbox"]) > iou_threshold:
                    continue
            remaining.append(det)
        detections_sorted = remaining
    return kept
