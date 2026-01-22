"""
Tiling module for AutoFactoryScope.
Handles splitting large layout images into 512x512 tiles and reassembling them.
"""

def split_into_tiles(image, tile_size=512, overlap=0.0):
    """Splits a large image into tiles and returns tiles with offsets."""
    width, height = image.size
    step = int(tile_size * (1.0 - overlap))
    step = max(1, step)
    tiles = []

    y = 0
    while y < height:
        x = 0
        tile_top = min(y, height - tile_size)
        tile_top = max(tile_top, 0)
        while x < width:
            tile_left = min(x, width - tile_size)
            tile_left = max(tile_left, 0)
            box = (tile_left, tile_top, tile_left + tile_size, tile_top + tile_size)
            tile = image.crop(box)
            tiles.append({"image": tile, "x": tile_left, "y": tile_top})
            x += step
            if tile_left + tile_size >= width:
                break
        y += step
        if tile_top + tile_size >= height:
            break

    return tiles

def assemble_tiles(tiles, original_size):
    """Assembles tiles back into a single image (if needed)."""
    from PIL import Image

    canvas = Image.new("RGB", original_size)
    for tile in tiles:
        canvas.paste(tile["image"], (tile["x"], tile["y"]))
    return canvas
