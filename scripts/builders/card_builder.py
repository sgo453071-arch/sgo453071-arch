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
    """Generate Linux Neofetch style system info card SVG with staggered line fade-in.

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
    anim = config_mgr.animation.get("fade", {})

    username = config_mgr.get_username()
    name = config_mgr.get_name()

    text_main = theme.get("text_main", "#c9d1d9")
    text_muted = theme.get("text_muted", "#8b949e")
    accent = theme.get("accent", "#58a6ff")
    accent_sec = theme.get("accent_secondary", "#bc8cff")
    success = theme.get("success", "#3fb950")
    warning = theme.get("warning", "#d29922")

    width = 460
    height = 420

    stacks = prof.get("stacks", {})
    backend_str = ", ".join(stacks.get("backend", ["FastAPI", "Node.js"])[:4])
    frontend_str = ", ".join(stacks.get("frontend", ["React", "Next.js"])[:4])
    db_str = ", ".join(stacks.get("database", ["PostgreSQL", "MongoDB"])[:3])
    cloud_str = ", ".join(stacks.get("cloud", ["AWS", "Docker"])[:3])
    tools_str = ", ".join(stacks.get("tools", ["Git", "VS Code"])[:3])

    socials = prof.get("socials", {})

    # Neofetch metadata rows
    items = [
        ("User", f"{name} ({username})", accent),
        ("Role", prof.get("roles", ["Software Engineer"])[0], text_main),
        ("OS", prof.get("os", "Linux / Windows"), accent_sec),
        ("Editor", prof.get("editor", "VS Code"), success),
        ("Learning", prof.get("learning", "Distributed Systems"), warning),
        ("Focus", prof.get("current_focus", "AI Applications"), text_main),
        ("Backend", backend_str, accent),
        ("Frontend", frontend_str, accent_sec),
        ("Database", db_str, success),
        ("Cloud", cloud_str, warning),
        ("Tools", tools_str, text_main),
        ("LeetCode", socials.get("leetcode", "shourya"), accent),
        ("GitHub", f"github.com/{username}", accent_sec),
        ("Portfolio", socials.get("portfolio", "shourya.dev"), success),
    ]

    line_delay_ms = anim.get("info_card_line_delay_ms", 100)
    line_duration_ms = anim.get("info_card_duration_ms", 500)

    css_rules = [
        f"""
        @keyframes fadeInLine {{
          from {{ opacity: 0; transform: translateX(-10px); }}
          to {{ opacity: 1; transform: translateX(0); }}
        }}
        .nf-line {{
          opacity: 0;
          animation: fadeInLine {line_duration_ms}ms ease-out forwards;
        }}
        .nf-key {{
          font-weight: 700;
          font-size: 12px;
          fill: {accent};
        }}
        .nf-sep {{
          fill: {text_muted};
        }}
        .nf-val {{
          font-size: 12px;
        }}
        .nf-logo {{
          font-size: 11px;
          font-family: monospace;
          fill: {success};
          font-weight: 700;
        }}
        """
    ]

    for idx in range(len(items) + 4):
        delay = idx * line_delay_ms
        css_rules.append(f".nfl-{idx} {{ animation-delay: {delay}ms; }}")

    custom_css = "\n".join(css_rules)

    # Linux OS Logo ASCII emblem for neofetch side column
    logo_lines = [
        "      /\\     ",
        "     /  \\    ",
        "    / /\\ \\   ",
        "   / /  \\ \\  ",
        "  / /    \\ \\ ",
        " / /______\\ \\",
        "/____________\\",
    ]

    inner_lines = []

    # Title header: shourya@github
    inner_lines.append(
        f'<g class="nf-line nfl-0" transform="translate(20, 24)">'
        f'<text font-size="14" font-weight="700" fill="{accent}">{escape_xml(username)}</text>'
        f'<text x="120" font-size="14" font-weight="700" fill="{text_muted}">@</text>'
        f'<text x="135" font-size="14" font-weight="700" fill="{success}">github</text>'
        f'</g>'
    )

    # Separator line: --------------
    inner_lines.append(
        f'<g class="nf-line nfl-1" transform="translate(20, 36)">'
        f'<line x1="0" y1="0" x2="420" y2="0" stroke="{theme.get("border", "#30363d")}" stroke-width="1.5"/>'
        f'</g>'
    )

    # Logo + Details Grid
    y_offset = 60
    for idx, (key, val, color) in enumerate(items):
        line_idx = idx + 2
        inner_lines.append(
            f'<g class="nf-line nfl-{line_idx}" transform="translate(20, {y_offset})">'
            f'<text x="0" y="0" class="nf-key">{escape_xml(key)}</text>'
            f'<text x="90" y="0" class="nf-sep">:</text>'
            f'<text x="105" y="0" class="nf-val" fill="{color}">{escape_xml(val)}</text>'
            f'</g>'
        )
        y_offset += 23

    # Color palette bar (Standard neofetch footer color blocks)
    palette_y = y_offset + 10
    colors = [accent, accent_sec, success, warning, "#ff5f56", "#ffbd2e", "#27c93f", "#c9d1d9"]
    blocks_svg = []
    x_pos = 20
    for c in colors:
        blocks_svg.append(f'<rect x="{x_pos}" y="{palette_y}" width="24" height="12" rx="3" fill="{c}"/>')
        x_pos += 28

    palette_line_idx = len(items) + 3
    inner_lines.append(f'<g class="nf-line nfl-{palette_line_idx}">{"".join(blocks_svg)}</g>')

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
