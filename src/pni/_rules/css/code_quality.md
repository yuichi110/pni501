# Code Quality, Cascade & Accessibility Standards (CSS)

## Core Principles
1. **Low Specificity & Zero `!important` Wars**: Keep selectors flat and class-based (BEM, CSS Modules, or `@layer` cascade layers), avoid ID selectors (`#nav`) and deep descendant chains (`> 3` levels), and reserve `!important` strictly for isolated utility overrides (`AstFacts.bug_risk_idioms`).
2. **Design Tokens & `stylelint` Hygiene**: Centralize colors, spacing, radii, z-index scales, and typography in `:root` custom properties (`--color-primary`, `--space-4`) rather than scattering magic hex colors/pixels, and enforce `stylelint` (`stylelint-config-standard`) + Prettier formatting.
3. **Accessibility-First Styling**: Never remove keyboard focus indicators (`outline: none` without a visible `:focus-visible` replacement!), respect `@media (prefers-reduced-motion: reduce)` for animations/transitions, use relative typography units (`rem`/`em` rather than fixed `px` blocking user zoom), and preserve WCAG AA color contrast (`>= 4.5:1`).
4. **Zero Unsafe `url()` / Remote `@import` Sinks**: Avoid `url("javascript:...")` or legacy `expression(...)` (`AstFacts.dangerous_sinks`), and avoid runtime remote `@import url("http://...")` (blocks rendering and leaks visitor metadata).

## Evaluation Thresholds
- **`PASS`**: `stylelint` clean, custom-property design tokens, flat low-specificity selectors, visible `:focus-visible` + `prefers-reduced-motion`, and zero `!important` abuse.
- **`WARN`**: Isolated magic color/z-index values or missing `prefers-reduced-motion` guard.
- **`FAIL`**: Global `outline: none` breaking keyboard accessibility, pervasive `!important` specificity wars, or unsafe remote/mixed-content `@import` URLs.
