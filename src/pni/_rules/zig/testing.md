# Testing & Leak-Detection Standards (Zig)

## Core Principles
1. **Built-In `test "..."` Blocks & `std.testing.allocator`**: Write co-located `test "..."` blocks and integration suites wired into `zig build test`, ALWAYS passing `std.testing.allocator` into allocating functions so every memory leak fails the test automatically (`AstFacts.test_functions_count`).
2. **Coverage & Fuzzing**: Maintain `>= 80%` line coverage via `kcov` / `llvm-cov` (`RuntimeFacts.coverage.line_coverage_pct`) and use `std.testing.checkAllAllocationFailures` to verify `errdefer` rollback paths on OOM.
3. **Deterministic Offline Isolation**: Use `std.testing.tmpDir` for filesystem tests, inject mock readers/writers (`std.io.fixedBufferStream`), and avoid live network calls.
4. **Meaningful Assertions**: Every `test` block must verify concrete outcomes via `std.testing.expectEqual`, `std.testing.expectEqualStrings`, or `std.testing.expectError` (`AstFacts.assertion_free_tests == 0`).

## Evaluation Thresholds
- **`PASS`**: Automated `zig build test` suite using `std.testing.allocator`, `assertion_free_tests == 0`, and coverage `>= 80%`.
- **`WARN`**: Coverage between `60%` and `79.9%`, or missing `checkAllAllocationFailures` OOM tests.
- **`FAIL`**: No automated tests (`test_files_count == 0`), memory leaks under `std.testing.allocator`, or assertion-free smoke tests.
