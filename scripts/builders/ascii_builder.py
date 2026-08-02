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
    cols: int = 50,
) -> Path:
    """Generate animated monochrome ASCII portrait SVG aligned with Neofetch card dimensions.

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
    text_main = theme.get("text_main", "#3fb950")
    accent = theme.get("accent", "#58a6ff")

    # Generate ASCII lines
    ascii_lines = convert_image_to_ascii(prepped_image, cols=cols, aspect_ratio=0.52)
    num_rows = len(ascii_lines)

    width = 410
    height = 420

    row_height = 11.5
    font_size = 9.5

    css_rules = [
        f"""
        @keyframes asciiFade {{
          from {{ opacity: 0; }}
          to {{ opacity: 1; }}
        }}
        .ascii-art {{
          font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
          font-size: {font_size}px;
          fill: {text_main};
          white-space: pre;
          opacity: 0;
          animation: asciiFade 0.4s ease-out forwards;
        }}
        .ascii-cursor {{
          fill: {accent};
          animation: asciiFade 0.6s infinite alternate;
        }}
        """
    ]

    for idx in range(num_rows):
        delay = idx * 25
        css_rules.append(f".ar-{idx} {{ animation-delay: {delay}ms; }}")

    custom_css = "\n".join(css_rules)

    lines_svg = []
    y_offset = 20
    for idx, line in enumerate(ascii_lines):
        escaped_line = escape_xml(line)
        lines_svg.append(
            f'<text x="16" y="{y_offset}" class="ascii-art ar-{idx}" xml:space="preserve">{escaped_line}</text>'
        )
        y_offset += row_height

    # Cursor
    lines_svg.append(
        f'<text x="16" y="{y_offset + 4}" class="ascii-art ar-{num_rows-1} ascii-cursor">█</text>'
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
