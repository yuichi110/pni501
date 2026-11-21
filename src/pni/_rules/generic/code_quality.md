# Generic Multi-Language Code Quality & Maintainability Standards

## Evaluation Thresholds (Deterministic `AstFacts`)
- **Unit Size**: Functions/methods/procedures > 50 effective lines (`complex_functions`) indicate decomposition debt.
- **Branching & Cognitive Complexity**: Branches > 7 or cognitive complexity > 15 (`complex_functions`) require refactoring into focused helpers.
- **Unit Interfacing**: > 6 parameters (`excessive_parameters`) should be replaced by cohesive config/DTO structures.
- **Mutable Global State**: Avoid mutable module-level globals (`global_state_usages`); pass dependencies explicitly.
- **Bug-Risk Idioms**: Eliminate language-specific unsafe constructs (`bug_risk_idioms`) such as unchecked panics/unwraps, `goto`/`ALTER`, `eval`, or silent error suppression.
- **Documentation**: Public APIs and exported modules should maintain clear header/doc comments (`docstring_coverage_pct >= 80%` when applicable).
