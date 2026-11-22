# Token Maps, Built-In Modules & Mixin Contract Standards (SCSS)

## Core Principles
1. **Built-In `sass:*` Modules Over Deprecated Global Functions**: Use `math.div($a, $b)` (`@use 'sass:math'`), `map.get()`, `color.scale()`, and `list.nth()` instead of deprecated `/` slash division and global `lighten()`/`darken()`/`map-get()` functions (`AstFacts.modernization_hints`).
2. **DSL Exemption & Mixin Parameter Contracts**: SCSS is a stylesheet preprocessor — evaluate contract clarity via explicit `@mixin`/`@function` parameter defaults, `@error` validation for invalid token keys, and structured Sass maps (`$spacing: (sm: 0.5rem, md: 1rem)`).
3. **CSS Custom Properties for Runtime Theming**: Expose runtime theme tokens (`--color-bg`, `--color-fg`) as CSS custom properties rather than duplicating entire compiled theme stylesheets via Sass variables.
4. **Zero Unscoped Private Members**: Prefix internal helper variables, mixins, and functions with `_` (`$_internal-helper`) so `@forward` exposes only intentional public APIs.

## Evaluation Thresholds
- **`PASS`**: Built-in `sass:math`/`sass:map`/`sass:color` modules, validated mixin/function contracts, `_` private prefixing, and CSS custom properties for runtime themes.
- **`WARN`**: Occasional legacy global `map-get()` or `/` division warnings.
- **`FAIL`**: Unvalidated token lookups silently emitting broken `null` CSS declarations or global namespace collisions.
