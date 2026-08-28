#!/usr/bin/env python3
"""
scripts/generate_portrait.py
Generates a crystal-clear, high-definition animated dot-matrix (stippling) portrait SVG.
Includes AI-based background removal, shadow lifting, adaptive histogram equalization (CLAHE),
and clean, sleek non-bubbly scanline fade-in animation.
"""

import os
import sys
import yaml
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import cv2

try:
    from render_readme import render_readme
except ImportError:
    from scripts.render_readme import render_readme

try:
    from generate_skills_svg import generate_skills_svg
except ImportError:
    from scripts.generate_skills_svg import generate_skills_svg


try:
    from generate_contributions_svg import generate_contributions_svg
except ImportError:
    from scripts.generate_contributions_svg import generate_contributions_svg

try:
    from generate_bento_svg import generate_bento_svg
except ImportError:
    from scripts.generate_bento_svg import generate_bento_svg


def load_config(config_path="config.yml"):
    default_config = {
        "github_username": "octocat",
        "display_name": "Developer",
        "headline": "🚀 Building Cool Stuff",
        "tagline": "DevOps & Cloud Engineer • Cloud Automation • Kubernetes",
        "bio": "",
        "links": {},
        "skills": [],
        "portrait": {
            "source_image": "assets/source-photo.jpg",
            "grid_spacing_px": 8,
            "canvas_size_px": 1000,
            "color_palette": "original",
            "duotone_light": "#ffffff",
            "duotone_dark": "#161b22",
            "reveal_style": "rows"
        }
    }
    
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            user_config = yaml.safe_load(f) or {}
            if "portrait" in user_config:
                default_config["portrait"].update(user_config["portrait"])
            for key in ["github_username", "display_name", "headline", "tagline", "bio", "links", "skills", "tech_stack", "human_side", "footer_text"]:
                if key in user_config:
                    default_config[key] = user_config[key]
    return default_config


def hex_to_rgb(hex_str):
    hex_str = hex_str.lstrip("#")
    if len(hex_str) == 3:
        hex_str = "".join([c * 2 for c in hex_str])
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))


