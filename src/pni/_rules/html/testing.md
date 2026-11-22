# Markup Validation, Accessibility & Link-Check Standards (HTML)

## Core Principles
1. **HTML Validation (`html-validate` / Nu Html Checker)**: Validate static HTML and rendered template output in CI for syntax errors, duplicate IDs, and invalid nesting.
2. **Automated Accessibility Audits (`axe-core` / Lighthouse / Pa11y)**: Run `axe-core` (e.g., via Playwright `@axe-core/playwright`) or Lighthouse CI to verify zero critical WCAG 2.1 AA violations (contrast, landmarks, labels, keyboard focus).
3. **Broken-Link & Asset Verification**: Run link checkers (`lychee`, `drawlib serve --check`, or Playwright route crawls) so zero dead internal links or missing images ship.
4. **DSL Exemption**: Evaluate HTML verification via `html-validate`, `axe-core`, and broken-link checks rather than unit-test coverage metrics.

## Evaluation Thresholds
- **`PASS`**: Automated HTML validation + accessibility (`axe-core`/Lighthouse) + broken-link checks in CI.
- **`WARN`**: HTML renders in E2E tests without dedicated accessibility or link-integrity gates.
- **`FAIL`**: Zero markup/accessibility validation on public web pages containing broken DOM or severe WCAG failures.
