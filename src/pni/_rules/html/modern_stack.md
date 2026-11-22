# Modern HTML5 & Web-Platform Idioms (`html/modern_stack`)

## Core Principles
1. **Native HTML Interactive Elements**: Prefer native `<dialog>`, `<details>`/`<summary>`, `<datalist>`, and the `popover` attribute over heavy custom JS modal/accordion re-implementations (`AstFacts.modernization_hints`).
2. **Modern Media & Performance**: Use `<picture>` with WebP/AVIF `<source>` fallbacks, `decoding="async"`, `loading="lazy"`, and `<link rel="preconnect">` purposefully.
3. **Security Headers & CSP Compatibility**: Keep markup compatible with strict nonce-based Content-Security-Policy (`script-src 'nonce-...'`, zero `'unsafe-inline'`).
4. **Clean Metadata**: Provide accurate `<title>`, `<meta name="description">`, canonical URL, and favicon links for public pages.
