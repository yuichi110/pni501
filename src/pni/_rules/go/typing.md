# Typing, Interfaces & Generics Standards (Go)

## Core Principles
1. **Consumer-Side Small Interfaces**: Define narrow, behavior-focused interfaces where they are consumed ("accept interfaces, return concrete structs").
2. **Avoid Untyped `any` / `interface{}`**: Prefer concrete types, narrow interfaces, or Go 1.18+ type parameters (`[T comparable]`, `[T any]`) over untyped `any` or `interface{}` in domain signatures (`AstFacts.type_safety_coverage_pct`, `AstFacts.weak_type_usages`).
3. **Avoid `unsafe.Pointer`**: Do not bypass the Go type system with `unsafe.Pointer` or `reflect` in business logic unless strictly required and isolated with thorough safety invariants (`AstFacts.type_safety_issues`).
4. **Scoped Linter Directives**: Never use bare `//nolint`; always scope exclusions to a specific analyzer with an inline rationale (`//nolint:errcheck // best-effort cleanup`; `AstFacts.unscoped_type_ignores == 0`).

## Evaluation Thresholds
- **`PASS`**: `type_safety_coverage_pct >= 90%`, `unscoped_type_ignores == 0`, zero unjustified `unsafe.Pointer` usages, and minimal untyped `any`/`interface{}` in domain APIs.
- **`WARN`**: `type_safety_coverage_pct` between `70%` and `89.9%`, or isolated `any` / unscoped `//nolint` occurrences.
- **`FAIL`**: `type_safety_coverage_pct < 70%` or pervasive untyped `interface{}`/`any` or unsafe pointer casts in business logic.
