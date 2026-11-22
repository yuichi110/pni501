# Testing Standards (PowerShell)

## Core Principles
1. **Pester v5 Suites (`*.Tests.ps1`)**: Organize unit and integration tests under `Tests/` or `tests/` (`*.Tests.ps1`) using Pester v5 (`Describe`, `Context`, `It`, `BeforeAll`/`BeforeEach`; `AstFacts.test_functions_count`).
2. **Coverage Target**: Maintain command/line coverage of 80% or higher via Pester `CodeCoverage` (JaCoCo/Cobertura export; `RuntimeFacts.coverage.line_coverage_pct` and `AstFacts.module_test_coverage_pct`).
3. **Deterministic Isolation**: Isolate filesystem writes via Pester `TestDrive:\`, mock external cmdlets/REST calls via `Mock` + `Should -Invoke`, and run cross-platform offline under `pwsh`.
4. **Meaningful Assertions**: Every `It` block must verify concrete outcomes (`Should -Be`, `Should -Throw`, `Should -HaveCount`; `AstFacts.assertion_free_tests == 0`).

## Evaluation Thresholds
- **`PASS`**: Automated Pester v5 `*.Tests.ps1` suite exists, `assertion_free_tests == 0`, `TestDrive:\` & `Mock` isolation, and measured coverage `>= 80%`.
- **`WARN`**: Coverage between `60%` and `79.9%`, or legacy Pester v4 syntax.
- **`FAIL`**: No automated tests (`test_files_count == 0`), coverage `< 60%`, or widespread assertion-free / host-mutating tests.
