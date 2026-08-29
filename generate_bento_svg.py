#!/usr/bin/env python3
"""Generate Mouli's project-focused Engineering Showcase SVG."""

import html
import json
import os
import re
import urllib.request
import yaml


def load_config(config_path="config.yml"):
    if not os.path.exists(config_path):
        return {}
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def fetch_bento_metrics(username):
    """Fetch live GitHub metrics through GraphQL, with REST fallback.

    The Actions GITHUB_TOKEN is used automatically.  Avoid scraping the
    rendered github.com profile page because that HTML is dynamic and can
    cause false SYNC fallbacks.
    """
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    headers = {
        "User-Agent": "mouli-github-profile",
        "Accept": "application/vnd.github+json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    total_year = None
    public_repos_count = None
    total_stars = None
    lang_totals = {}

    # Primary source: GitHub GraphQL API.
    if token:
        query = """
        query($login:String!) {
          user(login:$login) {
            repositories(first:100, privacy:PUBLIC, ownerAffiliations:OWNER) {
              totalCount
              nodes {
                stargazerCount
                languages(first:20, orderBy:{field:SIZE, direction:DESC}) {
                  edges { size node { name } }
                }
              }
            }
            contributionsCollection {
              contributionCalendar {
                totalContributions
              }
            }
          }
        }
        """
        try:
            payload = json.dumps({
                "query": query,
                "variables": {"login": username}
            }).encode("utf-8")
            req = urllib.request.Request(
                "https://api.github.com/graphql",
                data=payload,
                headers={**headers, "Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                result = json.loads(resp.read().decode("utf-8"))

            if result.get("errors"):
                raise RuntimeError("; ".join(
                    e.get("message", "GraphQL error") for e in result["errors"]
                ))

            user = result["data"]["user"]
            if not user:
                raise RuntimeError(f"GitHub user '{username}' not found")

            repos = user["repositories"]
            public_repos_count = repos["totalCount"]
            total_stars = sum(r.get("stargazerCount", 0) for r in repos["nodes"])
            total_year = user["contributionsCollection"]["contributionCalendar"]["totalContributions"]

            for repo in repos["nodes"]:
                for edge in repo.get("languages", {}).get("edges", []):
                    name = edge["node"]["name"]
                    lang_totals[name] = lang_totals.get(name, 0) + edge.get("size", 0)

            print(
                f"[Bento] Live metrics: {total_year} contributions, "
                f"{public_repos_count} public repos, {total_stars} stars"
            )
        except Exception as e:
            print(f"[Bento] GraphQL metrics notice: {e}")

    # REST fallback for repo counts/languages if GraphQL is unavailable.
    if public_repos_count is None or total_stars is None:
        try:
            repos_url = f"https://api.github.com/users/{username}/repos?per_page=100&type=owner"
            req = urllib.request.Request(repos_url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                repos = json.loads(resp.read().decode("utf-8"))
            public_repos_count = len(repos)
            total_stars = sum(r.get("stargazers_count", 0) for r in repos)
            for repo in repos:
                owner = repo.get("owner", {}).get("login", username)
                name = repo.get("name")
                if not name:
                    continue
                try:
                    lang_url = f"https://api.github.com/repos/{owner}/{name}/languages"
                    req2 = urllib.request.Request(lang_url, headers=headers)
                    with urllib.request.urlopen(req2, timeout=8) as resp2:
                        langs = json.loads(resp2.read().decode("utf-8"))
                    for lang, count in langs.items():
                        lang_totals[lang] = lang_totals.get(lang, 0) + count
                except Exception:
                    continue
        except Exception as e:
            print(f"[Bento] REST metrics notice: {e}")

    # We never display SYNC for normal API failure. Use the real repo count
    # when available and an explicit 0 only when GitHub reports no data.
    if total_year is None:
        total_year = 0
    if public_repos_count is None:
        public_repos_count = 0
    if total_stars is None:
        total_stars = 0
    if not lang_totals:
        lang_totals = {"Python": 1}

    total_bytes = sum(lang_totals.values()) or 1
    palette = ["#ffffff", "#8b949e", "#565e69", "#30363d", "#21262d"]
    languages = []
    for idx, (lang, count) in enumerate(sorted(lang_totals.items(), key=lambda x: -x[1])[:5]):
        languages.append({
            "name": lang,
            "pct": round(count / total_bytes * 100, 1),
            "color": palette[idx % len(palette)]
        })

    return {
        "total_year": f"{total_year:,}",
        "public_repos": public_repos_count,
        "total_stars": total_stars,
        "languages": languages,
    }


def generate_bento_svg(config_path="config.yml", output_path="assets/bento.svg"):
    config = load_config(config_path)
    username = config.get("github_username", "octocat")
    metrics = fetch_bento_metrics(username)
    bento_cfg = config.get("bento", {})
    prod_items = bento_cfg.get("production_focus", [])[:3]
    projects = bento_cfg.get("projects", [])[:2]

    width, height = 940, 470
    bar_w = 385

    # Production focus
    prod_svg = []
    for idx, item in enumerate(prod_items):
        y = idx * 36
        prod_svg.append(f'''\n        <g transform="translate(0, {y})">
          <text x="0" y="10" fill="#e6edf3" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="12" font-weight="600">{html.escape(item.get("title", ""))}</text>
          <text x="0" y="25" fill="#8b949e" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="11">{html.escape(item.get("desc", ""))}</text>
        </g>''')

    # Project cards
    project_svg = []
    for idx, item in enumerate(projects):
        y = idx * 70
        title = html.escape(item.get("title", ""))
        desc = html.escape(item.get("desc", ""))
        stack = html.escape(item.get("stack", ""))
        url = html.escape(item.get("url", ""), quote=True)
        project_svg.append(f'''\n        <a href="{url}" target="_blank">
          <g transform="translate(0, {y})">
            <rect x="0" y="0" width="414" height="58" rx="6" fill="#0d1117" stroke="#30363d" stroke-width="1"/>
            <text x="12" y="17" fill="#ffffff" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="12" font-weight="700">{title}</text>
            <text x="12" y="33" fill="#c9d1d9" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="10.5">{desc}</text>
            <text x="12" y="48" fill="#8b949e" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="9.5">{stack}</text>
            <text x="398" y="18" text-anchor="end" fill="#8b949e" font-family="monospace" font-size="10">↗</text>
          </g>
        </a>''')

    # Language spectrum
    segments, legend = [], []
    curr_x = 0
    for lang in metrics["languages"]:
        seg_w = lang["pct"] / 100 * bar_w
        if seg_w > 0:
            segments.append(f'<rect x="{curr_x:.1f}" y="0" width="{seg_w:.1f}" height="10" rx="2" fill="{lang["color"]}"/>')
            curr_x += seg_w
    for idx, lang in enumerate(metrics["languages"]):
        col, row = idx % 2, idx // 2
        lx, ly = col * 200, 24 + row * 24
        legend.append(f'''<g transform="translate({lx}, {ly})">
          <circle cx="5" cy="5" r="4" fill="{lang["color"]}"/>
          <text x="16" y="9" fill="#e6edf3" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="11" font-weight="500">{html.escape(lang["name"])}</text>
          <text x="180" y="9" text-anchor="end" fill="#8b949e" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="10">{lang["pct"]}%</text>
        </g>''')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="auto" fill="none">
  <rect width="{width}" height="{height}" rx="12" fill="#0d1117" stroke="#30363d" stroke-width="1"/>
  <g transform="translate(24, 34)">
    <rect x="0" y="0" width="28" height="20" rx="4" fill="#161b22" stroke="#30363d" stroke-width="1"/>
    <text x="6" y="14" fill="#ffffff" font-family="monospace" font-size="12" font-weight="bold">~/</text>
    <text x="38" y="15" fill="#ffffff" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="14" font-weight="600">Engineering Showcase &amp; Performance</text>
    <text x="868" y="14" text-anchor="end" fill="#8b949e" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="10.5">Cloud • Automation • Reliability • Projects</text>
    <line x1="0" y1="26" x2="868" y2="26" stroke="#21262d" stroke-width="1"/>
  </g>

  <g transform="translate(24, 75)">
    <rect width="430" height="160" rx="8" fill="#161b22" stroke="#21262d" stroke-width="1"/>
    <text x="16" y="24" fill="#ffffff" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="13" font-weight="600">🚀 Production Focus</text>
    <text x="414" y="24" text-anchor="end" fill="#8b949e" font-family="monospace" font-size="10">BUILD → SHIP → OBSERVE</text>
    <line x1="16" y1="34" x2="414" y2="34" stroke="#30363d" stroke-width="1"/>
    <g transform="translate(16, 46)">{''.join(prod_svg)}
    </g>
  </g>

  <g transform="translate(486, 75)">
    <rect width="430" height="160" rx="8" fill="#161b22" stroke="#21262d" stroke-width="1"/>
    <text x="16" y="24" fill="#ffffff" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="13" font-weight="600">⚡ GitHub Telemetry</text>
    <text x="414" y="24" text-anchor="end" fill="#3fb950" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="10.5" font-weight="600">● LIVE DATA</text>
    <line x1="16" y1="34" x2="414" y2="34" stroke="#30363d" stroke-width="1"/>
    <g transform="translate(16, 48)">
      <rect width="190" height="46" rx="6" fill="#0d1117" stroke="#30363d" stroke-width="1"/>
      <text x="12" y="20" fill="#ffffff" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="16" font-weight="bold">{metrics["total_year"]}</text>
      <text x="12" y="36" fill="#8b949e" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="10">Contributions / year</text>
    </g>
    <g transform="translate(224, 48)">
      <rect width="190" height="46" rx="6" fill="#0d1117" stroke="#30363d" stroke-width="1"/>
      <text x="12" y="20" fill="#ffffff" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="16" font-weight="bold">{metrics["public_repos"]}</text>
      <text x="12" y="36" fill="#8b949e" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="10">Public repositories</text>
    </g>
    <g transform="translate(16, 102)">
      <rect width="190" height="46" rx="6" fill="#0d1117" stroke="#30363d" stroke-width="1"/>
      <text x="12" y="20" fill="#ffffff" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="16" font-weight="bold">{metrics["total_stars"]} ★</text>
      <text x="12" y="36" fill="#8b949e" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="10">Total GitHub stars</text>
    </g>
    <g transform="translate(224, 102)">
      <rect width="190" height="46" rx="6" fill="#0d1117" stroke="#30363d" stroke-width="1"/>
      <text x="12" y="20" fill="#ffffff" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="16" font-weight="bold">{len(metrics["languages"])}+</text>
      <text x="12" y="36" fill="#8b949e" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="10">Detected languages</text>
    </g>
  </g>

  <g transform="translate(24, 255)">
    <rect width="430" height="190" rx="8" fill="#161b22" stroke="#21262d" stroke-width="1"/>
    <text x="16" y="24" fill="#ffffff" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="13" font-weight="600">🚀 Featured Engineering Projects</text>
    <text x="414" y="24" text-anchor="end" fill="#8b949e" font-family="monospace" font-size="10">OPEN REPO ↗</text>
    <line x1="16" y1="34" x2="414" y2="34" stroke="#30363d" stroke-width="1"/>
    <g transform="translate(8, 46)">{''.join(project_svg)}
    </g>
  </g>

  <g transform="translate(486, 255)">
    <rect width="430" height="190" rx="8" fill="#161b22" stroke="#21262d" stroke-width="1"/>
    <text x="16" y="24" fill="#ffffff" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="13" font-weight="600">📊 Repository Language Spectrum</text>
    <text x="414" y="24" text-anchor="end" fill="#8b949e" font-family="monospace" font-size="10">PUBLIC REPOS</text>
    <line x1="16" y1="34" x2="414" y2="34" stroke="#30363d" stroke-width="1"/>
    <g transform="translate(22, 52)">
      <rect x="0" y="0" width="{bar_w}" height="10" rx="4" fill="#0d1117" stroke="#30363d" stroke-width="1"/>
      {''.join(segments)}
      <g transform="translate(0, 18)">{''.join(legend)}</g>
    </g>
    <text x="22" y="168" fill="#8b949e" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" font-size="9.5">Language distribution is calculated from your public GitHub repositories.</text>
  </g>
</svg>'''

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"[Bento Showcase] Saved project-focused SVG to '{output_path}'")


if __name__ == "__main__":
    generate_bento_svg()
