# Code Quality Standards (Scala)

## Core Principles
1. **Scalafmt, Scalafix & Compiler Strictness**: Format with `scalafmt`, enforce `scalafix` / `WartRemover` and strict `scalacOptions` (`-Xfatal-warnings`, `-Wunused:all`), and avoid bare `@SuppressWarnings` without rationale (`AstFacts.unscoped_type_ignores == 0`).
2. **Scaladoc Coverage**: Document public packages, traits, enums/ADTs, classes, and methods with Scaladoc (`/** ... @param ... @return ... */`; `AstFacts.docstring_coverage_pct`, `AstFacts.missing_docstrings`).
3. **Pure Functional Discipline & Total Functions**: Avoid `null`, mutable `var`, non-local `return`, partial calls (`.get`, `.head`, `.tail` without guard), and blocking `Await.result` inside `Future`/effect pools (`AstFacts.bug_risk_idioms`); model absence and failure with `Option`, `Either`, `Try`, or `IO`/`ZIO`.
4. **Immutability & Bounded Complexity**: Keep `object` singletons stateless (`AstFacts.global_state_usages`), minimize wildcard imports (`import foo._` / `import foo.*` outside DSL syntax/implicits; `AstFacts.wildcard_imports`), and keep functions concise (`AstFacts.complex_functions`, `AstFacts.excessive_parameters`).

## Evaluation Thresholds
- **`PASS`**: `docstring_coverage_pct >= 80%`, zero `null`/`Await.result`/unchecked `.get`/mutable `object` globals, and scoped suppressions.
- **`WARN`**: `docstring_coverage_pct` between `60%` and `79.9%`, or isolated partial-function / complexity warnings.
- **`FAIL`**: `docstring_coverage_pct < 60%`, pervasive `null`/`var`/`Await.result` thread-pool starvation, or mutable global `object` state.
