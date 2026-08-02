"""Project Showcase Card SVG Builder."""

from pathlib import Path
from typing import Any, Dict, List

from utils.file_utils import ensure_dir, get_project_root, write_text
from utils.logger import get_logger
from utils.svg_utils import escape_xml, wrap_in_terminal_window

logger = get_logger("project_builder")


def build_project_card_svg(
    config_mgr: "ConfigManager",
    project_item: Dict[str, Any],
) -> Path:
    """Generate terminal-styled showcase SVG card for a single project.

    Args:
        config_mgr: ConfigManager instance.
        project_item: Project configuration dictionary.

    Returns:
        Path to rendered SVG project card file.
    """
    root = get_project_root()
    filename = project_item.get("output_file", f"project-{project_item.get('id', 'item')}.svg")
    output_path = root / "assets" / "generated" / filename
    ensure_dir(output_path.parent)

    theme = config_mgr.theme
    accent = theme.get("accent", "#58a6ff")
    accent_sec = theme.get("accent_secondary", "#bc8cff")
    success = theme.get("success", "#3fb950")
    warning = theme.get("warning", "#d29922")
    text_main = theme.get("text_main", "#c9d1d9")
    text_muted = theme.get("text_muted", "#8b949e")

    width = 380
    height = 250

    title = project_item.get("title", "Project Title")
    subtitle = project_item.get("subtitle", "")
    desc = project_item.get("description", "")
    status = project_item.get("status", "ACTIVE")
    tech_stack = project_item.get("tech_stack", [])
    highlights = project_item.get("highlights", [])

    status_color = success if status == "ACTIVE" else (warning if "DEVELOPMENT" in status else accent_sec)

    css_rules = f"""
      .p-title {{
        font-size: 15px;
        font-weight: 700;
        fill: {accent};
      }}
      .p-sub {{
        font-size: 11px;
        fill: {text_muted};
      }}
      .p-desc {{
        font-size: 11.5px;
        fill: {text_main};
      }}
      .p-status {{
        font-size: 10px;
        font-weight: 700;
        fill: {status_color};
      }}
      .p-bullet {{
        font-size: 10.5px;
        fill: {text_muted};
      }}
      .p-tag {{
        font-size: 10px;
        font-weight: 600;
        fill: {accent_sec};
      }}
    """

    # Wrap description lines
    desc_words = desc.split()
    desc_lines = []
    curr_line = ""
    for w in desc_words:
        if len(curr_line) + len(w) + 1 > 52:
            desc_lines.append(curr_line)
            curr_line = w
        else:
            curr_line = f"{curr_line} {w}".strip()
    if curr_line:
        desc_lines.append(curr_line)

    desc_svg = []
    dy = 50
    for l in desc_lines[:2]:
        desc_svg.append(f'<text x="20" y="{dy}" class="p-desc">{escape_xml(l)}</text>')
        dy += 16

    # Highlights bullets
    bullets_svg = []
    by = dy + 10
    for h in highlights[:2]:
        bullets_svg.append(
            f'<text x="20" y="{by}" class="p-bullet">➜ {escape_xml(h)}</text>'
        )
        by += 16

    # Tech Stack Tags
    tags_svg = []
    tx = 20
    ty = height - 70
    for tag in tech_stack[:4]:
        tag_w = len(tag) * 6.5 + 12
        tags_svg.append(
            f'<rect x="{tx}" y="{ty}" width="{tag_w}" height="18" rx="3" fill="{theme.get("background", "#0d1117")}" stroke="{theme.get("border", "#30363d")}" stroke-width="1"/>'
            f'<text x="{tx + 6}" y="{ty + 13}" class="p-tag">{escape_xml(tag)}</text>'
        )
        tx += tag_w + 6

    inner_content = f"""
      <!-- Title & Status Badge -->
      <g transform="translate(20, 24)">
        <text class="p-title">{escape_xml(title)}</text>
        <rect x="270" y="-12" width="70" height="18" rx="4" fill="{theme.get('background', '#0d1117')}" stroke="{status_color}" stroke-width="1"/>
        <text x="305" y="0" text-anchor="middle" class="p-status">{escape_xml(status)}</text>
      </g>
      <text x="20" y="38" class="p-sub">{escape_xml(subtitle)}</text>

      <!-- Description -->
      <g>
        {"".join(desc_svg)}
      </g>

      <!-- Highlights -->
      <g>
        {"".join(bullets_svg)}
      </g>

      <!-- Tech Stack Tags -->
      <g>
        {"".join(tags_svg)}
      </g>
    """

    svg_str = wrap_in_terminal_window(
        title=f"git show projects/{project_item.get('id', 'card')}",
        content_svg=inner_content,
        width=width,
        height=height,
        theme=theme,
        custom_css=css_rules,
    )

    write_text(output_path, svg_str)
    logger.info(f"Generated project card SVG -> {output_path}")
    return output_path


def build_all_project_cards(config_mgr: "ConfigManager") -> List[Path]:
    """Generate SVG cards for all projects specified in config/projects.json.

    Args:
        config_mgr: ConfigManager instance.

    Returns:
        List of paths to generated SVG card files.
    """
    paths = []
    for proj in config_mgr.projects:
        path = build_project_card_svg(config_mgr, proj)
        paths.append(path)
    return paths
