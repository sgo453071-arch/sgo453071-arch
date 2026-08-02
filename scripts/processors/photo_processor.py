"""Image processor for world-class ASCII portrait prep using edge detection and CLAHE tone balancing."""

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

try:
    import cv2  # type: ignore
    import numpy as np  # type: ignore
    HAS_CV2 = True
except Exception:
    HAS_CV2 = False


def process_profile_photo() -> Path:
    """Preprocess assets/profile.jpg into a masterclass high-detail prepped image.

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

            # Crop both suit shoulders and full head for complete portrait symmetry
            w, h = processed.size
            crop_left = int(w * 0.05)
            crop_top = int(h * 0.02)
            crop_right = int(w * 0.95)
            crop_bottom = int(h * 0.88)
            cropped = processed.crop((crop_left, crop_top, crop_right, crop_bottom))

            # Advanced Tone Balancing & Feature Enhancement using OpenCV if available
            if HAS_CV2:
                try:
                    # Convert PIL image to OpenCV BGR
                    open_cv_image = cv2.cvtColor(np.array(cropped.convert("RGB")), cv2.COLOR_RGB2BGR)
                    gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)

                    # CLAHE (Contrast Limited Adaptive Histogram Equalization)
                    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
                    equalized = clahe.apply(gray)

                    # Canny Edge Detection for sharp facial/suit contours
                    edges = cv2.Canny(equalized, 50, 150)

                    # Blend Equalized Grayscale (75%) + Edge Map (25%)
                    blended = cv2.addWeighted(equalized, 0.75, edges, 0.25, 0)

                    # Convert back to PIL Image
                    processed_pil = Image.fromarray(blended)
                    processed_pil.save(output_path, "PNG")
                    logger.info(f"Generated OpenCV CLAHE-enhanced portrait -> {output_path}")
                    return output_path
                except Exception as cv_err:
                    logger.warning(f"OpenCV enhancement bypassed: {cv_err}")

            # Fallback PIL Processing
            gray_pil = cropped.convert("L")

            # Equalize and Autocontrast
            equalized_pil = ImageOps.equalize(gray_pil)
            autocontrasted = ImageOps.autocontrast(gray_pil, cutoff=2)
            blended_pil = Image.blend(equalized_pil, autocontrasted, alpha=0.6)

            # Edge Sharpening Filter
            sharpened = blended_pil.filter(ImageFilter.SHARPEN)

            # Boost contrast
            enhancer = ImageEnhance.Contrast(sharpened)
            boosted = enhancer.enhance(1.9)

            boosted.save(output_path, "PNG")
            logger.info(f"Successfully processed masterclass photo -> {output_path}")
            return output_path
    except Exception as err:
        logger.error(f"Error processing profile photo: {err}")
        return input_path


if __name__ == "__main__":
    process_profile_photo()
