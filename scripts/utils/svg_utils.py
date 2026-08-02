"""SVG document generation and optimization helpers."""

import html
import re
from typing import Dict, List, Optional


def escape_xml(text: str) -> str:
    """Sanitize text for safe inclusion inside SVG XML tags.

    Args:
        text: Raw text string.

    Returns:
        XML escaped string.
    """
    return html.escape(str(text))


def minify_svg(svg_content: str) -> str:
    """Minify SVG XML content by trimming redundant whitespace and comments.

    Args:
        svg_content: Raw SVG markup.

    Returns:
        Optimized and minified SVG string.
    """
    # Remove XML comments (except style keyframes comments if any)
    minified = re.sub(r"<!--(?!.*?@keyframes).*?-->", "", svg_content, flags=re.DOTALL)
    # Collapse consecutive space characters outside quotes
    lines = [line.strip() for line in minified.splitlines() if line.strip()]
    return "\n".join(lines)


def wrap_in_terminal_window(
    title: str,
    content_svg: str,
    width: int,
    height: int,
    theme: Dict[str, str],
    custom_css: str = "",
    padding: int = 16,
) -> str:
    """Wrap SVG content inside a dark Linux terminal window frame.

    Args:
        title: Terminal title bar text (e.g. 'shourya@github:~$ whoami').
        content_svg: Inner SVG elements markup.
        width: Total canvas width in pixels.
        height: Total canvas height in pixels.
        theme: Theme palette dictionary.
        custom_css: Additional CSS animations/rules.
        padding: Internal window padding offset.

    Returns:
        Full stand-alone SVG document string.
    """
    bg = theme.get("background", "#0d1117")
    card_bg = theme.get("card_bg", "#161b22")
    header_bg = theme.get("header_bg", "#21262d")
    border = theme.get("border", "#30363d")
    text_main = theme.get("text_main", "#c9d1d9")
    text_muted = theme.get("text_muted", "#8b949e")
    font_family = theme.get(
        "font_family",
        "'JetBrains Mono', 'Fira Code', monospace",
    )

    header_height = 36
    rx = 8

    svg_doc = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&amp;display=swap');
      .term-window {{
        font-family: {font_family};
        fill: {text_main};
      }}
      .term-title {{
        font-size: 13px;
        font-weight: 600;
        fill: {text_muted};
      }}
      {custom_css}
    </style>
    <filter id="shadow" x="-5%" y="-5%" width="110%" height="110%">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#000000" flood-opacity="0.4"/>
    </filter>
  </defs>

  <g class="term-window">
    <!-- Window Outer Background & Border -->
    <rect x="2" y="2" width="{width - 4}" height="{height - 4}" rx="{rx}" fill="{card_bg}" stroke="{border}" stroke-width="1.5" filter="url(#shadow)"/>

    <!-- Terminal Title Bar -->
    <path d="M 2.75,{2 + rx} Q 2.75,2.75 {2 + rx},2.75 L {width - 2 - rx},2.75 Q {width - 2.75},2.75 {width - 2.75},{2 + rx} L {width - 2.75},{header_height} L 2.75,{header_height} Z" fill="{header_bg}"/>
    <line x1="2" y1="{header_height}" x2="{width - 2}" y2="{header_height}" stroke="{border}" stroke-width="1"/>

    <!-- Window Controls (Red, Yellow, Green Buttons) -->
    <circle cx="16" cy="19" r="5.5" fill="#ff5f56" />
    <circle cx="32" cy="19" r="5.5" fill="#ffbd2e" />
    <circle cx="48" cy="19" r="5.5" fill="#27c93f" />

    <!-- Terminal Window Title -->
    <text x="{width / 2}" y="23" text-anchor="middle" class="term-title">{escape_xml(title)}</text>

    <!-- Inner Window Body Content -->
    <g transform="translate(0, {header_height})">
      {content_svg}
    </g>
  </g>
</svg>"""

    return minify_svg(svg_doc)
