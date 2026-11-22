# Testing & Sanitizer Verification Standards (C)

## Core Principles
1. **Unit Testing Frameworks & CTest**: Maintain automated C unit tests (`Unity`, `CMocka`, `Check`, `Criterion`, or structured `assert()` test binaries registered with `ctest` / `meson test`; `AstFacts.test_functions_count`).
2. **Coverage & Sanitizer Execution**: Target `>= 80%` line/branch coverage via `gcov`/`lcov`/`gcovr` (`RuntimeFacts.coverage.line_coverage_pct`) AND execute the test suite under AddressSanitizer (`ASan`) + UndefinedBehaviorSanitizer (`UBSan`) or Valgrind to catch leaks, out-of-bounds accesses, and UB.
3. **Boundary & Fuzz Testing**: Explicitly test NULL pointers, zero-length buffers, maximum-length/overflow inputs, malformed wire bytes, and error-return paths (add `libFuzzer` / AFL harnesses for parsers).
4. **Meaningful Assertions**: Every test case must verify concrete return codes, buffer contents, and error outputs (`AstFacts.assertion_free_tests == 0`).

## Evaluation Thresholds
- **`PASS`**: Automated test suite exists, `assertion_free_tests == 0`, sanitizer-clean execution, and measured coverage `>= 80%`.
- **`WARN`**: Coverage between `60%` and `79.9%`, or tests run without ASan/UBSan enabled.
- **`FAIL`**: No automated tests (`test_files_count == 0`), coverage `< 60%`, or failing/leaking sanitizer checks.
