# Testing & Golden-File Verification Standards (COBOL)

## Core Principles
1. **Automated Unit & Batch Regression Tests**: Maintain repeatable tests using `cobol-check`, `GCBLUnit`, or GnuCOBOL test driver programs (`tests/test_*.cob` / `*_test.cbl`) plus golden-file input/output dataset comparisons for batch programs (`AstFacts.test_functions_count`).
2. **Coverage & Bounds Checking**: Compile test builds with runtime bounds/overflow checks enabled (`cobc -debug -ftrace` / `-fec=all` / IBM `SSRANGE`) and verify core business rules, boundary dates/leap years, rounding (`ROUNDED`), and `ON SIZE ERROR` overflow branches (`RuntimeFacts.coverage.line_coverage_pct`).
3. **Deterministic File & DB Isolation**: Drive batch tests against self-contained fixture files (temporary sequential/indexed datasets) and mock/stub `EXEC SQL` / `EXEC CICS` / external `CALL`s so suites run offline without mainframe connectivity.
4. **Meaningful Assertions**: Every test driver must assert expected output fields, return codes (`RETURN-CODE`), and `FILE STATUS` codes (`AstFacts.assertion_free_tests == 0`).

## Evaluation Thresholds
- **`PASS`**: Automated COBOL unit or golden-dataset regression tests run deterministically offline with bounds checking and meaningful assertions.
- **`WARN`**: Only happy-path golden tests exist without overflow/error-status boundary cases.
- **`FAIL`**: Zero automated tests (`test_files_count == 0`) and no repeatable verification harness.
