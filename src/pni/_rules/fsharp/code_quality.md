# Code Quality Standards (F#)

## Core Principles
1. **Fantomas, Strict Warnings & Signature Files**: Format code with `fantomas`, enable `<TreatWarningsAsErrors>true</TreatWarningsAsErrors>` and `<WarnOn>3390</WarnOn>` in `.fsproj`, and use `.fsi` interface files on public library modules (`AstFacts.unscoped_type_ignores == 0`).
2. **XML Documentation Comments**: Document public modules, discriminated unions, records, and functions with `///` XML docs (`AstFacts.docstring_coverage_pct`, `AstFacts.missing_docstrings`).
3. **Functional Purity & Safe Async**: Avoid `mutable` state, `ref` cells, `null`, `Option.get` / `List.head` partial calls, and blocking `Async.RunSynchronously` / `.Result` inside async workflows or ASP.NET/Giraffe request threads (`AstFacts.bug_risk_idioms`, `AstFacts.global_state_usages`). Use `use` bindings for `IDisposable` resources.
4. **Cohesive Pipelines & Explicit Module Boundaries**: Prefer `|>` pipelines and small pure functions (`AstFacts.complex_functions`, `AstFacts.excessive_parameters`), and leverage F#'s top-down compilation order to keep module dependency graphs strictly acyclic (`AstFacts.circular_dependencies == 0`).

## Evaluation Thresholds
- **`PASS`**: `docstring_coverage_pct >= 80%`, zero `Async.RunSynchronously`/partial `Option.get`/unguarded `mutable` globals, clean `use` disposal, and zero compiler warning suppression abuse.
- **`WARN`**: `docstring_coverage_pct` between `60%` and `79.9%`, or isolated `mutable` loops / complexity warnings.
- **`FAIL`**: `docstring_coverage_pct < 60%`, sync-over-async deadlocks, pervasive `null`/`mutable` state, or empty `try ... with _ -> ()` exception swallowing.
