"""
Visualization module for drawing detection results.

Provides utilities for drawing bounding boxes, labels, and generating
annotated images.
"""

import base64
import io
from typing import Sequence

import numpy as np
from numpy.typing import NDArray
from PIL import Image, ImageDraw, ImageFont

from .postprocess import Detection


# Color palette for bounding boxes (RGB)
COLORS = [
    (255, 99, 71),  # Tomato red
    (50, 205, 50),  # Lime green
    (30, 144, 255),  # Dodger blue
    (255, 215, 0),  # Gold
    (238, 130, 238),  # Violet
    (0, 255, 255),  # Cyan
    (255, 165, 0),  # Orange
    (147, 112, 219),  # Medium purple
]


def get_color(class_id: int) -> tuple[int, int, int]:
    """Get color for a class ID."""
    return COLORS[class_id % len(COLORS)]


def draw_bbox(
    draw: ImageDraw.ImageDraw,
    detection: Detection,
    color: tuple[int, int, int] | None = None,
    thickness: int = 3,
    show_label: bool = True,
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont | None = None,
) -> None:
    """
    Draw a single bounding box on an image.

    Args:
        draw: PIL ImageDraw object
        detection: Detection to draw
        color: RGB color tuple (default: auto from class)
        thickness: Line thickness
        show_label: Whether to draw label
        font: Font for label text
    """
    if color is None:
        color = get_color(detection.class_id)

    x1, y1, x2, y2 = detection.bbox

    # Draw rectangle
    for i in range(thickness):
        draw.rectangle(
            [x1 - i, y1 - i, x2 + i, y2 + i],
            outline=color,
        )

    if show_label:
        label = f"{detection.class_name} {detection.confidence:.2f}"

        # Get text size
        if font is None:
            try:
                font = ImageFont.truetype("arial.ttf", 14)
            except OSError:
                font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), label, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        # Draw label background
        label_y = max(0, y1 - text_h - 4)
        draw.rectangle(
            [x1, label_y, x1 + text_w + 4, label_y + text_h + 4],
            fill=color,
        )

        # Draw label text
        draw.text(
            (x1 + 2, label_y + 2),
            label,
            fill=(255, 255, 255),
            font=font,
        )


def draw_detections(
    image: Image.Image | NDArray[np.uint8],
    detections: Sequence[Detection],
    thickness: int = 3,
    show_labels: bool = True,
) -> Image.Image:
    """
    Draw all detections on an image.

    Args:
        image: PIL Image or numpy array
        detections: Sequence of Detection objects
        thickness: Bounding box line thickness
        show_labels: Whether to show labels with confidence

    Returns:
        Annotated PIL Image
    """
    if isinstance(image, np.ndarray):
        image = Image.fromarray(image)
    else:
        image = image.copy()

    draw = ImageDraw.Draw(image)

    # Try to load a nice font
    font: ImageFont.FreeTypeFont | ImageFont.ImageFont | None = None
    try:
        font = ImageFont.truetype("arial.ttf", 14)
    except OSError:
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except OSError:
            font = ImageFont.load_default()

    for det in detections:
        draw_bbox(draw, det, thickness=thickness, show_label=show_labels, font=font)

    return image


def image_to_base64(image: Image.Image, format: str = "PNG") -> str:
    """
    Encode a PIL Image as base64 string.

    Args:
        image: PIL Image to encode
        format: Image format (PNG, JPEG, etc.)

    Returns:
        Base64 encoded string
    """
    buffer = io.BytesIO()
    image.save(buffer, format=format)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")


def base64_to_image(data: str) -> Image.Image:
    """
    Decode a base64 string to PIL Image.

    Args:
        data: Base64 encoded image string

    Returns:
        PIL Image
    """
    buffer = io.BytesIO(base64.b64decode(data))
    return Image.open(buffer)


def create_annotated_image(
    image: Image.Image | NDArray[np.uint8],
    detections: Sequence[Detection],
    output_format: str = "PNG",
) -> tuple[Image.Image, str]:
    """
    Create an annotated image and return both PIL Image and base64.

    Args:
        image: Input image
        detections: Detection results
        output_format: Output image format

    Returns:
        Tuple of (annotated PIL Image, base64 string)
    """
    annotated = draw_detections(image, detections)
    b64 = image_to_base64(annotated, format=output_format)
    return annotated, b64
