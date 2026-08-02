"""Image processing and dot matrix halftone grid generator."""

import os
from pathlib import Path
from typing import Dict, List, Tuple

from .file_utils import ensure_dir, get_project_root
from .logger import get_logger

logger = get_logger("image_utils")


def ensure_profile_image() -> Path:
    """Ensure a source photo exists in assets/profile.jpg.

    Returns:
        Path to assets/profile.jpg file.
    """
    root = get_project_root()
    profile_path = root / "assets" / "profile.jpg"
    ensure_dir(profile_path.parent)
    return profile_path


def convert_image_to_dot_matrix(
    image_path: Path,
    cols: int = 54,
    rows: int = 48,
) -> List[Tuple[float, float, float, int]]:
    """Convert photo into precision (x, y, radius, brightness) dot matrix halftone grid.

    Args:
        image_path: Path to source photo.
        cols: Horizontal dot grid resolution.
        rows: Vertical dot grid resolution.

    Returns:
        List of (x_pos, y_pos, radius, brightness) dot tuples.
    """
    if not image_path.exists():
        image_path = ensure_profile_image()

    try:
        from PIL import Image, ImageEnhance, ImageFilter, ImageOps  # type: ignore

        with Image.open(image_path) as img:
            rgb = img.convert("RGB")
            w, h = rgb.size

            # Crop upper torso & head cleanly (5% to 85% bounds)
            cropped = rgb.crop((int(w * 0.05), int(h * 0.02), int(w * 0.95), int(h * 0.85)))
            gray = cropped.convert("L")

            # High contrast and edge sharpening
            enhanced = ImageOps.autocontrast(gray, cutoff=2)
            sharpened = enhanced.filter(ImageFilter.SHARPEN)

            enhancer = ImageEnhance.Contrast(sharpened)
            boosted = enhancer.enhance(1.8)

            resized = boosted.resize((cols, rows), Image.Resampling.LANCZOS)
            pixels = list(resized.getdata())

            # Layout bounds inside 360x340 portrait box
            box_w = 360
            box_h = 340
            dx = box_w / cols
            dy = box_h / rows

            dots = []
            for y in range(rows):
                for x in range(cols):
                    brightness = pixels[y * cols + x]
                    # Background noise cutoff (< 22) -> no dot
                    if brightness >= 22:
                        cx = 15 + (x + 0.5) * dx
                        cy = 12 + (y + 0.5) * dy
                        # Dynamic dot radius proportional to brightness (0.8px to 3.2px)
                        r = 0.8 + (brightness / 255.0) * 2.4
                        dots.append((cx, cy, r, brightness))

            return dots
    except Exception as err:
        logger.error(f"Error generating dot matrix grid: {err}")
        return []
