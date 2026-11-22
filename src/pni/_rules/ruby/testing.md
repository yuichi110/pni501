# Testing Standards (Ruby)

## Core Principles
1. **RSpec or Minitest Suites**: Organize specs under `spec/**/*_spec.rb` (RSpec) or `test/**/*_test.rb` (Minitest) mirroring `lib/` and `app/` (`AstFacts.test_functions_count`).
2. **Coverage Target**: Maintain line coverage of 80% or higher via `SimpleCov` (`RuntimeFacts.coverage.line_coverage_pct` and `AstFacts.module_test_coverage_pct`).
3. **Deterministic Isolation**: Stub outbound HTTP calls with `WebMock` / `VCR`, freeze clocks via `ActiveSupport::Testing::TimeHelpers` / `Timecop`, avoid database state leaks across examples, and ensure suites run offline.
4. **Meaningful Assertions**: Every `it` / `test` block must assert concrete expectations (`expect(...).to`, `assert_equal`, `assert_raises`; `AstFacts.assertion_free_tests == 0`).

## Evaluation Thresholds
- **`PASS`**: Automated RSpec/Minitest suite exists, `assertion_free_tests == 0`, and measured coverage `>= 80%`.
- **`WARN`**: Coverage between `60%` and `79.9%`, or isolated flaky time/database dependencies.
- **`FAIL`**: No automated tests (`test_files_count == 0`), coverage `< 60%`, or widespread assertion-free / live-network tests.
