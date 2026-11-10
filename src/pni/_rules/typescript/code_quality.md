# Code Quality Standards (TypeScript)

## Core Principles
1. **ESLint / Biome & Formatting**: Enforce ESLint (`@typescript-eslint`) or Biome and Prettier across all `.ts` and `.tsx` modules without unscoped disable comments.
2. **TSDoc / JSDoc Documentation**: Provide TSDoc (`/** ... */`) comments for all exported classes, interfaces, type aliases, functions, and React components.
3. **Immutability & Pure Functions**: Prefer `const` bindings, `readonly` properties/arrays, concise functions (<= 50 lines), and zero mutable module-level state.
4. **Error & Promise Hygiene**: Always handle rejected Promises (`try/catch` around `await` or `.catch(...)`), throw `Error` subclasses rather than strings, and avoid empty `catch {}` blocks or `==` loose equality.
