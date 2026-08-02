"""Image processing and ASCII conversion utilities."""

import os
from pathlib import Path
from typing import List, Tuple

from .file_utils import ensure_dir, get_project_root
from .logger import get_logger

logger = get_logger("image_utils")

# Character ramp optimized for dark terminal backgrounds (0=space/dark, 255=bright)
ASCII_RAMP = "   ..::-=+*#%@"


def ensure_profile_image() -> Path:
    """Ensure a source photo exists in assets/profile.jpg; generate sample if missing.

    Returns:
        Path to assets/profile.jpg file.
    """
    root = get_project_root()
    profile_path = root / "assets" / "profile.jpg"
    ensure_dir(profile_path.parent)

    if profile_path.exists():
        return profile_path

    logger.warning("assets/profile.jpg not found. Generating default developer portrait...")
    try:
        from PIL import Image, ImageDraw

        img = Image.new("RGB", (400, 400), color=(13, 17, 23))
        draw = ImageDraw.Draw(img)
        draw.ellipse([50, 50, 350, 350], fill=(22, 27, 34), outline=(88, 166, 255), width=4)
        draw.ellipse([140, 90, 260, 210], fill=(88, 166, 255))
        draw.ellipse([90, 220, 310, 370], fill=(88, 166, 255))
        img.save(profile_path, "JPEG")
    except Exception as err:
        logger.error(f"Could not generate profile image: {err}")

    return profile_path


def convert_image_to_ascii(
    image_path: Path,
    cols: int = 56,
    aspect_ratio: float = 0.50,
    contrast_factor: float = 1.6,
) -> List[str]:
    """Convert image file into clean list of ASCII string rows.

    Args:
        image_path: Path to source image.
        cols: Number of ASCII characters horizontally.
        aspect_ratio: Vertical font correction factor (~0.50 for standard monospace).
        contrast_factor: Contrast enhancement multiplier.

    Returns:
        List of strings, each string representing a row of ASCII art.
    """
    if not image_path.exists():
        image_path = ensure_profile_image()

    try:
        from PIL import Image, ImageEnhance, ImageOps

        with Image.open(image_path) as img:
            # Convert to Grayscale & Autocontrast
            gray = img.convert("L")
            enhanced = ImageOps.autocontrast(gray)

            # Boost contrast to make facial features sharp
            enhancer = ImageEnhance.Contrast(enhanced)
            boosted = enhancer.enhance(contrast_factor)

            # Resize keeping character aspect ratio
            w, h = boosted.size
            rows = int((h / w) * cols * aspect_ratio)
            rows = max(20, min(rows, 45))  # Keep rows between 20 and 45 for perfect card fit

            resized = boosted.resize((cols, rows), Image.Resampling.LANCZOS)
            pixels = list(resized.getdata())

            ramp_len = len(ASCII_RAMP)
            ascii_lines = []
            for y in range(rows):
                line = []
                for x in range(cols):
                    pixel_val = pixels[y * cols + x]
                    # Map 0 (dark) to ' ' space, 255 (bright) to '@'
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
