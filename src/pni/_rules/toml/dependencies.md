# Manifest & Config Governance Standards (TOML)

## Core Principles
1. **Standardized Tool Manifests (`pyproject.toml`, `Cargo.toml`, `mise.toml`)**: Consolidate tool configurations (Ruff, pytest, mypy, ty, coverage, Clippy) into canonical project TOML files (`pyproject.toml` PEP 621 / `Cargo.toml`) rather than scattering dozens of legacy dotfiles (`setup.cfg`, `.flake8`, `.isort.cfg`).
2. **Zero-Lockfile Exemption**: Standalone TOML config repositories do **not** require a package lockfile; when TOML serves as a language manifest (`pyproject.toml`, `Cargo.toml`, `alire.toml`, `fpm.toml`), follow that language's lockfile rules.
3. **Template vs. Secret Separation**: Commit `config.example.toml` with safe defaults and `.gitignore` environment-specific `secrets.toml` / `.streamlit/secrets.toml`.
4. **Automated Validation & Secret Scanning**: Validate TOML files in CI with `taplo check` / `tomllib` and Trivy secret scanning.

## Evaluation Thresholds
- **`PASS`**: Consolidated canonical TOML manifests, clean example-vs-ignored-secrets split, and zero committed credential TOML files.
- **`WARN`**: Fragmented legacy dotfiles alongside `pyproject.toml`.
- **`FAIL`**: Committed `secrets.toml` / credentials or broken project manifest schemas.
