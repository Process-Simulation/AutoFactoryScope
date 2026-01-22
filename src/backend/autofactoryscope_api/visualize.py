"""
Visualization module for AutoFactoryScope.
Handles drawing bounding boxes and labels on layout images.
"""

def draw_boxes(image, detections):
    """Draws bounding boxes on the image."""
    from PIL import ImageDraw

    draw = ImageDraw.Draw(image)
    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        draw.rectangle([x1, y1, x2, y2], outline="red", width=2)
    return image

def annotate_image(image, detections):
    """Adds labels and scores to the bounding boxes."""
    from PIL import ImageDraw, ImageFont

    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        label = det.get("label") or f"class {det.get('class_id', 0)}"
        score = det.get("score", 0.0)
        text = f"{label} {score:.2f}"
        draw.rectangle([x1, y1, x2, y2], outline="red", width=2)
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
        except Exception:
            text_w = 80
            text_h = 12
        text_bg = [x1, max(0, y1 - text_h - 4), x1 + text_w + 4, y1]
        draw.rectangle(text_bg, fill="red")
        draw.text((x1 + 2, max(0, y1 - text_h - 2)), text, fill="white", font=font)
    return image
