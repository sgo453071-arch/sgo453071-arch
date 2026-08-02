"""LeetCode 365-Day Submission Calendar Heatmap SVG Builder."""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List

from utils.file_utils import ensure_dir, get_project_root, read_json, write_text
from utils.logger import get_logger
from utils.svg_utils import escape_xml, wrap_in_terminal_window

logger = get_logger("leetcode_builder")


def build_leetcode_svg(
    config_mgr: "ConfigManager",
    output_filename: str = "leetcode-heatmap.svg",
) -> Path:
    """Generate animated 365-day LeetCode submission calendar heatmap SVG card.

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
            "streak": 261,
            "longest_streak": 261,
            "total_active_days": 261,
            "submission_calendar": {},
        },
    )

    username = leetcode_data.get("username", "Sg19o")
    total_solved = leetcode_data.get("total_solved", 319)
    streak = leetcode_data.get("streak", 261)
    longest_streak = leetcode_data.get("longest_streak", max(261, streak))
    active_days = leetcode_data.get("total_active_days", 261)
    sub_map = leetcode_data.get("submission_calendar", {})

    width = 800
    height = 230

    # Build 52 weeks (364 days) calendar grid ending today
    now = datetime.now(timezone.utc)
    today_date = now.date()

    # Find last Sunday to align 52 full columns
    days_since_sunday = (today_date.weekday() + 1) % 7
    end_date = today_date
    start_date = end_date - timedelta(days=(52 * 7 - 1) + days_since_sunday)

    # Convert submission_calendar timestamps to YYYY-MM-DD counts
    daily_counts = {}
    for ts_str, cnt in sub_map.items():
        try:
            ts = int(ts_str)
            dt = datetime.fromtimestamp(ts, timezone.utc).date()
            daily_counts[dt.strftime("%Y-%m-%d")] = int(cnt)
        except Exception:
            pass

    # Heatmap Theme: Signature LeetCode Amber/Orange Palette
    c_l0 = "#161b22"
    c_l1 = "#7c2d12"
    c_l2 = "#c2410c"
    c_l3 = "#f97316"
    c_l4 = "#ffa116"

    css_rules = f"""
      @keyframes heatFade {{
        from {{ opacity: 0; transform: scale(0.6); }}
        to {{ opacity: 1; transform: scale(1); }}
      }}
      .lc-tile {{
        opacity: 0;
        animation: heatFade 0.25s ease-out forwards;
        transform-origin: center;
      }}
      .lc-stat-title {{
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 10px;
        fill: {text_muted};
        letter-spacing: 0.5px;
      }}
      .lc-stat-val {{
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 16px;
        font-weight: bold;
      }}
      .lc-label {{
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 9px;
        fill: {text_muted};
      }}
      .lc-footer-txt {{
        font-family: 'JetBrains Mono', 'Fira Code', monospace;
        font-size: 10.5px;
        font-weight: bold;
        fill: {text_main};
      }}
    """

    # Top Header Summary
    header_svg = f"""
      <g transform="translate(35, 18)">
        <g transform="translate(0, 0)">
          <text x="0" y="0" class="lc-stat-title">TOTAL SOLVED</text>
          <text x="0" y="18" class="lc-stat-val" fill="#FFA116">{total_solved}</text>
        </g>
        <g transform="translate(200, 0)">
          <text x="0" y="0" class="lc-stat-title">CURRENT STREAK</text>
          <text x="0" y="18" class="lc-stat-val" fill="#ff7b72">{streak} days 🔥</text>
        </g>
        <g transform="translate(410, 0)">
          <text x="0" y="0" class="lc-stat-title">LONGEST STREAK</text>
          <text x="0" y="18" class="lc-stat-val" fill="{accent}">{longest_streak} days</text>
        </g>
        <g transform="translate(610, 0)">
          <text x="0" y="0" class="lc-stat-title">ACTIVE DAYS</text>
          <text x="0" y="18" class="lc-stat-val" fill="{theme.get('success', '#3fb950')}">{active_days} days</text>
        </g>
      </g>
      <line x1="35" y1="48" x2="765" y2="48" stroke="{theme.get('border', '#30363d')}" stroke-width="1"/>
    """

    # Render 52-Week Grid
    grid_svg = []
    month_labels = []
    current_month = None

    cell_size = 10
    cell_gap = 3.2
    grid_x_start = 68
    grid_y_start = 74

    curr = start_date
    col = 0
    row = 0

    tile_index = 0
    while curr <= end_date and col < 52:
        date_str = curr.strftime("%Y-%m-%d")
        count = daily_counts.get(date_str, 0)

        # Level determination
        if count == 0:
            color = c_l0
        elif count == 1:
            color = c_l1
        elif count <= 3:
            color = c_l2
        elif count <= 5:
            color = c_l3
        else:
            color = c_l4

        px = grid_x_start + col * (cell_size + cell_gap)
        py = grid_y_start + row * (cell_size + cell_gap)

        delay = min(700, tile_index * 3)
        grid_svg.append(
            f'<rect x="{px:.1f}" y="{py:.1f}" width="{cell_size}" height="{cell_size}" rx="2" fill="{color}" class="lc-tile" style="animation-delay: {delay}ms;"><title>{date_str}: {count} submissions</title></rect>'
        )

        # Month labels at the top of the grid
        if row == 0 and curr.month != current_month:
            current_month = curr.month
            m_name = curr.strftime("%b")
            month_labels.append(
                f'<text x="{px:.1f}" y="{grid_y_start - 6}" class="lc-label">{m_name}</text>'
            )

        row += 1
        if row > 6:
            row = 0
            col += 1

        curr += timedelta(days=1)
        tile_index += 1

    # Day labels on the left (Mon, Wed, Fri)
    day_labels_svg = f"""
      <text x="35" y="{grid_y_start + 18}" class="lc-label">Mon</text>
      <text x="35" y="{grid_y_start + 44}" class="lc-label">Wed</text>
      <text x="35" y="{grid_y_start + 70}" class="lc-label">Fri</text>
    """

    # Footer
    footer_y = 194
    footer_svg = f"""
      <text x="68" y="{footer_y}" class="lc-footer-txt">{total_solved} LeetCode problems solved in the last year</text>
      <g transform="translate(620, {footer_y - 9})">
        <text x="0" y="8" class="lc-label">Less</text>
        <rect x="28" y="0" width="10" height="10" rx="2" fill="{c_l0}"/>
        <rect x="41" y="0" width="10" height="10" rx="2" fill="{c_l1}"/>
        <rect x="54" y="0" width="10" height="10" rx="2" fill="{c_l2}"/>
        <rect x="67" y="0" width="10" height="10" rx="2" fill="{c_l3}"/>
        <rect x="80" y="0" width="10" height="10" rx="2" fill="{c_l4}"/>
        <text x="96" y="8" class="lc-label">More</text>
      </g>
    """

    inner_content = f"""
      {header_svg}
      {"".join(month_labels)}
      {day_labels_svg}
      {"".join(grid_svg)}
      {footer_svg}
    """

    svg_str = wrap_in_terminal_window(
        title=f"git log --leetcode --author={username}",
        content_svg=inner_content,
        width=width,
        height=height,
        theme=theme,
        custom_css=css_rules,
    )

    write_text(output_path, svg_str)
    logger.info(f"Generated LeetCode calendar heatmap SVG -> {output_path}")
    return output_path
