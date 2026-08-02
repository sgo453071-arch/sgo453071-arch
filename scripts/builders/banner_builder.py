"""Terminal Header Banner SVG Builder."""

from pathlib import Path
from typing import Dict

from utils.file_utils import ensure_dir, get_project_root, write_text
from utils.logger import get_logger
from utils.svg_utils import escape_xml, wrap_in_terminal_window

logger = get_logger("banner_builder")


def build_terminal_banner(
    config_mgr: "ConfigManager",
    output_filename: str = "terminal-banner.svg",
) -> Path:
    """Generate animated terminal prompt banner SVG.

    Args:
        config_mgr: ConfigManager instance.
        output_filename: Target output file name.

    Returns:
        Path to rendered SVG artifact file.
    """
    root = get_project_root()
    output_path = root / "assets" / "generated" / output_filename
    ensure_dir(output_path.parent)

    username = config_mgr.get_username()
    theme = config_mgr.theme
    anim = config_mgr.animation.get("typing", {})

    prompt_user = theme.get("prompt_user", "#58a6ff")
    prompt_host = theme.get("prompt_host", "#3fb950")
    prompt_path = theme.get("prompt_path", "#bc8cff")
    text_main = theme.get("text_main", "#c9d1d9")
    accent = theme.get("accent", "#58a6ff")

    width = 800
    height = 140

    command_text = escape_xml("whoami && cat profile.txt")

    custom_css = f"""
      @keyframes typing {{
        0% {{ width: 0; }}
        80% {{ width: 22ch; }}
        100% {{ width: 22ch; }}
      }}
      @keyframes blink {{
        50% {{ opacity: 0; }}
      }}
      .typewriter {{
        font-size: 15px;
        font-weight: 600;
        white-space: nowrap;
        overflow: hidden;
        display: inline-block;
        animation: typing 2.5s steps(22, end) forwards;
      }}
      .cursor {{
        font-size: 16px;
        font-weight: 700;
        fill: {accent};
        animation: blink 0.6s infinite;
      }}
      .p-user {{ fill: {prompt_user}; font-weight: 700; }}
      .p-host {{ fill: {prompt_host}; font-weight: 700; }}
      .p-path {{ fill: {prompt_path}; font-weight: 700; }}
    """

    inner_content = f"""
      <!-- Command Prompt Header -->
      <g transform="translate(20, 30)">
        <text font-size="15">
          <tspan class="p-user">{username}</tspan>
          <tspan fill="{text_main}">@</tspan>
          <tspan class="p-host">github</tspan>
          <tspan fill="{text_main}">:</tspan>
          <tspan class="p-path">~</tspan>
          <tspan fill="{text_main}">$ </tspan>
        </text>
        
        <!-- Typing command -->
        <g transform="translate(185, -13)">
          <foreignObject width="500" height="30">
            <div xmlns="http://www.w3.org/1999/xhtml" style="font-family: inherit; color: {text_main};">
              <span class="typewriter">{command_text}</span>
            </div>
          </foreignObject>
        </g>
        
        <!-- Cursor -->
        <text x="375" y="0" class="cursor">█</text>
      </g>

      <!-- Welcome Banner Subtitle -->
      <g transform="translate(20, 68)">
        <text fill="{theme.get('text_muted', '#8b949e')}" font-size="13">
          Welcome to {username}'s interactive terminal workspace. Type commands or scroll to explore profile.
        </text>
      </g>
    """

    svg_str = wrap_in_terminal_window(
        title=f"bash - {username}@github:~",
        content_svg=inner_content,
        width=width,
        height=height,
        theme=theme,
        custom_css=custom_css,
    )

    write_text(output_path, svg_str)
    logger.info(f"Generated terminal banner SVG -> {output_path}")
    return output_path
