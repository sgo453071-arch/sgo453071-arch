"""Image processing and multi-tone ASCII conversion utilities."""

import os
from pathlib import Path
from typing import Dict, List, Tuple

from .file_utils import ensure_dir, get_project_root
from .logger import get_logger

logger = get_logger("image_utils")

# Multi-tone character ramp
ASCII_RAMP = "   ..::-=+*#%@"


def ensure_profile_image() -> Path:
    """Ensure a source photo exists in assets/profile.jpg.

    Returns:
        Path to assets/profile.jpg file.
    """
    root = get_project_root()
    profile_path = root / "assets" / "profile.jpg"
    ensure_dir(profile_path.parent)
    return profile_path


def convert_image_to_ascii_grid(
    image_path: Path,
    cols: int = 70,
    aspect_ratio: float = 0.48,
) -> List[List[Tuple[str, int]]]:
    """Convert prepped image into structured (character, intensity_val) grid for multi-color rendering.

    Args:
        image_path: Path to source image.
        cols: Number of ASCII characters horizontally.
        aspect_ratio: Vertical font correction factor (~0.48 for standard monospace).

    Returns:
        2D Grid of (character, pixel_brightness) tuples.
    """
    if not image_path.exists():
        image_path = ensure_profile_image()

    try:
        from PIL import Image, ImageEnhance, ImageFilter, ImageOps  # type: ignore

        with Image.open(image_path) as img:
            gray = img.convert("L")
            enhanced = ImageOps.autocontrast(gray, cutoff=2)
            sharpened = enhanced.filter(ImageFilter.SHARPEN)

            enhancer = ImageEnhance.Contrast(sharpened)
            boosted = enhancer.enhance(1.8)

            w, h = boosted.size
            rows = int((h / w) * cols * aspect_ratio)
            rows = max(32, min(rows, 42))

            resized = boosted.resize((cols, rows), Image.Resampling.LANCZOS)
            pixels = list(resized.getdata())

            ramp_len = len(ASCII_RAMP)
            grid = []
            for y in range(rows):
                row_cells = []
                for x in range(cols):
                    pixel_val = pixels[y * cols + x]
                    if pixel_val < 16:
                        row_cells.append((" ", 0))
                    else:
                        char_idx = int((pixel_val / 255.0) * (ramp_len - 1))
                        row_cells.append((ASCII_RAMP[char_idx], pixel_val))
                grid.append(row_cells)

            return grid
    except Exception as err:
        logger.error(f"Error converting image to ASCII grid: {err}")
        return [[(" ", 0)]]


def convert_image_to_ascii(
    image_path: Path,
    cols: int = 70,
    aspect_ratio: float = 0.48,
    contrast_factor: float = 1.9,
) -> List[str]:
    """Fallback plain text ASCII converter.

    Args:
        image_path: Path to source image.
        cols: Number of ASCII characters horizontally.
        aspect_ratio: Vertical font correction factor.
        contrast_factor: Contrast multiplier.

    Returns:
        List of ASCII strings.
    """
    grid = convert_image_to_ascii_grid(image_path, cols=cols, aspect_ratio=aspect_ratio)
    return ["".join(cell[0] for cell in row) for row in grid]
