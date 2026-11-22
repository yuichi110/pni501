# Code Quality Standards (C#)

## Core Principles
1. **.NET Analyzers & Formatting**: Enforce `.editorconfig`, `dotnet format`, and Roslyn analyzers (`<AnalysisLevel>latest</AnalysisLevel>`, `<TreatWarningsAsErrors>true</TreatWarningsAsErrors>`) with scoped `#pragma warning disable` directives accompanied by rationale (`AstFacts.unscoped_type_ignores == 0`).
2. **XML Documentation Comments**: Document public assemblies, classes, records, interfaces, and methods with XML doc comments (`/// <summary>...</summary>`, `<param>`, `<returns>`; `AstFacts.docstring_coverage_pct`, `AstFacts.missing_docstrings`).
3. **Async & Resource Discipline**: Never use `async void` outside UI event handlers, never block asynchronously with `.Result` or `.Wait()` (thread-pool starvation/deadlock risk; `AstFacts.bug_risk_idioms`), pass `CancellationToken` through async chains, and dispose every `IDisposable` / `IAsyncDisposable` via `using` / `await using`.
4. **Cohesive Design & DI Over Static Mutable State**: Use constructor-based `IServiceCollection` dependency injection, avoid mutable static fields (`AstFacts.global_state_usages`), never swallow exceptions with empty `catch {}` blocks, and keep classes/methods concise (`AstFacts.complex_functions`, `AstFacts.excessive_parameters`).

## Evaluation Thresholds
- **`PASS`**: `docstring_coverage_pct >= 80%`, zero `async void`/`.Result`/`.Wait()`/empty-`catch` idioms, zero unguarded mutable static state, and scoped analyzer suppressions.
- **`WARN`**: `docstring_coverage_pct` between `60%` and `79.9%`, or isolated complexity / `using` cleanup warnings.
- **`FAIL`**: `docstring_coverage_pct < 60%`, sync-over-async deadlocks (`.Result`/`.Wait()`), `async void` in services, or unguarded shared mutable static state.
