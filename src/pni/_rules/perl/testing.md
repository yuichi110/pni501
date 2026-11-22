# Testing Standards (Perl)

## Core Principles
1. **TAP Test Suites (`t/*.t` + `prove`)**: Organize automated tests under `t/` (`*.t`) using `Test2::V0` (preferred modern standard) or `Test::More` (`done_testing;`), runnable deterministically via `prove -lv t/` (`AstFacts.test_functions_count`).
2. **Coverage Target**: Maintain statement/branch coverage of 80% or higher via `Devel::Cover` (`cover -test`; `RuntimeFacts.coverage.line_coverage_pct` and `AstFacts.module_test_coverage_pct`).
3. **Deterministic Isolation**: Use `File::Temp` (`tempdir(CLEANUP => 1)`) for filesystem tests, mock network/DB handles via dependency injection or `Test2::Tools::Mock` / `DBD::SQLite` in-memory databases, and avoid depending on live external endpoints.
4. **Meaningful Assertions**: Every `.t` script must assert concrete outcomes (`is`, `like`, `dies`, `ok` with descriptive test names; `AstFacts.assertion_free_tests == 0`).

## Evaluation Thresholds
- **`PASS`**: Automated `t/*.t` suite exists, `assertion_free_tests == 0`, deterministic offline execution, and measured coverage `>= 80%`.
- **`WARN`**: Coverage between `60%` and `79.9%`, or missing error-path / edge-case tests.
- **`FAIL`**: No automated tests (`test_files_count == 0`), coverage `< 60%`, or widespread assertion-free / environment-fragile tests.
