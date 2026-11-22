# pni501 Documentation & Sample Reports Portal (`docs_src/` -> `docs/`)

This directory is the **Single Source of Truth (SSOT)** for the official **`pni501` (Project Nemesis Index)** bilingual (`en` + `ja`) website and published sample audit / migration reports served on GitHub Pages at **[https://www.pni501.com](https://www.pni501.com)**.

> **Source of Truth**: Edit only files inside `docs_src/`. Never manually edit compiled HTML/PDF artifacts in `docs/`.

---

## Directory Layout

```text
docs_src/
├── build.sh                                # Master build: site + all sample reports + portal link check
├── serve.sh                                # Local preview server on docs/
├── site/                                   # Official bilingual site (drawlib type = "site") -> docs/
│   ├── drawlib.toml
│   ├── en/
│   └── ja/
└── reports/                                # Published PNI Workflow v2 sample reports -> docs/reports/<slug>/
    ├── py_api_fastapi_clean/               # drawlib.toml + _facts/*.json + en/*.md + ja/*.md
    ├── java_api_spring_messy/              # drawlib.toml + _facts/*.json + en/*.md + ja/*.md
    ├── java_api_spring_messy_migration/    # drawlib.toml + _facts/*.json + en/*.md + ja/*.md
    └── php_wp_plugin_messy/                # drawlib.toml + _facts/*.json + en/*.md + ja/*.md
```

Each report under `docs_src/reports/<slug>/` compiles into `docs/reports/<slug>/`:
- `index.html`, `en/index.html`, `ja/index.html` (bilingual interactive HTML report)
- `<slug>_en.pdf`, `<slug>_ja.pdf`, `<slug>.pdf` (A4 vector PDFs with Table of Contents)
- `<slug>_score.json` (v2.0), `<slug>_summary.json`, `<slug>_findings.sarif` (or `<slug>_migration_plan.json`)

---

## Building & Verifying

```bash
# Build site + all sample reports + verify zero broken links across docs/
./docs_src/build.sh

# Launch local preview server (http://127.0.0.1:8000)
./docs_src/serve.sh
```
