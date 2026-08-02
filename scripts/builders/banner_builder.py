"""Terminal Header Banner SVG Builder."""

from pathlib import Path

from utils.file_utils import ensure_dir, get_project_root, write_text
from utils.logger import get_logger
from utils.svg_utils import escape_xml, wrap_in_terminal_window

logger = get_logger("banner_builder")


def build_terminal_banner(
    config_mgr: "ConfigManager",
    output_filename: str = "terminal-banner.svg",
) -> Path:
    """Generate animated terminal prompt banner SVG using robust native SVG text.

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

    prompt_user = theme.get("prompt_user", "#58a6ff")
    prompt_host = theme.get("prompt_host", "#3fb950")
    prompt_path = theme.get("prompt_path", "#bc8cff")
    text_main = theme.get("text_main", "#c9d1d9")
    text_muted = theme.get("text_muted", "#8b949e")
    accent = theme.get("accent", "#58a6ff")

    width = 800
    height = 110

    custom_css = f"""
      @keyframes blink {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0; }}
      }}
      .banner-text {{
        font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
        font-size: 14px;
      }}
      .cursor {{
        fill: {accent};
        animation: blink 0.8s infinite;
      }}
      .p-user {{ fill: {prompt_user}; font-weight: bold; }}
      .p-host {{ fill: {prompt_host}; font-weight: bold; }}
      .p-path {{ fill: {prompt_path}; font-weight: bold; }}
      .p-cmd  {{ fill: {text_main}; }}
    """

    inner_content = f"""
      <!-- Native SVG Command Prompt Text Line -->
      <text x="20" y="32" class="banner-text">
        <tspan class="p-user">{escape_xml(username)}</tspan>
        <tspan fill="{text_main}">@</tspan>
        <tspan class="p-host">github</tspan>
        <tspan fill="{text_main}">:</tspan>
        <tspan class="p-path">~</tspan>
        <tspan fill="{text_main}">$ </tspan>
        <tspan class="p-cmd">whoami &amp;&amp; cat profile.txt</tspan>
        <tspan class="cursor"> █</tspan>
      </text>

      <!-- Subtitle -->
      <text x="20" y="58" class="banner-text" font-size="12" fill="{text_muted}">
        Welcome to {escape_xml(username)}'s interactive terminal workspace. Scroll to explore profile.
      </text>
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
