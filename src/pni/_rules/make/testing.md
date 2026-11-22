# Build Verification & Dry-Run Testing Standards (Makefile)

## Core Principles
1. **Dry-Run (`make -n`) & `checkmake` Verification**: Validate Makefiles in CI with `checkmake` and `make -n <target>` dry runs to confirm syntax, variable expansion, and dependency graphs without executing destructive side effects.
2. **Standardized Lifecycle Targets**: Provide predictable, non-interactive `make test`, `make lint`, `make build`, and `make clean` targets that return exact non-zero exit codes on failure (`AstFacts.test_functions_count`).
3. **Parallel-Safe (`make -j`) Dependency Graphs**: Ensure build targets declare complete prerequisites so `make -j` parallel builds never race on missing output directories (`mkdir -p $(@D)` or order-only `| $(BUILD_DIR)`).
4. **DSL Exemption**: Evaluate Makefile quality via `checkmake`, dry-run validation, and `make -j` cleanliness rather than unit-test coverage metrics.

## Evaluation Thresholds
- **`PASS`**: Clean `make -n` / `checkmake`, parallel-safe prerequisites, and deterministic `test`/`lint`/`clean` targets.
- **`WARN`**: Missing `mkdir -p $(@D)` order-only dir creation or missing `checkmake` lint step.
- **`FAIL`**: Race-prone parallel builds, broken `clean` target, or suppressed errors (`-cmd` hiding test failures).
