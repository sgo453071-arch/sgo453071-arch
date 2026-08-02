"""LeetCode Stats SVG Builder with Active Streak Display."""

from pathlib import Path
from typing import Any, Dict

from utils.file_utils import ensure_dir, get_project_root, read_json, write_text
from utils.logger import get_logger
from utils.svg_utils import escape_xml, wrap_in_terminal_window

logger = get_logger("leetcode_builder")


def build_leetcode_svg(
    config_mgr: "ConfigManager",
    output_filename: str = "leetcode-stats.svg",
) -> Path:
    """Generate animated terminal-styled LeetCode progress SVG card with active streak.

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

    leetcode_data = read_json(
        root / "cache" / "leetcode.json",
        fallback={
            "username": "Sg19o",
            "total_solved": 319,
            "easy_solved": 145,
            "easy_total": 820,
            "medium_solved": 152,
            "medium_total": 1720,
            "hard_solved": 22,
            "hard_total": 730,
            "acceptance_rate": 65.4,
            "ranking": 245000,
            "streak": 261,
            "total_active_days": 261,
        },
    )

    username = leetcode_data.get("username", "Sg19o")
    total_solved = leetcode_data.get("total_solved", 319)
    ranking = leetcode_data.get("ranking", 0)
    ranking_str = f"#{ranking:,}" if ranking > 0 else "N/A"
    streak = leetcode_data.get("streak", 261)
    streak_str = f"{streak} days 🔥"

    easy_s = leetcode_data.get("easy_solved", 145)
    easy_t = max(1, leetcode_data.get("easy_total", 820))
    easy_pct = min(100, int((easy_s / easy_t) * 100))

    med_s = leetcode_data.get("medium_solved", 152)
    med_t = max(1, leetcode_data.get("medium_total", 1720))
    med_pct = min(100, int((med_s / med_t) * 100))

    hard_s = leetcode_data.get("hard_solved", 22)
    hard_t = max(1, leetcode_data.get("hard_total", 730))
    hard_pct = min(100, int((hard_s / hard_t) * 100))

    width = 800
    height = 230

    css_rules = f"""
      @keyframes barGrow {{
        from {{ width: 0; }}
      }}
      .lc-stat-title {{
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 11px;
        fill: {text_muted};
      }}
      .lc-stat-val {{
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 16px;
        font-weight: bold;
        fill: {accent};
      }}
      .lc-diff-label {{
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 12px;
        font-weight: bold;
      }}
      .lc-diff-count {{
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 11.5px;
        fill: {text_main};
      }}
      .lc-bar-bg {{
        fill: {theme.get('background', '#0d1117')};
        stroke: {theme.get('border', '#30363d')};
        stroke-width: 1;
      }}
      .lc-bar-fill {{
        animation: barGrow 1.2s ease-out forwards;
      }}
    """

    # Top Header Summary with Streak
    stats_svg = f"""
      <g transform="translate(35, 18)">
        <g transform="translate(0, 0)">
          <text x="0" y="0" class="lc-stat-title">TOTAL SOLVED</text>
          <text x="0" y="18" class="lc-stat-val" fill="#FFA116">{total_solved}</text>
        </g>
        <g transform="translate(180, 0)">
          <text x="0" y="0" class="lc-stat-title">CURRENT STREAK</text>
          <text x="0" y="18" class="lc-stat-val" fill="#ff7b72">{streak_str}</text>
        </g>
        <g transform="translate(380, 0)">
          <text x="0" y="0" class="lc-stat-title">GLOBAL RANKING</text>
          <text x="0" y="18" class="lc-stat-val" fill="{accent}">{ranking_str}</text>
        </g>
        <g transform="translate(580, 0)">
          <text x="0" y="0" class="lc-stat-title">ACCEPTANCE</text>
          <text x="0" y="18" class="lc-stat-val" fill="{theme.get('success', '#3fb950')}">{leetcode_data.get('acceptance_rate', 65.4)}%</text>
        </g>
      </g>
      <line x1="35" y1="48" x2="765" y2="48" stroke="{theme.get('border', '#30363d')}" stroke-width="1"/>
    """

    # Difficulty Bars Layout
    bar_max_w = 460
    easy_bar_w = max(6, int((easy_s / (easy_s + med_s + hard_s or 1)) * bar_max_w * 1.6))
    med_bar_w = max(6, int((med_s / (easy_s + med_s + hard_s or 1)) * bar_max_w * 1.6))
    hard_bar_w = max(6, int((hard_s / (easy_s + med_s + hard_s or 1)) * bar_max_w * 1.6))

    bars_svg = f"""
      <g transform="translate(35, 66)">
        <!-- EASY -->
        <g transform="translate(0, 0)">
          <text x="0" y="14" class="lc-diff-label" fill="#00b8a3">Easy</text>
          <rect x="90" y="2" width="{bar_max_w}" height="14" rx="4" class="lc-bar-bg"/>
          <rect x="90" y="2" width="{easy_bar_w}" height="14" rx="4" fill="#00b8a3" class="lc-bar-fill"/>
          <text x="{105 + bar_max_w}" y="14" class="lc-diff-count"><tspan font-weight="bold">{easy_s}</tspan> / {easy_t} ({easy_pct}%)</text>
        </g>

        <!-- MEDIUM -->
        <g transform="translate(0, 32)">
          <text x="0" y="14" class="lc-diff-label" fill="#ffc01e">Medium</text>
          <rect x="90" y="2" width="{bar_max_w}" height="14" rx="4" class="lc-bar-bg"/>
          <rect x="90" y="2" width="{med_bar_w}" height="14" rx="4" fill="#ffc01e" class="lc-bar-fill"/>
          <text x="{105 + bar_max_w}" y="14" class="lc-diff-count"><tspan font-weight="bold">{med_s}</tspan> / {med_t} ({med_pct}%)</text>
        </g>

        <!-- HARD -->
        <g transform="translate(0, 64)">
          <text x="0" y="14" class="lc-diff-label" fill="#ff375f">Hard</text>
          <rect x="90" y="2" width="{bar_max_w}" height="14" rx="4" class="lc-bar-bg"/>
          <rect x="90" y="2" width="{hard_bar_w}" height="14" rx="4" fill="#ff375f" class="lc-bar-fill"/>
          <text x="{105 + bar_max_w}" y="14" class="lc-diff-count"><tspan font-weight="bold">{hard_s}</tspan> / {hard_t} ({hard_pct}%)</text>
        </g>
      </g>
    """

    inner_content = f"""
      {stats_svg}
      {bars_svg}
    """

    svg_str = wrap_in_terminal_window(
        title=f"leetcode --user {username} --stats",
        content_svg=inner_content,
        width=width,
        height=height,
        theme=theme,
        custom_css=css_rules,
    )

    write_text(output_path, svg_str)
    logger.info(f"Generated LeetCode stats SVG -> {output_path}")
    return output_path
