"""GitHub Contribution Heatmap SVG Builder."""

from pathlib import Path
from typing import Any, Dict, List

from utils.file_utils import ensure_dir, get_project_root, read_json, write_text
from utils.logger import get_logger
from utils.svg_utils import escape_xml, wrap_in_terminal_window

logger = get_logger("contribution_builder")


def build_contribution_heatmap_svg(
    config_mgr: "ConfigManager",
    output_filename: str = "contribution-graph.svg",
) -> Path:
    """Generate animated GitHub contribution heatmap SVG matching reference design.

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
    anim = config_mgr.animation.get("heatmap", {})

    username = config_mgr.get_username()
    data_path = root / "cache" / "contributions.json"
    contributions_data = read_json(
        data_path,
        fallback={
            "total_contributions": 61,
            "current_streak": 2,
            "longest_streak": 18,
            "most_active_day": {"date": "N/A", "count": 4},
            "days": [],
        },
    )

    days = contributions_data.get("days", [])
    total_contribs = contributions_data.get("total_contributions", 61)
    current_streak = contributions_data.get("current_streak", 2)
    longest_streak = contributions_data.get("longest_streak", 18)
    most_active = contributions_data.get("most_active_day", {"date": "N/A", "count": 4})

    levels = theme.get(
        "heatmap_levels",
        ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"],
    )

    cell_size = 11
    cell_gap = 3
    margin_x = 35
    margin_y = 62
    width = 800
    height = 230

    cell_delay_ms = anim.get("diagonal_reveal_cell_ms", 10)

    css_rules = [
        f"""
        @keyframes scaleDiagonal {{
          0% {{ opacity: 0; transform: scale(0.2); }}
          100% {{ opacity: 1; transform: scale(1); }}
        }}
        .hm-cell {{
          transform-origin: center;
          opacity: 0;
          animation: scaleDiagonal 0.3s ease-out forwards;
        }}
        .stat-title {{
          font-family: 'JetBrains Mono', 'Fira Code', monospace;
          font-size: 11px;
          fill: {theme.get('text_muted', '#8b949e')};
        }}
        .stat-val {{
          font-family: 'JetBrains Mono', 'Fira Code', monospace;
          font-size: 15px;
          font-weight: bold;
          fill: {theme.get('accent', '#58a6ff')};
        }}
        .hm-legend {{
          font-family: 'JetBrains Mono', 'Fira Code', monospace;
          font-size: 10.5px;
          fill: {theme.get('text_muted', '#8b949e')};
        }}
        .hm-total-text {{
          font-family: 'JetBrains Mono', 'Fira Code', monospace;
          font-size: 12px;
          font-weight: bold;
          fill: {theme.get('text_main', '#c9d1d9')};
        }}
        """
    ]

    # Header Summary Stats
    stats_svg = f"""
      <g transform="translate(35, 18)">
        <g transform="translate(0, 0)">
          <text x="0" y="0" class="stat-title">TOTAL CONTRIBUTIONS</text>
          <text x="0" y="18" class="stat-val">{total_contribs}</text>
        </g>
        <g transform="translate(200, 0)">
          <text x="0" y="0" class="stat-title">CURRENT STREAK</text>
          <text x="0" y="18" class="stat-val" fill="{theme.get('success', '#3fb950')}">{current_streak} days 🔥</text>
        </g>
        <g transform="translate(400, 0)">
          <text x="0" y="0" class="stat-title">LONGEST STREAK</text>
          <text x="0" y="18" class="stat-val" fill="{theme.get('accent_secondary', '#bc8cff')}">{longest_streak} days</text>
        </g>
        <g transform="translate(600, 0)">
          <text x="0" y="0" class="stat-title">MOST ACTIVE DAY</text>
          <text x="0" y="18" class="stat-val" fill="{theme.get('warning', '#d29922')}">{most_active.get('count', 0)} ({most_active.get('date', 'N/A')})</text>
        </g>
      </g>
      <line x1="35" y1="48" x2="765" y2="48" stroke="{theme.get('border', '#30363d')}" stroke-width="1"/>
    """

    # Grid Cell Layout
    grid_cells = []
    max_days = min(len(days), 52 * 7)

    for i in range(max_days):
        col = i // 7
        row = i % 7
        day_item = days[i]
        level = min(day_item.get("level", 0), len(levels) - 1)
        fill_color = levels[level]

        x = margin_x + col * (cell_size + cell_gap)
        y = margin_y + row * (cell_size + cell_gap)

        delay = (col + row) * cell_delay_ms

        grid_cells.append(
            f'<rect class="hm-cell" x="{x}" y="{y}" width="{cell_size}" height="{cell_size}" rx="2.5" ry="2.5" fill="{fill_color}" style="animation-delay: {delay}ms;"/>'
        )

    # Weekday Labels (Mon, Wed, Fri)
    day_labels = []
    days_names = ["Mon", "Wed", "Fri"]
    day_indices = [1, 3, 5]
    for name, idx in zip(days_names, day_indices):
        y_pos = margin_y + idx * (cell_size + cell_gap) + 9
        day_labels.append(
            f'<text x="12" y="{y_pos}" class="hm-legend">{name}</text>'
        )

    # Month Labels
    month_labels = []
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    for idx, m in enumerate(months):
        col_pos = int(idx * (52 / 12))
        x_pos = margin_x + col_pos * (cell_size + cell_gap)
        month_labels.append(
            f'<text x="{x_pos}" y="{margin_y - 8}" class="hm-legend">{m}</text>'
        )

    # Footer line: X contributions in the last year & Legend
    footer_y = margin_y + 7 * (cell_size + cell_gap) + 16
    total_summary_svg = f'<text x="35" y="{footer_y + 8}" class="hm-total-text">{total_contribs} contributions in the last year</text>'

    legend_x = 620
    legend_svg = [
        f'<text x="{legend_x - 30}" y="{footer_y + 8}" class="hm-legend">Less</text>'
    ]
    curr_x = legend_x
    for lvl_color in levels:
        legend_svg.append(
            f'<rect x="{curr_x}" y="{footer_y}" width="{cell_size}" height="{cell_size}" rx="2" fill="{lvl_color}"/>'
        )
        curr_x += cell_size + cell_gap
    legend_svg.append(
        f'<text x="{curr_x + 5}" y="{footer_y + 8}" class="hm-legend">More</text>'
    )

    custom_css = "\n".join(css_rules)

    inner_content = f"""
      {stats_svg}
      <g>
        {"".join(month_labels)}
        {"".join(day_labels)}
        {"".join(grid_cells)}
        {total_summary_svg}
        {"".join(legend_svg)}
      </g>
    """

    svg_str = wrap_in_terminal_window(
        title=f"git log --contributions --author={username}",
        content_svg=inner_content,
        width=width,
        height=height,
        theme=theme,
        custom_css=custom_css,
    )

    write_text(output_path, svg_str)
    logger.info(f"Generated contribution heatmap SVG -> {output_path}")
    return output_path
