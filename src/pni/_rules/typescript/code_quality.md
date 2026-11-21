# Code Quality Standards (TypeScript)

## Core Principles
1. **ESLint / Biome & Formatting**: Enforce ESLint (`@typescript-eslint`) or Biome and Prettier across all `.ts` and `.tsx` modules without unscoped disable comments (`ProjectFacts.tooling_modernization_issues`, `AstFacts.import_hygiene_coverage_pct`).
2. **TSDoc / JSDoc Documentation**: Provide TSDoc (`/** ... */`) comments for all exported classes, interfaces, type aliases, functions, and React components (`AstFacts.docstring_coverage_pct`, `AstFacts.doc_signature_mismatches`).
3. **Immutability & Pure Functions**: Prefer `const` bindings, `readonly` properties/arrays, concise functions (`<= 50` lines; `AstFacts.complex_functions`, `AstFacts.excessive_parameters`), and zero mutable module-level state (`AstFacts.global_state_usages`).
4. **Error & Promise Hygiene**: Always handle rejected Promises (`try/catch` around `await` or `.catch(...)`), throw `Error` subclasses rather than strings, and avoid empty `catch {}` blocks or `==` loose equality (`AstFacts.bug_risk_idioms`).

## Evaluation Thresholds
- **`PASS`**: `import_hygiene_coverage_pct >= 90%`, `docstring_coverage_pct >= 80%`, `doc_signature_mismatches == 0`, and zero high-severity `bug_risk_idioms` or unguarded `global_state_usages`.
- **`WARN`**: `docstring_coverage_pct` between `60%` and `79.9%`, or isolated complexity/style issues.
- **`FAIL`**: `docstring_coverage_pct < 60%`, pervasive empty catches / unhandled promises, or active shared mutable module state hazards.
