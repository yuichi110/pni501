# Generic Type Safety & Contract Standards

## Evaluation Criteria (`AstFacts`)
- **Explicit Interfaces**: Public functions, service boundaries, and data schemas should carry explicit types/contracts (`type_safety_coverage_pct` where applicable to the language).
- **Avoid Escape Hatches**: Minimize weak/unchecked type casts (`any`, `dynamic`, `unsafe`, `void*`, raw `Object`, `SuppressWarnings`/`#pragma warning disable`) and justify any unavoidable usage with a scoped comment.
- **Not Applicable Languages**: For dynamically typed scripting languages or pure configuration/IaC DSLs where static type annotations do not apply, mark type-safety metrics as `not_applicable` (`null`).
