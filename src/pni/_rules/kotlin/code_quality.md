# Code Quality Standards (Kotlin)

## Core Principles
1. **ktlint & Detekt Hygiene**: Format code via `ktlint` / `ktfmt`, enforce `detekt` static checks, avoid wildcard imports (`import foo.*`; `AstFacts.wildcard_imports`), and scope `@Suppress("...")` annotations narrowly with rationale (`AstFacts.unscoped_type_ignores == 0`).
2. **KDoc Documentation**: Document public packages, classes, interfaces, sealed hierarchies, and functions with KDoc (`/** ... @param ... @return ... */`; `AstFacts.docstring_coverage_pct`, `AstFacts.missing_docstrings`).
3. **Structured Concurrency & Null Safety**: Never use `GlobalScope.launch` (leaks unstructured coroutines), never swallow `CancellationException` inside broad `catch (e: Exception)` blocks, avoid non-null assertions (`!!`) in production paths (`AstFacts.bug_risk_idioms`), and close `AutoCloseable` resources via `.use { ... }`.
4. **Immutability & Clean State**: Prefer `val` over `var`, immutable collections (`List`/`Map`), and constructor injection over mutable `object` / `companion object` singletons (`AstFacts.global_state_usages`, `AstFacts.complex_functions`, `AstFacts.excessive_parameters`).

## Evaluation Thresholds
- **`PASS`**: `docstring_coverage_pct >= 80%`, zero `GlobalScope`/swallowed `CancellationException`/pervasive `!!`, zero unguarded mutable `object` singletons, and scoped `@Suppress`.
- **`WARN`**: `docstring_coverage_pct` between `60%` and `79.9%`, or isolated complexity / wildcard-import warnings.
- **`FAIL`**: `docstring_coverage_pct < 60%`, unstructured `GlobalScope` leaks, swallowed `CancellationException`, or pervasive `!!` NPE hazards.
