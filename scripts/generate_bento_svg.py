#!/usr/bin/env python3
import os

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_HEADERS = {"Accept": "application/vnd.github+json"}

if GITHUB_TOKEN:
    GITHUB_HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"


"""Generate Mouli's project-focused Engineering Showcase SVG."""

import html
import json
import re
import urllib.request
import yaml


def load_config(config_path="config.yml"):
    if not os.path.exists(config_path):
        return {}

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def fetch_bento_metrics(username):
    total_year = "SYNC"

    try:
        url = f"https://github.com/users/{username}/contributions"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        with urllib.request.urlopen(req, timeout=8) as resp:
            text = resp.read().decode("utf-8")

        match = re.search(
            r'([0-9,]+)\s+contributions?\s+in\s+the\s+last\s+year',
            text
        )

        if match:
            total_year = match.group(1)

    except Exception as e:
        print(f"[Bento] Contribution fetch notice: {e}")

    total_stars = "SYNC"
    public_repos_count = "SYNC"
    lang_totals = {}

    try:
        repos_url = (
            f"https://api.github.com/users/{username}/repos"
            f"?per_page=100&sort=updated"
        )

        req = urllib.request.Request(
            repos_url,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        with urllib.request.urlopen(req, timeout=8) as resp:
            repos = json.loads(resp.read().decode("utf-8"))

        public_repos_count = len(repos)

        total_stars = sum(
            r.get("stargazers_count", 0)
            for r in repos
        )

        # GitHub's repo listing does not contain language byte totals,
        # so collect language totals from each public repo when possible.
        for repo in repos:
            owner = repo.get("owner", {}).get(
                "login",
                username
            )

            name = repo.get("name")

            if not name:
                continue

            try:
                lang_url = (
                    f"https://api.github.com/repos/"
                    f"{owner}/{name}/languages"
                )

                req2 = urllib.request.Request(
                    lang_url,
                    headers={"User-Agent": "Mozilla/5.0"}
                )

                with urllib.request.urlopen(
                    req2,
                    timeout=5
                ) as resp2:
                    langs = json.loads(
                        resp2.read().decode("utf-8")
                    )

                for lang, count in langs.items():
                    lang_totals[lang] = (
                        lang_totals.get(lang, 0) + count
                    )

            except Exception:
                continue

    except Exception as e:
        print(f"[Bento] Repo metrics notice: {e}")

    if not lang_totals:
        lang_totals = {}

    total_bytes = sum(lang_totals.values()) or 1

    # GitHub Linguist is GitHub's source of truth for language colors.
    # Percentages remain calculated from the real GitHub language byte totals.
    language_colors = {}

    try:
        linguist_url = (
            "https://raw.githubusercontent.com/"
            "github-linguist/linguist/"
            "main/lib/linguist/languages.yml"
        )

        linguist_req = urllib.request.Request(
            linguist_url,
            headers={"User-Agent": "Mozilla/5.0"}
        )

        with urllib.request.urlopen(
            linguist_req,
            timeout=8
        ) as resp:
            linguist_data = yaml.safe_load(
                resp.read().decode("utf-8")
            ) or {}

        for language_name, language_info in linguist_data.items():
            if isinstance(language_info, dict):
                color = language_info.get("color")

                if isinstance(color, str) and color.strip():
                    language_colors[language_name] = color.strip()

    except Exception as e:
        print(f"[Bento] Language color fetch notice: {e}")

    languages = []

    # Show every language returned by GitHub.
    # No hardcoded language limit.
    for lang, count in sorted(
        lang_totals.items(),
        key=lambda x: -x[1]
    ):
        languages.append({
            "name": lang,
            "pct": round(
                count / total_bytes * 100,
                1
            ),
            "color": language_colors.get(
                lang,
                "#8b949e"
            )
        })

    return {
        "total_year": total_year,
        "public_repos": public_repos_count,
        "total_stars": total_stars,
        "languages": languages
    }


def generate_bento_svg(
    config_path="config.yml",
    output_path="assets/bento.svg"
):
    config = load_config(config_path)

    username = config.get(
        "github_username",
        "octocat"
    )

    metrics = fetch_bento_metrics(username)

    bento_cfg = config.get("bento", {})

    prod_items = bento_cfg.get(
        "production_focus",
        []
    )[:3]

    projects = bento_cfg.get(
        "projects",
        []
    )[:2]

    width = 940
    bar_w = 385

    # ---------------------------------------------------------
    # Production Focus
    # ---------------------------------------------------------

    prod_svg = []

    for idx, item in enumerate(prod_items):
        y = idx * 36

        prod_svg.append(
            f'''
        <g transform="translate(0, {y})">
          <text x="0" y="10"
                fill="#e6edf3"
                font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
                font-size="12"
                font-weight="600">{html.escape(item.get("title", ""))}</text>

          <text x="0" y="25"
                fill="#8b949e"
                font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
                font-size="11">{html.escape(item.get("desc", ""))}</text>
        </g>'''
        )

    # ---------------------------------------------------------
    # Project Cards
    # ---------------------------------------------------------

    project_svg = []

    for idx, item in enumerate(projects):
        y = idx * 70

        title = html.escape(
            item.get("title", "")
        )

        desc = html.escape(
            item.get("desc", "")
        )

        stack = html.escape(
            item.get("stack", "")
        )

        url = html.escape(
            item.get("url", ""),
            quote=True
        )

        project_svg.append(
            f'''
        <a href="{url}" target="_blank">
          <g transform="translate(0, {y})">

            <rect x="0" y="0"
                  width="414"
                  height="58"
                  rx="6"
                  fill="#0d1117"
                  stroke="#30363d"
                  stroke-width="1"/>

            <text x="12" y="17"
                  fill="#ffffff"
                  font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
                  font-size="12"
                  font-weight="700">{title}</text>

            <text x="12" y="33"
                  fill="#c9d1d9"
                  font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
                  font-size="10.5">{desc}</text>

            <text x="12" y="48"
                  fill="#8b949e"
                  font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
                  font-size="9.5">{stack}</text>

            <text x="398" y="18"
                  text-anchor="end"
                  fill="#8b949e"
                  font-family="monospace"
                  font-size="10">↗</text>

          </g>
        </a>'''
        )

    # ---------------------------------------------------------
    # Repository Language Spectrum
    # ---------------------------------------------------------

    segments = []
    legend = []

    # Each language gets its own bar.
    # Every bar starts from the exact same 0% point.
    language_bar_height = 4
    language_bar_gap = 3

    for idx, lang in enumerate(metrics["languages"]):

        seg_w = (
            lang["pct"] / 100
        ) * bar_w

        if seg_w > 0:
            bar_y = idx * (language_bar_height + language_bar_gap)

            segments.append(
                f'<rect '
                f'x="0" '
                f'y="{bar_y:.1f}" '
                f'width="{seg_w:.1f}" '
                f'height="{language_bar_height}" '
                f'rx="2" '
                f'fill="{lang["color"]}"/>'
            )

    # ---------------------------------------------------------
    # Dynamic Language Layout
    # ---------------------------------------------------------

    language_count = len(
        metrics["languages"]
    )

    # Keep the current 3-column visual design.
    legend_columns = 3

    legend_width = (
        bar_w / legend_columns
    )

    # Automatically calculate how many rows are needed.
    legend_rows = max(
        1,
        (
            language_count
            + legend_columns
            - 1
        )
        // legend_columns
    )

    # Keep the current clean row spacing.
    row_height = 22

    legend_font_size = 10.5

    # ---------------------------------------------------------
    # Build Language Legend
    # ---------------------------------------------------------

    for idx, lang in enumerate(
        metrics["languages"]
    ):

        col = (
            idx
            % legend_columns
        )

        row = (
            idx
            // legend_columns
        )

        lx = (
            col
            * legend_width
        )

        ly = (
            18
            + row * row_height
        )

        legend.append(
            f"""
<g transform="translate({lx:.1f}, {ly:.1f})">

  <circle
      cx="5"
      cy="5"
      r="4"
      fill="{lang["color"]}"
  />

  <text
      x="16"
      y="9"
      fill="#e6edf3"
      font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
      font-size="{legend_font_size}"
      font-weight="500">{html.escape(lang["name"])}</text>

  <text
      x="{legend_width - 10:.1f}"
      y="9"
      text-anchor="end"
      fill="#8b949e"
      font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
      font-size="9.5">{lang["pct"]}%</text>

</g>"""
        )

    # ---------------------------------------------------------
    # Dynamic Card Height
    # ---------------------------------------------------------
    #
    # The card grows when GitHub returns more language rows.
    # There is NO footer anymore.
    #

    language_bar_area_height = max(
        10,
        language_count * (language_bar_height + language_bar_gap)
        - language_bar_gap
    )

    language_card_height = max(
        190,
        90
        + language_bar_area_height
        + legend_rows * row_height
    )

    overall_height = (
        255
        + language_card_height
        + 25
    )

    # ---------------------------------------------------------
    # SVG
    # ---------------------------------------------------------

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 {width} {overall_height}"
    width="100%"
    height="auto"
    fill="none">

  <rect
      width="{width}"
      height="{overall_height}"
      rx="12"
      fill="#0d1117"
      stroke="#30363d"
      stroke-width="1"/>

  <!-- ===================================================== -->
  <!-- Header -->
  <!-- ===================================================== -->

  <g transform="translate(24, 34)">

    <rect
        x="0"
        y="0"
        width="28"
        height="20"
        rx="4"
        fill="#161b22"
        stroke="#30363d"
        stroke-width="1"/>

    <text
        x="6"
        y="14"
        fill="#ffffff"
        font-family="monospace"
        font-size="12"
        font-weight="bold">~/</text>

    <text
        x="38"
        y="15"
        fill="#ffffff"
        font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
        font-size="14"
        font-weight="600">
      Engineering Showcase &amp; Performance
    </text>

    <text
        x="868"
        y="14"
        text-anchor="end"
        fill="#8b949e"
        font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
        font-size="10.5">
      Cloud • Automation • Reliability • Projects
    </text>

    <line
        x1="0"
        y1="26"
        x2="868"
        y2="26"
        stroke="#21262d"
        stroke-width="1"/>

  </g>

  <!-- ===================================================== -->
  <!-- Production Focus -->
  <!-- ===================================================== -->

  <g transform="translate(24, 75)">

    <rect
        width="430"
        height="160"
        rx="8"
        fill="#161b22"
        stroke="#21262d"
        stroke-width="1"/>

    <text
        x="16"
        y="24"
        fill="#ffffff"
        font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
        font-size="14"
        font-weight="600">
      🚀 Production Focus
    </text>

    <text
        x="414"
        y="24"
        text-anchor="end"
        fill="#8b949e"
        font-family="monospace"
        font-size="10">
      BUILD → SHIP → OBSERVE
    </text>

    <line
        x1="16"
        y1="34"
        x2="414"
        y2="34"
        stroke="#30363d"
        stroke-width="1"/>

    <g transform="translate(16, 48)">
      {''.join(prod_svg)}
    </g>

  </g>

  <!-- ===================================================== -->
  <!-- GitHub Telemetry -->
  <!-- ===================================================== -->

  <g transform="translate(486, 75)">

    <rect
        width="430"
        height="160"
        rx="8"
        fill="#161b22"
        stroke="#21262d"
        stroke-width="1"/>

    <text
        x="16"
        y="24"
        fill="#ffffff"
        font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
        font-size="14"
        font-weight="600">
      ⚡ GitHub Telemetry
    </text>

    <text
        x="414"
        y="24"
        text-anchor="end"
        fill="#3fb950"
        font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
        font-size="10.5"
        font-weight="600">
      ● LIVE DATA
    </text>

    <line
        x1="16"
        y1="34"
        x2="414"
        y2="34"
        stroke="#30363d"
        stroke-width="1"/>

    <!-- Contributions -->

    <g transform="translate(16, 48)">

      <rect
          width="190"
          height="46"
          rx="6"
          fill="#0d1117"
          stroke="#30363d"
          stroke-width="1"/>

      <text
          x="12"
          y="20"
          fill="#ffffff"
          font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
          font-size="16"
          font-weight="bold">
        {metrics["total_year"]}
      </text>

      <text
          x="12"
          y="36"
          fill="#8b949e"
          font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
          font-size="10">
        Contributions / year
      </text>

    </g>

    <!-- Public repositories -->

    <g transform="translate(224, 48)">

      <rect
          width="190"
          height="46"
          rx="6"
          fill="#0d1117"
          stroke="#30363d"
          stroke-width="1"/>

      <text
          x="12"
          y="20"
          fill="#ffffff"
          font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
          font-size="16"
          font-weight="bold">
        {metrics["public_repos"]}
      </text>

      <text
          x="12"
          y="36"
          fill="#8b949e"
          font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
          font-size="10">
        Public repositories
      </text>

    </g>

    <!-- Stars -->

    <g transform="translate(16, 102)">

      <rect
          width="190"
          height="46"
          rx="6"
          fill="#0d1117"
          stroke="#30363d"
          stroke-width="1"/>

      <text
          x="12"
          y="20"
          fill="#ffffff"
          font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
          font-size="16"
          font-weight="bold">

        {metrics["total_stars"]}

        <tspan fill="#FFD700">★</tspan>

      </text>

      <text
          x="12"
          y="36"
          fill="#8b949e"
          font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
          font-size="10">
        Total GitHub stars
      </text>

    </g>

    <!-- Detected languages -->

    <g transform="translate(224, 102)">

      <rect
          width="190"
          height="46"
          rx="6"
          fill="#0d1117"
          stroke="#30363d"
          stroke-width="1"/>

      <text
          x="12"
          y="20"
          fill="#ffffff"
          font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
          font-size="16"
          font-weight="bold">

        {len(metrics["languages"])}

        <tspan fill="#39d353">+</tspan>

      </text>

      <text
          x="12"
          y="36"
          fill="#8b949e"
          font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
          font-size="10">
        Detected languages
      </text>

    </g>

  </g>

  <!-- ===================================================== -->
  <!-- Featured Engineering Projects -->
  <!-- ===================================================== -->

  <g transform="translate(24, 255)">

    <rect
        width="430"
        height="{language_card_height}"
        rx="8"
        fill="#161b22"
        stroke="#21262d"
        stroke-width="1"/>

    <text
        x="16"
        y="24"
        fill="#ffffff"
        font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
        font-size="14"
        font-weight="600">
      🚀 Featured Engineering Projects
    </text>

    <text
        x="414"
        y="24"
        text-anchor="end"
        fill="#8b949e"
        font-family="monospace"
        font-size="10">
      OPEN REPO ↗
    </text>

    <line
        x1="16"
        y1="34"
        x2="414"
        y2="34"
        stroke="#30363d"
        stroke-width="1"/>

    <g transform="translate(8, 48)">
      {''.join(project_svg)}
    </g>

  </g>

  <!-- ===================================================== -->
  <!-- Repository Language Spectrum -->
  <!-- ===================================================== -->

  <g transform="translate(486, 255)">

    <rect
        width="430"
        height="{language_card_height}"
        rx="8"
        fill="#161b22"
        stroke="#21262d"
        stroke-width="1"/>

    <text
        x="16"
        y="24"
        fill="#ffffff"
        font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
        font-size="14"
        font-weight="600">
      📊 Repository Language Spectrum
    </text>

    <text
        x="414"
        y="24"
        text-anchor="end"
        fill="#8b949e"
        font-family="monospace"
        font-size="10">
      PUBLIC REPOS
    </text>

    <line
        x1="16"
        y1="34"
        x2="414"
        y2="34"
        stroke="#30363d"
        stroke-width="1"/>

    <!-- Language bar -->

    <g transform="translate(16, 52)">

      <rect
          x="0"
          y="0"
          width="{bar_w}"
          height="{max(10, len(metrics["languages"]) * (language_bar_height + language_bar_gap) - language_bar_gap)}"
          rx="4"
          fill="#0d1117"
          stroke="#30363d"
          stroke-width="1"/>

      {''.join(segments)}

      <!-- ================================================= -->
      <!-- Dynamic white column separators -->
      <!-- ================================================= -->
      <!--
           X positions stay tied to the 3 language columns.
           Top begins below the language bar.
           Bottom grows automatically with the language rows.
      -->

      <g opacity="0.90">

  <!-- Separator between language columns -->
  <line
      x1="{legend_width - 2:.1f}"
      y1="{max(18, len(metrics["languages"]) * (language_bar_height + language_bar_gap) + 8):.1f}"
      x2="{legend_width - 2:.1f}"
      y2="{max(18, len(metrics["languages"]) * (language_bar_height + language_bar_gap) + 8) + legend_rows * row_height - 4:.1f}"
      stroke="#ffffff"
      stroke-width="1"/>

  <!-- Separator between language columns -->
  <line
      x1="{legend_width * 2 - 2:.1f}"
      y1="{max(18, len(metrics["languages"]) * (language_bar_height + language_bar_gap) + 8):.1f}"
      x2="{legend_width * 2 - 2:.1f}"
      y2="{max(18, len(metrics["languages"]) * (language_bar_height + language_bar_gap) + 8) + legend_rows * row_height - 4:.1f}"
      stroke="#ffffff"
      stroke-width="1"/>

</g>
      <!-- Language legend -->

      <g transform="translate(0, {max(18, len(metrics["languages"]) * (language_bar_height + language_bar_gap) + 8)})">
        {''.join(legend)}
      </g>

    </g>

  </g>

</svg>'''

    os.makedirs(
        os.path.dirname(output_path),
        exist_ok=True
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as f:
        f.write(svg)

    print(
        f"[Bento Showcase] Saved project-focused SVG to '{output_path}'"
    )


if __name__ == "__main__":
    generate_bento_svg()
