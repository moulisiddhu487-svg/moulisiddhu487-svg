#!/usr/bin/env python3
"""
scripts/render_readme.py
Renders README.md using config.yml and templates/README.template.md.
Formats links, badges, tech stack, and sections in a cohesive Monochrome Dark theme.
"""

import os
import yaml

BADGE_CONFIGS = {
    "linkedin": {
        "label": "LinkedIn",
        "color": "0A66C2",
        "logo": "linkedin",
        "logo_color": "ffffff"
    },
    "x": {
        "label": "X",
        "color": "161b22",
        "logo": "x",
        "logo_color": "ffffff"
    },
    "twitter": {
        "label": "Twitter",
        "color": "161b22",
        "logo": "twitter",
        "logo_color": "ffffff"
    },
    "email": {
        "label": "Email",
        "color": "EA4335",
        "logo": "gmail",
        "logo_color": "ffffff"
    },
    "portfolio": {
        "label": "Portfolio",
        "color": "00A86B",
        "logo": "safari",
        "logo_color": "ffffff"
    },
    "website": {
        "label": "Website",
        "color": "161b22",
        "logo": "google-chrome",
        "logo_color": "ffffff"
    },
    "github": {
        "label": "GitHub",
        "color": "181717",
        "logo": "github",
        "logo_color": "ffffff"
    }
}


def load_config(config_path="config.yml"):
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def format_link_badges(links):
    if not links:
        return ""
    
    badge_tags = []
    for key, url in links.items():
        if not url:
            continue
        key_lower = key.lower().strip()
        target_url = url
        if key_lower == "email" and not target_url.startswith("mailto:"):
            target_url = f"mailto:{target_url}"

        badge_info = BADGE_CONFIGS.get(key_lower, {
            "label": key.capitalize(),
            "color": "161b22",
            "logo": "link",
            "logo_color": "ffffff"
        })

        badge_url = (
            f"https://img.shields.io/badge/{badge_info['label']}-{badge_info['color']}"
            f"?style=for-the-badge&logo={badge_info['logo']}&logoColor={badge_info['logo_color']}"
        )
        badge_tag = (
            f'<a href="{target_url}" target="_blank">\n'
            f'    <img src="{badge_url}" height="30" alt="{badge_info["label"]}"/>\n'
            f'  </a>'
        )
        badge_tags.append(badge_tag)

    return "\n  &nbsp;\n  ".join(badge_tags)


def format_tech_stack(tech_stack):
    if not tech_stack:
        return ""
    
    rows = []
    for item in tech_stack:
        category = item.get("category", "")
        icons = item.get("icons", "")
        rows.append(f'| **{category}** | <img src="https://skillicons.dev/icons?i={icons}&theme=dark" /> |')

    table_body = "\n".join(rows)
    return (
        "\n---\n\n"
        "### 🛠️ Core Tooling & Technologies\n\n"
        '<div align="center">\n\n'
        "| **Category** | **Technologies** |\n"
        "| :--- | :--- |\n"
        f"{table_body}\n\n"
        "</div>\n"
    )


def format_human_side(human_side):
    if not human_side:
        return ""
    
    items = []
    for item in human_side:
        title = item.get("title", "")
        desc = item.get("desc", "")
        items.append(f"* **{title}:** {desc}")

    body = "\n".join(items)
   return (
    "\n---\n\n"
    "### 🌐 Beyond the Terminal\n\n"
    "I enjoy staying curious beyond day-to-day engineering and continuously exploring new ways to learn, create, and recharge.\n\n"
    f"{body}\n"
)


def format_typing_svg(typing_lines):
    """Generate a readme-typing-svg URL from a list of text lines."""
    if not typing_lines:
        return ""
    import urllib.parse
    encoded_lines = ";".join(
        urllib.parse.quote(line, safe="") for line in typing_lines
    )
    url = (
        f"https://readme-typing-svg.demolab.com?font=Fira+Code&size=16"
        f"&pause=1000&color=FFFFFF&center=true&vCenter=true"
        f"&width=500&height=36&lines={encoded_lines}"
    )
    return f'<img src="{url}" alt="Typing Subtitle" />'


def format_featured_projects(projects):
    if not projects:
        return ""

    parts = ["\n\n### 🚀 Featured Projects\n"]

    for project in projects:
        name = project.get("name", "Project")
        desc = project.get("description", "")
        links = []

        if project.get("api_url"):
            links.append(f'[Live API]({project["api_url"]})')

        if project.get("repo_url"):
            links.append(f'[GitHub Repository]({project["repo_url"]})')

        suffix = " • ".join(links)

        if suffix:
            parts.append(f"**{name}**  \n{desc}  \n{suffix}\n")
        else:
            parts.append(f"**{name}**  \n{desc}\n")

    parts.append("*Explore the implementation and source code through the links above.*")
    return "\n".join(parts)

def format_profile_details(education, certifications):
    if not education and not certifications:
        return ""
    parts = ["\n---\n\n### 🎓 Education & Certification\n"]
    for item in education or []:
        parts.append(f"* {item}")
    for item in certifications or []:
        parts.append(f"* 🏅 {item}")
    return "\n".join(parts) + "\n"


def render_readme(config_path="config.yml", template_path="templates/README.template.md", output_path="README.md"):
    config = load_config(config_path)

    github_username = config.get("github_username", "octocat")
    display_name = config.get("display_name", "Developer")
    headline = config.get("headline", "🚀 Building Cool Stuff")
    tagline = config.get("tagline", "")
    bio = config.get("bio", "").strip()
    links = config.get("links", {})
    tech_stack = config.get("tech_stack", [])
    human_side = config.get("human_side", [])
    typing_lines = config.get("typing_lines", [])
    footer_text = config.get("footer_text", "Let's build something incredible together.")
    featured_projects = config.get("featured_projects", [])
    education = config.get("education", [])
    certifications = config.get("certifications", [])

    links_badges = format_link_badges(links)
    tech_stack_section = format_tech_stack(tech_stack)
    human_side_section = format_human_side(human_side)
    featured_projects_section = format_featured_projects(featured_projects)
    profile_details_section = format_profile_details(education, certifications)
    typing_svg = format_typing_svg(typing_lines)

    if os.path.exists(template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            template_content = f.read()
    else:
        template_content = "{{ display_name }}\n{{ bio }}"

    rendered = template_content
    rendered = rendered.replace("{{ github_username }}", github_username)
    rendered = rendered.replace("{{ display_name }}", display_name)
    rendered = rendered.replace("{{ headline }}", headline)
    rendered = rendered.replace("{{ tagline }}", tagline)
    rendered = rendered.replace("{{ bio }}", bio)
    rendered = rendered.replace("{{ links_badges }}", links_badges)
    rendered = rendered.replace("{{ tech_stack_section }}", tech_stack_section)
    rendered = rendered.replace("{{ human_side_section }}", human_side_section)
    rendered = rendered.replace("{{ featured_projects_section }}", featured_projects_section)
    rendered = rendered.replace("{{ profile_details_section }}", profile_details_section)
    rendered = rendered.replace("{{ typing_svg }}", typing_svg)
    rendered = rendered.replace("{{ footer_text }}", footer_text)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(rendered)

    print(f"[README] Rendered README.md successfully from '{config_path}'")


if __name__ == "__main__":
    render_readme()
