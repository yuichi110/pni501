# Typing, Input Assertions & S3/S7 Contract Standards (R)

## Core Principles
1. **Dynamic Typing Exemption & Defensive Assertions**: R is dynamically typed — do **NOT** penalize R code for lacking compile-time static type annotations. Evaluate contract safety via explicit input validation (`stopifnot(...)`, `vctrs::vec_assert`, `checkmate::assert_*`, `rlang::arg_match`) and `roxygen2` `@param`/`@return` documentation.
2. **Predictable Return Types (Type Stability)**: Functions must return a consistent type regardless of input edge cases (e.g., avoid `sapply()` which silently flips between vector, list, and matrix — use `vapply()` or `purrr::map_*()`; always set `drop = FALSE` when subsetting matrices/data frames in programmatic code).
3. **Explicit `NA` & Missing-Value Handling**: Handle `NA`, `NaN`, `NULL`, and zero-row `data.frame`/`tibble` inputs explicitly rather than relying on silent recycling or implicit coercion.
4. **Structured Classes (S3 / S7 / R6)**: Validate invariants inside explicit S3 constructors (`new_*()`, `validate_*()`) or S7 typed property classes rather than passing unvalidated nested lists across module boundaries.

## Evaluation Thresholds
- **`PASS`**: Type-stable return contracts (`vapply`/`purrr::map_*`, `drop = FALSE`), explicit input assertions on public APIs, and `NA`/empty-input guards.
- **`WARN`**: Isolated `sapply()` or unvalidated public arguments on internal helpers.
- **`FAIL`**: Pervasive `sapply()` type instability, silent recycling bugs, or unchecked `NA`/zero-row crashes across core functions.
