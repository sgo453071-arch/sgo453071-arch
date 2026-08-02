"""Image processor for photo preparation and background isolation."""

import sys
from pathlib import Path

# Ensure scripts directory is on sys.path
scripts_dir = Path(__file__).resolve().parent.parent
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from utils.file_utils import ensure_dir, get_project_root
from utils.image_utils import ensure_profile_image
from utils.logger import get_logger

logger = get_logger("photo_processor")

try:
    from PIL import Image, ImageEnhance, ImageFilter, ImageOps  # type: ignore
    HAS_PIL = True
except Exception:
    HAS_PIL = False

try:
    import rembg  # type: ignore
    HAS_REMBG = True
except Exception:
    HAS_REMBG = False


def process_profile_photo() -> Path:
    """Preprocess assets/profile.jpg into balanced, full-torso assets/source-prepped.png.

    Returns:
        Path to generated assets/source-prepped.png.
    """
    root = get_project_root()
    input_path = root / "assets" / "profile.jpg"
    output_path = root / "assets" / "source-prepped.png"

    if not input_path.exists():
        input_path = ensure_profile_image()

    ensure_dir(output_path.parent)

    if not HAS_PIL:
        logger.warning("Pillow library not loaded, returning original input path.")
        return input_path

    try:
        with Image.open(input_path) as img:
            processed = img
            if HAS_REMBG:
                try:
                    logger.info("Applying rembg background removal...")
                    processed_bytes = rembg.remove(img)
                    if isinstance(processed_bytes, Image.Image):
                        processed = processed_bytes
                except Exception as rembg_err:
                    logger.warning(f"rembg background removal bypassed: {rembg_err}")

            # Crop both shoulders fully to maintain full suit symmetry
            w, h = processed.size
            crop_left = int(w * 0.10)
            crop_top = int(h * 0.04)
            crop_right = int(w * 0.90)
            crop_bottom = int(h * 0.85)
            cropped = processed.crop((crop_left, crop_top, crop_right, crop_bottom))

            # Convert to grayscale
            gray = cropped.convert("L")

            # Equalize histogram to lift shadow details on right shoulder
            equalized = ImageOps.equalize(gray)

            # Blend equalized image with autocontrast to balance highlights & shadow
            autocontrasted = ImageOps.autocontrast(gray, cutoff=2)
            blended = Image.blend(equalized, autocontrasted, alpha=0.5)

            # Edge sharpening filter
            sharpened = blended.filter(ImageFilter.SHARPEN)

            # Boost contrast
            enhancer = ImageEnhance.Contrast(sharpened)
            boosted = enhancer.enhance(1.8)

            boosted.save(output_path, "PNG")
            logger.info(f"Successfully processed balanced suit photo -> {output_path}")
            return output_path
    except Exception as err:
        logger.error(f"Error processing profile photo: {err}")
        return input_path


if __name__ == "__main__":
    process_profile_photo()
