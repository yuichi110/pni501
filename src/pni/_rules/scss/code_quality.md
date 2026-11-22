# Code Quality & Sass Architecture Standards (SCSS)

## Core Principles
1. **Modern `@use` / `@forward` Module System (Retire Legacy `@import`)**: Use namespaced `@use 'tokens' as t;` and `@forward` instead of deprecated `@import` (which leaks globals and duplicates compiled CSS across partials; `AstFacts.modernization_hints`).
2. **Shallow Nesting (`<= 3` Levels) & Prefer `@mixin` Over `@extend`**: Keep selector nesting shallow (`max-nesting-depth <= 3`) to prevent bloated high-specificity output CSS, prefer `@mixin` or CSS custom properties over `@extend` across unrelated components, and avoid `!important` wars (`AstFacts.bug_risk_idioms`).
3. **Stylelint SCSS & Accessibility Hygiene**: Lint with `stylelint-config-standard-scss`, preserve visible `:focus-visible` outlines and `prefers-reduced-motion` guards, and isolate design tokens cleanly (`_tokens.scss`).
4. **SassDoc Comments**: Document shared public `@mixin`, `@function`, and token maps with SassDoc (`/// @param ... @return ...`; `AstFacts.docstring_coverage_pct`).

## Evaluation Thresholds
- **`PASS`**: Dart Sass `@use`/`@forward`, nesting `<= 3`, `stylelint` clean, SassDoc on shared mixins/functions, and zero `!important`/focus-removal anti-patterns.
- **`WARN`**: Legacy `@import` partials awaiting migration or nesting depth 4 in isolated components.
- **`FAIL`**: Deprecated `node-sass` syntax, runaway deep nesting (`>= 5` levels) producing bloated CSS, or broken keyboard focus / accessibility overrides.
