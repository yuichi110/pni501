# Typing & JSDoc Contract Standards (JavaScript)

## Core Principles
1. **JSDoc Type Annotations (`@param` / `@returns`)**: Annotate all exported functions and methods with explicit JSDoc `@param {Type} name` and `@returns {Type}` contracts, or provide companion `.d.ts` declaration files.
2. **Type-Checked JavaScript (`// @ts-check` or `checkJs`)**: Enable `checkJs: true` in `jsconfig.json` / `tsconfig.json` or `// @ts-check` in core modules to catch type mismatches statically.
3. **Avoid Untyped `@param {*}` / `@param {any}`**: Model complex object contracts with `@typedef` or runtime schema validators (`zod` / `joi`) rather than untyped `any` / `*` shapes.
4. **Boundary Input Validation**: Validate external JSON payloads, URL parameters, and environment variables at module entry boundaries before property access.
