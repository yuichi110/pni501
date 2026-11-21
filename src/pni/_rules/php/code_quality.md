# Code Quality Standards (PHP)

## Core Principles
1. **PSR-12 & Clean Namespace Structure**: Adhere to PER Coding Style / PSR-12, organize classes under PSR-4 namespaces, keep `use` statements alphabetically sorted at the top of each file (`AstFacts.import_hygiene_coverage_pct`), and eliminate ad-hoc `include` / `require_once` chains in application logic (`AstFacts.late_imports`).
2. **Separation of Concerns (Zero Spaghetti Templates)**: Strictly separate HTTP routing/input handling, domain business logic, database queries, and HTML presentation. Never mix raw SQL queries, business loops, and inline HTML output (`?>...<?php`) in a single script.
3. **Eliminate Superglobal & Global State Coupling**: Prohibit direct reads/writes to `$_GET`, `$_POST`, `$_REQUEST`, `$_SESSION`, `$_COOKIE`, `$_FILES`, `$GLOBALS`, and `global $var` inside domain or service code (`AstFacts.global_state_usages`); encapsulate input in typed Request/DTO objects.
4. **Error Handling & PHPDoc Hygiene**: Never silence runtime failures with the `@` error-suppression operator or terminate domain logic with `die()` / `exit()` (`AstFacts.bug_risk_idioms`). Provide accurate `/** ... */` PHPDoc blocks aligned with parameter signatures on public classes, interfaces, and methods (`AstFacts.docstring_coverage_pct`, `AstFacts.doc_signature_mismatches`).
5. **State Bleed vs. Legacy Idiom Precision**: Distinguish active cross-request or persistent-worker state mutation (static mutable class properties in Octane/Swoole workers, unguarded `$_SESSION` / `$GLOBALS` writes) from method-local legacy PHP APIs or unused procedural helpers, classifying the latter accurately as modernization debt rather than runtime race conditions.

## Evaluation Thresholds
- **`PASS`**: `import_hygiene_coverage_pct >= 90%`, `docstring_coverage_pct >= 80%`, `doc_signature_mismatches == 0`, and zero superglobal/error-suppression hazards in domain code.
- **`WARN`**: Moderate PHPDoc or complexity gaps without superglobal coupling or spaghetti templates.
- **`FAIL`**: Mixed SQL/HTML spaghetti scripts, pervasive `@` error suppression, or direct superglobal mutations in business logic.
