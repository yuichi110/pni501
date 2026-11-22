# Testing Standards (R)

## Core Principles
1. **`testthat` 3rd Edition Suites**: Organize unit tests under `tests/testthat/test-*.R` mirroring `R/*.R` using `testthat` edition 3 (`Config/testthat/edition: 3` in `DESCRIPTION`; `AstFacts.test_functions_count`).
2. **Coverage Target**: Maintain line coverage of 80% or higher via `covr::package_coverage()` (`RuntimeFacts.coverage.line_coverage_pct` and `AstFacts.module_test_coverage_pct`).
3. **Deterministic Isolation & Reproducible Seeds**: Set explicit seeds (`withr::local_seed(...)`) for stochastic algorithms, use `withr::local_tempdir()` / `withr::local_envvar()` to avoid global side effects, mock HTTP/DB boundaries offline (`httptest2` / `with_mocked_bindings`), and guard live tests appropriately.
4. **Meaningful Assertions**: Every `test_that("...", { ... })` block must assert concrete values, tolerances, or errors (`expect_equal`, `expect_identical`, `expect_error`, `expect_snapshot`; `AstFacts.assertion_free_tests == 0`).

## Evaluation Thresholds
- **`PASS`**: Automated `testthat` suite exists, `assertion_free_tests == 0`, deterministic seeds/isolation, and measured coverage `>= 80%`.
- **`WARN`**: Coverage between `60%` and `79.9%`, or stochastic tests missing explicit seed pinning.
- **`FAIL`**: No automated tests (`test_files_count == 0`), coverage `< 60%`, or widespread assertion-free / live-network tests.
