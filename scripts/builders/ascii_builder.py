"""Pure SVG Dot Matrix Halftone Portrait SVG Builder."""

from pathlib import Path
from typing import TYPE_CHECKING, List

from utils.file_utils import ensure_dir, get_project_root, write_text
from utils.image_utils import convert_image_to_dot_matrix, ensure_profile_image
from utils.logger import get_logger
from utils.svg_utils import wrap_in_terminal_window

if TYPE_CHECKING:
    from utils.config import ConfigManager

logger = get_logger("ascii_builder")


def build_ascii_svg(
    config_mgr: "ConfigManager",
    output_filename: str = "dots-portrait.svg",
) -> Path:
    """Generate pure animated SVG dot matrix halftone portrait card.

    Args:
        config_mgr: ConfigManager instance.
        output_filename: Target output file name.

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
    bg = theme.get("background", "#0d1117")

    width = 390
    height = 410

    # Colors for dot matrix highlights
    c_high = "#f0f6fc"  # Ice White for face highlights
    c_mid = "#38bdf8"   # Matrix Cyan for skin & facial features
    c_low = "#58a6ff"   # Deep Blue for suit coat & shoulders

    # Generate 54x48 precision dot matrix points
    dots = convert_image_to_dot_matrix(prepped_image, cols=54, rows=48)
    num_dots = len(dots)

    css_rules = [
        f"""
        @keyframes dotPop {{
          from {{ opacity: 0; transform: scale(0.2); }}
          to {{ opacity: 1; transform: scale(1); }}
        }}
        .dot-tile {{
          opacity: 0;
          animation: dotPop 0.3s ease-out forwards;
          transform-origin: center;
        }}
        .portrait-hud {{
          font-family: 'JetBrains Mono', 'Fira Code', monospace;
          font-size: 10px;
          fill: {accent};
          letter-spacing: 0.5px;
        }}
        .portrait-footer {{
          font-family: 'JetBrains Mono', 'Fira Code', monospace;
          font-size: 10.5px;
          fill: {text_muted};
        }}
        .portrait-cursor {{
          fill: {text_main};
          animation: dotPop 0.6s infinite alternate;
        }}
        """
    ]

    # Batch animation delays
    for idx in range(0, num_dots, 15):
        delay = min(600, int(idx * 0.4))
        css_rules.append(f".d-group-{idx} {{ animation-delay: {delay}ms; }}")

    custom_css = "\n".join(css_rules)

    circles_svg = []
    for idx, (cx, cy, r, brightness) in enumerate(dots):
        if brightness > 165:
            color = c_high
        elif brightness > 95:
            color = c_mid
        else:
            color = c_low

        grp = (idx // 15) * 15
        circles_svg.append(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.2f}" fill="{color}" class="dot-tile d-group-{grp}"/>'
        )

    inner_content = f"""
      <!-- Inner Terminal Photo Frame -->
      <g transform="translate(15, 12)">
        <rect x="0" y="0" width="360" height="340" rx="8" fill="{bg}" stroke="{theme.get('border', '#30363d')}" stroke-width="1"/>
        
        <!-- SVG Dot Matrix Halftone Portrait -->
        <g transform="translate(0, 0)">
          {"".join(circles_svg)}
        </g>
        
        <!-- Tech Matrix Corner Brackets -->
        <path d="M 8,20 L 8,8 L 20,8" stroke="{accent}" stroke-width="2" fill="none"/>
        <path d="M 340,8 L 352,8 L 352,20" stroke="{accent}" stroke-width="2" fill="none"/>
        <path d="M 8,320 L 8,332 L 20,332" stroke="{accent}" stroke-width="2" fill="none"/>
        <path d="M 340,332 L 352,332 L 352,320" stroke="{accent}" stroke-width="2" fill="none"/>

        <!-- Top Right Tech HUD Label -->
        <text x="345" y="24" text-anchor="end" class="portrait-hud">[SYS_ID: ARCH_DOTS]</text>
      </g>

      <!-- Bottom Status Line inside Terminal Window -->
      <text x="16" y="375" class="portrait-footer">[STATUS] 100% OPERATIONAL <tspan class="portrait-cursor">█</tspan></text>
    """

    svg_str = wrap_in_terminal_window(
        title=f"{config_mgr.get_username()} ~ portrait",
        content_svg=inner_content,
        width=width,
        height=height,
        theme=theme,
        custom_css=custom_css,
    )

    write_text(output_path, svg_str)
    logger.info(f"Generated pure SVG dot matrix halftone portrait -> {output_path}")
    return output_path
