# Testing Standards (Go)

## Core Principles
1. **Table-Driven Standard `testing`**: Write table-driven unit tests (`func TestXxx(t *testing.T)`) using `t.Run(...)` subtests co-located in `*_test.go` files alongside the package under test (`AstFacts.test_functions_count`).
2. **Coverage Target**: Maintain statement coverage of 80% or higher (`go test -coverprofile=coverage.out ./...`; `RuntimeFacts.coverage.line_coverage_pct` and `AstFacts.module_test_coverage_pct`) across core packages.
3. **Deterministic & Race-Free**: Isolate external network/database dependencies via narrow interfaces, mark helper functions with `t.Helper()`, and ensure tests pass offline under `-race`.
4. **Meaningful Assertions**: Verify both happy-path outputs and error branches (`t.Fatalf`, `t.Errorf`, `errors.Is`, `errors.As`, or `testify/require`; `AstFacts.assertion_free_tests == 0`).

## Evaluation Thresholds
- **`PASS`**: Automated `*_test.go` suite exists, `assertion_free_tests == 0`, and measured coverage `>= 80%`.
- **`WARN`**: Coverage between `60%` and `79.9%`, or isolated assertion/isolation gaps.
- **`FAIL`**: No automated tests (`test_files_count == 0`), coverage `< 60%`, or widespread assertion-free/network-coupled tests.
