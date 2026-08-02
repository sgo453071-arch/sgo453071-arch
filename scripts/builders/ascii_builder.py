"""ASCII Portrait SVG Builder with Multi-Tone Color Highlighting."""

from pathlib import Path
from typing import TYPE_CHECKING, List

from utils.file_utils import ensure_dir, get_project_root, write_text
from utils.image_utils import convert_image_to_ascii_grid, ensure_profile_image
from utils.logger import get_logger
from utils.svg_utils import escape_xml, wrap_in_terminal_window

if TYPE_CHECKING:
    from utils.config import ConfigManager

logger = get_logger("ascii_builder")


def build_ascii_svg(
    config_mgr: "ConfigManager",
    output_filename: str = "ascii-profile.svg",
    cols: int = 70,
) -> Path:
    """Generate multi-tone crystal-clear animated ASCII portrait SVG.

    Args:
        config_mgr: ConfigManager instance.
        output_filename: Target output file name.
        cols: Number of characters per ASCII row.

    Returns:
        Path to rendered SVG file.
    """
    root = get_project_root()
    output_path = root / "assets" / "generated" / output_filename
    ensure_dir(output_path.parent)

    prepped_image = root / "assets" / "source-prepped.png"
    if not prepped_image.exists():
        prepped_image = ensure_profile_image()

    theme = config_mgr.theme
    text_main = theme.get("text_main", "#c9d1d9")
    text_muted = theme.get("text_muted", "#8b949e")

    # Colors for multi-tone portrait clarity
    color_high = "#f0f6fc"  # Bright white/ice for skin highlights & shirt collar
    color_mid = "#38bdf8"   # Vibrant cyan for face contours & features
    color_low = "#58a6ff"   # Soft blue for suit jacket & shoulders

    # Generate 70-column multi-tone ASCII grid
    grid = convert_image_to_ascii_grid(prepped_image, cols=cols, aspect_ratio=0.48)
    num_rows = len(grid)

    width = 390
    height = 410

    row_height = 8.6
    font_size = 7.6

    css_rules = [
        f"""
        @keyframes asciiFade {{
          from {{ opacity: 0; }}
          to {{ opacity: 1; }}
        }}
        .ascii-art {{
          font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
          font-size: {font_size}px;
          font-weight: 700;
          white-space: pre;
          opacity: 0;
          animation: asciiFade 0.3s ease-out forwards;
        }}
        .c-high {{ fill: {color_high}; }}
        .c-mid  {{ fill: {color_mid}; }}
        .c-low  {{ fill: {color_low}; }}
        .ascii-cursor {{
          fill: {text_main};
          animation: asciiFade 0.6s infinite alternate;
        }}
        .ascii-footer {{
          font-family: 'JetBrains Mono', 'Fira Code', monospace;
          font-size: 10px;
          fill: {text_muted};
        }}
        """
    ]

    for idx in range(num_rows):
        delay = idx * 10
        css_rules.append(f".ar-{idx} {{ animation-delay: {delay}ms; }}")

    custom_css = "\n".join(css_rules)

    lines_svg = []
    y_offset = 16
    for idx, row in enumerate(grid):
        tspans = []
        for char, brightness in row:
            escaped_char = escape_xml(char)
            if brightness > 165:
                cls = "c-high"
            elif brightness > 90:
                cls = "c-mid"
            else:
                cls = "c-low"
            tspans.append(f'<tspan class="{cls}">{escaped_char}</tspan>')

        lines_svg.append(
            f'<text x="8" y="{y_offset}" class="ascii-art ar-{idx}" xml:space="preserve">{"".join(tspans)}</text>'
        )
        y_offset += row_height

    # Footer status inside portrait card
    lines_svg.append(
        f'<text x="8" y="375" class="ascii-footer">[STATUS] 100% OPERATIONAL <tspan class="ascii-cursor">█</tspan></text>'
    )

    inner_content = "\n".join(lines_svg)

    svg_str = wrap_in_terminal_window(
        title=f"{config_mgr.get_username()} ~ portrait",
        content_svg=inner_content,
        width=width,
        height=height,
        theme=theme,
        custom_css=custom_css,
    )

    write_text(output_path, svg_str)
    logger.info(f"Generated multi-tone crystal-clear ASCII profile SVG -> {output_path}")
    return output_path
