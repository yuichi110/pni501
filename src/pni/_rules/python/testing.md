# Testing Standards (Python)

## Core Principles
1. **Pytest Framework**: Use `pytest` for all unit and integration tests (`AstFacts.test_functions_count`).
2. **Coverage Target**: Maintain line coverage of 80% or higher across domain packages (`RuntimeFacts.coverage.line_coverage_pct` when measured, alongside `AstFacts.module_test_coverage_pct`).
3. **Deterministic & Isolated**: Unit tests must run offline without external network dependencies or execution-order coupling, and every test function must execute meaningful assertions (`AstFacts.assertion_free_tests == 0`).
4. **Mirror Structure**: Test files should mirror the `src/` directory layout (e.g., `tests/<pkg>/test_cli.py`).

## Evaluation Thresholds
- **`PASS`**: Automated pytest suite exists, `assertion_free_tests == 0`, and measured coverage `>= 80%` (or strong `module_test_coverage_pct` on static-only runs).
- **`WARN`**: Coverage between `60%` and `79.9%`, or minor assertion/isolation gaps.
- **`FAIL`**: No automated tests (`test_files_count == 0`), coverage `< 60%`, or widespread assertion-free/flaky tests.
