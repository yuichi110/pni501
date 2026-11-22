# Typing, Props/Emits Contracts & `vue-tsc` Standards (Vue)

## Core Principles
1. **TypeScript SFCs (`<script setup lang="ts">`) & `vue-tsc`**: Use `<script setup lang="ts">` with `tsconfig.json` `"strict": true` and run `vue-tsc --noEmit` in CI to type-check templates and scripts together (`AstFacts.type_safety_coverage_pct`).
2. **Type-Based Macros (`defineProps<T>()` / `defineEmits<T>()`)**: Declare strongly typed `defineProps<Props>()`, `defineEmits<Emits>()`, `defineSlots<Slots>()`, and `defineModel<T>()` contracts instead of untyped runtime array props (`defineProps(['foo', 'bar'])`) or `PropType<any>` (`AstFacts.weak_type_usages`).
3. **Typed Refs, Composables & Pinia Stores**: Explicitly type empty/nullable refs (`ref<User | null>(null)`), `InjectionKey<T>` for `provide`/`inject`, and composable return contracts; avoid `: any`, `as any`, and `@ts-ignore` (`AstFacts.type_safety_issues`, `AstFacts.unscoped_type_ignores`).
4. **Pure JS Vue Projects**: If a Vue repo intentionally uses plain JavaScript (no `typescript` dependency), evaluate runtime `defineProps({ ... })` validators (`type`, `required`, `validator`) and JSDoc rather than penalizing missing `.ts` syntax.

## Evaluation Thresholds
- **`PASS`**: `vue-tsc` strict type safety (`type_safety_coverage_pct >= 90%`), typed `defineProps`/`defineEmits`/`InjectionKey`, and zero `@ts-ignore` / `any` abuse.
- **`WARN`**: Partial typed props/emits or isolated `any` casts in component adapters.
- **`FAIL`**: Untyped array props across core components, pervasive `any`/`@ts-ignore`, or broken `vue-tsc` template contracts.
