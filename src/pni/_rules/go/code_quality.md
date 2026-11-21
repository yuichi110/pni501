# Code Quality Standards (Go)

## Core Principles
1. **Effective Go & Static Analysis**: Format all sources with `gofmt`/`goimports` (`AstFacts.import_hygiene_coverage_pct`, `AstFacts.wildcard_imports`) and enforce `go vet` and `golangci-lint` checks without unscoped `//nolint` directives (`AstFacts.unscoped_type_ignores`).
2. **GoDoc Comments**: Document every exported package, type, constant, variable, function, and method with a complete sentence starting with the declared identifier (`// FunctionName ...`; `AstFacts.docstring_coverage_pct`, `AstFacts.missing_docstrings`).
3. **Explicit Error Handling**: Always check returned `error` values explicitly (`if err != nil`), wrap errors with context (`fmt.Errorf("...: %w", err)`), and never silently ignore returned errors while using companion return values (`val, _ := ...`) or trigger `panic(...)` in library packages (`AstFacts.bug_risk_idioms`).
4. **Package Cohesion & Zero Global State**: Organize cohesive, domain-oriented packages (`internal/`, `pkg/`, `cmd/`), keep functions concise (`AstFacts.complex_functions`, `AstFacts.excessive_parameters`), avoid mutable package-level variables (`AstFacts.global_state_usages`), and pass `context.Context` as the first parameter for I/O or cancellation boundaries.

## Evaluation Thresholds
- **`PASS`**: `import_hygiene_coverage_pct >= 90%`, `docstring_coverage_pct >= 80%`, zero ignored errors / library `panic(...)`, and zero unguarded mutable package globals.
- **`WARN`**: `docstring_coverage_pct` between `60%` and `79.9%`, or isolated complexity/import hygiene warnings.
- **`FAIL`**: `docstring_coverage_pct < 60%`, pervasive ignored errors / `defer`-in-loop / library panics, or unguarded concurrent package state.
