# External Tool & Build Dependency Standards (Makefile)

## Core Principles
1. **Explicit Tool Preflight & Overridable Binaries**: Parameterize external commands (`CC ?= gcc`, `PYTHON ?= uv run python`, `DOCKER ?= docker`) so developers and CI can override toolchains cleanly, and verify non-standard CLI tools exist before executing complex pipelines.
2. **Zero-Lockfile Exemption**: Makefiles do **not** have a package lockfile — do **NOT** penalize Make repos for lacking one; instead check that Make recipes invoke language package managers cleanly using committed project lockfiles (`uv sync --frozen`, `npm ci`, `cargo build --locked`).
3. **Declare Real File Prerequisites**: List real source/header inputs as prerequisites on build targets (rather than running everything unconditionally as `.PHONY`) so incremental builds stay fast and accurate.
4. **POSIX vs GNU Make Clarity**: Name GNU-specific files `GNUmakefile` or document GNU Make `>= 4.0` requirement when relying on GNU extensions (`.ONESHELL`, `.SHELLFLAGS`, `$(abspath ...)`).

## Evaluation Thresholds
- **`PASS`**: Overridable toolchain variables, lockfile-honoring build recipes, real file prerequisites, and clear GNU/POSIX compatibility.
- **`WARN`**: Hardcoded tool paths (`/usr/local/bin/...`) or undocumented GNU Make 4+ requirements.
- **`FAIL`**: Recipes bypassing lockfiles (`pip install` unpinned / `curl | sh`) or hardcoded developer-only paths.
