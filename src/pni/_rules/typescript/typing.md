# Typing & Strict Compiler Standards (TypeScript)

## Core Principles
1. **Strict Compiler Mode (`"strict": true`)**: Enable `"strict": true` (including `noImplicitAny`, `strictNullChecks`, and `noUncheckedIndexedAccess`) in `tsconfig.json` (`ProjectFacts.tooling_modernization_issues`).
2. **Zero `any` & Safe Narrowing**: Never use `: any` or `as any` (`AstFacts.weak_type_usages`); use `unknown` at external I/O boundaries and narrow types via type guards, discriminated unions, or schema validators (`zod` / `valibot`).
3. **Explicit Public API Signatures**: Declare explicit parameter and return types on all exported functions, class methods, and public hooks so API contracts are compiler-enforced (`AstFacts.type_safety_coverage_pct`, `AstFacts.type_safety_issues`).
4. **No Unscoped `@ts-ignore`**: Never use `@ts-ignore` or `@ts-nocheck` (`AstFacts.unscoped_type_ignores == 0`); if a suppression is unavoidable, use `@ts-expect-error` with an explanatory reason.

## Evaluation Thresholds
- **`PASS`**: `"strict": true` enabled, `type_safety_coverage_pct >= 90%`, `unscoped_type_ignores == 0`, and zero unjustified `any` casts.
- **`WARN`**: `type_safety_coverage_pct` between `70%` and `89.9%`, or isolated `any` / `@ts-ignore` occurrences.
- **`FAIL`**: `"strict": false` (or missing `tsconfig.json`), `type_safety_coverage_pct < 70%`, or pervasive `any` / `@ts-nocheck`.
