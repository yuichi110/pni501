# Typing, Interfaces & Generics Standards (Go)

## Core Principles
1. **Consumer-Side Small Interfaces**: Define narrow, behavior-focused interfaces where they are consumed ("accept interfaces, return concrete structs").
2. **Avoid Untyped `any` / `interface{}`**: Prefer concrete types, narrow interfaces, or Go 1.18+ type parameters (`[T comparable]`, `[T any]`) over untyped `any` or `interface{}` in domain signatures.
3. **Avoid `unsafe.Pointer`**: Do not bypass the Go type system with `unsafe.Pointer` or `reflect` in business logic unless strictly required and isolated with thorough safety invariants.
4. **Scoped Linter Directives**: Never use bare `//nolint`; always scope exclusions to a specific analyzer with an inline rationale (`//nolint:errcheck // best-effort cleanup`).
