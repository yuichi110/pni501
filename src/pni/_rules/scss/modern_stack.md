# Modern Dart Sass & Native-CSS Interop Idioms (`scss/modern_stack`)

## Core Principles
1. **Migrate Off Legacy Sass Features Before Dart Sass 2.0**: Replace `@import` with `@use`/`@forward`, `/` division with `math.div()`, `lighten()`/`darken()` with `color.adjust()`/`color.scale()`, and mixed declarations after nested rules cleanly (`AstFacts.modernization_hints`).
2. **Prefer Native CSS Where Possible**: Use native CSS custom properties (`var(--*)`), `calc()`, `clamp()`, Grid/Flexbox, and `@layer` instead of redundant Sass compile-time wrappers.
3. **Automated Migration & Fast Builds**: Use `sass-migrator` for legacy upgrades and `sass-embedded` (or Vite built-in modern Sass API) for fast incremental builds.
4. **Zero Hardcoded Remote HTTP Assets**: Keep all `url(...)` asset references relative/bundled or HTTPS.
