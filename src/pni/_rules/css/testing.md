# Stylelint, Visual-Regression & Accessibility Testing Standards (CSS)

## Core Principles
1. **Automated `stylelint` CI Gate**: Run `stylelint "**/*.css"` in CI catching invalid properties, duplicate selectors, unknown custom properties, and specificity regressions.
2. **Visual Regression & Responsive Viewport Checks**: Verify key UI states (mobile/tablet/desktop viewports, dark/light themes, RTL, 200% text zoom) via Playwright visual snapshots (`toHaveScreenshot()`) or Storybook/Chromatic where applicable.
3. **Contrast & Reduced-Motion Checks**: Validate computed foreground/background contrast ratios via `axe-core` / Lighthouse CI.
4. **DSL Exemption**: Evaluate CSS verification via `stylelint`, visual regression snapshots, and contrast checks rather than unit-test line coverage metrics.

## Evaluation Thresholds
- **`PASS`**: Automated `stylelint` gate + responsive/contrast verification in CI.
- **`WARN`**: CSS builds cleanly without `stylelint` or automated contrast checks.
- **`FAIL`**: Zero CSS lint/validation on large multi-stylesheet apps with broken layouts or contrast failures.
