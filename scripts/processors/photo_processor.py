"""Image processor for high-definition crystal-clear terminal profile portrait."""

import base64
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


def process_profile_photo() -> Path:
    """Preprocess assets/profile.jpg into a 100% unclipped crystal-clear HD terminal portrait.

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
            # Preserve full original frame so coat, face, tie, and arms are 100% complete
            full_frame = img.convert("RGB")

            # High resolution 480x480 for ultra-crisp display inside SVG
            resized = full_frame.resize((480, 480), Image.Resampling.LANCZOS)

            # Contrast, Color & Sharpness Enhancements
            contrast_enhancer = ImageEnhance.Contrast(resized)
            boosted_contrast = contrast_enhancer.enhance(1.20)

            color_enhancer = ImageEnhance.Color(boosted_contrast)
            boosted_color = color_enhancer.enhance(1.15)

            sharpness_enhancer = ImageEnhance.Sharpness(boosted_color)
            final_img = sharpness_enhancer.enhance(1.50)

            final_img.save(output_path, "PNG", quality=98)
            logger.info(f"Successfully processed HD full-suit portrait -> {output_path}")
            return output_path
    except Exception as err:
        logger.error(f"Error processing profile photo: {err}")
        return input_path


def get_profile_photo_base64() -> str:
    """Get base64 Data URI of assets/source-prepped.png for inline SVG embedding.

    Returns:
        Base64 string formatted as data:image/png;base64,...
    """
    output_path = process_profile_photo()
    try:
        with open(output_path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
            return f"data:image/png;base64,{encoded}"
    except Exception as err:
        logger.error(f"Error encoding photo to base64: {err}")
        return ""


if __name__ == "__main__":
    process_profile_photo()
