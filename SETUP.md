# 🚀 Quick Setup Guide

Get your own animated GitHub profile README in minutes. **You only edit 2 things — everything else is automated.**

---

## 📋 What You Do (3 Steps)

### Step 1 · Fork & Rename
1. Click the **Fork** button on this repository.
2. Rename the fork to match **your GitHub username exactly**.
   - Example: if your username is `octocat`, the repo must be `octocat/octocat`.

### Step 2 · Personalize (only 2 files to touch)

**① Drop your photo** at `assets/source-photo.jpg`
> Any portrait photo (JPG or PNG) works. The script will automatically remove the background, center your face, enhance lighting, and convert it into the animated dot-matrix portrait. Your source photo stays local — it's gitignored and never pushed to GitHub.

**② Edit `config.yml`** — this single file controls your entire profile:
```yaml
github_username: "your-github-username"
display_name: "Your Name"
headline: "🚀 Your Headline Here"
tagline: "Your Title • Your Specialty"

# These lines rotate in an animated typing effect under your name
typing_lines:
  - "First animated line"
  - "Second animated line"
  - "Third animated line"

bio: |
  A short 2-3 line summary about what you do.

links:
  linkedin: "https://www.linkedin.com/in/your-profile"
  x: "https://x.com/your-handle"
  email: "your-email@example.com"
  portfolio: "https://your-portfolio.com"

# These power the animated Skill Radar chart
skills:
  - name: "Skill Name"
    level: 85          # 0-100 percentage
    category: "Category"

# Icon rows from skillicons.dev
tech_stack:
  - category: "Category Name"
    icons: "react,python,typescript"

# Customises the 2x2 Bento Engineering Showcase
bento:
  production_focus:
    - title: "📱 What You Build"
      desc: "Short description of your primary output"
    - title: "🧠 Technical Focus"
      desc: "Your core technical domain"
    - title: "🌐 Stack"
      desc: "Your primary stack and tools"
  milestones:
    - badge: "🏆 Achievement One"
      desc: "Brief description"
    - badge: "🚀 Achievement Two"
      desc: "Brief description"
    - badge: "🔄 Achievement Three"
      desc: "Brief description"

# Portrait rendering settings
portrait:
  source_image: "assets/source-photo.jpg"
  grid_spacing_px: 8        # smaller = more dots/detail (6-14)
  canvas_size_px: 1000      # canvas resolution
  color_palette: "original" # "original", "monochrome", or "duotone"
  reveal_style: "rows"      # "rows" | "columns" | "diagonal"
```

### Step 3 · Generate & Push

```bash
# Install dependencies (one time only)
pip install -r requirements.txt

# Generate everything — one command does it all
python scripts/generate_portrait.py

# Preview locally before pushing (opens in browser)
python scripts/preview.py

# When you're happy with the preview, push to GitHub
git add assets/ README.md config.yml
git commit -m "feat: personalize profile"
git push origin main
```

**That's it.** Visit `https://github.com/<your-username>` to see your live profile. 🎉

---

## ⚡ Live Auto-Updates vs. Static (Optional)

By default, your profile is **static** — the SVGs capture your metrics at the time of generation.

* **Option A: Manual Updates (Default — no setup required)**:
  Whenever you push new code or want to refresh your numbers, simply re-run:
  ```bash
  python scripts/generate_portrait.py
  git add assets/ README.md config.yml
  git commit -m "chore: refresh profile metrics"
  git push origin main
  ```

* **Option B: Automatic Background Updates (GitHub Actions — 100% Free)**:
  The repository already comes with `.github/workflows/update-profile.yml` pre-configured. To enable it so GitHub automatically refreshes your contribution graph and telemetry every 12 hours:
  1. In your repository on GitHub, go to **Settings** → **Actions** → **General**.
  2. Under **Workflow permissions**, select **"Read and write permissions"** and click **Save**.
  3. Go to the **Actions** tab on GitHub and click **"I understand my workflows, go ahead and enable them"** (if prompted).
  
  *That's it! GitHub will now auto-update your stats twice daily in the background. If you prefer to keep everything manual, you don't need to do anything at all.*

---

## 🔄 How the Generator Works

You only ever run **one command**: `python scripts/generate_portrait.py`

It automatically chains all 5 scripts in order:

