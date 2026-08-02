"""ASCII Portrait SVG Builder."""

from pathlib import Path
from typing import List

from utils.file_utils import ensure_dir, get_project_root, write_text
from utils.image_utils import convert_image_to_ascii, ensure_profile_image
from utils.logger import get_logger
from utils.svg_utils import escape_xml, wrap_in_terminal_window

logger = get_logger("ascii_builder")


def build_ascii_svg(
    config_mgr: "ConfigManager",
    output_filename: str = "ascii-profile.svg",
    cols: int = 58,
) -> Path:
    """Generate animated row-by-row monochrome ASCII portrait SVG.

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
    text_main = theme.get("text_main", "#00ff41")
    accent = theme.get("accent", "#58a6ff")

    # Generate ASCII lines
    ascii_lines = convert_image_to_ascii(prepped_image, cols=cols, aspect_ratio=0.52)
    num_rows = len(ascii_lines)

    row_height = 14
    font_size = 11
    width = max(420, cols * 7 + 40)
    height = num_rows * row_height + 70

    # Build keyframes for sequential row-by-row typing (plays ONCE)
    row_delay_ms = 40
    total_anim_duration = num_rows * row_delay_ms

    css_rules = [
        f"""
        @keyframes fadeInRow {{
          from {{ opacity: 0; transform: translateY(2px); }}
          to {{ opacity: 1; transform: translateY(0); }}
        }}
        @keyframes cursorBlink {{
          0%, 100% {{ opacity: 1; }}
          50% {{ opacity: 0; }}
        }}
        .ascii-row {{
          font-size: {font_size}px;
          fill: {text_main};
          opacity: 0;
          animation: fadeInRow 0.2s ease-out forwards;
        }}
        .ascii-cursor {{
          fill: {accent};
          animation: cursorBlink 0.6s infinite;
        }}
        """
    ]

    # Dynamic delay for each row
    for idx in range(num_rows):
        delay = idx * row_delay_ms
        css_rules.append(f".r-{idx} {{ animation-delay: {delay}ms; }}")

    custom_css = "\n".join(css_rules)

    lines_svg = []
    y_offset = 24
    for idx, line in enumerate(ascii_lines):
        escaped_line = escape_xml(line)
        lines_svg.append(
            f'<text x="20" y="{y_offset}" class="ascii-row r-{idx}" xml:space="preserve">{escaped_line}</text>'
        )
        y_offset += row_height

    # Final blinking cursor position below ASCII portrait
    cursor_y = y_offset + 5
    lines_svg.append(
        f'<text x="20" y="{cursor_y}" class="ascii-row r-{num_rows-1} ascii-cursor">█</text>'
    )

    inner_content = "\n".join(lines_svg)

    svg_str = wrap_in_terminal_window(
        title=f"cat assets/profile.ascii",
        content_svg=inner_content,
        width=width,
        height=height,
        theme=theme,
        custom_css=custom_css,
    )

    write_text(output_path, svg_str)
    logger.info(f"Generated ASCII profile SVG -> {output_path}")
    return output_path
