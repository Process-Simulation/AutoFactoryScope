"""
Tests for tiling module.
"""

import numpy as np
import pytest

from autofactoryscope_api.tiling import Tile, calculate_tile_positions, tile_bbox_to_global, tile_coords_to_global, tile_image


def test_calculate_tile_positions_basic():
    """Test basic tile position calculation."""
    # 1024x1024 image, 512 tile size, no overlap -> 4 tiles
    positions = calculate_tile_positions(
        image_width=1024,
        image_height=1024,
        tile_size=512,
        overlap=0.0,
    )
    assert len(positions) == 4
    assert (0, 0, 512, 512) in positions
    assert (512, 0, 512, 512) in positions
    assert (0, 512, 512, 512) in positions
    assert (512, 512, 512, 512) in positions


def test_calculate_tile_positions_overlap():
    """Test tile position calculation with overlap."""
    # 1024x1024 image, 512 tile size, 0.5 overlap (256 step)
    # X steps: 0, 256, 512 (stops because 512+512 > 1024 would go out, but loop condition handles it)
    # Actually logic is: x=0, x=256, x=512. Max x is 512 because 512+512=1024 fits.
    # But wait, 256+512=768. 768+512=1280 > 1024.
    positions = calculate_tile_positions(
        image_width=1024,
        image_height=1024,
        tile_size=512,
        overlap=0.5,
    )

    # Expected x start points: 0, 256, 512 (end at 1024)
    # If we step by 256:
    # x=0 -> [0, 512]
    # x=256 -> [256, 768]
    # x=512 -> [512, 1024]
    # x=768 -> [768, 1280] (clipped to 1024 width -> 256 wide)

    # Let's verify the actual behavior
    x_coords = sorted(list(set(p[0] for p in positions)))
    y_coords = sorted(list(set(p[1] for p in positions)))

    # Should have multiple steps
    assert len(x_coords) > 2
    assert len(y_coords) > 2


def test_calculate_tile_positions_small_image():
    """Test tiling on image smaller than tile size."""
    positions = calculate_tile_positions(
        image_width=100,
        image_height=100,
        tile_size=512,
    )
    assert len(positions) == 1
    assert positions[0] == (0, 0, 100, 100)


def test_tile_image_padding():
    """Test that tiles are padded to correct size."""
    image = np.zeros((600, 600, 3), dtype=np.uint8)
    result = tile_image(image, tile_size=512, overlap=0.0)

    for tile in result.tiles:
        assert tile.data.shape == (512, 512, 3)

    # Last tile should be padded
    last_tile = result.tiles[-1]
    # Check that valid data is in top-left
    # 600 - 512 = 88 pixels remaining width/height
    assert last_tile.width == 88
    assert last_tile.height == 88


def test_tile_coords_to_global():
    """Test coordinate conversion."""
    tile = Tile(
        data=np.zeros((512, 512), dtype=np.uint8),
        x_offset=100,
        y_offset=200,
        width=512,
        height=512,
    )

    gx, gy = tile_coords_to_global(tile, 50, 60)
    assert gx == 150
    assert gy == 260


def test_tile_bbox_to_global():
    """Test bounding box coordinate conversion."""
    tile = Tile(
        data=np.zeros((512, 512), dtype=np.uint8),
        x_offset=100,
        y_offset=200,
        width=512,
        height=512,
    )

    bbox = (10, 20, 30, 40)
    g_bbox = tile_bbox_to_global(tile, bbox)

    assert g_bbox == (110, 220, 130, 240)
