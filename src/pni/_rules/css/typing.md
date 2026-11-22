# Custom-Property Contracts, Units & Cascade Standards (CSS)

## Core Principles
1. **Explicit Units, Logical Properties & `@property` Registration**: Use semantic relative units (`rem`, `em`, `%`, `ch`, `dvh`) intentionally, prefer CSS logical properties (`margin-inline`, `padding-block`, `inset-inline-start`) for RTL/i18n readiness, and register animated/typed custom properties with `@property --name { syntax: '<color>'; inherits: false; initial-value: ...; }` where supported.
2. **DSL Exemption (Avoid False Positives)**: CSS is a declarative stylesheet language — do **NOT** apply software type-annotation rules. Evaluate contract clarity via disciplined design-token naming (`--surface-*`, `--text-*`, `--space-*`) and explicit `@layer reset, base, components, utilities;` ordering.
3. **Clean Shorthand vs Longhand Discipline**: Avoid accidental resets from shorthand properties (`background:`, `font:`, `border:`) clobbering inherited sub-properties.
4. **Zero Duplicate / Dead Declarations**: Eliminate duplicate properties within a rule block and unused legacy vendor prefixes (`-webkit-border-radius`, `-moz-box-shadow`) better handled by Autoprefixer/Lightning CSS.

## Evaluation Thresholds
- **`PASS`**: Consistent design-token naming, `@layer` / clean cascade order, relative units, and zero duplicate/dead vendor prefixes.
- **`WARN`**: Occasional hardcoded `px` font sizes or redundant vendor prefixes.
- **`FAIL`**: Conflicting cascade overrides, broken shorthand resets, or unmaintainable duplicate stylesheets.
