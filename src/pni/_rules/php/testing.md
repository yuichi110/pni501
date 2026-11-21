# Testing & Coverage Standards (PHP)

## Core Principles
1. **Automated PHPUnit / Pest Suite**: Maintain deterministic automated unit and feature tests under `tests/` configured via `phpunit.xml` or `phpunit.xml.dist` (PHPUnit 10/11+ or Pest; `AstFacts.test_functions_count`).
2. **Meaningful Assertions & Edge-Case Coverage**: Every test method (`test*` or `#[Test]`) must execute explicit assertions (`$this->assertSame(...)`, `$this->expectException(...)`, or Pest `expect(...)`; `AstFacts.assertion_free_tests == 0`) covering nominal paths, validation failures, and security boundaries.
3. **Offline Hermetic Execution & PCOV Coverage**: Tests must run offline without live external databases or HTTP APIs (use in-memory `pdo_sqlite`, fakes, or mocks) and target `>= 80%` statement/branch coverage measured with `pcov` (`RuntimeFacts.coverage.line_coverage_pct`, `AstFacts.module_test_coverage_pct`).

## Evaluation Thresholds
- **`PASS`**: Automated PHPUnit/Pest suite exists, `assertion_free_tests == 0`, and measured coverage `>= 80%`.
- **`WARN`**: Coverage between `60%` and `79.9%`, or isolated assertion/isolation gaps.
- **`FAIL`**: No automated tests (`test_files_count == 0`), coverage `< 60%`, or widespread assertion-free/network-coupled tests.
