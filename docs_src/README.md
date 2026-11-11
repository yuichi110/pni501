# pni501 Official Documentation Website (`drawlib site`)

This directory contains the source Markdown pages, embedded Drawlib Python diagrams, and shared styling assets for the official **`pni501` (Project Nemesis Index)** bilingual (`en` + `ja`) documentation website published at **[https://www.pni501.com](https://www.pni501.com)**.

> **Source of Truth**: Edit only files inside `docs_src/`. Never manually edit the compiled HTML files in `docs/`.

---

## 1. Directory Structure

```text
docs_src/
├── drawlib.toml                         # Project manifest (type = "site", style = "default", [i18n] en/ja, [seo])
├── styles.py                            # Global Drawlib style & color tokens (DefaultStyles / DefaultColors)
├── utils.py                             # Reusable drawing helper functions (`service_card`, `connect`)
├── style.css                            # Responsive sidebar & documentation page stylesheet
├── template.html                        # Jinja2 multi-page HTML layout template
├── _assets/                             # Official pni501 brand logos & browser tab favicon
│   ├── logo.png
│   ├── logo_dark.png
│   └── favicon.png
├── build.sh                             # Master build script (compiles HTML into ../docs/)
├── build_html.sh                        # Compiles docs_src/ -> ../docs/ and preserves CNAME & .nojekyll
├── build_markdown.sh                    # Optional GitHub-flavored Markdown export (../docs_markdown/)
├── build_image.sh                       # Optional standalone diagram image export (../docs_images/)
├── serve.sh                             # Local preview server & link checker (`drawlib serve ../docs/ --check`)
├── en/                                  # English documentation pages (default_lang = "en")
│   ├── navbar.md                        # Sidebar navigation hierarchy
│   ├── index.md                         # Home / Overview
│   ├── 01_getting_started/              # Background & Core Concepts, Quickstart, Use Cases, Release Notes
│   ├── 02_architecture/                 # Domain Architecture & Cascade, Stateful Pull-Push Engine
│   ├── 03_workflows_and_actions/        # Workflows & Pre-Flight Gates, 15 Actions & 12 Primitives, Analyzers & Pentest
│   ├── 04_scoring_and_reports/          # 7-Axis Scoring Model, Drawlib Visual Reporter
│   └── 05_languages_and_reference/      # Supported 6 Languages, Rules & CLI Reference
└── ja/                                  # Japanese documentation pages (strict skeleton & diagram parity with en/)
    ├── navbar.md
    ├── index.md
    ├── 01_getting_started/
    ├── 02_architecture/
    ├── 03_workflows_and_actions/
    ├── 04_scoring_and_reports/
    └── 05_languages_and_reference/
```

---

## 2. Building & Verifying

From the repository root:

```bash
# Compile static HTML website into docs/ (preserves docs/CNAME and docs/.nojekyll)
./docs_src/build.sh

# Verify zero broken links or missing assets in compiled docs/
uv run drawlib serve docs/ --check

# Launch local preview server
./docs_src/serve.sh
```
