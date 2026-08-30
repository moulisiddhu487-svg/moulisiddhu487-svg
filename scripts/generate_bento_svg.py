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
    """Fetch live metrics for exactly the configured GitHub account.

    This function fails closed: if GitHub identity/repository/language data
    cannot be verified completely, the caller must not overwrite bento.svg.
    """

    if not username or username == "octocat":
        raise RuntimeError(
            "A real GitHub username is required; refusing to use octocat."
        )

    api_headers = dict(GITHUB_HEADERS)
    api_headers["User-Agent"] = "mouli-profile-bento"

    def github_json(url, timeout=8):
        req = urllib.request.Request(
            url,
            headers=api_headers
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))

    total_year = "SYNC"

    try:
        url = f"https://github.com/users/{username}/contributions"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "mouli-profile-bento"}
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

    # ---------------------------------------------------------
    # Verify the GitHub account before reading any metrics.
    # ---------------------------------------------------------

    profile = github_json(
        f"https://api.github.com/users/{username}",
        timeout=8
    )

    actual_login = str(profile.get("login", "")).strip()

    if actual_login.lower() != username.lower():
        raise RuntimeError(
            f"GitHub identity mismatch: requested '{username}', "
            f"received '{actual_login or 'unknown'}'."
        )

    if profile.get("type") != "User":
        raise RuntimeError(
            f"GitHub account '{username}' is not a normal user account."
        )

    # ---------------------------------------------------------
    # Public repositories OWNED by this exact account.
    #
    # type=owner prevents unrelated/member repositories and avoids
    # accidentally counting repositories from another account.
    # Pagination keeps the data correct if the account grows past 100 repos.
    # ---------------------------------------------------------

    repos = []
    page = 1

    while True:
        repos_url = (
            f"https://api.github.com/users/{username}/repos"
            f"?per_page=100&page={page}&type=owner&sort=updated"
        )

        page_repos = github_json(repos_url, timeout=8)

        if not isinstance(page_repos, list):
            raise RuntimeError(
                f"Unexpected repository response for '{username}'."
            )

        repos.extend(page_repos)

        if len(page_repos) < 100:
            break

        page += 1

        # Safety guard against an unexpected API loop.
        if page > 20:
            raise RuntimeError(
                "Repository pagination exceeded the safety limit."
            )

    # Keep only public repositories owned by the verified account.
    verified_repos = []

    for repo in repos:
        owner_login = str(
            repo.get("owner", {}).get("login", "")
        ).strip()

        if owner_login.lower() != actual_login.lower():
            raise RuntimeError(
                f"Repository owner mismatch for '{repo.get('name', 'unknown')}'."
            )

        if repo.get("private") is False:
            verified_repos.append(repo)

    total_stars = sum(
        int(repo.get("stargazers_count", 0) or 0)
        for repo in verified_repos
    )

    public_repos_count = len(verified_repos)

    # ---------------------------------------------------------
    # Real GitHub language byte totals.
    # ---------------------------------------------------------

    lang_totals = {}
    language_fetch_failures = []

    for repo in verified_repos:
        name = repo.get("name")

        if not name:
            continue

        lang_url = (
            f"https://api.github.com/repos/"
            f"{actual_login}/{name}/languages"
        )

        try:
            langs = github_json(lang_url, timeout=8)

            if not isinstance(langs, dict):
                raise RuntimeError("Unexpected language response.")

            for lang, count in langs.items():
                lang_totals[lang] = (
                    lang_totals.get(lang, 0) + int(count)
                )

        except Exception as e:
            language_fetch_failures.append(
                f"{name}: {e}"
            )

    if language_fetch_failures:
        raise RuntimeError(
            "Could not fetch language data for every repository. "
            "Refusing to publish incomplete language metrics. "
            + "; ".join(language_fetch_failures)
        )

    if not lang_totals:
        # A profile with public repositories but no detectable source
        # languages is valid; keep the language list empty.
        total_bytes = 1
    else:
        total_bytes = sum(lang_totals.values())

    # ---------------------------------------------------------
    # GitHub Linguist colors.
    # ---------------------------------------------------------

    language_colors = {}

    try:
        linguist_url = (
            "https://raw.githubusercontent.com/"
            "github-linguist/linguist/"
            "main/lib/linguist/languages.yml"
        )

        linguist_req = urllib.request.Request(
            linguist_url,
            headers={"User-Agent": "mouli-profile-bento"}
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

    # This repository belongs to this GitHub account.
    # If config.yml later gets a github_username entry, it must match.
    configured_username = config.get("github_username")
    username = configured_username or "moulisiddhu487-svg"

    if username.lower() != "moulisiddhu487-svg":
        raise RuntimeError(
            "github_username must be 'moulisiddhu487-svg' "
            "so this profile can never display another account's data."
        )

    metrics = fetch_bento_metrics(username)

    bento_cfg = config.get("bento", {})

    prod_items = bento_cfg.get(
        "production_focus",
        []
    )[:3]

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
    # Repository Language Spectrum
    # ---------------------------------------------------------
    #
    # Each GitHub language gets its own horizontal bar.
    # Every bar starts at the same 0% point.
    # Rows are shown from lowest percentage to highest.
    # GitHub percentages and GitHub Linguist colors are untouched.
    # ---------------------------------------------------------

    segments = []

    language_count = len(metrics["languages"])

    # One row per language. This automatically grows with GitHub data.
    language_row_height = 18
    language_row_gap = 5
    language_bar_height = 12
    language_bar_width = 650

    # Lowest percentage first, highest percentage last.
    display_languages = sorted(
        metrics["languages"],
        key=lambda lang: lang["pct"]
    )

    for idx, lang in enumerate(display_languages):

        pct = float(lang["pct"])

        bar_width = (
            pct / 100.0
        ) * language_bar_width

        y = idx * (
            language_row_height
            + language_row_gap
        )

        if bar_width <= 0:
            continue

        # Actual percentage width. Every bar starts at x=0.
        segments.append(
            f'''
        <rect
            x="0"
            y="{y:.1f}"
            width="{bar_width:.1f}"
            height="{language_bar_height}"
            rx="4"
            fill="{lang["color"]}"/>
        '''
        )

        pct_text = f'{pct:.1f}%'

        # Percentage sits immediately after the colored portion.
        pct_x = bar_width + 7

        segments.append(
            f'''
        <text
            x="{pct_x:.1f}"
            y="{y + 7.4:.1f}"
            fill="#e6edf3"
            font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
            font-size="9.5"
            font-weight="700">{pct_text}</text>
        '''
        )

        # Language name is kept in one fixed column at the right side
        # of the language area, outside every colored bar.
        # This keeps all language names perfectly aligned.
        name_x = language_bar_width + 14

        segments.append(
            f'''
        <text
            x="{name_x:.1f}"
            y="{y + 7.4:.1f}"
            fill="#e6edf3"
            font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
            font-size="10.5"
            font-weight="700">{html.escape(lang["name"])}</text>
        '''
        )

    # Total vertical space occupied by the automatically generated rows.
    language_bar_area_height = max(
        language_bar_height,
        language_count * (
            language_row_height
            + language_row_gap
        ) - language_row_gap
    )

    # ---------------------------------------------------------
    # Dynamic Card Height
    # ---------------------------------------------------------
    #
    # The card grows when GitHub returns more language rows.
    # There is NO footer anymore.
    #

    # Card height follows the number of GitHub languages.
    # More languages = more rows = taller card.
    language_card_height = max(
        190,
        84
        + language_bar_area_height
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
  <!-- Repository Language Spectrum -->
  <!-- ===================================================== -->

  <g transform="translate(24, 255)">

    <rect
        width="892"
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
        x="876"
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
        x2="876"
        y2="34"
        stroke="#30363d"
        stroke-width="1"/>

    <g transform="translate(16, 52)">
      {''.join(segments)}
    </g>

  </g>
</svg>'''

    os.makedirs(
        os.path.dirname(output_path),
        exist_ok=True
    )

    with open(
        output_pa
