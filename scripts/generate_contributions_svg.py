#!/usr/bin/env python3
"""
scripts/generate_contributions_svg.py
Generates a bespoke, ultra-sleek Monochrome Contribution & Activity Flow SVG.
Directly fetches live contribution data from GitHub with zero third-party proxy downtime.
"""

import math
import os
import re
import urllib.request
import yaml
from datetime import datetime


def load_config(config_path="config.yml"):
    if not os.path.exists(config_path):
        return {}
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def fetch_github_contributions(username="octocat"):
    url = f"https://github.com/users/{username}/contributions"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            html = resp.read().decode("utf-8")
    except Exception as e:
        print(f"[Contributions] Notice: Could not fetch live calendar ({e}). Using fallback.")
        return None

    # Map tooltips: tooltip id/for -> count text
    tooltip_map = {}
    for m in re.finditer(r'<tool-tip[^>]*for="([^"]+)"[^>]*>([^<]+)</tool-tip>', html):
        tooltip_map[m.group(1)] = m.group(2).strip()

    days = []
    for m in re.finditer(r'<td[^>]*data-date="([^"]+)"[^>]*id="([^"]+)"[^>]*data-level="([^"]+)"', html):
        date_str = m.group(1)
        comp_id = m.group(2)
        level = int(m.group(3))
        tip = tooltip_map.get(comp_id, "")
        
        count = 0
        cnt_m = re.search(r'([0-9]+)\s+contribution', tip)
        if cnt_m:
            count = int(cnt_m.group(1))
        
        days.append({"date": date_str, "level": level, "count": count})

    days.sort(key=lambda d: d["date"])
    
    total_match = re.search(r'([0-9,]+)\s+contributions?\s+in\s+the\s+last\s+year', html)
    total_text = total_match.group(1) if total_match else str(sum(d["count"] for d in days))
    
    return {
        "days": days,
        "total_year": total_text
    }


def generate_bezier_path(points):
    """Generate smooth cubic Bezier SVG path through 2D points."""
    if not points:
        return ""
    if len(points) == 1:
        return f"M {points[0][0]},{points[0][1]}"
    
    d = [f"M {points[0][0]:.1f},{points[0][1]:.1f}"]
    for i in range(len(points) - 1):
        p0 = points[max(0, i - 1)]
        p1 = points[i]
        p2 = points[i + 1]
        p3 = points[min(len(points) - 1, i + 2)]
        
        # Tension factor
        t = 0.2
        cp1x = p1[0] + (p2[0] - p0[0]) * t
        cp1y = p1[1] + (p2[1] - p0[1]) * t
        cp2x = p2[0] - (p3[0] - p1[0]) * t
        cp2y = p2[1] - (p3[1] - p1[1]) * t
        
        d.append(f"C {cp1x:.1f},{cp1y:.1f} {cp2x:.1f},{cp2y:.1f} {p2[0]:.1f},{p2[1]:.1f}")
    
    return " ".join(d)


