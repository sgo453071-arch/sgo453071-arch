"""Image processing and ASCII conversion utilities."""

import os
from pathlib import Path
from typing import List, Tuple

from .file_utils import ensure_dir, get_project_root
from .logger import get_logger

logger = get_logger("image_utils")

# Character ramp from dense to light
ASCII_CHARS = "@$B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "


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
        from PIL import Image, ImageDraw, ImageFont

        # Generate a stylized default profile picture (400x400)
        img = Image.new("RGB", (400, 400), color=(13, 17, 23))
        draw = ImageDraw.Draw(img)

        # Outer avatar circle
        draw.ellipse([50, 50, 350, 350], fill=(22, 27, 34), outline=(88, 166, 255), width=4)

        # Head / Shoulders silhouette
        draw.ellipse([140, 90, 260, 210], fill=(88, 166, 255))
        draw.ellipse([90, 220, 310, 370], fill=(88, 166, 255))

        img.save(profile_path, "JPEG")
        logger.info(f"Generated sample profile photo at {profile_path}")
    except Exception as err:
        logger.error(f"Could not generate profile image with Pillow: {err}")

    return profile_path


def convert_image_to_ascii(
    image_path: Path,
    cols: int = 70,
    aspect_ratio: float = 0.55,
    contrast_factor: float = 1.4,
) -> List[str]:
    """Convert image file into list of ASCII string rows.

    Args:
        image_path: Path to source image.
        cols: Number of ASCII characters horizontally.
        aspect_ratio: Vertical font correction factor (~0.55 for standard terminal fonts).
        contrast_factor: Contrast adjustment multiplier.

    Returns:
        List of strings, each string representing a row of ASCII art.
    """
    if not image_path.exists():
        image_path = ensure_profile_image()

    try:
        from PIL import Image, ImageEnhance, ImageOps

        with Image.open(image_path) as img:
            # Convert to Grayscale
            img = img.convert("L")

            # Auto contrast & enhance
            img = ImageOps.autocontrast(img)
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(contrast_factor)

            # Resize keeping aspect ratio
            w, h = img.size
            rows = int((h / w) * cols * aspect_ratio)
            rows = max(15, min(rows, 90))  # Cap bound rows for optimal SVG height

            img = img.resize((cols, rows), Image.Resampling.LANCZOS)
            pixels = img.getdata()

            # Map pixels to ASCII character ramp
            ramp_len = len(ASCII_CHARS)
            ascii_lines = []
            for y in range(rows):
                line = ""
                for x in range(cols):
                    pixel_val = pixels[y * cols + x]
                    char_idx = int((pixel_val / 255.0) * (ramp_len - 1))
                    line += ASCII_CHARS[char_idx]
                ascii_lines.append(line)

            return ascii_lines
    except Exception as err:
        logger.error(f"Error converting image to ASCII: {err}")
        # Fallback default ASCII portrait
        return [
            "  .----------------.  ",
            " |  ASCII PORTRAIT  | ",
            " |   [ DEVELOPER ]  | ",
            "  '----------------'  ",
        ]
