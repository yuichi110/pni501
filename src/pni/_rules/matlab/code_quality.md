# Code Quality Standards (MATLAB)

## Core Principles
1. **Functions Over Workspace Scripts & Zero `eval`/`global` Abuse**: Encapsulate reusable logic in `.m` functions or `classdef` classes rather than scripts mutating the base workspace; forbid `eval`, `evalin`, `assignin`, and `feval` on untrusted strings (CWE-94; `AstFacts.dangerous_sinks`), forbid `global` variables (`AstFacts.global_state_usages`), and never call `clear all` / `close all` / `cd` inside reusable functions.
2. **Pre-Allocation, Vectorization & Code Analyzer Cleanliness**: Pre-allocate matrices before loops (`zeros(n, m)`) rather than dynamically growing arrays inside `for` loops, avoid shadowing built-in identifiers (`i`, `j`, `sum`, `length`, `mean`), terminate statements with `;` to avoid console spam, and resolve `checkcode` / Code Analyzer warnings with scoped `%#ok<...>` only when justified (`AstFacts.unscoped_type_ignores == 0`).
3. **Structured Help Comments**: Begin every `.m` function and `classdef` with a MATLAB help header block (`% FUNCNAME Summary ...` with Inputs/Outputs/Example) so `help funcname` works cleanly (`AstFacts.docstring_coverage_pct`).
4. **Explicit Error IDs & Resource Cleanup**: Throw structured errors with identifiers (`error('MyPkg:InvalidInput', '...')`) and pair `fopen`/temp handles with `onCleanup(@() fclose(fid))` (`AstFacts.bug_risk_idioms`, `AstFacts.complex_functions`).

## Evaluation Thresholds
- **`PASS`**: Function/class encapsulation (zero `eval`/`global`/`clear all` in functions), pre-allocated loops, `onCleanup` resource safety, and `help` headers `>= 80%`.
- **`WARN`**: `docstring_coverage_pct` between `60%` and `79.9%`, or isolated un-preallocated helper loops.
- **`FAIL`**: `eval`/`evalin`/`system` injection sinks, pervasive `global` state, `clear all` inside libraries, or unchecked `fopen` / error swallowing.
