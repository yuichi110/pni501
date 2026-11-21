# Code Quality Standards (Python)

## Core Principles
1. **PEP 8 Compliance**: Follow PEP 8 style guide. Enforce formatting and linting with Ruff (`ProjectFacts.tooling_modernization_issues`).
2. **Docstrings**: Provide Google-style docstrings for all public modules, functions, and classes (`AstFacts.docstring_coverage_pct`, `AstFacts.missing_docstrings`, `AstFacts.empty_docstrings`, `AstFacts.doc_signature_mismatches`).
3. **Naming Conventions**: Use `snake_case` for functions/variables, `PascalCase` for classes, `UPPER_SNAKE_CASE` for constants.
4. **Line Length & Complexity**: Keep line lengths within 120 characters and functions concise and low-complexity (`AstFacts.complex_functions`, `AstFacts.excessive_parameters`).
5. **Shared Mutable State vs. Local Legacy Idioms**: Strictly distinguish active cross-request/thread race conditions (mutable module-level globals, singleton attributes, or mutable default arguments mutated at runtime: `AstFacts.global_state_usages`) from function-local deprecated/legacy stdlib calls or unused helpers (`AstFacts.bug_risk_idioms`, `AstFacts.modernization_hints`), reporting the latter as modernization debt rather than concurrent state corruption.

## Evaluation Thresholds
- **`PASS`**: `docstring_coverage_pct >= 80%`, `empty_docstrings == 0`, `doc_signature_mismatches == 0`, and zero high-severity `bug_risk_idioms` or unguarded `global_state_usages`.
- **`WARN`**: `docstring_coverage_pct` between `60%` and `79.9%`, or isolated style/complexity warnings.
- **`FAIL`**: `docstring_coverage_pct < 60%`, pervasive `complex_functions` / silent exception swallowing, or active shared mutable state race conditions.
