# Modern Svelte 5 / SvelteKit 2 Stack Idioms (`svelte/modern_stack`)

## Core Principles
1. **Svelte 5 Runes & Snippets**: Adopt `$state`, `$derived`, `$props`, `$bindable`, and `{#snippet}`/`{@render}` over legacy `$:` reactive labels, `createEventDispatcher`, and `<slot>` in Svelte 5 codebases (`AstFacts.modernization_hints`).
2. **Server-Only Secret Isolation**: Keep secret keys strictly inside `$env/static/private` / `$env/dynamic/private` and `*.server.ts` modules — never import private env vars or DB clients in client `.svelte` components (`AstFacts.hardcoded_secrets`, `AstFacts.scattered_env_access`).
3. **Hardened Fetch & Form Actions**: Pass `AbortSignal.timeout(...)` on outbound `fetch()` calls (`AstFacts.missing_io_timeouts`), validate SvelteKit form actions server-side (Zod/Valibot), and preserve built-in CSRF protection (`checkOrigin: true`).
4. **Clean Diagnostics**: Remove stray `console.log` calls from production components (`AstFacts.unstructured_logging`).
