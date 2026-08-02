"""Skills Category SVG Builder."""

from pathlib import Path
from typing import Dict, List

from utils.file_utils import ensure_dir, get_project_root, write_text
from utils.logger import get_logger
from utils.svg_utils import escape_xml, wrap_in_terminal_window

logger = get_logger("skills_builder")


def build_skills_svg(
    config_mgr: "ConfigManager",
    output_filename: str = "skills.svg",
) -> Path:
    """Generate terminal-styled skills category matrix SVG.

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

    stacks = prof.get("stacks", {})

    width = 800
    height = 310

    accent = theme.get("accent", "#58a6ff")
    accent_sec = theme.get("accent_secondary", "#bc8cff")
    success = theme.get("success", "#3fb950")
    warning = theme.get("warning", "#d29922")
    text_main = theme.get("text_main", "#c9d1d9")
    text_muted = theme.get("text_muted", "#8b949e")

    categories = [
        ("Languages", stacks.get("languages", ["Python", "TypeScript", "C++", "SQL"]), accent),
        ("Backend Stack", stacks.get("backend", ["FastAPI", "Node.js", "Express", "Django"]), accent_sec),
        ("Frontend Stack", stacks.get("frontend", ["React", "Next.js", "Tailwind", "Redux"]), success),
        ("Database & Cache", stacks.get("database", ["PostgreSQL", "MongoDB", "Redis", "SQLite"]), warning),
        ("Cloud & Infrastructure", stacks.get("cloud", ["AWS", "Docker", "Vercel", "Linux"]), accent),
        ("DevOps & CI/CD", stacks.get("devops", ["Git", "GitHub Actions", "Docker", "Bash"]), accent_sec),
        ("Tools & Utilities", stacks.get("tools", ["VS Code", "Postman", "Figma", "Linux CLI"]), success),
    ]

    css_rules = [
        f"""
        @keyframes popInBox {{
          from {{ opacity: 0; transform: translateY(12px) scale(0.96); }}
          to {{ opacity: 1; transform: translateY(0) scale(1); }}
        }}
        .skill-box {{
          opacity: 0;
          animation: popInBox 0.4s ease-out forwards;
        }}
        .cat-title {{
          font-size: 13px;
          font-weight: 700;
        }}
        .tag-pill {{
          font-size: 11px;
          font-weight: 600;
          fill: {text_main};
        }}
        """
    ]

    for idx in range(len(categories)):
        delay = idx * 120
        css_rules.append(f".sb-{idx} {{ animation-delay: {delay}ms; }}")

    custom_css = "\n".join(css_rules)

    # 2 columns layout
    col_w = 370
    box_h = 60
    gap_x = 20
    gap_y = 12

    boxes_svg = []
    for idx, (title, items, color) in enumerate(categories):
        col = idx % 2
        row = idx // 2

        x = 20 + col * (col_w + gap_x)
        y = 15 + row * (box_h + gap_y)

        pills_svg = []
        px = 12
        for tag in items[:4]:
            tag_w = len(tag) * 7.5 + 16
            pills_svg.append(
                f'<rect x="{px}" y="28" width="{tag_w}" height="22" rx="4" fill="{theme.get("background", "#0d1117")}" stroke="{color}" stroke-opacity="0.6" stroke-width="1"/>'
                f'<text x="{px + 8}" y="43" class="tag-pill">{escape_xml(tag)}</text>'
            )
            px += tag_w + 8

        boxes_svg.append(
            f'<g class="skill-box sb-{idx}" transform="translate({x}, {y})">'
            f'<rect x="0" y="0" width="{col_w}" height="{box_h}" rx="6" fill="{theme.get("header_bg", "#21262d")}" stroke="{theme.get("border", "#30363d")}" stroke-width="1"/>'
            f'<text x="12" y="18" class="cat-title" fill="{color}"># {escape_xml(title)}</text>'
            f'<g>{"".join(pills_svg)}</g>'
            f'</g>'
        )

    inner_content = "\n".join(boxes_svg)

    svg_str = wrap_in_terminal_window(
        title="cat skills.config.json",
        content_svg=inner_content,
        width=width,
        height=height,
        theme=theme,
        custom_css=custom_css,
    )

    write_text(output_path, svg_str)
    logger.info(f"Generated skills SVG -> {output_path}")
    return output_path
