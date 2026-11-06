# pni501 (Project Nemesis Index)

**Project Nemesis Index (PNI)** evaluates software development project health and generates diagnostic reports to help engineering teams identify risks, maintain architectural integrity, and improve delivery velocity.

---

## Overview

Software projects naturally accumulate friction—technical debt, uneven test coverage, stagnant dependencies, architectural drift, and workflow bottlenecks. **PNI (Project Nemesis Index)** analyzes software repositories to produce quantifiable health scores and actionable reports.

- **Package Name (PyPI)**: `pni501`
- **Import Module**: `pni`
- **CLI Command**: `pni`
- **Developer Management Tool**: `./pcli`

---

## Installation

Install via `pip`:

```bash
pip install pni501
```

Or using `uv`:

```bash
uv add pni501
```

---

## Quickstart

Verify the installation:

```bash
pni version
```

Display CLI options and help:

```bash
pni --help
```

Initialize PNI in a repository and run a stateful workflow:

```bash
pni init
pni workflows list
pni workflows start full_audit
```

---

## Documentation (`docs_src/`)

Comprehensive architectural and mechanism documentation for `pni501` is maintained as a **Drawlib `doc` project** inside [`docs_src/`](docs_src/README.md):

- **Source of Truth**: `docs_src/doc_src/en/` (`00_cover.md` – `06_scoring_and_drawlib_reporter.md`, configured via `docs_src/doc_src/drawlib.toml`)
- **Compiled HTML**: `docs_src/doc_html/index.html` (`docs_src/doc_html/en/index.html`)
- **Printable A4 Vector PDF**: `docs_src/doc.pdf`
- **GitHub-Flavored Markdown**: `docs_src/doc_markdown/`
- **Rebuild Command**: `./docs_src/doc_src/build.sh` (or `uv run pni report build doc --src-dir docs_src --output-dir docs_src`)

---

## Development

This project is managed with `uv` and uses `./pcli` (`tools/pcli`) for development workflows.

### 1. Shell Setup

Run `./pcli` to inspect available toolsets or source it to enable dynamic autocompletion:

```bash
./pcli                    # Display available toolsets
source ./pcli             # Register 'pcli' shell alias & autocompletion
```

### 2. Available Toolsets

| Toolset | Command | Description |
| :--- | :--- | :--- |
| **`code-check`** | `./pcli code-check all [--fix]` | Ruff linting & formatting, Ty static type checking |
| **`test`** | `./pcli test all [--cov]` | Run pytest unit tests with coverage |
| **`pypi`** | `./pcli pypi check-version` | Verify versions, inspect dependencies & publish |

```bash
# Code Quality
./pcli code-check lint [--fix]
./pcli code-check type
./pcli code-check lines
./pcli code-check all

# Testing
./pcli test all
./pcli test pni
./pcli test pcli

# PyPI Management
./pcli pypi check-version
./pcli pypi publish --test-pypi
./pcli pypi publish
```

---

## License

This project is licensed under the Apache 2.0 License. See [LICENSE](LICENSE) for details.