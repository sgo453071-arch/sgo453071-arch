"""Image processor for photo preparation and background isolation."""

from pathlib import Path
from typing import Optional

from utils.file_utils import ensure_dir, get_project_root
from utils.image_utils import ensure_profile_image
from utils.logger import get_logger

logger = get_logger("photo_processor")


def process_profile_photo() -> Path:
    """Preprocess assets/profile.jpg into contrast-boosted assets/source-prepped.png.

    Returns:
        Path to generated assets/source-prepped.png.
    """
    root = get_project_root()
    input_path = root / "assets" / "profile.jpg"
    output_path = root / "assets" / "source-prepped.png"

    if not input_path.exists():
        input_path = ensure_profile_image()

    ensure_dir(output_path.parent)

    try:
        from PIL import Image, ImageEnhance, ImageFilter, ImageOps

        with Image.open(input_path) as img:
            # Step 1: Attempt background removal if rembg is available
            processed = img
            try:
                import rembg
                logger.info("Applying rembg background removal...")
                processed_bytes = rembg.remove(img)
                if isinstance(processed_bytes, Image.Image):
                    processed = processed_bytes
            except Exception as rembg_err:
                logger.warning(f"rembg background removal bypassed: {rembg_err}")

            # Step 2: Grayscale & Contrast boost
            gray = processed.convert("L")
            enhanced = ImageOps.autocontrast(gray)

            enhancer = ImageEnhance.Contrast(enhanced)
            contrast_boosted = enhancer.enhance(1.5)

            # Step 3: Sharpen edges
            sharpened = contrast_boosted.filter(ImageFilter.SHARPEN)

            sharpened.save(output_path, "PNG")
            logger.info(f"Successfully processed photo -> {output_path}")
            return output_path
    except Exception as err:
        logger.error(f"Error processing profile photo: {err}")
        return input_path


if __name__ == "__main__":
    process_profile_photo()
