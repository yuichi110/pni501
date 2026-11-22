# Dart Sass Compiler & Stylesheet Dependency Standards (SCSS)

## Core Principles
1. **Supported Dart Sass (`sass` >= 1.77 / `sass-embedded`)**: Use official Dart Sass (`sass` or `sass-embedded`) — strictly retire deprecated `node-sass` (LibSass EOL, insecure native bindings; `ProjectFacts.language_version_constraint`).
2. **Committed Lockfile & Clean `devDependencies`**: Place `sass`, `stylelint`, `stylelint-config-standard-scss`, and `postcss` in `devDependencies` with pinned versions and a single committed lockfile (`pnpm-lock.yaml` / `package-lock.json`; `ProjectFacts.lockfiles_found`).
3. **Zero Deprecated `~` Webpack Import Hacks**: Use Dart Sass `loadPaths` / `pkg:` importers instead of legacy `~package/...` tilde imports.
4. **Minimal Vendor Bloat**: Import only needed partials from large Sass frameworks (e.g., Bootstrap individual partials) rather than compiling unused modules.

## Evaluation Thresholds
- **`PASS`**: Dart Sass (`sass` / `sass-embedded`), committed lockfile, clean `devDependencies`, and zero `node-sass` or `~` legacy imports.
- **`WARN`**: Aging Dart Sass version emitting unresolved deprecation warnings.
- **`FAIL`**: Deprecated `node-sass` dependency, missing lockfile, or broken unpinned external CSS imports.
