# Code Quality Standards (Ruby)

## Core Principles
1. **RuboCop & Frozen Strings**: Include `# frozen_string_literal: true` at the top of Ruby source files, format and lint with RuboCop (`rubocop`, `rubocop-rails`, `rubocop-rspec`), and scope `# rubocop:disable` comments to specific cops with inline rationale (`AstFacts.unscoped_type_ignores == 0`).
2. **YARD / RDoc Documentation**: Document public modules, classes, and methods using YARD (`@param`, `@return`, `@raise`) or RDoc comments (`AstFacts.docstring_coverage_pct`, `AstFacts.missing_docstrings`).
3. **Avoid Unsafe Metaprogramming & Bare Rescues**: Never rescue `Exception` or use empty `rescue` blocks that silently swallow errors; forbid dynamic `eval`, `instance_eval`, `class_eval`, `send` on untrusted input, or unsafe `YAML.load` / `Marshal.load` (`AstFacts.bug_risk_idioms`, `AstFacts.dangerous_sinks`).
4. **Zero Mutable Global / Class-Variable State**: Avoid `$global` variables and `@@class_variables` shared across requests/threads (`AstFacts.global_state_usages`); keep service objects and methods cohesive (`AstFacts.complex_functions`, `AstFacts.excessive_parameters`).

## Evaluation Thresholds
- **`PASS`**: `docstring_coverage_pct >= 80%`, `# frozen_string_literal: true` consistent, zero bare `rescue Exception` / `eval` / `@@class_variable` races, and scoped RuboCop disables.
- **`WARN`**: `docstring_coverage_pct` between `60%` and `79.9%`, or isolated method complexity / RuboCop style warnings.
- **`FAIL`**: `docstring_coverage_pct < 60%`, unsafe `eval`/`YAML.load`/`Marshal.load` on untrusted data, or pervasive mutable class/global state.
