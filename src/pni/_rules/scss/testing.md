# SCSS Compilation, Stylelint & Sass-True Testing Standards (SCSS)

## Core Principles
1. **Zero-Warning Sass Compilation & Stylelint CI Gate**: Compile all entrypoints with `sass --fatal-deprecation=...` and run `stylelint "**/*.scss"` in CI so deprecations, syntax errors, and nesting violations fail fast.
2. **Unit Tests for Complex Sass Functions/Mixins (`sass-true`)**: For shared design-system libraries with non-trivial Sass `@function` / `@mixin` logic, verify generated CSS deterministically with `sass-true` + Vitest/Jest (`AstFacts.test_functions_count`).
3. **Visual & Contrast Verification**: Validate compiled CSS output with responsive visual snapshots and WCAG contrast checks (`axe-core` / Lighthouse).
4. **DSL Exemption**: Evaluate SCSS verification via zero-warning compilation, `stylelint`, and `sass-true` / visual checks rather than line-coverage metrics.

## Evaluation Thresholds
- **`PASS`**: Automated `sass` build + `stylelint` CI gates (plus `sass-true` for complex design-system libraries).
- **`WARN`**: Compilation runs in CI without `stylelint` or deprecation warning flags.
- **`FAIL`**: Broken SCSS compilation or ignored Sass deprecation errors blocking compiler upgrades.
