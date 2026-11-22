# Modern CSS (Grid, `@layer`, Nesting & Container Queries) Idioms (`css/modern_stack`)

## Core Principles
1. **CSS Grid, Flexbox & `gap` Over Legacy Floats**: Replace `float: left`/`clearfix` hacks and rigid table-based page layouts with CSS Grid, Flexbox, and `gap` (`AstFacts.modernization_hints`).
2. **Native CSS Nesting, `@layer` & Container Queries (`@container`)**: Adopt native CSS custom properties, `:is()`/`:where()` (zero-specificity wrappers), `@layer` cascade ordering, `clamp()` fluid typography, and `@container` component-responsive queries.
3. **GPU-Friendly Animations**: Animate `transform` and `opacity` instead of layout-thrashing `top`/`left`/`width`/`height` properties, and honor `prefers-reduced-motion`.
4. **Modern Color & Theming**: Use `color-scheme: light dark` and semantic CSS tokens (`light-dark(...)` / `oklch(...)` where browser support permits) for clean dark-mode theming.
