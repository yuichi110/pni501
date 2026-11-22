# Code Quality Standards (Vue)

## Core Principles
1. **Vue 3 `<script setup>` & ESLint Hygiene**: Enforce `eslint-plugin-vue` (`plugin:vue/vue3-recommended`) and Prettier/Biome formatting, keep SFCs cohesive (`<template>`, `<script setup>`, `<style scoped>`), and avoid unscoped `eslint-disable` comments (`AstFacts.unscoped_type_ignores == 0`).
2. **XSS & Template Safety**: Never pass unsanitized user data to `v-html` (CWE-79; sanitize explicitly with DOMPurify if unavoidable) or call `eval`/`new Function` inside component scripts (`AstFacts.dangerous_sinks`). Always pair `v-for` with a stable unique `:key` (never an array index for mutable lists) and never combine `v-if` and `v-for` on the same element.
3. **One-Way Data Flow & Lifecycle Cleanup**: Never mutate `props` directly inside child components (emit events or use `defineModel`), clean up timers/listeners/watchers in `onUnmounted` (`onScopeDispose`), and isolate cross-component state in Pinia stores rather than ad-hoc module globals (`AstFacts.global_state_usages`).
4. **Component Cohesion & Documentation**: Extract reusable domain logic into composables (`use*.ts`), keep components concise (`AstFacts.complex_functions`, `AstFacts.excessive_parameters`), and document public props/emits/composables with TSDoc/JSDoc (`AstFacts.docstring_coverage_pct`).

## Evaluation Thresholds
- **`PASS`**: Zero unsanitized `v-html`/`eval` sinks, consistent `<script setup>`, clean props/emit data flow, scoped styles, and `docstring_coverage_pct >= 70%` on public composables/props.
- **`WARN`**: Mixed Options API + Composition API, missing `:key` or minor component complexity warnings.
- **`FAIL`**: Unsanitized `v-html` XSS or `eval` sinks, direct prop mutations, or bloated monolithic SFCs with leaked listeners.
