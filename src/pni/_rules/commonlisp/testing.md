# Testing Standards (Common Lisp)

## Core Principles
1. **FiveAM / Rove / Parachute Wired to `asdf:test-system`**: Organize tests under `tests/` or `t/` in a dedicated `<sys>/tests` ASDF system runnable via `(asdf:test-system :my-pkg)` (`FiveAM`, `Rove`, `Parachute`, or `Coalton` tests; `AstFacts.test_functions_count`).
2. **Coverage Target**: Maintain expression/branch coverage of 80% or higher via SBCL `sb-cover` (`RuntimeFacts.coverage.line_coverage_pct` and `AstFacts.module_test_coverage_pct`).
3. **Deterministic Isolation**: Bind dynamic specials cleanly via `let` inside test fixtures, use `uiop:with-temporary-file` / temporary directories for filesystem tests, and ensure `(asdf:test-system ...)` exits non-zero in CI on failure (never leave interactive debugger enabled — run SBCL with `--non-interactive`).
4. **Meaningful Assertions**: Every test must assert concrete values or conditions (`is`, `ok`, `signals`, `fail`; `AstFacts.assertion_free_tests == 0`).

## Evaluation Thresholds
- **`PASS`**: Automated ASDF-wired test system exists, exits non-zero on failure under `--non-interactive`, `assertion_free_tests == 0`, and coverage `>= 80%`.
- **`WARN`**: Coverage between `60%` and `79.9%`, or missing condition/error-path tests (`signals`).
- **`FAIL`**: No automated tests (`test_files_count == 0`), coverage `< 60%`, or test runner silently returning exit code 0 on failures.
