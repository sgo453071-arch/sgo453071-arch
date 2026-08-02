"""Pre-flight and post-build validation suite."""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Tuple

from utils.file_utils import get_project_root, read_json
from utils.logger import get_logger

logger = get_logger("validator")


def validate_preflight() -> bool:
    """Validate project structure and configuration files before building.

    Returns:
        True if preflight validation passes, False otherwise.
    """
    root = get_project_root()
    logger.info("Executing pre-flight validation checks...")

    required_configs = [
        root / "config" / "profile.json",
        root / "config" / "theme.json",
        root / "config" / "animation.json",
        root / "config" / "projects.json",
    ]

    for config_path in required_configs:
        if not config_path.exists():
            logger.error(f"Missing required configuration file: {config_path}")
            return False
        data = read_json(config_path, fallback=None)
        if data is None:
            logger.error(f"Invalid JSON in config file: {config_path}")
            return False

    # Check theme pointer validity
    theme_ptr = read_json(root / "config" / "theme.json", fallback={})
    theme_name = theme_ptr.get("active_theme", "github")
    theme_path = root / "themes" / f"{theme_name}.json"
    if not theme_path.exists():
        logger.error(f"Configured theme file missing: {theme_path}")
        return False

    logger.info("Pre-flight validation passed successfully.")
    return True


def validate_output_svgs() -> bool:
    """Validate XML syntax and presence of all rendered SVG files in assets/generated/.

    Returns:
        True if all output SVGs are valid XML documents.
    """
    root = get_project_root()
    gen_dir = root / "assets" / "generated"

    expected_svgs = [
        "profile-hd-portrait.svg",
        "info-card.svg",
        "contribution-graph.svg",
        "leetcode-heatmap.svg",
        "skills.svg",
        "project-disha.svg",
        "project-ai.svg",
        "project-portfolio.svg",
    ]

    success = True
    for svg_name in expected_svgs:
        svg_file = gen_dir / svg_name
        if not svg_file.exists():
            logger.error(f"Expected output SVG missing: {svg_file}")
            success = False
            continue

        try:
            tree = ET.parse(svg_file)
            root_elem = tree.getroot()
            if not root_elem.tag.endswith("svg"):
                logger.error(f"{svg_name} root XML tag is not <svg>")
                success = False
        except Exception as xml_err:
            logger.error(f"Invalid SVG XML syntax in {svg_name}: {xml_err}")
            success = False

    if success:
        logger.info("All output SVGs validated successfully.")
    return success


if __name__ == "__main__":
    if validate_preflight():
        print("Preflight validation OK")
    else:
        print("Preflight validation FAILED")
