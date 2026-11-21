# Code Quality Standards (JavaScript)

## Core Principles
1. **ESLint / Biome & Modern ES Modules**: Enforce ESLint or Biome and Prettier across all `.js`, `.jsx`, and `.mjs` files (`ProjectFacts.tooling_modernization_issues`, `AstFacts.import_hygiene_coverage_pct`), preferring ES Modules (`import`/`export`) over legacy CommonJS (`require`).
2. **JSDoc Documentation**: Provide JSDoc (`/** ... */`) comments with `@param` and `@returns` tags for all exported classes, functions, and React components (`AstFacts.docstring_coverage_pct`, `AstFacts.doc_signature_mismatches`).
3. **Immutability & Lexical Scope**: Use `const` by default (`let` only when reassignment is required, never `var`), concise functions (`<= 50` lines; `AstFacts.complex_functions`, `AstFacts.excessive_parameters`), zero mutable module-level state (`AstFacts.global_state_usages`), and strict equality (`===` / `!==`).
4. **Error & Promise Hygiene**: Always handle rejected Promises (`try/catch` around `await` or `.catch(...)`), throw `Error` instances rather than strings, and avoid empty `catch {}` blocks (`AstFacts.bug_risk_idioms`).

## Evaluation Thresholds
- **`PASS`**: `import_hygiene_coverage_pct >= 90%`, `docstring_coverage_pct >= 80%`, `doc_signature_mismatches == 0`, and zero high-severity `bug_risk_idioms` or unguarded `global_state_usages`.
- **`WARN`**: `docstring_coverage_pct` between `60%` and `79.9%`, or isolated complexity/style issues.
- **`FAIL`**: `docstring_coverage_pct < 60%`, pervasive `var` / loose equality / empty catches, or active shared mutable module state hazards.
