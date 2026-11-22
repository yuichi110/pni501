# Code Quality Standards (R)

## Core Principles
1. **Tidyverse Style, `lintr` & `R CMD check`**: Format code with `styler` / `air`, lint with `lintr`, and ensure packages pass `R CMD check --as-cran` with zero ERRORs/WARNINGs (`ProjectFacts.tooling_modernization_issues`).
2. **Eliminate Classic R Pitfalls & Global Mutation**: Never use `<<-` super-assignment to mutate global environments (`AstFacts.global_state_usages`, `AstFacts.bug_risk_idioms`), never call `attach()` (pollutes search path), always write `TRUE`/`FALSE` instead of overwritable `T`/`F`, use `seq_along(x)`/`seq_len(n)` instead of `1:length(x)` (breaks on empty vectors), and never call `rm(list = ls())` or `setwd()` inside reusable packages/functions.
3. **Eliminate Code/Command Injection Sinks**: Never pass untrusted text to `eval(parse(text = ...))` (CWE-94) or unsanitized strings to `system()` / `system2()` (CWE-78; `AstFacts.dangerous_sinks`).
4. **Roxygen2 Documentation & Modular Functions**: Document exported functions with `roxygen2` comments (`#' @param`, `#' @return`, `#' @export`; `AstFacts.docstring_coverage_pct`), use `pkg::fn()` namespace qualification inside packages (never `library()` inside `R/` package files), and keep functions concise (`AstFacts.complex_functions`, `AstFacts.excessive_parameters`).

## Evaluation Thresholds
- **`PASS`**: Zero `<<-`/`attach()`/`eval(parse())`/`system()` injection sinks, `TRUE`/`FALSE` & `seq_along` discipline, `roxygen2` coverage `>= 80%` on exports, and explicit `pkg::fn()` qualification in packages.
- **`WARN`**: `roxygen2` coverage between `60%` and `79.9%`, or isolated `1:length(x)` / style warnings.
- **`FAIL`**: Pervasive `<<-` global state or `attach()`, `eval(parse())` / `system()` injection sinks, `library()` calls inside package `R/` files, or `setwd()` side effects.
