#!/usr/bin/env python3
"""
scripts/generate_skills_svg.py
Generates an animated, ultra-sleek Monochrome Skill Radar & Capability HUD SVG.
Includes radar polygon expansion, rotating radar beam, vertex pulse, and animated progress bars.
"""

import math
import os
import html
import yaml

def load_config(config_path="config.yml"):
    if not os.path.exists(config_path):
        return {}
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def generate_skills_svg(config_path="config.yml", output_path="assets/skills.svg"):
    config = load_config(config_path)
    
    raw_skills = config.get("skills", [
        {"name": "Kubernetes", "level": 90, "category": "Cloud-Native"},
        {"name": "Docker", "level": 88, "category": "Containers"},
        {"name": "Linux / Bash", "level": 86, "category": "Systems"},
        {"name": "Jenkins / GitHub Actions", "level": 84, "category": "CI/CD"},
        {"name": "AWS", "level": 82, "category": "Cloud"},
        {"name": "Azure", "level": 80, "category": "Cloud"},
        {"name": "Prometheus / Grafana", "level": 78, "category": "Observability"},
        {"name": "Terraform / Ansible", "level": 76, "category": "Automation"}
    ])

    skills_data = []
    for s in raw_skills:
        skills_data.append({
            "name": html.escape(str(s.get("name", ""))),
            "level": int(s.get("level", 80)),
            "category": html.escape(str(s.get("category", "General")))
        })

    width = 940
    height = 370
    
    rcx = 245
    rcy = 215
    max_r = 95
    
    num_skills = len(skills_data)
    angle_step = (2 * math.pi) / max(1, num_skills)
    
    # Concentric rings
    rings_svg = []
    for level_pct in [0.25, 0.50, 0.75, 1.0]:
        r = max_r * level_pct
        points = []
        for i in range(num_skills):
            angle = i * angle_step - math.pi / 2
            px = rcx + r * math.cos(angle)
            py = rcy + r * math.sin(angle)
            points.append(f"{px:.1f},{py:.1f}")
        pts_str = " ".join(points)
        stroke_color = "#30363d" if level_pct == 1.0 else "#21262d"
        stroke_dash = 'stroke-dasharray="3,3"' if level_pct < 1.0 else ""
        rings_svg.append(f'    <polygon points="{pts_str}" fill="none" stroke="{stroke_color}" stroke-width="1" {stroke_dash}/>')

    # Spoke axes, data points, labels
    axes_svg = []
    data_points = []
    labels_svg = []
    vertex_dots = []
    
    for i, item in enumerate(skills_data):
        angle = i * angle_step - math.pi / 2
        
        ox = rcx + max_r * math.cos(angle)
        oy = rcy + max_r * math.sin(angle)
        axes_svg.append(f'    <line x1="{rcx}" y1="{rcy}" x2="{ox:.1f}" y2="{oy:.1f}" stroke="#21262d" stroke-width="1"/>')
        
        pct = max(0.1, min(1.0, item.get("level", 80) / 100.0))
        dx = rcx + (max_r * pct) * math.cos(angle)
        dy = rcy + (max_r * pct) * math.sin(angle)
        data_points.append(f"{dx:.1f},{dy:.1f}")
        
        vertex_delay = 0.3 + i * 0.08
        vertex_dots.append(
            f'    <circle class="vertex-dot" cx="{dx:.1f}" cy="{dy:.1f}" r="3.5" '
            f'fill="#ffffff" stroke="#0d1117" stroke-width="1.5" style="animation-delay: {vertex_delay:.2f}s;"/>'
        )
        
        lx = rcx + (max_r + 18) * math.cos(angle)
        ly = rcy + (max_r + 16) * math.sin(angle)
        
        anchor = "middle"
        if math.cos(angle) > 0.25:
            anchor = "start"
        elif math.cos(angle) < -0.25:
            anchor = "end"
            
        labels_svg.append(
            f'    <text x="{lx:.1f}" y="{ly + 4:.1f}" text-anchor="{anchor}" '
            f'fill="#c9d1d9" font-family="-apple-system, BlinkMacSystemFont, \'Segoe UI\', Helvetica, Arial, sans-serif" '
            f'font-size="11" font-weight="500">{item["name"]}</text>'
        )

    data_pts_str = " ".join(data_points)
    radar_polygon = (
        f'    <!-- Radar Data Polygon -->\n'
        f'    <polygon class="radar-poly" points="{data_pts_str}" fill="rgba(255, 255, 255, 0.09)" stroke="#ffffff" stroke-width="1.8"/>\n'
    )

    # Right: Proficiency Progress HUD
    bars_svg = []
    hud_start_x = 480
    hud_start_y = 95
    bar_width = 415
    
    top_skills = sorted(skills_data, key=lambda s: s.get("level", 0), reverse=True)[:6]

    # Brand colors for the six displayed technologies.
    brand_colors = {
        "Kubernetes": "#326CE5",
        "Docker": "#2496ED",
        "Linux / Bash": "#FCC624",
        "Jenkins / GitHub Actions": "#D24939",
        "AWS": "#FF9900",
        "Azure": "#0078D4",
    }
    
    for idx, s in enumerate(top_skills):
        y_offset = hud_start_y + idx * 40
        lvl = s.get("level", 85)
        cat = s.get("category", "General")
        fill_w = (bar_width * (lvl / 100.0))
        delay = 0.2 + idx * 0.12
        bar_color = brand_colors.get(s["name"], "#ffffff")
        
        bars_svg.append(f'''
    <!-- Skill {idx+1}: {s["name"]} -->
    <g transform="translate({hud_start_x}, {y_offset})">
      <text x="0" y="0" fill="#e6edf3" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif" font-size="12" font-weight="600">{s["name"]}</text>
      <text x="{bar_width}" y="0" text-anchor="end" fill="#8b949e" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif" font-size="11">{cat} • <tspan fill="#ffffff" font-weight="600">{lvl}%</tspan></text>
      <!-- Track -->
      <rect x="0" y="8" width="{bar_width}" height="6" rx="3" fill="#161b22" stroke="#21262d" stroke-width="1"/>
      <!-- Fill with CSS grow animation -->
      <rect class="hud-bar bar-{idx}" x="0" y="8" width="{fill_w:.1f}" height="6" rx="3" fill="{bar_color}" style="animation-delay: {delay:.2f}s;"/>
    </g>''')

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="auto" fill="none">
  <defs>
    <style>
      @keyframes radarExpand {{
        0% {{ transform: scale(0.1); opacity: 0; }}
        70% {{ transform: scale(1.04); opacity: 0.95; }}
        100% {{ transform: scale(1); opacity: 1; }}
      }}
      @keyframes radarSweep {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
      }}
      @keyframes vertexPop {{
        0% {{ transform: scale(0); opacity: 0; }}
        100% {{ transform: scale(1); opacity: 1; }}
      }}
      @keyframes barGrow {{
        0% {{ transform: scaleX(0); }}
        100% {{ transform: scaleX(1); }}
      }}
      .radar-poly {{
        transform-origin: {rcx}px {rcy}px;
        animation: radarExpand 1.0s cubic-bezier(0.16, 1, 0.3, 1) forwards;
      }}
      .radar-sweep-beam {{
        transform-origin: {rcx}px {rcy}px;
        animation: radarSweep 8s linear infinite;
      }}
      .vertex-dot {{
        transform-box: fill-box;
        transform-origin: center;
        opacity: 0;
        animation: vertexPop 0.4s ease-out forwards;
      }}
      .hud-bar {{
        transform-origin: left center;
        animation: barGrow 0.9s cubic-bezier(0.16, 1, 0.3, 1) both;
      }}
    </style>
    <linearGradient id="radarSweepGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#39ff88" stop-opacity="0.42"/>
      <stop offset="100%" stop-color="#39ff88" stop-opacity="0.0"/>
    </linearGradient>
  </defs>

  <!-- Card Background -->
  <rect width="{width}" height="{height}" rx="12" fill="#0d1117" stroke="#30363d" stroke-width="1"/>

  <!-- Card Header -->
  <g transform="translate(24, 34)">
    <rect x="0" y="0" width="28" height="20" rx="4" fill="#161b22" stroke="#30363d" stroke-width="1"/>
    <text x="6" y="14" fill="#ffffff" font-family="monospace" font-size="12" font-weight="bold">~/</text>
    <text x="38" y="15" fill="#ffffff" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif" font-size="14" font-weight="600">Technical Capability &amp; Skill Radar</text>
    <text x="{width - 48}" y="14" text-anchor="end" fill="#8b949e" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif" font-size="11">Specialist Breakdown</text>
    <line x1="0" y1="28" x2="{width - 48}" y2="28" stroke="#21262d" stroke-width="1"/>
  </g>

  <!-- Left: Skill Radar -->
  <g>
    <!-- Background Rotating Sweep Beam -->
    <path class="radar-sweep-beam" d="M {rcx} {rcy} L {rcx} {rcy - max_r} A {max_r} {max_r} 0 0 1 {rcx + max_r * 0.707} {rcy - max_r * 0.707} Z" fill="url(#radarSweepGrad)"/>
    <path class="radar-sweep-beam" d="M {rcx} {rcy} L {rcx} {rcy - max_r}" fill="none" stroke="#39ff88" stroke-width="1.6" stroke-linecap="round" opacity="0.7"/>
{chr(10).join(rings_svg)}
{chr(10).join(axes_svg)}
{radar_polygon}
{chr(10).join(vertex_dots)}
{chr(10).join(labels_svg)}
  </g>

  <!-- Center Divider -->
  <line x1="455" y1="80" x2="455" y2="340" stroke="#21262d" stroke-width="1" stroke-dasharray="4,4"/>

  <!-- Right: Proficiency Progress HUD -->
  <g>
{chr(10).join(bars_svg)}
  </g>
</svg>
'''
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"[Skills HUD] Saved animated XML SVG with perfected clearance to {output_path}")


if __name__ == "__main__":
    generate_skills_svg()
