"""Neofetch Info Card SVG Builder."""

from pathlib import Path
from typing import Dict, List

from utils.file_utils import ensure_dir, get_project_root, write_text
from utils.logger import get_logger
from utils.svg_utils import escape_xml, wrap_in_terminal_window

logger = get_logger("card_builder")


def build_info_card_svg(
    config_mgr: "ConfigManager",
    output_filename: str = "info-card.svg",
) -> Path:
    """Generate Linux Neofetch style system info card SVG with reliable native text rendering.

    Args:
        config_mgr: ConfigManager instance.
        output_filename: Target output file name.

    Returns:
        Path to rendered SVG file.
    """
    root = get_project_root()
    output_path = root / "assets" / "generated" / output_filename
    ensure_dir(output_path.parent)

    prof = config_mgr.profile
    theme = config_mgr.theme

    username = config_mgr.get_username()
    name = config_mgr.get_name()

    text_main = theme.get("text_main", "#c9d1d9")
    text_muted = theme.get("text_muted", "#8b949e")
    accent = theme.get("accent", "#58a6ff")
    accent_sec = theme.get("accent_secondary", "#bc8cff")
    success = theme.get("success", "#3fb950")
    warning = theme.get("warning", "#d29922")

    width = 410
    height = 420

    stacks = prof.get("stacks", {})
    backend_str = ", ".join(stacks.get("backend", ["FastAPI", "Node.js"])[:3])
    frontend_str = ", ".join(stacks.get("frontend", ["React", "Next.js"])[:3])
    db_str = ", ".join(stacks.get("database", ["PostgreSQL", "MongoDB"])[:2])
    cloud_str = ", ".join(stacks.get("cloud", ["AWS", "Docker"])[:2])
    tools_str = ", ".join(stacks.get("tools", ["Git", "VS Code"])[:2])

    socials = prof.get("socials", {})

    items = [
        ("OS", prof.get("os", "Linux / Windows"), accent_sec),
        ("Host", f"github.com/{username}", accent),
        ("Role", prof.get("roles", ["Software Engineer"])[0], text_main),
        ("Focus", prof.get("current_focus", "AI Applications")[:32], warning),
        ("Learning", prof.get("learning", "Distributed Systems")[:32], success),
        ("Editor", prof.get("editor", "VS Code"), accent_sec),
        ("Backend", backend_str, accent),
        ("Frontend", frontend_str, accent_sec),
        ("Database", db_str, success),
        ("Cloud", cloud_str, warning),
        ("Tools", tools_str, text_main),
        ("LeetCode", "leetcode.com/u/Sg19o", warning),
        ("LinkedIn", "linkedin.com/in/sg19o", accent),
    ]

    css_rules = [
        f"""
        @keyframes simpleFade {{
          from {{ opacity: 0; }}
          to {{ opacity: 1; }}
        }}
        .nf-row {{
          opacity: 0;
          animation: simpleFade 0.4s ease-out forwards;
        }}
        .nf-text {{
          font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
          font-size: 11.5px;
        }}
        .nf-key {{
          font-weight: bold;
          fill: {accent};
        }}
        .nf-sep {{
          fill: {text_muted};
        }}
        """
    ]

    for idx in range(len(items) + 4):
        delay = idx * 60
        css_rules.append(f".nfr-{idx} {{ animation-delay: {delay}ms; }}")

    custom_css = "\n".join(css_rules)

    inner_lines = []

    # Title header: sgo453071-arch@github
    inner_lines.append(
        f'<g class="nf-row nfr-0">'
        f'<text x="20" y="24" class="nf-text" font-size="13" font-weight="bold">'
        f'<tspan fill="{accent}">{escape_xml(username)}</tspan>'
        f'<tspan fill="{text_muted}">@</tspan>'
        f'<tspan fill="{success}">github</tspan>'
        f'</text>'
        f'</g>'
    )

    # Separator line
    inner_lines.append(
        f'<g class="nf-row nfr-1">'
        f'<line x1="20" y1="34" x2="390" y2="34" stroke="{theme.get("border", "#30363d")}" stroke-width="1"/>'
        f'</g>'
    )

    # Details Grid
    y_pos = 52
    for idx, (key, val, color) in enumerate(items):
        line_idx = idx + 2
        inner_lines.append(
            f'<g class="nf-row nfr-{line_idx}">'
            f'<text x="20" y="{y_pos}" class="nf-text">'
            f'<tspan class="nf-key">{escape_xml(key)}</tspan>'
            f'<tspan class="nf-sep" x="90">:</tspan>'
            f'<tspan fill="{color}" x="105">{escape_xml(val)}</tspan>'
            f'</text>'
            f'</g>'
        )
        y_pos += 21

    # Color palette bar (Standard neofetch footer color blocks)
    palette_y = y_pos + 6
    colors = [accent, accent_sec, success, warning, "#ff5f56", "#ffbd2e", "#27c93f", "#c9d1d9"]
    blocks_svg = []
    px = 20
    for c in colors:
        blocks_svg.append(f'<rect x="{px}" y="{palette_y}" width="22" height="10" rx="2" fill="{c}"/>')
        px += 26

    palette_line_idx = len(items) + 3
    inner_lines.append(f'<g class="nf-row nfr-{palette_line_idx}">{"".join(blocks_svg)}</g>')

    inner_content = "\n".join(inner_lines)

    svg_str = wrap_in_terminal_window(
        title=f"neofetch --user {username}",
        content_svg=inner_content,
        width=width,
        height=height,
        theme=theme,
        custom_css=custom_css,
    )

    write_text(output_path, svg_str)
    logger.info(f"Generated info card SVG -> {output_path}")
    return output_path
