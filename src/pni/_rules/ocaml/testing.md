# Testing Standards (OCaml)

## Core Principles
1. **Alcotest / OUnit2 / Expect Tests + QCheck**: Organize tests under `test/` (or `ppx_expect` inline tests) wired to `dune runtest`, combining unit specs with `QCheck` property tests (`AstFacts.test_functions_count`).
2. **Coverage Target**: Maintain instrumentation coverage of 80% or higher via `bisect_ppx` (`dune runtest --instrument-with bisect_ppx`; `RuntimeFacts.coverage.line_coverage_pct` and `AstFacts.module_test_coverage_pct`).
3. **Pure Core & Deterministic Isolation**: Parameterize I/O modules via OCaml functors or first-class modules so tests execute completely offline without external services.
4. **Meaningful Assertions**: Every test case must verify concrete values or error variants (`Alcotest.(check ...)`, `assert_equal`, `%expect`; `AstFacts.assertion_free_tests == 0`).

## Evaluation Thresholds
- **`PASS`**: Automated `dune runtest` suite exists, `assertion_free_tests == 0`, deterministic offline isolation, and coverage `>= 80%`.
- **`WARN`**: Coverage between `60%` and `79.9%`, or missing `Error` variant test cases.
- **`FAIL`**: No automated tests (`test_files_count == 0`), coverage `< 60%`, or widespread assertion-free / network-coupled tests.
