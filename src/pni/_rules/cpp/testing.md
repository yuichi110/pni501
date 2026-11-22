# Testing & Sanitizer Standards (C++)

## Core Principles
1. **Modern C++ Unit Test Frameworks**: Organize tests under `tests/` using GoogleTest (`TEST`, `TEST_F`, `TEST_P`), Catch2 (`TEST_CASE`, `REQUIRE`), or doctest integrated with `ctest` (`AstFacts.test_functions_count`).
2. **Coverage & Sanitizers**: Target `>= 80%` line/branch coverage via `gcovr`/`llvm-cov` (`RuntimeFacts.coverage.line_coverage_pct`) AND execute tests under AddressSanitizer (`ASan`) + UndefinedBehaviorSanitizer (`UBSan`) (plus `TSan` for multithreaded code).
3. **Deterministic Isolation & Mocking**: Inject interfaces or templates for I/O, network, and clock boundaries (`gMock` or lightweight fakes), avoid `std::this_thread::sleep_for` synchronization races, and run offline.
4. **Meaningful Assertions**: Every test must assert concrete results/exceptions (`EXPECT_EQ`, `ASSERT_THROW`, `REQUIRE`; `AstFacts.assertion_free_tests == 0`).

## Evaluation Thresholds
- **`PASS`**: Automated GoogleTest/Catch2/CTest suite exists, `assertion_free_tests == 0`, sanitizer-clean runs, and measured coverage `>= 80%`.
- **`WARN`**: Coverage between `60%` and `79.9%`, or tests run without ASan/UBSan.
- **`FAIL`**: No automated tests (`test_files_count == 0`), coverage `< 60%`, or failing sanitizer/leak checks.
