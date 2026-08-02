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
    """Generate Neofetch info card SVG matching reference design layout.

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
    accent = theme.get("accent", "#38bdf8")
    accent_sec = theme.get("accent_secondary", "#bc8cff")
    success = theme.get("success", "#3fb950")
    warning = theme.get("warning", "#d29922")

    width = 390
    height = 410

    stacks = prof.get("stacks", {})
    frontend_str = ", ".join(stacks.get("frontend", ["React", "Next.js", "TypeScript", "Tailwind"])[:4])
    backend_str = ", ".join(stacks.get("backend", ["Node.js", "Python", "FastAPI", "Express"])[:4])
    db_str = ", ".join(stacks.get("database", ["PostgreSQL", "MongoDB", "Redis"])[:3])
    cloud_str = ", ".join(stacks.get("cloud", ["AWS", "Docker", "Vercel"])[:3])

    socials = prof.get("socials", {})

    css_rules = [
        f"""
        @keyframes lineFade {{
          from {{ opacity: 0; }}
          to {{ opacity: 1; }}
        }}
        .nf-row {{
          opacity: 0;
          animation: lineFade 0.3s ease-out forwards;
        }}
        .nf-txt {{
          font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
          font-size: 11px;
        }}
        .nf-user {{
          font-size: 14px;
          font-weight: bold;
          fill: {success};
        }}
        .nf-section {{
          font-size: 12px;
          font-weight: bold;
          fill: {accent};
        }}
        .nf-k {{
          font-weight: bold;
          fill: {text_main};
        }}
        .nf-v {{
          fill: {text_muted};
        }}
        """
    ]

    for idx in range(16):
        css_rules.append(f".nfr-{idx} {{ animation-delay: {idx * 40}ms; }}")

    custom_css = "\n".join(css_rules)

    inner_lines = []

    # Title: sgo453071-arch@github
    inner_lines.append(
        f'<g class="nf-row nfr-0">'
        f'<text x="16" y="24" class="nf-txt nf-user">{escape_xml(username)}@github</text>'
        f'<line x1="16" y1="32" x2="370" y2="32" stroke="{theme.get("border", "#30363d")}" stroke-width="1"/>'
        f'</g>'
    )

    # General Info
    inner_lines.append(
        f'<g class="nf-row nfr-1">'
        f'<text x="16" y="50" class="nf-txt"><tspan class="nf-k">Role</tspan><tspan x="90" fill="{text_muted}">:</tspan><tspan x="102" fill="{text_main}">Software Engineer &amp; Full Stack</tspan></text>'
        f'</g>'
    )
    inner_lines.append(
        f'<g class="nf-row nfr-2">'
        f'<text x="16" y="68" class="nf-txt"><tspan class="nf-k">Focus</tspan><tspan x="90" fill="{text_muted}">:</tspan><tspan x="102" fill="{text_main}">AI Tools &amp; Systems Architecture</tspan></text>'
        f'</g>'
    )
    inner_lines.append(
        f'<g class="nf-row nfr-3">'
        f'<text x="16" y="86" class="nf-txt"><tspan class="nf-k">OS</tspan><tspan x="90" fill="{text_muted}">:</tspan><tspan x="102" fill="{text_main}">Linux / Windows (WSL2)</tspan></text>'
        f'</g>'
    )

    # Tech Stack Section Header
    inner_lines.append(
        f'<g class="nf-row nfr-4">'
        f'<text x="16" y="116" class="nf-txt nf-section">> Tech Stack</text>'
        f'</g>'
    )
    inner_lines.append(
        f'<g class="nf-row nfr-5">'
        f'<text x="16" y="136" class="nf-txt"><tspan class="nf-k">Frontend</tspan><tspan x="90" fill="{text_muted}">:</tspan><tspan x="102" fill="{accent}">{escape_xml(frontend_str)}</tspan></text>'
        f'</g>'
    )
    inner_lines.append(
        f'<g class="nf-row nfr-6">'
        f'<text x="16" y="154" class="nf-txt"><tspan class="nf-k">Backend</tspan><tspan x="90" fill="{text_muted}">:</tspan><tspan x="102" fill="{accent_sec}">{escape_xml(backend_str)}</tspan></text>'
        f'</g>'
    )
    inner_lines.append(
        f'<g class="nf-row nfr-7">'
        f'<text x="16" y="172" class="nf-txt"><tspan class="nf-k">Database</tspan><tspan x="90" fill="{text_muted}">:</tspan><tspan x="102" fill="{success}">{escape_xml(db_str)}</tspan></text>'
        f'</g>'
    )
    inner_lines.append(
        f'<g class="nf-row nfr-8">'
        f'<text x="16" y="190" class="nf-txt"><tspan class="nf-k">Cloud</tspan><tspan x="90" fill="{text_muted}">:</tspan><tspan x="102" fill="{warning}">{escape_xml(cloud_str)}</tspan></text>'
        f'</g>'
    )

    # Highlights & Links Section Header
    inner_lines.append(
        f'<g class="nf-row nfr-9">'
        f'<text x="16" y="222" class="nf-txt nf-section">> Profiles &amp; Highlights</text>'
        f'</g>'
    )
    inner_lines.append(
        f'<g class="nf-row nfr-10">'
        f'<text x="16" y="242" class="nf-txt" fill="{text_main}">• LinkedIn : <tspan fill="{accent}">linkedin.com/in/sg19o</tspan></text>'
        f'</g>'
    )
    inner_lines.append(
        f'<g class="nf-row nfr-11">'
        f'<text x="16" y="260" class="nf-txt" fill="{text_main}">• LeetCode : <tspan fill="{warning}">leetcode.com/u/Sg19o</tspan></text>'
        f'</g>'
    )
    inner_lines.append(
        f'<g class="nf-row nfr-12">'
        f'<text x="16" y="278" class="nf-txt" fill="{text_main}">• GitHub   : <tspan fill="{success}">github.com/{escape_xml(username)}</tspan></text>'
        f'</g>'
    )
    inner_lines.append(
        f'<g class="nf-row nfr-13">'
        f'<text x="16" y="296" class="nf-txt" fill="{text_main}">• Projects : <tspan fill="{accent_sec}">DISHA FOR INDIA, Future AI</tspan></text>'
        f'</g>'
    )

    # Footer color blocks
    palette_y = 330
    colors = [accent, accent_sec, success, warning, "#ff5f56", "#ffbd2e", "#27c93f", "#c9d1d9"]
    blocks_svg = []
    px = 16
    for c in colors:
        blocks_svg.append(f'<rect x="{px}" y="{palette_y}" width="20" height="10" rx="2" fill="{c}"/>')
        px += 24

    inner_lines.append(f'<g class="nf-row nfr-14">{"".join(blocks_svg)}</g>')

    inner_content = "\n".join(inner_lines)

    svg_str = wrap_in_terminal_window(
        title=f"{username} ~ info",
        content_svg=inner_content,
        width=width,
        height=height,
        theme=theme,
        custom_css=custom_css,
    )

    write_text(output_path, svg_str)
    logger.info(f"Generated info card SVG -> {output_path}")
    return output_path
