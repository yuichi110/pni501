# Code Quality Standards (Swift)

## Core Principles
1. **SwiftLint / swift-format Hygiene**: Enforce consistent formatting via `swift-format` and static lint rules via `SwiftLint`, avoiding bare `// swiftlint:disable:all` overrides (`AstFacts.unscoped_type_ignores == 0`).
2. **DocC Documentation Comments**: Document public modules, structs, classes, actors, protocols, and functions using `///` DocC markup (`- Parameters:`, `- Returns:`, `- Throws:`; `AstFacts.docstring_coverage_pct`, `AstFacts.missing_docstrings`).
3. **Zero Force-Unwraps & ARC Retain-Cycle Prevention**: Forbid force-unwrapping (`!`), `try!`, `as!`, and `fatalError()` in production logic (`AstFacts.bug_risk_idioms`); use `guard let`, `if let`, `throws`, and `[weak self]` in escaping closures to prevent reference cycles.
4. **Value Semantics & Actor Isolation**: Prefer immutable `struct`/`enum` value types over reference `class` hierarchies, avoid mutable `static var` global state (`AstFacts.global_state_usages`), and keep functions concise (`AstFacts.complex_functions`, `AstFacts.excessive_parameters`).

## Evaluation Thresholds
- **`PASS`**: `docstring_coverage_pct >= 80%`, zero production force-unwraps (`!`/`try!`/`as!`), zero unguarded `static var` globals, and scoped lint overrides.
- **`WARN`**: `docstring_coverage_pct` between `60%` and `79.9%`, or isolated complexity / ARC closure review items.
- **`FAIL`**: `docstring_coverage_pct < 60%`, pervasive `!`/`try!`/`as!` crash hazards, or data-race-prone mutable global `var` state.
