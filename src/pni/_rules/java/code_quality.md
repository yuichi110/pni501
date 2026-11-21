# Code Quality Standards (Java)

## Core Principles
1. **Google Java Style & Static Analysis**: Adhere to Google Java Style Guide and enforce Checkstyle / SpotBugs / ErrorProne checks (`ProjectFacts.tooling_modernization_issues`).
2. **Javadoc Documentation**: Provide clear Javadoc (`/** ... */`) for all public classes, interfaces, records, enums, and public non-`@Override` methods (`AstFacts.docstring_coverage_pct`, `AstFacts.empty_docstrings`, `AstFacts.doc_signature_mismatches`).
3. **Naming Conventions**: Use `PascalCase` for types, `camelCase` for methods and fields, `UPPER_SNAKE_CASE` for `static final` constants, and lowercase reverse-domain names for packages.
4. **Immutability & Cohesion**: Prefer `final` fields, Java `record` value types, concise methods (`<= 50` lines, `AstFacts.complex_functions`, `AstFacts.excessive_parameters`), and zero mutable `static` state (`AstFacts.global_state_usages`, `AstFacts.bug_risk_idioms`).

## Evaluation Thresholds
- **`PASS`**: `docstring_coverage_pct >= 80%`, `doc_signature_mismatches == 0`, zero mutable `static` state race conditions, and clean import hygiene (`AstFacts.import_hygiene_coverage_pct >= 90%`).
- **`WARN`**: `docstring_coverage_pct` between `60%` and `79.9%`, or isolated complexity/import warnings.
- **`FAIL`**: `docstring_coverage_pct < 60%`, pervasive `complex_functions` / empty `catch` blocks, or active shared mutable singleton/static state hazards.
