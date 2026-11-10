# Code Quality Standards (Go)

## Core Principles
1. **Effective Go & Static Analysis**: Format all sources with `gofmt`/`goimports` and enforce `go vet` and `golangci-lint` checks without unscoped `//nolint` directives.
2. **GoDoc Comments**: Document every exported package, type, constant, variable, function, and method with a complete sentence starting with the declared identifier (`// FunctionName ...`).
3. **Explicit Error Handling**: Always check returned `error` values explicitly (`if err != nil`), wrap errors with context (`fmt.Errorf("...: %w", err)`), and never discard errors via blank identifier (`_ = ...`) or trigger `panic(...)` in library packages.
4. **Package Cohesion & Zero Global State**: Organize cohesive, domain-oriented packages (`internal/`, `pkg/`, `cmd/`), avoid mutable package-level variables, and pass `context.Context` as the first parameter for I/O or cancellation boundaries.
