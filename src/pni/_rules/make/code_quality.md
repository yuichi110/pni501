# Code Quality & Safe Recipe Standards (Makefile)

## Core Principles
1. **Explicit `.PHONY`, `.DELETE_ON_ERROR` & Strict Shell**: Declare every non-file target (`all`, `build`, `test`, `clean`, `lint`, `help`) in `.PHONY`, include `.DELETE_ON_ERROR:` so failed recipes never leave corrupt partial output artifacts, and configure `SHELL := bash` + `.SHELLFLAGS := -eu -o pipefail -c` (`AstFacts.bug_risk_idioms`).
2. **Prevent Destructive Empty-Variable Expansion & Shell Injection**: Quote variable expansions inside shell recipes (`"$(TARGET)"`), **never** run `rm -rf $(BUILD_DIR)/*` without verifying `$(BUILD_DIR)` is non-empty (catastrophic `rm -rf /*` hazard; `AstFacts.dangerous_sinks`), and never execute `curl | sh` inside recipes.
3. **Simply Expanded Variables (`:=`) Over Expensive Recursive `=`**: Use `:=` when assigning `$(shell ...)` outputs so external commands execute once instead of re-running on every variable expansion, and use `?=` for user-overridable defaults.
4. **Self-Documenting `help` Target & `checkmake` Hygiene**: Provide a `.DEFAULT_GOAL := help` target documenting public commands (`## Description` comments; `AstFacts.docstring_coverage_pct`) and keep recipes clean under `checkmake`.

## Evaluation Thresholds
- **`PASS`**: `.PHONY` declared, `.DELETE_ON_ERROR:`, strict `SHELL` / quoting, `:=` for `$(shell ...)`, zero `rm -rf $(VAR)/` or `curl | sh` hazards, and self-documenting targets.
- **`WARN`**: Missing `.DELETE_ON_ERROR:` or `.DEFAULT_GOAL := help`, or recursive `=` with `$(shell ...)`.
- **`FAIL`**: Unchecked `rm -rf $(VAR)/` hazards, `curl | sh` remote code execution, missing `.PHONY` colliding with directories (`test/`, `build/`), or hardcoded host paths.
