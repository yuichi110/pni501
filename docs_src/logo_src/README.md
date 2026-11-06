# pni501 Logo Project

This directory contains the standalone Python scripts that generate the official pni501 brand logos (`docs_src/logo/`) using Drawlib ("Illustration as Code").

---

## 1. Directory Structure

- `logo_src/`: Source Python illustration scripts (**Source of Truth**).
  - `_assets/`: Bundled `Bodoni Moda` (`bodoni_moda_bold.ttf`, `bodoni_moda_regular.ttf`) fonts and [`OFL.txt`](_assets/OFL.txt) licensed under SIL Open Font License 1.1.
  - `build.sh` / `build_image.sh`: Build scripts to execute drawing scripts and generate images in `docs_src/logo/`.
  - `styles.py`: Global styles script (Cyber Teal `#05A8AB` and Bodoni Moda Didone serif typography).
  - `utils.py`: Reusable logo drawing functions (`draw_logo`, `draw_logo_icon`).
  - `logo.py` / `logo_transparent.py`: Official horizontal brand logo `PROJECT [△ NI] 501` (`docs_src/logo/logo.png`, `docs_src/logo/logo_transparent.png`).
  - `logo_dark.py` / `logo_dark_transparent.py`: Official horizontal brand logo for dark backgrounds.
  - `logo_icon.py` / `logo_icon_transparent.py`: Standalone icon mark `△ PNI 501` (`docs_src/logo/logo_icon.png`, `docs_src/logo/logo_icon_transparent.png`).
  - `logo_icon_dark.py` / `logo_icon_dark_transparent.py`: Standalone icon mark for dark backgrounds.
  - `favicon.py`: Official rounded white-card favicon for browsers and tabs (`docs_src/logo/favicon.png`).
- `logo/`: Generated logo images directory (**Do not edit directly**).

---

## 2. Building Logo Images

Run the build script from `docs_src/` or inside `docs_src/logo_src/`:

```bash
./docs_src/logo_src/build.sh
```

Or via Drawlib CLI directly:

```bash
uv run drawlib build image docs_src/logo_src/ -o docs_src/logo/
```
