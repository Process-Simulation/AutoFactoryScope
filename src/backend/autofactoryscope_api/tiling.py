"""
Image tiling module for processing large factory layout images.

Splits large images into overlapping tiles for inference,
then provides utilities to map detections back to global coordinates.
"""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True)
class Tile:
    """Represents a single tile from a larger image."""

    data: NDArray[np.uint8]
    x_offset: int
    y_offset: int
    width: int
    height: int

    @property
    def bounds(self) -> tuple[int, int, int, int]:
        """Return (x1, y1, x2, y2) bounds in global coordinates."""
        return (
            self.x_offset,
            self.y_offset,
            self.x_offset + self.width,
            self.y_offset + self.height,
        )


@dataclass(frozen=True)
class TilingResult:
    """Result of tiling an image."""

    tiles: list[Tile]
    original_width: int
    original_height: int
    tile_size: int
    overlap: float


def calculate_tile_positions(
    image_width: int,
    image_height: int,
    tile_size: int = 512,
    overlap: float = 0.1,
) -> list[tuple[int, int, int, int]]:
    """
    Calculate tile positions for an image.

    Args:
        image_width: Width of the source image
        image_height: Height of the source image
        tile_size: Size of each square tile
        overlap: Overlap ratio between tiles (0.0 to 0.5)

    Returns:
        List of (x_offset, y_offset, width, height) tuples
    """
    if overlap < 0 or overlap > 0.5:
        raise ValueError("Overlap must be between 0.0 and 0.5")

    if tile_size <= 0:
        raise ValueError("Tile size must be positive")

    step = int(tile_size * (1 - overlap))
    if step <= 0:
        step = 1

    positions: list[tuple[int, int, int, int]] = []

    y = 0
    while y < image_height:
        x = 0
        while x < image_width:
            # Calculate actual tile dimensions (may be smaller at edges)
            w = min(tile_size, image_width - x)
            h = min(tile_size, image_height - y)

            positions.append((x, y, w, h))

            # Move to next column
            if x + tile_size >= image_width:
                break
            x += step

        # Move to next row
        if y + tile_size >= image_height:
            break
        y += step

    return positions


def tile_image(
    image: NDArray[np.uint8],
    tile_size: int = 512,
    overlap: float = 0.1,
) -> TilingResult:
    """
    Split an image into overlapping tiles.

    Args:
        image: Input image as numpy array (H, W, C) or (H, W)
        tile_size: Size of each square tile
        overlap: Overlap ratio between tiles

    Returns:
        TilingResult containing all tiles and metadata
    """
    if image.ndim == 2:
        height, width = image.shape
    elif image.ndim == 3:
        height, width = image.shape[:2]
    else:
        raise ValueError(f"Expected 2D or 3D image, got shape {image.shape}")

    positions = calculate_tile_positions(width, height, tile_size, overlap)

    tiles: list[Tile] = []
    for x, y, w, h in positions:
        tile_data = image[y : y + h, x : x + w].copy()

        # Pad tile to full size if at edge
        if w < tile_size or h < tile_size:
            if image.ndim == 3:
                padded = np.zeros((tile_size, tile_size, image.shape[2]), dtype=np.uint8)
            else:
                padded = np.zeros((tile_size, tile_size), dtype=np.uint8)
            padded[:h, :w] = tile_data
            tile_data = padded

        tiles.append(
            Tile(
                data=tile_data,
                x_offset=x,
                y_offset=y,
                width=w,
                height=h,
            )
        )

    return TilingResult(
        tiles=tiles,
        original_width=width,
        original_height=height,
        tile_size=tile_size,
        overlap=overlap,
    )


def tile_coords_to_global(
    tile: Tile,
    local_x: float,
    local_y: float,
) -> tuple[float, float]:
    """
    Convert tile-local coordinates to global image coordinates.

    Args:
        tile: The tile containing the detection
        local_x: X coordinate within the tile
        local_y: Y coordinate within the tile

    Returns:
        (global_x, global_y) coordinates
    """
    return (tile.x_offset + local_x, tile.y_offset + local_y)


def tile_bbox_to_global(
    tile: Tile,
    bbox: tuple[float, float, float, float],
) -> tuple[float, float, float, float]:
    """
    Convert a bounding box from tile coordinates to global coordinates.

    Args:
        tile: The tile containing the detection
        bbox: (x1, y1, x2, y2) in tile-local coordinates

    Returns:
        (x1, y1, x2, y2) in global image coordinates
    """
    x1, y1, x2, y2 = bbox
    return (
        tile.x_offset + x1,
        tile.y_offset + y1,
        tile.x_offset + x2,
        tile.y_offset + y2,
    )
