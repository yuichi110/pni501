# Typing, Discriminated Unions & Units-of-Measure Standards (F#)

## Core Principles
1. **Domain Modeling with DUs & Records**: Make invalid states unrepresentable via Discriminated Unions (`type PaymentStatus = ...`), single-case wrapper DUs (`type UserId = UserId of Guid`), `Result<'T, 'Err>`, and `Option<'T>` rather than `null`, `obj`, or stringly-typed flags (`AstFacts.type_safety_coverage_pct`).
2. **Avoid Unsafe Downcasts (`:?`, `:?>`) & `unbox`**: Minimize runtime downcasts (`:?>`), `unbox`, and untyped `obj` signatures (`AstFacts.weak_type_usages`, `AstFacts.type_safety_issues`), and avoid `[<AllowNullLiteral>]` outside .NET C# interop boundaries.
3. **Explicit Public Signatures**: Annotate public APIs (via `.fsi` files or explicit parameter/return annotations) so Hindley-Milner inference cannot silently widen a signature to `obj` or break binary compatibility.
4. **Scoped `#nowarn` Directives**: Never add bare `#nowarn` disabling incomplete pattern-match warnings (`25`, `26`; `AstFacts.unscoped_type_ignores == 0`).

## Evaluation Thresholds
- **`PASS`**: Rich DUs/records/`Result`, zero unjustified `unbox`/`:?>`/`obj`, explicit public boundaries, and zero incomplete-match suppressions.
- **`WARN`**: Missing `.fsi` files on library modules or isolated `obj` casts at serialization/C# interop layers.
- **`FAIL`**: Disabled pattern-match warnings (`#nowarn "25"`), pervasive `unbox`/`obj`, or `[<AllowNullLiteral>]` domain types.
