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
