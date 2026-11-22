# Testing, Sanitizer & Reference-Oracle Standards (CUDA)

## Core Principles
1. **CPU Reference-Oracle Tests (GoogleTest / Catch2 / PyTorch Test)**: Verify every custom CUDA kernel against a deterministic CPU reference implementation across non-power-of-two sizes, unaligned tail elements (`n = 1, 31, 32, 33, 1025`), and edge values (`0`, `NaN`, `Inf`; `AstFacts.test_functions_count`).
2. **`compute-sanitizer` Verification**: Run test binaries under NVIDIA `compute-sanitizer` (`--tool memcheck`, `--tool racecheck`, `--tool initcheck`, `--tool synccheck`) to catch out-of-bounds global/shared memory accesses, race conditions, and warp sync bugs.
3. **Deterministic Tolerance & Coverage**: Assert numerical parity with explicit `fp32`/`fp16`/`bf16` relative/absolute tolerances (accounting for non-associative floating-point reductions) and track host/launcher coverage via `gcov`/`llvm-cov`.
4. **Meaningful Assertions**: Every test must assert concrete numerical outputs and `cudaSuccess` error status (`AstFacts.assertion_free_tests == 0`).

## Evaluation Thresholds
- **`PASS`**: Automated CPU-oracle kernel tests covering tail/edge sizes, `compute-sanitizer` clean execution, and explicit tolerances.
- **`WARN`**: Only power-of-two happy-path kernel sizes tested or `compute-sanitizer` not wired in CI.
- **`FAIL`**: No automated kernel verification tests (`test_files_count == 0`) or benchmark-only scripts without correctness assertions.
