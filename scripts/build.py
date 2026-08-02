"""Master CLI Build Script for Animated Terminal GitHub Profile Engine."""

import argparse
import sys
from pathlib import Path

# Ensure scripts directory is on sys.path for direct python execution
scripts_dir = Path(__file__).resolve().parent
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from builders.ascii_builder import build_ascii_svg
from builders.banner_builder import build_terminal_banner
from builders.card_builder import build_info_card_svg
from builders.contribution_builder import build_contribution_heatmap_svg
from builders.project_builder import build_all_project_cards
from builders.readme_builder import build_readme_file
from builders.skills_builder import build_skills_svg
from fetchers.github_fetcher import fetch_github_contributions
from processors.photo_processor import process_profile_photo
from utils.config import ConfigManager
from utils.logger import get_logger
from validators.validate import validate_output_svgs, validate_preflight

logger = get_logger("build_engine")


def run_build(theme_override: str = None) -> bool:
    """Execute complete profile build pipeline.

    Args:
        theme_override: Optional theme name to override active theme config.

    Returns:
        True if build completed successfully, False on error.
    """
    logger.info("==================================================")
    logger.info("Starting Custom Terminal Profile Build Engine")
    logger.info("==================================================")

    # Step 1: Load Configuration & Theme Engine
    config_mgr = ConfigManager(theme_override=theme_override)

    # Step 2: Pre-flight Validation
    if not validate_preflight():
        logger.error("Pre-flight validation failed. Aborting build.")
        return False

    # Step 3: Photo Processing & ASCII Prep
    logger.info("Step 1/9: Processing profile photo...")
    process_profile_photo()

    # Step 4: Generate ASCII SVG
    logger.info("Step 2/9: Rendering ASCII portrait SVG...")
    build_ascii_svg(config_mgr)

    # Step 5: Generate Terminal Banner SVG
    logger.info("Step 3/9: Rendering terminal header banner SVG...")
    build_terminal_banner(config_mgr)

    # Step 6: Generate Neofetch Card SVG
    logger.info("Step 4/9: Rendering neofetch info card SVG...")
    build_info_card_svg(config_mgr)

    # Step 7: Fetch Contributions Data & Render Heatmap SVG
    logger.info("Step 5/9: Scraping GitHub contributions & metrics...")
    fetch_github_contributions(config_mgr.get_username())

    logger.info("Step 6/9: Rendering contribution heatmap SVG...")
    build_contribution_heatmap_svg(config_mgr)

    # Step 8: Generate Skills Matrix SVG
    logger.info("Step 7/9: Rendering skills category matrix SVG...")
    build_skills_svg(config_mgr)

    # Step 9: Generate Project Cards SVG
    logger.info("Step 8/9: Rendering project showcase cards...")
    build_all_project_cards(config_mgr)

    # Step 10: Build Master README.md
    logger.info("Step 9/9: Assembling master README.md file...")
    build_readme_file(config_mgr)

    # Step 11: Output Validation
    logger.info("Validating generated artifacts...")
    if not validate_output_svgs():
        logger.error("Output validation failed!")
        return False

    logger.info("==================================================")
    logger.info("Build Completed Successfully! Profile is updated.")
    logger.info("==================================================")
    return True


def main():
    parser = argparse.ArgumentParser(
        description="Build custom animated Linux terminal GitHub profile README."
    )
    parser.add_argument(
        "--theme",
        type=str,
        choices=["github", "matrix", "dracula", "catppuccin", "nord", "tokyonight"],
        help="Override active color theme preset.",
    )
    args = parser.parse_args()

    success = run_build(theme_override=args.theme)
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
