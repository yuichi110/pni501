# External CDN, Font & Asset Dependency Standards (HTML)

## Core Principles
1. **Self-Host Critical Assets or Pin SRI-Verified CDN Versions**: Prefer bundling/self-hosting JS, CSS, and fonts (better privacy, offline reliability, and supply-chain control); when loading external CDNs (`unpkg`, `jsdelivr`, `cdnjs`), pin exact SemVer versions (never `@latest`) AND include `integrity="sha384-..."` (`ProjectFacts.unpinned_dependencies`, `AstFacts.dangerous_sinks`).
2. **Zero-Lockfile Exemption**: Pure static HTML / template directories do **not** require a lockfile unless paired with a Node/frontend build (`package.json`).
3. **Non-Blocking Script Loading**: Load scripts with `defer` or `type="module"` rather than render-blocking `<script>` tags in `<head>`, and set explicit `width`/`height` + `loading="lazy"` on below-the-fold images to prevent Cumulative Layout Shift (CLS).
4. **Security Auditing**: Audit linked third-party JS libraries (e.g. legacy jQuery `< 3.5`) for known XSS CVEs.

## Evaluation Thresholds
- **`PASS`**: Self-hosted or exact-version + SRI-verified HTTPS CDN assets, non-blocking `defer`/`module` scripts, and zero vulnerable legacy JS includes.
- **`WARN`**: Third-party CDN links missing `integrity` hashes or render-blocking `<head>` scripts.
- **`FAIL`**: Unpinned `@latest` CDN scripts, mixed-content `http://` scripts, or bundled vulnerable legacy JS libraries.
