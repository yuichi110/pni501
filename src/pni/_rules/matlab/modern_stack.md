# Modern MATLAB (R2022b+ / R2024a+) Idioms (`matlab/modern_stack`)

## Core Principles
1. **Modern MATLAB Syntax & Namespaces**: Use `+package` namespace folders, `arguments` validation blocks, `dictionary` / `table` / `timetable` over nested `struct` arrays, `readmatrix`/`readtable` over legacy `csvread`/`xlsread`, and `weboptions('Timeout', ...)` on `webread`/`webwrite` calls (`AstFacts.modernization_hints`, `AstFacts.missing_io_timeouts`).
2. **Eliminate Shell & Code-Execution Sinks**: Avoid `system(...)` / `!cmd` with unsanitized strings (CWE-78) and `eval` / `evalc` (CWE-94; `AstFacts.dangerous_sinks`).
3. **Modern Linear Algebra & Parallelism**: Use `A \ b` instead of `inv(A) * b` (numerically superior and faster) and keep `parfor` loops independent of mutable shared state.
4. **Clean Diagnostics**: Use `warning('MyPkg:Id', ...)` / structured logging rather than un-semicoloned statements or scattered `disp(...)` calls (`AstFacts.unstructured_logging`).
