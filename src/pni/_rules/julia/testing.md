# Testing Standards (Julia)

## Core Principles
1. **Standard `Test` (`test/runtests.jl`) & `Aqua.jl` / `JET.jl`**: Organize tests under `test/runtests.jl` (with modular `test_*.jl` files) using `@testset`, `@test`, `@test_throws`, and `@inferred` (`AstFacts.test_functions_count`), plus `Aqua.test_all` for method ambiguities and unbound args.
2. **Coverage Target**: Maintain line coverage of 80% or higher via `julia --code-coverage=user` + `Coverage.jl` (`RuntimeFacts.coverage.line_coverage_pct` and `AstFacts.module_test_coverage_pct`).
3. **Deterministic Numerical & Offline Isolation**: Pin RNG seeds (`Random.Xoshiro(seed)` — avoid mutating global RNG when testing parallel code), use `mktempdir()` for temporary files, and verify floating-point outputs with `isapprox` (`≈`, `rtol`/`atol`).
4. **Meaningful Assertions**: Every `@testset` must assert concrete numerical/structural outputs and error paths (`@test`, `@test_throws`; `AstFacts.assertion_free_tests == 0`).

## Evaluation Thresholds
- **`PASS`**: Automated `test/runtests.jl` suite exists, `assertion_free_tests == 0`, deterministic seeds/isolation, and coverage `>= 80%`.
- **`WARN`**: Coverage between `60%` and `79.9%`, or missing `@inferred` type-stability assertions.
- **`FAIL`**: No automated tests (`test_files_count == 0`), coverage `< 60%`, or widespread assertion-free / live-network tests.