def generate_contributions_svg(config_path="config.yml", output_path="assets/contributions.svg"):
    config = load_config(config_path)
    username = config.get("github_username", "octocat")
    
    contrib_data = fetch_github_contributions(username)
    
    if contrib_data and contrib_data.get("days"):
        all_days = contrib_data["days"]
        total_year = contrib_data["total_year"]
        # Take last 31 days
        recent_days = all_days[-31:]
    else:
        # Fallback simulated realistic curve if offline
        total_year = "SYNC"
        recent_days = [{"date": f"Day {i}", "count": 0} for i in range(31)]

    counts = [d["count"] for d in recent_days]
    total_30d = sum(counts)
    max_val = max(max(counts), 6)  # ensure headroom
    
    width = 890
    height = 240
    
    pad_left = 50
    pad_right = 35
    pad_top = 75
    pad_bottom = 40
    
    plot_w = width - pad_left - pad_right
    plot_h = height - pad_top - pad_bottom
    baseline_y = pad_top + plot_h
    
    # Calculate (x, y) coordinates
    n = len(recent_days)
    points = []
    for i, d in enumerate(recent_days):
        x = pad_left + (i / max(1, n - 1)) * plot_w
        val = d["count"]
        # Normalized height with gentle curve
        y = baseline_y - (val / max_val) * (plot_h * 0.90)
        points.append((x, y))

    # Bezier curve path
    line_path_d = generate_bezier_path(points)
    
    # Area path closed at bottom baseline
    area_path_d = f"{line_path_d} L {points[-1][0]:.1f},{baseline_y} L {points[0][0]:.1f},{baseline_y} Z"
    
    # Horizontal grid lines
    grid_lines_svg = []
    for level_pct in [0.0, 0.33, 0.66, 1.0]:
        gy = baseline_y - level_pct * (plot_h * 0.90)
        val_label = int(round(level_pct * max_val))
        grid_lines_svg.append(
            f'    <line x1="{pad_left}" y1="{gy:.1f}" x2="{width - pad_right}" y2="{gy:.1f}" stroke="#21262d" stroke-width="1" stroke-dasharray="3,3"/>\n'
            f'    <text x="{pad_left - 10}" y="{gy + 4:.1f}" text-anchor="end" fill="#8b949e" font-family="-apple-system, BlinkMacSystemFont, \'Segoe UI\', sans-serif" font-size="10">{val_label}</text>'
        )

    # Date labels along X axis
    x_labels_svg = []
    label_step = max(1, n // 5)
    for i in range(0, n, label_step):
        px, py = points[i]
        d_str = recent_days[i]["date"]
        try:
            dt = datetime.strptime(d_str, "%Y-%m-%d")
            label_text = dt.strftime("%b %d")
        except Exception:
            label_text = d_str
        
        x_labels_svg.append(
            f'    <text x="{px:.1f}" y="{baseline_y + 20}" text-anchor="middle" fill="#8b949e" '
            f'font-family="-apple-system, BlinkMacSystemFont, \'Segoe UI\', sans-serif" font-size="10">{label_text}</text>'
        )

    # Active day marker dots
    dots_svg = []
    for i, (px, py) in enumerate(points):
        cnt = recent_days[i]["count"]
        if cnt > 0:
            r = min(4.5, 2.5 + (cnt / max_val) * 2.0)
            dots_svg.append(
                f'    <circle cx="{px:.1f}" cy="{py:.1f}" r="{r:.1f}" fill="#ff0000" stroke="#0d1117" stroke-width="1.5">\n'
                f'      <title>{cnt} contribution{"s" if cnt != 1 else ""} on {recent_days[i]["date"]}</title>\n'
                f'    </circle>'
            )

    peak_day_val = max(counts)

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="auto" fill="none">
  <defs>
    <style>
      @keyframes drawLine {{
        0% {{ stroke-dashoffset: 2000; opacity: 0; }}
        10% {{ opacity: 1; }}
        100% {{ stroke-dashoffset: 0; opacity: 1; }}
      }}
      @keyframes areaFade {{
        0% {{ opacity: 0; }}
        100% {{ opacity: 1; }}
      }}
      .flow-line {{
        stroke-dasharray: 2000;
        stroke-dashoffset: 0;
        animation: drawLine 1.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
      }}
      .flow-area {{
        animation: areaFade 1.4s ease-in-out forwards;
      }}
    </style>
    <linearGradient id="curveGradient" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#ffffff" stop-opacity="0.18"/>
      <stop offset="60%" stop-color="#ffffff" stop-opacity="0.04"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0.00"/>
    </linearGradient>
  </defs>

  <!-- Card Background -->
  <rect width="{width}" height="{height}" rx="12" fill="#0d1117" stroke="#30363d" stroke-width="1"/>

  <!-- Header -->
  <g transform="translate(24, 34)">
    <rect x="0" y="0" width="28" height="20" rx="4" fill="#161b22" stroke="#30363d" stroke-width="1"/>
    <text x="6" y="14" fill="#ffffff" font-family="monospace" font-size="12" font-weight="bold">~/</text>
    <text x="38" y="15" fill="#ffffff" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif" font-size="14" font-weight="600">Activity &amp; Contribution Flow</text>
    
    <!-- Right live summary metrics -->
    <text x="{width - 48}" y="14" text-anchor="end" fill="#8b949e" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif" font-size="11">
      <tspan fill="#39d353" font-weight="600">{total_year}</tspan> Total Year  •  <tspan fill="#39d353" font-weight="600">{total_30d}</tspan> in 30D  •  Peak: <tspan fill="#39d353" font-weight="600">{peak_day_val}/day</tspan>
    </text>
    <line x1="0" y1="26" x2="{width - 48}" y2="26" stroke="#21262d" stroke-width="1"/>
  </g>

  <!-- Background Grids & Labels -->
  <g>
{chr(10).join(grid_lines_svg)}
{chr(10).join(x_labels_svg)}
  </g>

  <!-- Area Fill -->
  <path class="flow-area" d="{area_path_d}" fill="url(#curveGradient)"/>

  <!-- Spline Curve Line -->
  <path class="flow-line" d="{line_path_d}" fill="none" stroke="#39d353" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>

  <!-- Data Point Circles -->
  <g>
{chr(10).join(dots_svg)}
  </g>
</svg>
'''
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"[Contributions Flow] Saved live monochrome SVG to '{output_path}'")


if __name__ == "__main__":
    generate_contributions_svg()