```
config.yml + source-photo.jpg
        │
        ▼
┌──────────────────────────┐
│  generate_portrait.py    │  Removes background, enhances lighting,
│  (entry point)           │  converts photo → animated dot-matrix SVG
└──────────┬───────────────┘
           │ calls ▼
┌──────────────────────────┐
│  generate_skills_svg.py  │  Reads skills: from config.yml →
│                          │  generates animated radar chart SVG
└──────────┬───────────────┘
           │ calls ▼
┌──────────────────────────────┐
│ generate_contributions_svg.py│  Fetches live contributions from GitHub →
│                              │  generates animated activity flow SVG
└──────────┬───────────────────┘
           │ calls ▼
┌──────────────────────────────┐
│ generate_bento_svg.py        │  Native GitHub metrics + milestones →
│                              │  generates 2x2 Bento Showcase SVG
└──────────┬───────────────────┘
           │ calls ▼
┌──────────────────────────┐
│  render_readme.py        │  Fills {{ placeholders }} in the template
│                          │  with your config data → generates README.md
└──────────────────────────┘

Then optionally:
┌──────────────────────────┐
│  preview.py              │  Renders README.md as GitHub Dark Mode HTML
│  (run separately)        │  with embedded SVGs → preview.html
└──────────────────────────┘
```

**You never edit any Python files or the template.** Everything flows from `config.yml`.

---

## 🎨 Customizing the Portrait

Adjust the portrait look anytime in `config.yml` under `portrait:`:

| Setting | Options | Description |
| :--- | :--- | :--- |
| `color_palette` | `original`, `monochrome`, `duotone` | Sample colors from photo, grayscale, or custom two-tone |
| `duotone_light` | Hex code (e.g. `#60a5fa`) | Highlight color in duotone mode |
| `duotone_dark` | Hex code (e.g. `#0f172a`) | Shadow color in duotone mode |
| `reveal_style` | `rows`, `columns`, `diagonal` | Draw-in animation pattern |
| `grid_spacing_px` | `6` to `14` | Dot density (smaller = sharper, larger = minimalist) |

After any change, just rerun: `python scripts/generate_portrait.py`

---

## 📁 Project Structure

```
your-username/
├── .github/
│   └── workflows/
│       └── update-profile.yml      # Auto-refreshes metrics on a schedule (every 12h)
├── config.yml                      # ← EDIT THIS to personalize everything
├── assets/
│   ├── source-photo.jpg            # ← DROP YOUR PHOTO HERE (gitignored, stays local)
│   ├── portrait.svg                # Auto-generated dot-matrix portrait
│   ├── skills.svg                  # Auto-generated skill radar chart
│   ├── contributions.svg           # Auto-generated live activity flow
│   └── bento.svg                   # Auto-generated 2x2 Bento Showcase
├── templates/
│   └── README.template.md          # Layout template (don't edit)
├── scripts/
│   ├── generate_portrait.py        # Entry point — runs all generators
│   ├── generate_skills_svg.py      # Generates skill radar from config
│   ├── generate_contributions_svg.py# Generates live contribution graph
│   ├── generate_bento_svg.py       # Generates 2x2 Bento Showcase
│   ├── render_readme.py            # Fills template → README.md
│   └── preview.py                  # Generates local preview HTML
├── README.md                       # Auto-generated (don't edit directly)
├── requirements.txt                # Python dependencies
├── SETUP.md                        # This guide
└── .gitignore                      # Excludes preview.html, source photo, cache
```

---

## ❓ FAQ

**Q: Does my profile update automatically when I push new code to other repos?**
> Yes! The included GitHub Actions workflow (`update-profile.yml`) runs automatically every 12 hours (and whenever you edit `config.yml`) to fetch your latest contribution calendar and metrics, updating the SVGs in your repository with zero manual work. You can also trigger an instant refresh anytime from the **Actions** tab by clicking **Run workflow**.

**Q: Where does the contribution data come from?**
> Everything is pulled directly from GitHub's own native contribution calendar and public API — not from any third-party Vercel proxy. This means zero rate limits, zero HTTP 402 payment errors, and 100% uptime.

**Q: Can I change which languages appear in the Bento Language Spectrum?**
> The language data comes from your actual public repositories via the GitHub API — it reflects real bytes of code. Jupyter Notebook (`.ipynb`) is excluded by default because its JSON cell output bloats byte counts artificially. If you want to manually adjust the `lang_totals` fallback, edit `scripts/generate_bento_svg.py` lines 40–45.

**Q: The preview shows broken images.**
> Run `python scripts/preview.py` to regenerate it. The preview embeds all SVGs as base64 so it works offline.

**Q: Do I need to edit any Python files or the template?**
> No. Everything is driven by `config.yml`. The scripts and template are generic — they work for any user without modification.

