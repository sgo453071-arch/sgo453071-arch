"""Crystal-Clear Terminal Portrait SVG Builder embedding HD base64 image with HUD elements."""

from pathlib import Path
from typing import TYPE_CHECKING, List

from processors.photo_processor import get_profile_photo_base64, process_profile_photo
from utils.file_utils import ensure_dir, get_project_root, write_text
from utils.logger import get_logger
from utils.svg_utils import wrap_in_terminal_window

if TYPE_CHECKING:
    from utils.config import ConfigManager

logger = get_logger("ascii_builder")


def build_ascii_svg(
    config_mgr: "ConfigManager",
    output_filename: str = "profile-hd-portrait.svg",
) -> Path:
    """Generate 100% crystal-clear animated terminal portrait SVG embedding HD base64 photo.

    Args:
        config_mgr: ConfigManager instance.
        output_filename: Target output file name.

    Returns:
        Path to rendered SVG file.
    """
    root = get_project_root()
    output_path = root / "assets" / "generated" / output_filename
    ensure_dir(output_path.parent)

    theme = config_mgr.theme
    accent = theme.get("accent", "#38bdf8")
    text_main = theme.get("text_main", "#c9d1d9")
    text_muted = theme.get("text_muted", "#8b949e")
    bg = theme.get("background", "#0d1117")

    width = 390
    height = 410

    # Get HD base64 image
    img_b64 = get_profile_photo_base64()

    css_rules = f"""
      @keyframes imgFade {{
        from {{ opacity: 0; transform: scale(0.96); }}
        to {{ opacity: 1; transform: scale(1); }}
      }}
      @keyframes blinkCursor {{
        0%, 49% {{ opacity: 1; }}
        50%, 100% {{ opacity: 0; }}
      }}
      .portrait-img {{
        animation: imgFade 0.6s ease-out forwards;
        transform-origin: center;
      }}
      .portrait-border {{
        stroke: {accent};
        stroke-width: 1.5;
        fill: none;
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
        animation: blinkCursor 0.8s infinite;
      }}
    """

    inner_content = f"""
      <!-- Inner Terminal Photo Frame -->
      <g transform="translate(15, 12)">
        <rect x="0" y="0" width="360" height="340" rx="8" fill="{bg}" stroke="{theme.get('border', '#30363d')}" stroke-width="1"/>
        <image href="{img_b64}" x="0" y="0" width="360" height="340" preserveAspectRatio="xMidYMid slice" class="portrait-img" clip-path="url(#img-clip)"/>
        
        <!-- Corner HUD Bracket Highlights -->
        <path d="M 8,20 L 8,8 L 20,8" stroke="{accent}" stroke-width="2" fill="none"/>
        <path d="M 340,8 L 352,8 L 352,20" stroke="{accent}" stroke-width="2" fill="none"/>
        <path d="M 8,320 L 8,332 L 20,332" stroke="{accent}" stroke-width="2" fill="none"/>
        <path d="M 340,332 L 352,332 L 352,320" stroke="{accent}" stroke-width="2" fill="none"/>

        <!-- Top Right Tech HUD Label -->
        <text x="345" y="24" text-anchor="end" class="portrait-hud">[SYS_ID: ARCH_01]</text>
      </g>

      <!-- Clip Path for rounded corners -->
      <defs>
        <clipPath id="img-clip">
          <rect x="0" y="0" width="360" height="340" rx="8"/>
        </clipPath>
      </defs>

      <!-- Bottom Status Line inside Terminal Window -->
      <text x="16" y="375" class="portrait-footer">[STATUS] 100% OPERATIONAL <tspan class="portrait-cursor">█</tspan></text>
    """

    svg_str = wrap_in_terminal_window(
        title=f"{config_mgr.get_username()} ~ portrait",
        content_svg=inner_content,
        width=width,
        height=height,
        theme=theme,
        custom_css=css_rules,
    )

    write_text(output_path, svg_str)
    logger.info(f"Generated crystal-clear HD terminal portrait SVG -> {output_path}")
    return output_path
