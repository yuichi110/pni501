# Testing Standards (Bash / Shell)

## Core Principles
1. **Bats (`bats-core`) / ShellSpec Suites**: Organize automated tests under `tests/*.bats` or `tests/*_test.sh` using `bats-core` (`@test "..."`), `shunit2`, or `ShellSpec`, verifying exit codes (`$status`) and stdout/stderr (`$output`; `AstFacts.test_functions_count`).
2. **Syntax & Static Verification Gates**: Run `bash -n` syntax checks and `shellcheck` across all `*.sh` / `*.bash` files in CI alongside functional unit tests (`RuntimeFacts.coverage.line_coverage_pct`).
3. **Deterministic Sandbox Isolation**: Execute scripts against temporary directories (`$BATS_TEST_TMPDIR` / `mktemp -d`), stub external CLIs via a prepended test `PATH`, and ensure tests never touch host home directories or live networks.
4. **Meaningful Assertions**: Every `@test` case must assert exit status and expected output/files (including failure paths and malformed inputs; `AstFacts.assertion_free_tests == 0`).

## Evaluation Thresholds
- **`PASS`**: Automated Bats/ShellSpec tests + `shellcheck` exist, `assertion_free_tests == 0`, isolated temp fixtures, and happy/error paths covered.
- **`WARN`**: Only `bash -n` / `shellcheck` or happy-path smoke scripts exist without error-branch assertions.
- **`FAIL`**: No automated tests (`test_files_count == 0`) or tests that mutate host filesystem / rely on live network state.
