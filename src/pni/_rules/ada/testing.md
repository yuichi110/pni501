# Testing & Contract-Verification Standards (Ada)

## Core Principles
1. **AUnit / Ahven / GNATtest Suites**: Organize automated tests under `tests/` (`*_test.adb` / `test_*.adb`) wired to `alr test` or a dedicated `tests.gpr`, running with runtime contract assertions enabled (`-gnata`; `AstFacts.test_functions_count`).
2. **Coverage & Formal Verification**: Maintain `>= 80%` statement/decision coverage via `gnatcov` / `gcov` (`RuntimeFacts.coverage.line_coverage_pct`) — and MC/DC or `gnatprove` proofs for safety-critical modules.
3. **Boundary & Constraint_Error Testing**: Explicitly verify range-subtype boundaries (`'First`, `'Last`), `Pre`/`Post` contract violations (`Assertion_Error`), `Constraint_Error` handling, and deterministic offline isolation.
4. **Meaningful Assertions**: Every test routine must assert concrete expectations via `AUnit.Assertions.Assert` (or explicit failure exit code; `AstFacts.assertion_free_tests == 0`).

## Evaluation Thresholds
- **`PASS`**: Automated AUnit/Ahven/GPR test suite with `-gnata` enabled, `assertion_free_tests == 0`, boundary/exception tests, and coverage `>= 80%`.
- **`WARN`**: Coverage between `60%` and `79.9%`, or tests compiled without `-gnata` contract checks.
- **`FAIL`**: No automated tests (`test_files_count == 0`), coverage `< 60%`, or assertion-free print-only drivers.
