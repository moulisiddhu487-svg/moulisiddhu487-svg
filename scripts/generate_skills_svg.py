#!/usr/bin/env python3
"""
scripts/generate_skills_svg.py
Generates an animated, ultra-sleek Monochrome Skill Radar & Capability HUD SVG.
Includes radar polygon expansion, rotating radar beam, vertex pulse, and animated progress bars.
"""

import math
import random
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

    # Metal radar bezel (real-radar look): drop shadow, brushed-steel ring
    # with outer rim and inner bevel, dark screen face, seam groove, top
    # sheen, and cross-slotted bolt rivets like real Phillips screws.
    bezel_svg = []
    bezel_svg.append(f'    <circle cx="{rcx}" cy="{rcy + 3}" r="109" fill="#000000" opacity="0.35"/>')
    bezel_svg.append(f'    <circle cx="{rcx}" cy="{rcy}" r="106.8" fill="none" stroke="#000000" stroke-width="1.2" opacity="0.55"/>')
    bezel_svg.append(f'    <circle cx="{rcx}" cy="{rcy}" r="102" fill="none" stroke="url(#metalRingGrad)" stroke-width="9"/>')
    bezel_svg.append(f'    <circle cx="{rcx}" cy="{rcy}" r="97.8" fill="none" stroke="#ffffff" stroke-width="1" opacity="0.14"/>')
    bezel_svg.append(f'    <circle cx="{rcx}" cy="{rcy}" r="97" fill="#0a0f16"/>')
    bezel_svg.append(f'    <circle cx="{rcx}" cy="{rcy}" r="97" fill="none" stroke="#000000" stroke-width="1" opacity="0.6"/>')
    # Top sheen arc across the bezel (10 o'clock -> 2 o'clock over the top)
    sheen_start = (rcx + 102 * math.cos(math.radians(210)), rcy + 102 * math.sin(math.radians(210)))
    sheen_end = (rcx + 102 * math.cos(math.radians(330)), rcy + 102 * math.sin(math.radians(330)))
    bezel_svg.append(f'    <path d="M {sheen_start[0]:.1f} {sheen_start[1]:.1f} A 102 102 0 0 1 {sheen_end[0]:.1f} {sheen_end[1]:.1f}" fill="none" stroke="#ffffff" stroke-width="2.5" stroke-linecap="round" opacity="0.28"/>')
    # Cross-slotted dome bolts around the bezel, every 45 degrees
    for k in range(8):
        ang = math.radians(k * 45)
        bx = rcx + 102 * math.cos(ang)
        by = rcy + 102 * math.sin(ang)
        bezel_svg.append(f'    <circle cx="{bx:.1f}" cy="{by:.1f}" r="3.0" fill="url(#boltGrad)" stroke="#14191f" stroke-width="0.8"/>')
        bezel_svg.append(f'    <line x1="{bx - 1.6:.1f}" y1="{by:.1f}" x2="{bx + 1.6:.1f}" y2="{by:.1f}" stroke="#1c2128" stroke-width="0.7" stroke-linecap="round"/>')
        bezel_svg.append(f'    <line x1="{bx:.1f}" y1="{by - 1.6:.1f}" x2="{bx:.1f}" y2="{by + 1.6:.1f}" stroke="#1c2128" stroke-width="0.7" stroke-linecap="round"/>')
        bezel_svg.append(f'    <circle cx="{bx - 0.9:.1f}" cy="{by - 0.9:.1f}" r="0.9" fill="#ffffff" opacity="0.8"/>')

    # Spotted contacts: MANY glowing lights, not the same few dots in
    # the same places. 10 lights are scattered at RANDOM positions
    # (seeded, so the repo's auto-regeneration reproduces the same dots
    # instead of shuffling them on every workflow run), each on a mixed
    # rhythm (every pass / 2nd / 3rd / 4th), so which lights pop up
    # keeps changing and never settles into an obvious pattern. Periods
    # stay multiples of the 30s sweep so every light still fires exactly
    # when the beam reaches it. Radius capped at 78 so the 18px swell
    # stays inside the r=97 face; lights kept 28px apart so none overlap.
    # Each light is ONE glowing dot (r=3, dotGlow halo): it comes on
    # screen INSTANTLY at full brightness when the sweep reaches it,
    # then increases in size while losing opacity, swelling to 6x
    # (18px) and vanishing once the beam has passed (the 90-degree beam
    # covers a point for 7.5s). Sweep starts pointing up and rotates
    # clockwise, so a contact at sweep-angle a (clockwise from 12
    # o'clock) is hit at a/360*30 seconds.
    rng = random.Random(20261028)
    contacts = []
    placed = []
    tries = 0
    while len(contacts) < 10 and tries < 500:
        tries += 1
        bearing = rng.uniform(0, 360)
        radius = rng.uniform(30, 78)
        a = math.radians(bearing)
        px = radius * math.sin(a)
        py = -radius * math.cos(a)
        if any((px - qx) ** 2 + (py - qy) ** 2 < 28 ** 2 for qx, qy in placed):
            continue
        placed.append((px, py))
        contacts.append({
            "sweep_deg": bearing,
            "radius": radius,
            "period_mult": rng.choice([1, 2, 3, 4]),
        })
    contacts_svg = []
    for c in contacts:
        a = math.radians(c["sweep_deg"])
        ccx = rcx + c["radius"] * math.sin(a)
        ccy = rcy - c["radius"] * math.cos(a)
        hit = c["sweep_deg"] / 360.0 * 30.0
        n = c["period_mult"]
        contacts_svg.append(
            f'    <circle class="light{n}" cx="{ccx:.1f}" cy="{ccy:.1f}" r="3" fill="#ff3b30" opacity="0" filter="url(#dotGlow)" style="animation-delay: {hit:.2f}s;"/>'
        )

    # Smooth radar beam like the reference scope: NOT a flat triangle, but
    # a fan of thin sectors fading smoothly from the bright leading edge
    # back along the tail (SVG has no conic gradient, so graded slices
    # are how real radar UIs fake the angular fade).
    beam_slices = []
    num_slices = 30
    step_deg = 90.0 / num_slices
    for k in range(num_slices):
        a1 = math.radians(-90 - k * step_deg)
        a2 = math.radians(-90 - (k + 1) * step_deg)
        x1 = rcx + max_r * math.cos(a1)
        y1 = rcy + max_r * math.sin(a1)
        x2 = rcx + max_r * math.cos(a2)
        y2 = rcy + max_r * math.sin(a2)
        op = 0.5 * (1 - k / num_slices)
        beam_slices.append(f'    <path class="radar-sweep-beam" d="M {rcx} {rcy} L {x1:.1f} {y1:.1f} A {max_r} {max_r} 0 0 0 {x2:.1f} {y2:.1f} Z" fill="#39ff88" opacity="{op:.3f}"/>')

    # Fine scope grid inside the radar face, like the reference scope.
    grid_svg = []
    gx = rcx - 96
    while gx <= rcx + 96:
        grid_svg.append(f'    <line x1="{gx}" y1="{rcy - 96}" x2="{gx}" y2="{rcy + 96}" stroke="#39ff88" stroke-width="0.5" opacity="0.06"/>')
        gx += 16
    gy = rcy - 96
    while gy <= rcy + 96:
        grid_svg.append(f'    <line x1="{rcx - 96}" y1="{gy}" x2="{rcx + 96}" y2="{gy}" stroke="#39ff88" stroke-width="0.5" opacity="0.06"/>')
        gy += 16

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
    
    # Bars follow the same order as the radar (config order), all 8 skills.
    bar_skills = skills_data

    # Brand colors for the displayed technologies.
    brand_colors = {
        "Kubernetes": "#326CE5",
        "Docker": "#2496ED",
        "Linux / Bash": "#FCC624",
        "Jenkins / GitHub Actions": "#D24939",
        "AWS": "#FF9900",
        "Azure": "#0078D4",
        "Prometheus / Grafana": "#E6522C",
        "Terraform / Ansible": "#844FBA",
    }
    
    for idx, s in enumerate(bar_skills):
        y_offset = hud_start_y + idx * 32
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
      @keyframes lightBloom1 {{
        0% {{ transform: scale(1); opacity: 1; }}
        6.25% {{ transform: scale(2); opacity: 0.7; }}
        12.5% {{ transform: scale(3); opacity: 0.45; }}
        18.75% {{ transform: scale(4.5); opacity: 0.2; }}
        25% {{ transform: scale(6); opacity: 0; }}
        100% {{ transform: scale(6); opacity: 0; }}
      }}
      @keyframes lightBloom2 {{
        0% {{ transform: scale(1); opacity: 1; }}
        3.13% {{ transform: scale(2); opacity: 0.7; }}
        6.25% {{ transform: scale(3); opacity: 0.45; }}
        9.38% {{ transform: scale(4.5); opacity: 0.2; }}
        12.5% {{ transform: scale(6); opacity: 0; }}
        100% {{ transform: scale(6); opacity: 0; }}
      }}
      @keyframes lightBloom3 {{
        0% {{ transform: scale(1); opacity: 1; }}
        2.08% {{ transform: scale(2); opacity: 0.7; }}
        4.17% {{ transform: scale(3); opacity: 0.45; }}
        6.25% {{ transform: scale(4.5); opacity: 0.2; }}
        8.33% {{ transform: scale(6); opacity: 0; }}
        100% {{ transform: scale(6); opacity: 0; }}
      }}
      @keyframes lightBloom4 {{
        0% {{ transform: scale(1); opacity: 1; }}
        1.56% {{ transform: scale(2); opacity: 0.7; }}
        3.13% {{ transform: scale(3); opacity: 0.45; }}
        4.69% {{ transform: scale(4.5); opacity: 0.2; }}
        6.25% {{ transform: scale(6); opacity: 0; }}
        100% {{ transform: scale(6); opacity: 0; }}
      }}
      .radar-poly {{
        transform-origin: {rcx}px {rcy}px;
        animation: radarExpand 1.0s cubic-bezier(0.16, 1, 0.3, 1) forwards;
      }}
      .radar-sweep-beam {{
        transform-origin: {rcx}px {rcy}px;
        animation: radarSweep 30s linear infinite;
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
      .light1 {{
        transform-box: fill-box;
        transform-origin: center;
        opacity: 0;
        animation: lightBloom1 30s linear infinite;
      }}
      .light2 {{
        transform-box: fill-box;
        transform-origin: center;
        opacity: 0;
        animation: lightBloom2 60s linear infinite;
      }}
      .light3 {{
        transform-box: fill-box;
        transform-origin: center;
        opacity: 0;
        animation: lightBloom3 90s linear infinite;
      }}
      .light4 {{
        transform-box: fill-box;
        transform-origin: center;
        opacity: 0;
        animation: lightBloom4 120s linear infinite;
      }}
    </style>
    <filter id="dotGlow" x="-150%" y="-150%" width="400%" height="400%">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feMerge>
        <feMergeNode in="blur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <linearGradient id="metalRingGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#f7fafc"/>
      <stop offset="12%" stop-color="#d3dae1"/>
      <stop offset="22%" stop-color="#aab3bd"/>
      <stop offset="32%" stop-color="#767f89"/>
      <stop offset="42%" stop-color="#565e68"/>
      <stop offset="50%" stop-color="#3f4750"/>
      <stop offset="58%" stop-color="#6d7680"/>
      <stop offset="68%" stop-color="#a7b0b9"/>
      <stop offset="78%" stop-color="#d9dfe5"/>
      <stop offset="88%" stop-color="#eef2f5"/>
      <stop offset="100%" stop-color="#8b959f"/>
    </linearGradient>
    <radialGradient id="boltGrad" cx="35%" cy="30%" r="75%">
      <stop offset="0%" stop-color="#e8edf3"/>
      <stop offset="40%" stop-color="#9aa5b1"/>
      <stop offset="75%" stop-color="#565e68"/>
      <stop offset="100%" stop-color="#2f363e"/>
    </radialGradient>
    <clipPath id="radarFaceClip">
      <circle cx="{rcx}" cy="{rcy}" r="97"/>
    </clipPath>
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
{chr(10).join(bezel_svg)}
    <!-- Fine scope grid inside the radar face -->
    <g clip-path="url(#radarFaceClip)">
{chr(10).join(grid_svg)}
    </g>
    <!-- Background Rotating Sweep Beam: smooth graded fan, like the reference scope -->
{chr(10).join(beam_slices)}
    <path class="radar-sweep-beam" d="M {rcx} {rcy} L {rcx} {rcy - max_r}" fill="none" stroke="#39ff88" stroke-width="2" stroke-linecap="round" opacity="0.95"/>
{chr(10).join(rings_svg)}
{chr(10).join(axes_svg)}
{radar_polygon}
{chr(10).join(vertex_dots)}
{chr(10).join(contacts_svg)}
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