def generate_crystal_portrait(config):
    p_cfg = config.get("portrait", {})
    source_image = p_cfg.get("source_image", "assets/source-photo.jpg")
    grid_spacing = int(p_cfg.get("grid_spacing_px", 8))
    canvas_size = int(p_cfg.get("canvas_size_px", 1000))
    palette_mode = p_cfg.get("color_palette", "original").lower()
    duotone_light = hex_to_rgb(p_cfg.get("duotone_light", "#ffffff"))
    duotone_dark = hex_to_rgb(p_cfg.get("duotone_dark", "#161b22"))
    reveal_style = p_cfg.get("reveal_style", "rows").lower()

    if not os.path.exists(source_image):
        print(f"[Error] Source image not found at '{source_image}'")
        sys.exit(1)

    print(f"[Portrait] Processing '{source_image}'...")
    orig = Image.open(source_image).convert("RGB")

    # 1. Background removal using rembg
    try:
        from rembg import remove
        print("[Portrait] Isolating subject using AI background removal...")
        bg_removed = remove(orig)
    except Exception as e:
        print(f"[Portrait] rembg fallback notice: {e}")
        bg_removed = orig

    w, h = orig.size

    # 2. Head & Face Centered Framing
    if bg_removed.mode == "RGBA":
        alpha = np.array(bg_removed.split()[-1])
        non_zero = np.argwhere(alpha > 30)
        if len(non_zero) > 0:
            y_min, x_min = non_zero.min(axis=0)
            y_max, x_max = non_zero.max(axis=0)
            sub_w = x_max - x_min
            sub_h = y_max - y_min
            head_size = int(sub_w * 1.15)
            cx = (x_min + x_max) // 2
            cy = y_min + int(sub_h * 0.40)
            x1 = max(0, min(cx - head_size // 2, w - head_size))
            y1 = max(0, min(cy - head_size // 2, h - head_size))
            crop_box = (x1, y1, min(w, x1 + head_size), min(h, y1 + head_size))
            cropped = bg_removed.crop(crop_box)
        else:
            crop_w = int(w * 0.80)
            cropped = bg_removed.crop(((w-crop_w)//2, int(h*0.05), (w+crop_w)//2, int(h*0.05)+crop_w))
    else:
        crop_w = int(w * 0.80)
        cropped = bg_removed.crop(((w-crop_w)//2, int(h*0.05), (w+crop_w)//2, int(h*0.05)+crop_w))

    cropped = cropped.resize((canvas_size, canvas_size), Image.Resampling.LANCZOS)

    if cropped.mode == "RGBA":
        r, g, b, a = cropped.split()
        rgb_img = Image.merge("RGB", (r, g, b))
        alpha_np = np.array(a, dtype=np.float32) / 255.0
    else:
        rgb_img = cropped.convert("RGB")
        alpha_np = np.ones((canvas_size, canvas_size), dtype=np.float32)

    # 3. Dramatic Lighting Correction, Shadow Lifting & CLAHE
    rgb_cv = cv2.cvtColor(np.array(rgb_img), cv2.COLOR_RGB2BGR)
    lab = cv2.cvtColor(rgb_cv, cv2.COLOR_BGR2LAB)
    l_ch, a_ch, b_ch = cv2.split(lab)

    # Lift shadows
    l_float = l_ch.astype(np.float32) / 255.0
    l_lifted = np.power(l_float, 0.42) * 255.0
    l_lifted = np.clip(l_lifted, 0, 255).astype(np.uint8)

    # CLAHE adaptive equalization for sharp facial details
    clahe = cv2.createCLAHE(clipLimit=3.8, tileGridSize=(8, 8))
    l_clahe = clahe.apply(l_lifted)

    lab_enhanced = cv2.merge((l_clahe, a_ch, b_ch))
    rgb_enhanced = cv2.cvtColor(lab_enhanced, cv2.COLOR_LAB2RGB)

    enhanced_pil = Image.fromarray(rgb_enhanced)
    enhanced_pil = ImageEnhance.Color(enhanced_pil).enhance(1.45)
    enhanced_pil = ImageEnhance.Sharpness(enhanced_pil).enhance(2.4)

    gray = enhanced_pil.convert("L")
    edges = gray.filter(ImageFilter.FIND_EDGES)
    edges = ImageEnhance.Contrast(edges).enhance(2.8)

    gray_np = np.array(gray, dtype=np.float32)
    edge_np = np.array(edges, dtype=np.float32)
    rgb_np = np.array(enhanced_pil)

    # 4. Generate Stippling Grid
    cols = canvas_size // grid_spacing
    rows = canvas_size // grid_spacing
    cell_w = canvas_size / cols
    cell_h = canvas_size / rows

    groups = {}
    total_dots = 0

    max_r = min(4.4, grid_spacing * 0.46)
    min_r = 0.65

    for r_idx in range(rows):
        for c_idx in range(cols):
            cx = (c_idx + 0.5) * cell_w
            cy = (r_idx + 0.5) * cell_h

            x1 = max(0, int(cx - cell_w * 0.5))
            y1 = max(0, int(cy - cell_h * 0.5))
            x2 = min(canvas_size, int(cx + cell_w * 0.5 + 1))
            y2 = min(canvas_size, int(cy + cell_h * 0.5 + 1))

            cell_alpha = np.mean(alpha_np[y1:y2, x1:x2])
            if cell_alpha < 0.12:
                continue

            cell_gray = np.mean(gray_np[y1:y2, x1:x2])
            cell_edge = np.mean(edge_np[y1:y2, x1:x2])
            cell_rgb = np.mean(rgb_np[y1:y2, x1:x2], axis=(0, 1)).astype(int)

            tone_factor = (1.0 - (cell_gray / 255.0)) ** 0.85
            edge_factor = min(1.0, (cell_edge / 38.0) ** 1.1)

            weight = (0.52 * tone_factor) + (0.48 * edge_factor)
            weight = weight * (cell_alpha ** 0.6)

            radius = min_r + weight * (max_r - min_r)
            if radius < 0.45:
                continue

            if palette_mode == "duotone":
                t = cell_gray / 255.0
                cr = int(duotone_dark[0] + t * (duotone_light[0] - duotone_dark[0]))
                cg = int(duotone_dark[1] + t * (duotone_light[1] - duotone_dark[1]))
                cb = int(duotone_dark[2] + t * (duotone_light[2] - duotone_dark[2]))
                hex_col = f"#{cr:02x}{cg:02x}{cb:02x}"
            elif palette_mode == "monochrome":
                # Pure monochrome luminance ramp
                val = int(cell_gray)
                hex_col = f"#{val:02x}{val:02x}{val:02x}"
            else:
                hex_col = f"#{cell_rgb[0]:02x}{cell_rgb[1]:02x}{cell_rgb[2]:02x}"

            if reveal_style == "columns":
                g_idx = c_idx
            elif reveal_style == "diagonal":
                g_idx = r_idx + c_idx
            else:
                g_idx = r_idx

            if g_idx not in groups:
                groups[g_idx] = []

            groups[g_idx].append((round(cx, 1), round(cy, 1), round(radius, 2), hex_col))
            total_dots += 1

    print(f"[Portrait] Generated {total_dots} dots across {len(groups)} scanlines.")

    # Sleek, non-bubbly linear raster sweep (smooth fade-in with zero scale bouncing)
    num_groups = len(groups)
    total_duration = 1.8
    step_delay = total_duration / max(1, num_groups)

    css_lines = [
        "  @keyframes scanlineFade {",
        "    0% { opacity: 0; }",
        "    100% { opacity: 1; }",
        "  }",
        "  .dot-group {",
        "    opacity: 0;",
        "    animation: scanlineFade 0.22s ease-in-out forwards;",
        "  }"
    ]
    for g_idx in sorted(groups.keys()):
        delay = g_idx * step_delay
        css_lines.append(f"  .g-{g_idx} {{ animation-delay: {delay:.3f}s; }}")

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {canvas_size} {canvas_size}" width="100%" height="auto">',
        '  <defs>',
        '    <style>',
        "\n".join(css_lines),
        '    </style>',
        '    <radialGradient id="bgGlow" cx="50%" cy="45%" r="55%">',
        '      <stop offset="0%" stop-color="#161b22" stop-opacity="1"/>',
        '      <stop offset="100%" stop-color="#0a0d12" stop-opacity="1"/>',
        '    </radialGradient>',
        '  </defs>',
        f'  <rect width="{canvas_size}" height="{canvas_size}" fill="url(#bgGlow)" rx="24"/>'
    ]

    for g_idx in sorted(groups.keys()):
        dots = groups[g_idx]
        svg_parts.append(f'  <g class="dot-group g-{g_idx}">')
        for cx, cy, rad, col in dots:
            svg_parts.append(f'    <circle cx="{cx}" cy="{cy}" r="{rad}" fill="{col}"/>')
        svg_parts.append('  </g>')

    svg_parts.append('</svg>\n')

    output_path = "assets/portrait.svg"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_parts))

    file_size_kb = os.path.getsize(output_path) / 1024.0
    print(f"[Portrait] SVG successfully saved to '{output_path}' ({file_size_kb:.1f} KB)")


if __name__ == "__main__":
    cfg = load_config()
    generate_crystal_portrait(cfg)
    generate_skills_svg()
    generate_contributions_svg()
    generate_bento_svg()
    render_readme()
