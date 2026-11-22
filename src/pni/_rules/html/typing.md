# Document Structure, Form Attributes & ARIA Contract Standards (HTML)

## Core Principles
1. **Valid HTML5 Document Structure & Attribute Contracts**: Enforce single `<h1>` per page with monotonic heading hierarchy (`h1 -> h2 -> h3`, never skipping levels for styling), unique `id` attributes across the document, and explicit `type="button"` on non-submit `<button>` elements inside `<form>` (`AstFacts.bug_risk_idioms`).
2. **DSL Exemption (Avoid False Positives)**: HTML is a declarative markup language — do **NOT** apply software type-annotation rules. Evaluate contract correctness via native form input types (`type="email"`, `required`, `autocomplete="..."`, `inputmode`), valid ARIA roles/attributes (`aria-label`, `aria-expanded`), and `sandbox` attributes on `<iframe>`.
3. **Hardened Forms & Iframes**: Use `method="POST"` with CSRF tokens on state-changing forms (never pass secrets/tokens in `GET` query strings) and lock down third-party `<iframe>` embeds with explicit `sandbox` and `allow` directives.
4. **No Deprecated Presentational Tags**: Eliminate obsolete HTML4 tags/attributes (`<font>`, `<center>`, `<marquee>`, `bgcolor`, `align`).

## Evaluation Thresholds
- **`PASS`**: Valid HTML5 nesting, unique IDs, explicit button/input types, valid ARIA, and hardened `<iframe>`/`<form>` attributes.
- **`WARN`**: Skipped heading levels or missing `autocomplete` attributes on auth forms.
- **`FAIL`**: Unsandboxed untrusted `<iframe>` embeds, sensitive credentials submitted via `GET`, or invalid broken DOM nesting.
