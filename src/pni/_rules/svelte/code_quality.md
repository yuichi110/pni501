# Code Quality Standards (Svelte)

## Core Principles
1. **Svelte Check, ESLint & Component Hygiene**: Enforce `svelte-check`, `eslint-plugin-svelte`, and Prettier formatting, keep `.svelte` components cohesive, and avoid unscoped `eslint-disable` / `svelte-ignore` comments (`AstFacts.unscoped_type_ignores == 0`).
2. **Eliminate `{@html}` XSS & Dynamic Eval Sinks**: Never pass unsanitized user data into `{@html expr}` (CWE-79; sanitize explicitly via DOMPurify when rendering trusted rich text is unavoidable) or call `eval`/`new Function` (`AstFacts.dangerous_sinks`). Always provide a keyed `{#each items as item (item.id)}` key expression on mutable lists.
3. **SSR State Isolation (Zero Cross-Request Store Leaks)**: In SvelteKit apps, **never** store per-request / per-user data in module-level `writable()` stores or `$state` singletons (leaks state across SSR requests; `AstFacts.global_state_usages`) — pass request state through `load` / `setContext`.
4. **Effect Hygiene & Documentation**: Clean up event listeners/timers via return callbacks in `$effect` / `onMount`, keep components modular (`AstFacts.complex_functions`), and document public components/utilities (`AstFacts.docstring_coverage_pct`).

## Evaluation Thresholds
- **`PASS`**: Zero unsanitized `{@html}`/`eval` sinks, zero SSR cross-request module store leaks, keyed `{#each}` blocks, and clean `svelte-check` hygiene.
- **`WARN`**: Missing keys on minor lists, mixed Svelte 4/5 reactivity patterns, or isolated component complexity.
- **`FAIL`**: Unsanitized `{@html}` XSS sinks, cross-request SSR user-data store leaks, or bloated monolithic components with leaked subscriptions.
