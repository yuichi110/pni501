# Testing & Numerical Verification Standards (Fortran)

## Core Principles
1. **Automated Unit Tests (`test-drive` / `pFUnit` / `fpm test` / CTest)**: Organize tests under `test/` (`test_*.f90`) wired to `fpm test` or `ctest`, verifying both analytical edge cases and numerical conservation invariants (`AstFacts.test_functions_count`).
2. **Coverage & Runtime Bounds Checking**: Target `>= 80%` coverage via `gcov`/`gcovr` (`RuntimeFacts.coverage.line_coverage_pct`) AND run test suites with `-fcheck=all` (bounds, pointer, allocation checks) and FPE traps enabled.
3. **Deterministic Tolerance & Offline Isolation**: Verify floating-point outputs with explicit relative/absolute tolerances (`abs(actual - expected) <= tol`), pin RNG seeds, and isolate input/output fixture files in temporary directories.
4. **Meaningful Assertions**: Every test program must return a non-zero exit status (`error stop 1`) on assertion failure (`AstFacts.assertion_free_tests == 0`).

## Evaluation Thresholds
- **`PASS`**: Automated `fpm test`/CTest suite with explicit tolerances, `-fcheck=all` clean execution, and coverage `>= 80%`.
- **`WARN`**: Coverage between `60%` and `79.9%`, or tests run without bounds/FPE checks.
- **`FAIL`**: No automated tests (`test_files_count == 0`), coverage `< 60%`, or smoke programs that only `print *` without failing on wrong outputs.
