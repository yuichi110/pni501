# Typing & Strict Compiler Standards (TypeScript)

## Core Principles
1. **Strict Compiler Mode (`"strict": true`)**: Enable `"strict": true` (including `noImplicitAny`, `strictNullChecks`, and `noUncheckedIndexedAccess`) in `tsconfig.json`.
2. **Zero `any` & Safe Narrowing**: Never use `: any` or `as any`; use `unknown` at external I/O boundaries and narrow types via type guards, discriminated unions, or schema validators (`zod` / `valibot`).
3. **Explicit Public API Signatures**: Declare explicit parameter and return types on all exported functions, class methods, and public hooks so API contracts are compiler-enforced.
4. **No Unscoped `@ts-ignore`**: Never use `@ts-ignore` or `@ts-nocheck`; if a suppression is unavoidable, use `@ts-expect-error` with an explanatory reason.
