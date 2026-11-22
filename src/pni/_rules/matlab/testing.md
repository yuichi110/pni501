# Testing & Numerical Verification Standards (MATLAB)

## Core Principles
1. **`matlab.unittest` Framework (`*Test.m` / `test_*.m`)**: Organize unit tests under `tests/` using class-based `matlab.unittest.TestCase` (`methods (Test)`) or function-based `functiontests(localfunctions)` runnable via `runtests` (or `MOxUnit` when targeting GNU Octave CI; `AstFacts.test_functions_count`).
2. **Coverage Target**: Maintain statement/branch coverage of 80% or higher via `matlab.unittest.plugins.CodeCoveragePlugin` (Cobertura export; `RuntimeFacts.coverage.line_coverage_pct`).
3. **Deterministic Numerical Tolerances & Fixture Isolation**: Use `verifyEqual(testCase, actual, expected, 'RelTol', 1e-6, 'AbsTol', 1e-9)` for floating-point assertions, pin RNG streams (`rng(42, 'twister')` with `onCleanup` restore), and use `TemporaryFolderFixture` for temporary files.
4. **Meaningful Assertions**: Every test method must verify concrete outputs or error IDs (`verifyEqual`, `verifyError`; `AstFacts.assertion_free_tests == 0`).

## Evaluation Thresholds
- **`PASS`**: Automated `matlab.unittest`/MOxUnit suite exists, `assertion_free_tests == 0`, explicit tolerances & RNG pinning, and coverage `>= 80%`.
- **`WARN`**: Coverage between `60%` and `79.9%`, or missing error-ID / boundary-matrix tests.
- **`FAIL`**: No automated tests (`test_files_count == 0`), coverage `< 60%`, or scripts that only plot figures without programmatic verification.
