"""Image processor for Stylized Terminal Matrix Vector Portrait."""

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

try:
    import cv2  # type: ignore
    import numpy as np  # type: ignore
    HAS_CV2 = True
except Exception:
    HAS_CV2 = False


def process_profile_photo() -> Path:
    """Preprocess assets/profile.jpg into a stylized, high-contrast terminal matrix portrait.

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
            rgb = img.convert("RGB")
            w, h = rgb.size

            # Full upper torso framing
            cropped = rgb.crop((int(w * 0.05), int(h * 0.02), int(w * 0.95), int(h * 0.85)))
            resized = cropped.resize((420, 420), Image.Resampling.LANCZOS)

            if HAS_CV2:
                try:
                    # Convert to OpenCV BGR
                    cv_img = cv2.cvtColor(np.array(resized), cv2.COLOR_RGB2BGR)
                    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

                    # Bilateral filter for smooth skin shading (removes noise dots)
                    smooth = cv2.bilateralFilter(gray, 9, 75, 75)

                    # CLAHE contrast enhancement for facial features
                    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
                    enhanced = clahe.apply(smooth)

                    # Adaptive threshold for clean vector line contours
                    edges = cv2.adaptiveThreshold(
                        enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
                    )

                    # Create Matrix color posterized palette: Cyberpunk Cyan & Soft Blue
                    color_posterized = cv2.stylization(cv_img, sigma_s=60, sigma_r=0.45)

                    # Combine smooth color posterization with clean line contours
                    combined = cv2.bitwise_and(color_posterized, color_posterized, mask=edges)

                    result_pil = Image.fromarray(cv2.cvtColor(combined, cv2.COLOR_BGR2RGB))
                    result_pil.save(output_path, "PNG")
                    logger.info(f"Generated OpenCV Stylized Matrix Portrait -> {output_path}")
                    return output_path
                except Exception as cv_err:
                    logger.warning(f"OpenCV stylization bypassed: {cv_err}")

            # Fallback PIL Processing (Smooth Posterization)
            gray_pil = resized.convert("L")
            poster = ImageOps.posterize(resized, 3)
            contrast_enhancer = ImageEnhance.Contrast(poster)
            boosted = contrast_enhancer.enhance(1.3)
            boosted.save(output_path, "PNG")
            logger.info(f"Generated PIL Posterized Portrait -> {output_path}")
            return output_path
    except Exception as err:
        logger.error(f"Error processing profile photo: {err}")
        return input_path


def get_profile_photo_base64() -> str:
    """Get base64 Data URI of assets/source-prepped.png.

    Returns:
        Base64 string.
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
