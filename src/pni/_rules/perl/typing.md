# Typing, Subroutine Signatures & Contract Standards (Perl)

## Core Principles
1. **Dynamic Typing Exemption & Runtime Validation**: Perl is dynamically typed — do **NOT** penalize Perl code for lacking compile-time static type annotations. Evaluate contract clarity via Perl 5.36+ subroutine signatures (`sub calc ($x, $y = 0) { ... }`), `Type::Params` / `Type::Tiny`, or `Moo`/`Moose` typed attributes (`isa => Str`).
2. **Avoid Unvalidated `@_` Unpacking & Symbolic References**: Prefer explicit subroutine signatures or structured named-parameter validation (`%args` checked against `Type::Params`) over sprawling positional `@_` indexing (`AstFacts.excessive_parameters`), and keep `no strict 'refs'` forbidden outside audited metaprogramming (`AstFacts.unscoped_type_ignores`).
3. **Explicit Numeric vs String Operators**: Distinguish numeric (`==`, `<`, `+`) from string (`eq`, `lt`, `.`) comparisons so implicit type coercion does not silently corrupt control flow (`AstFacts.bug_risk_idioms`).
4. **Structured Objects Over Deep Unblessed Hash Trees**: Use `Moo` / `Moose` / Perl 5.38+ `use feature 'class'` objects with explicit attribute validation for core domain models.

## Evaluation Thresholds
- **`PASS`**: Clear subroutine signatures or `Moo`/`Type::Tiny` parameter contracts, zero `no strict 'refs'` abuse, and disciplined numeric/string comparison hygiene.
- **`WARN`**: Legacy `@_` unpacking without validation or undocumented hash-ref parameter conventions.
- **`FAIL`**: `no strict 'refs'` symbolic-reference hazards, pervasive implicit coercion bugs, or opaque untyped hash-bag APIs across core modules.
