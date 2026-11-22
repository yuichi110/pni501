# Modern Vue 3 / Nuxt 3 Stack Idioms (`vue/modern_stack`)

## Core Principles
1. **Vue 3 Composition API & Pinia**: Migrate legacy Vue 2 Options API mixins, Vuex, `Vue.prototype`, and global event buses to `<script setup>`, composables (`use*`), and Pinia stores (`AstFacts.modernization_hints`).
2. **Vite & Modern Nuxt 3 Tooling**: Prefer Vite / Nuxt 3 (Nitro) over deprecated Vue CLI / Webpack 4, and use `defineModel()` (Vue 3.4+) for cleaner two-way bindings.
3. **SSR & Client Security Hygiene**: Guard browser-only globals (`window`, `document`, `localStorage`) inside `onMounted` or `import.meta.client` for SSR/Nuxt apps, never expose server secrets in `VITE_*` / `NUXT_PUBLIC_*` env vars (`AstFacts.hardcoded_secrets`, `AstFacts.scattered_env_access`), and configure request timeouts on `fetch` / `$fetch` / `axios` (`AstFacts.missing_io_timeouts`).
4. **Clean Telemetry**: Avoid stray `console.log` statements in production components (`AstFacts.unstructured_logging`).
