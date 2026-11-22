# Typing, Concurrency Safety & Protocols Standards (Swift)

## Core Principles
1. **Swift 6 Strict Concurrency & `Sendable`**: Enforce `Sendable` conformance across actor and `Task` boundaries, prefer `actor` isolation over manual locks, and avoid `@unchecked Sendable` unless internal synchronization invariants are documented (`AstFacts.type_safety_issues`).
2. **Avoid `Any` / `AnyObject` & Force Casts**: Prefer protocol existential bounds (`any Protocol`), opaque types (`some Protocol`), generics, and `enum` associated values over untyped `Any` / `AnyObject` dictionaries or `as!` downcasts (`AstFacts.type_safety_coverage_pct`, `AstFacts.weak_type_usages`).
3. **Typed Throws & Explicit Error Enums**: Model recoverable failures with `enum ... : Error` (and Swift 6 typed throws `throws(DomainError)` where appropriate) rather than stringly-typed errors or `nil` sentinels.
4. **Unsafe Pointer Isolation**: Confine `UnsafePointer` / `UnsafeMutableRawPointer` / `unsafeBitCast` strictly to audited C-interop wrappers.

## Evaluation Thresholds
- **`PASS`**: `type_safety_coverage_pct >= 95%`, zero `as!`/`Any` domain abuse, `Sendable`/actor discipline, and isolated unsafe pointer usage.
- **`WARN`**: Isolated `Any`/`@unchecked Sendable` at external serialization or C-interop boundaries.
- **`FAIL`**: Pervasive `Any` / `as!` casts, undocumented `@unchecked Sendable` data races, or raw pointer misuse in business logic.
