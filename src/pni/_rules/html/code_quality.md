# Code Quality, Security & Accessibility Standards (HTML)

## Core Principles
1. **CSP Readiness & Zero Inline Script/Event-Handler XSS**: Avoid inline event handlers (`onclick="..."`, `onload="..."`, `onerror="..."`) and `javascript:` URLs (breaks strict Content-Security-Policy and invites XSS CWE-79; `AstFacts.dangerous_sinks`), and always pair `target="_blank"` links with `rel="noopener noreferrer"` (`AstFacts.bug_risk_idioms`).
2. **Semantic HTML5 Landmarks & WCAG 2.1 AA Accessibility**: Start documents with `<!DOCTYPE html>` and `<html lang="...">`, include `<meta charset="utf-8">` and `<meta name="viewport">`, use semantic landmarks (`<header>`, `<nav>`, `<main>`, `<footer>`, `<button>` instead of clickable `<div>`), provide meaningful `alt` text on `<img>`, and pair form controls with `<label for="...">`.
3. **Subresource Integrity (SRI) & HTTPS Only**: Every third-party CDN `<script src="https://...">` or `<link rel="stylesheet">` MUST use HTTPS and pin `integrity="sha384-..."` + `crossorigin="anonymous"` (CWE-829; `AstFacts.dangerous_sinks`) — never load mixed-content `http://` assets.
4. **Template Auto-Escaping & Clean Formatting**: In server templates (Jinja2/Twig/ERB/Go html/template), keep auto-escaping enabled (audit `|safe` / `raw` markers strictly), validate markup with `html-validate`, and keep templates clean and readable.

## Evaluation Thresholds
- **`PASS`**: Zero inline `on*` / `javascript:` XSS sinks, `rel="noopener noreferrer"` on `_blank`, SRI on CDN tags, semantic HTML5 + `<html lang>` + `alt`/`<label>` accessibility.
- **`WARN`**: Missing `alt` on minor decorative icons (`alt=""`), missing `rel="noopener"`, or non-semantic `<div>` buttons.
- **`FAIL`**: Inline `onclick`/unsanitized template `|safe` XSS sinks, unverified third-party HTTP/non-SRI CDN scripts, or broken accessibility blocking keyboard/screen-reader navigation.
