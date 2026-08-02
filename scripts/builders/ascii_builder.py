"""ASCII Portrait SVG Builder."""

from pathlib import Path
from typing import TYPE_CHECKING, List

from utils.file_utils import ensure_dir, get_project_root, write_text
from utils.image_utils import convert_image_to_ascii, ensure_profile_image
from utils.logger import get_logger
from utils.svg_utils import escape_xml, wrap_in_terminal_window

if TYPE_CHECKING:
    from utils.config import ConfigManager

logger = get_logger("ascii_builder")


def build_ascii_svg(
    config_mgr: "ConfigManager",
    output_filename: str = "ascii-profile.svg",
    cols: int = 68,
) -> Path:
    """Generate world-class high-resolution animated monochrome ASCII portrait SVG.

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
    accent = theme.get("accent", "#38bdf8")
    text_main = theme.get("text_main", "#c9d1d9")
    text_muted = theme.get("text_muted", "#8b949e")

    # Generate 68-column high-detail ASCII lines
    ascii_lines = convert_image_to_ascii(prepped_image, cols=cols, aspect_ratio=0.48)
    num_rows = len(ascii_lines)

    width = 390
    height = 410

    row_height = 8.8
    font_size = 7.8

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
          fill: {accent};
          white-space: pre;
          opacity: 0;
          animation: asciiFade 0.3s ease-out forwards;
        }}
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
    for idx, line in enumerate(ascii_lines):
        escaped_line = escape_xml(line)
        lines_svg.append(
            f'<text x="10" y="{y_offset}" class="ascii-art ar-{idx}" xml:space="preserve">{escaped_line}</text>'
        )
        y_offset += row_height

    # Footer status inside portrait card
    lines_svg.append(
        f'<text x="10" y="375" class="ascii-footer">[STATUS] 100% OPERATIONAL <tspan class="ascii-cursor">█</tspan></text>'
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
    logger.info(f"Generated masterclass ASCII profile SVG -> {output_path}")
    return output_path
