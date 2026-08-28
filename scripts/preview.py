#!/usr/bin/env python3
"""
scripts/preview.py
Generates a standalone, pre-rendered preview.html styled identically to GitHub's Dark Mode.
Embeds all SVGs directly so that double-clicking preview.html works 100% offline in any browser.
"""

import os
import sys
import re
import base64
import yaml
import webbrowser
import http.server
import socketserver

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


def _load_display_name():
    if os.path.exists("config.yml"):
        with open("config.yml", "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
        return cfg.get("display_name", "Developer")
    return "Developer"


def generate_preview_html():
    generate_skills_svg()
    generate_contributions_svg()
    generate_bento_svg()
    render_readme()

    if not os.path.exists("README.md"):
        print("[Error] README.md not found.")
        return None

    with open("README.md", "r", encoding="utf-8") as f:
        md_content = f.read()

    # Pre-render markdown to HTML cleanly
    html_body = md_content

    # Embed local SVGs as base64 data-uris so they render in file:// without browser CORS blocks
    for asset_path in ["assets/portrait.svg", "assets/skills.svg", "assets/contributions.svg", "assets/bento.svg"]:
        if os.path.exists(asset_path):
            with open(asset_path, "rb") as svg_f:
                b64_str = base64.b64encode(svg_f.read()).decode("utf-8")
                data_uri = f"data:image/svg+xml;base64,{b64_str}"
                html_body = html_body.replace(asset_path, data_uri)

    display_name = _load_display_name()

    html_template = f"""<!DOCTYPE html>
<html lang="en" data-color-mode="dark" data-dark-theme="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GitHub Profile Preview - {display_name}</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.5.1/github-markdown-dark.min.css">
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <style>
    body {{
      background-color: #0d1117;
      color: #e6edf3;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif;
      margin: 0;
      padding: 32px 16px;
      display: flex;
      justify-content: center;
    }}
    .preview-container {{
      max-width: 900px;
      width: 100%;
      background-color: #0d1117;
      border: 1px solid #30363d;
      border-radius: 8px;
      padding: 36px;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
    }}
    .preview-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid #21262d;
      padding-bottom: 14px;
      margin-bottom: 28px;
    }}
    .preview-badge {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: #161b22;
      border: 1px solid #30363d;
      border-radius: 20px;
      padding: 4px 14px;
      font-size: 12px;
      color: #8b949e;
    }}
    .markdown-body {{
      background-color: transparent !important;
      color: #e6edf3 !important;
    }}
    .markdown-body hr {{
      background-color: #21262d !important;
      height: 1px !important;
      margin: 28px 0 !important;
    }}
    .markdown-body table {{
      background-color: transparent !important;
      border: none !important;
    }}
    .markdown-body table td, .markdown-body table th {{
      border: none !important;
      background-color: transparent !important;
    }}
    .markdown-body img {{
      max-width: 100%;
      background-color: transparent !important;
    }}
  </style>
</head>
<body>
  <div class="preview-container">
    <div class="preview-header">
      <div style="font-weight: 600; font-size: 14px; color: #ffffff;">
        👤 GitHub Profile README Preview (Monochrome Theme)
      </div>
      <div class="preview-badge">
        <span style="color: #3fb950;">●</span> Live Local Preview
      </div>
    </div>
    
    <article id="content" class="markdown-body">
    </article>
  </div>

  <script>
    // Raw markdown with embedded assets
    const rawMarkdown = `{html_body.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')}`;
    
    marked.setOptions({{
      gfm: true,
      breaks: true
    }});
    
    document.getElementById('content').innerHTML = marked.parse(rawMarkdown);
  </script>
</body>
</html>
"""
    with open("preview.html", "w", encoding="utf-8") as f:
        f.write(html_template)

    print("[Preview] Generated 'preview.html' successfully with embedded SVGs.")
    return "preview.html"


def serve_preview(port=8000):
    generate_preview_html()
    os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")
    
    handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer(("", port), handler) as httpd:
            url = f"http://localhost:{port}/preview.html"
            print(f"[Preview] Serving live profile preview at: {url}")
            print("[Preview] Press Ctrl+C to stop.")
            try:
                webbrowser.open(url)
            except Exception:
                pass
            httpd.serve_forever()
    except OSError:
        with socketserver.TCPServer(("", port + 1), handler) as httpd:
            url = f"http://localhost:{port + 1}/preview.html"
            print(f"[Preview] Serving live profile preview at: {url}")
            print("[Preview] Press Ctrl+C to stop.")
            try:
                webbrowser.open(url)
            except Exception:
                pass
            httpd.serve_forever()


if __name__ == "__main__":
    if "--serve" in sys.argv or "-s" in sys.argv:
        serve_preview()
    else:
        generate_preview_html()
        print("[Preview] You can open 'preview.html' in any web browser, or run:")
        print("          python scripts/preview.py --serve")
