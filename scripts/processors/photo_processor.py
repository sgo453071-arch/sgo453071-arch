"""Image processor for full-frame ASCII portrait prep rendering full suit and hands."""

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
    """Preprocess assets/profile.jpg keeping 100% full frame to capture arms, hands, and suit.

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

            # Keep 100% full frame width and height so right arm, hand, and suit sleeve are preserved
            full_frame = processed

            # Advanced Tone Balancing & Feature Enhancement using OpenCV if available
            if HAS_CV2:
                try:
                    open_cv_image = cv2.cvtColor(np.array(full_frame.convert("RGB")), cv2.COLOR_RGB2BGR)
                    gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)

                    # Gamma correction to illuminate lower-right hand and arm area
                    gamma = 1.3
                    inv_gamma = 1.0 / gamma
                    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
                    gamma_corrected = cv2.LUT(gray, table)

                    # CLAHE Adaptive Histogram Equalization
                    clahe = cv2.createCLAHE(clipLimit=3.5, tileGridSize=(8, 8))
                    equalized = clahe.apply(gamma_corrected)

                    # Canny Edge Detection for sharp hand, suit, and face contours
                    edges = cv2.Canny(equalized, 40, 140)

                    # Blend Equalized Grayscale (80%) + Edge Map (20%)
                    blended = cv2.addWeighted(equalized, 0.80, edges, 0.20, 0)

                    processed_pil = Image.fromarray(blended)
                    processed_pil.save(output_path, "PNG")
                    logger.info(f"Generated full-frame arm & hand enhanced portrait -> {output_path}")
                    return output_path
                except Exception as cv_err:
                    logger.warning(f"OpenCV enhancement bypassed: {cv_err}")

            # Fallback PIL Processing
            gray_pil = full_frame.convert("L")

            # Equalize and Autocontrast
            equalized_pil = ImageOps.equalize(gray_pil)
            autocontrasted = ImageOps.autocontrast(equalized_pil, cutoff=1)

            # Edge Sharpening Filter
            sharpened = autocontrasted.filter(ImageFilter.SHARPEN)

            # Boost contrast
            enhancer = ImageEnhance.Contrast(sharpened)
            boosted = enhancer.enhance(1.8)

            boosted.save(output_path, "PNG")
            logger.info(f"Successfully processed full-frame photo -> {output_path}")
            return output_path
    except Exception as err:
        logger.error(f"Error processing profile photo: {err}")
        return input_path


if __name__ == "__main__":
    process_profile_photo()
