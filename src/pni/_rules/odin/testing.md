# Testing & Tracking-Allocator Standards (Odin)

## Core Principles
1. **Built-In `@(test)` Procedures (`odin test`)**: Organize tests in `*_test.odin` files (or `tests/` packages) annotated with `@(test) proc(t: ^testing.T)` executed via `odin test` (`AstFacts.test_functions_count`).
2. **Automatic Leak & Bad-Free Detection**: Note that `odin test` wires `mem.Tracking_Allocator` by default (and custom test harnesses should verify `len(track.allocation_map) == 0` and `len(track.bad_free_array) == 0`) so memory leaks and double-frees fail tests deterministically.
3. **Boundary, Zero-Value & Offline Isolation**: Test zero-initialized structs, empty slices, error return paths, and temporary directories offline without external network dependencies (`RuntimeFacts.coverage.line_coverage_pct`).
4. **Meaningful Assertions**: Every `@(test)` procedure must verify concrete outcomes via `testing.expect_value`, `testing.expect`, or `testing.expectf` (`AstFacts.assertion_free_tests == 0`).

## Evaluation Thresholds
- **`PASS`**: Automated `@(test)` suite passing cleanly under `odin test` with zero allocation leaks, `assertion_free_tests == 0`, and boundary coverage.
- **`WARN`**: Happy-path tests only (missing error-return or empty-slice edge cases).
- **`FAIL`**: No automated tests (`test_files_count == 0`), memory leaks / bad frees under tracking allocator, or assertion-free tests.
