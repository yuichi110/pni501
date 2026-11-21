# Typing & JSDoc Contract Standards (JavaScript)

## Core Principles
1. **JSDoc Type Annotations (`@param` / `@returns`)**: Annotate all exported functions and methods with explicit JSDoc `@param {Type} name` and `@returns {Type}` contracts (`AstFacts.type_safety_coverage_pct`, `AstFacts.type_safety_issues`), or provide companion `.d.ts` declaration files.
2. **Type-Checked JavaScript (`// @ts-check` or `checkJs`)**: Enable `checkJs: true` in `jsconfig.json` / `tsconfig.json` or `// @ts-check` in core modules to catch type mismatches statically (`AstFacts.unscoped_type_ignores == 0`).
3. **Avoid Untyped `@param {*}` / `@param {any}`**: Model complex object contracts with `@typedef` or runtime schema validators (`zod` / `joi`) rather than untyped `any` / `*` shapes (`AstFacts.weak_type_usages`).
4. **Boundary Input Validation**: Validate external JSON payloads, URL parameters, and environment variables at module entry boundaries before property access.

## Evaluation Thresholds
- **`PASS`**: `type_safety_coverage_pct >= 80%`, `unscoped_type_ignores == 0`, and boundary inputs schema-validated.
- **`WARN`**: `type_safety_coverage_pct` between `50%` and `79.9%`, or isolated `*`/`any` JSDoc annotations.
- **`FAIL`**: `type_safety_coverage_pct < 50%` or pervasive unvalidated external payloads across API boundaries.
