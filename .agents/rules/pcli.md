---
trigger: always_on
---

# Development CLI (pcli) for pni501

All routine development operations—static analysis, testing, code quality checks, and PyPI publishing—are managed via `./pcli` (`tools/pcli/`, built with Python + Typer + Rich).

Always use `./pcli` instead of running raw tool commands manually.

---

## 1. Quick Overview & Shell Setup

Run `./pcli` with no arguments to display the summary table of all toolsets:

```bash
./pcli                    # Display available toolsets table
source ./pcli             # Register 'pcli' alias and dynamic Tab autocompletion in current shell
```

| Toolset | Module (`tools/pcli/`) | Primary Purpose |
| :--- | :--- | :--- |
| **`code-check`** | `code_check/` | Code quality & static analysis (Ruff lint/format, Ty type check, line count) |
| **`test`** | `test.py` | Unit test execution via pytest + coverage + xdist parallelization |
| **`pypi`** | `pypi/` | Dependency auditing, version checks, and TestPyPI/PyPI publishing |

---

## 2. Toolset Reference

### 2.1. `code-check` — Code Quality & Static Analysis
```bash
./pcli code-check all [--fix]       # Run lint and type checks in sequence
./pcli code-check lint [--fix]      # Run Ruff linter & formatter on src/, tests/, tools/
./pcli code-check type              # Run Ty static type checker on src/pni, tests/, tools/
./pcli code-check lines             # Count and display source and test code lines
```

### 2.2. `test` — Test Execution & Coverage
```bash
./pcli test all [--cov/--no-cov] [--cov-report] [--parallel/--no-parallel]
./pcli test pni [--cov/--no-cov] [--cov-report] [--parallel/--no-parallel]
./pcli test pcli [--cov/--no-cov]
./pcli test target <shortcut_or_path> [--cov] [--cov-report] [--parallel]
```

### 2.3. `pypi` — Dependency & PyPI Release Management
```bash
./pcli pypi deps                                     # Show dependencies in pyproject.toml
./pcli pypi dep-releases <package> [--from YEAR]     # Query PyPI release history for a package
./pcli pypi list-versions [--test-pypi]              # List all published pni501 versions
./pcli pypi latest [--test-pypi]                     # Show latest published version
./pcli pypi check-version [--allow-jump] [--test-pypi]
./pcli pypi publish [--allow-jump] [--test-pypi]     # Build and publish package to TestPyPI or PyPI
```