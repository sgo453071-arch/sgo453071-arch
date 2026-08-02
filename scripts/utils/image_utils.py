"""Image processing and ASCII conversion utilities."""

import os
from pathlib import Path
from typing import List, Tuple

from .file_utils import ensure_dir, get_project_root
from .logger import get_logger

logger = get_logger("image_utils")

# Masterpiece high-contrast ASCII character ramp
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


def convert_image_to_ascii(
    image_path: Path,
    cols: int = 68,
    aspect_ratio: float = 0.48,
    contrast_factor: float = 2.0,
) -> List[str]:
    """Convert prepped image into world-class high-resolution ASCII portrait.

    Args:
        image_path: Path to source image.
        cols: Number of ASCII characters horizontally.
        aspect_ratio: Vertical font correction factor (~0.48 for standard monospace).
        contrast_factor: Contrast enhancement multiplier.

    Returns:
        List of strings, each string representing a row of ASCII art.
    """
    if not image_path.exists():
        image_path = ensure_profile_image()

    try:
        from PIL import Image, ImageEnhance, ImageFilter, ImageOps  # type: ignore

        with Image.open(image_path) as img:
            gray = img.convert("L")
            enhanced = ImageOps.autocontrast(gray, cutoff=2)

            # Edge sharpening for eyes, tie, and suit contours
            sharpened = enhanced.filter(ImageFilter.SHARPEN)

            # Contrast boost
            enhancer = ImageEnhance.Contrast(sharpened)
            boosted = enhancer.enhance(contrast_factor)

            # Resize to 68-column high-detail ASCII grid
            w, h = boosted.size
            rows = int((h / w) * cols * aspect_ratio)
            rows = max(32, min(rows, 42))

            resized = boosted.resize((cols, rows), Image.Resampling.LANCZOS)
            pixels = list(resized.getdata())

            ramp_len = len(ASCII_RAMP)
            ascii_lines = []
            for y in range(rows):
                line = []
                for x in range(cols):
                    pixel_val = pixels[y * cols + x]
                    # Pure black background (< 15) stays clean space ' '
                    if pixel_val < 15:
                        line.append(" ")
                    else:
                        char_idx = int((pixel_val / 255.0) * (ramp_len - 1))
                        line.append(ASCII_RAMP[char_idx])
                ascii_lines.append("".join(line))

            return ascii_lines
    except Exception as err:
        logger.error(f"Error converting image to ASCII: {err}")
        return [
            "  .----------------.  ",
            " |  ASCII PORTRAIT  | ",
            " |   [ DEVELOPER ]  | ",
            "  '----------------'  ",
        ]
