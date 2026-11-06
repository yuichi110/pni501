# Code Quality Standards (PHP)

## Core Principles
1. **PSR-12 & Clean Namespace Structure**: Adhere to PER Coding Style / PSR-12, organize classes under PSR-4 namespaces, keep `use` statements alphabetically sorted at the top of each file, and eliminate ad-hoc `include` / `require_once` chains in application logic.
2. **Separation of Concerns (Zero Spaghetti Templates)**: Strictly separate HTTP routing/input handling, domain business logic, database queries, and HTML presentation. Never mix raw SQL queries, business loops, and inline HTML output (`?>...<?php`) in a single script.
3. **Eliminate Superglobal & Global State Coupling**: Prohibit direct reads/writes to `$_GET`, `$_POST`, `$_REQUEST`, `$_SESSION`, `$_COOKIE`, `$_FILES`, `$GLOBALS`, and `global $var` inside domain or service code; encapsulate input in typed Request/DTO objects.
4. **Error Handling & PHPDoc Hygiene**: Never silence runtime failures with the `@` error-suppression operator or terminate domain logic with `die()` / `exit()`. Provide accurate `/** ... */` PHPDoc blocks aligned with parameter signatures on public classes, interfaces, and methods.
5. **State Bleed vs. Legacy Idiom Precision**: Distinguish active cross-request or persistent-worker state mutation (static mutable class properties in Octane/Swoole workers, unguarded `$_SESSION` / `$GLOBALS` writes) from method-local legacy PHP APIs or unused procedural helpers, classifying the latter accurately as modernization debt rather than runtime race conditions.
