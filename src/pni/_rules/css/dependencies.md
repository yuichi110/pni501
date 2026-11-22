# External Stylesheet, Font & PostCSS Dependency Standards (CSS)

## Core Principles
1. **Local / Bundled Fonts & Stylesheets**: Prefer self-hosted `woff2` fonts (`font-display: swap`) and bundled CSS dependencies (`PostCSS` / `Lightning CSS` / `Tailwind`) over render-blocking third-party `@import url("https://fonts.googleapis.com/...")` inside CSS files.
2. **Explicit Browser Targets (`browserslist`)**: Declare supported browser targets in `browserslist` (`package.json` or `.browserslistrc`) so Autoprefixer / Lightning CSS generate exact, minimal compatibility prefixes.
3. **Zero-Lockfile Exemption**: Standalone CSS directories without a Node bundler legitimately omit a lockfile; when paired with PostCSS/Tailwind/Stylelint, commit the single package manager lockfile (`package-lock.json` / `pnpm-lock.yaml`).
4. **Minimal Unused CSS Bloat**: Purge unused utility/framework styles in production builds and avoid loading multiple overlapping CSS frameworks.

## Evaluation Thresholds
- **`PASS`**: Self-hosted or properly linked assets, explicit `browserslist` targets, zero render-blocking external `@import`, and lean production bundles.
- **`WARN`**: Missing `font-display: swap` or missing `.browserslistrc`.
- **`FAIL`**: Render-blocking third-party `http://` `@import`s or massive duplicate/unused CSS frameworks shipped unpurged.
