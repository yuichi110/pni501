# Code Quality Standards (JavaScript)

## Core Principles
1. **ESLint / Biome & Modern ES Modules**: Enforce ESLint or Biome and Prettier across all `.js`, `.jsx`, and `.mjs` files, preferring ES Modules (`import`/`export`) over legacy CommonJS (`require`).
2. **JSDoc Documentation**: Provide JSDoc (`/** ... */`) comments with `@param` and `@returns` tags for all exported classes, functions, and React components.
3. **Immutability & Lexical Scope**: Use `const` by default (`let` only when reassignment is required, never `var`), concise functions (<= 50 lines), and strict equality (`===` / `!==`).
4. **Error & Promise Hygiene**: Always handle rejected Promises (`try/catch` around `await` or `.catch(...)`), throw `Error` instances rather than strings, and avoid empty `catch {}` blocks.
