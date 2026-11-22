# Typing, `svelte-check` & Props Standards (Svelte)

## Core Principles
1. **Strict TypeScript (`<script lang="ts">`) & `svelte-check`**: Use `<script lang="ts">` with `"strict": true` in `tsconfig.json` and run `svelte-check --tsconfig ./tsconfig.json` in CI so template bindings and props are type-checked end-to-end (`AstFacts.type_safety_coverage_pct`).
2. **Typed `$props()` & SvelteKit `$types`**: Type component props explicitly via `let { user, onSave }: Props = $props();` (Svelte 5) or typed `export let` (Svelte 4), and import generated `./$types` (`PageServerLoad`, `Actions`, `RequestHandler`) in SvelteKit routes instead of manually typing `any` (`AstFacts.weak_type_usages`).
3. **Avoid `: any`, `as any` & `@ts-ignore`**: Eliminate untyped escape hatches and document rare `@ts-expect-error` usages with rationale (`AstFacts.type_safety_issues`, `AstFacts.unscoped_type_ignores == 0`).
4. **Pure JS Svelte Projects**: When a repository intentionally uses JavaScript without TypeScript, evaluate JSDoc `@type` annotations and `svelte-check` JS checking rather than penalizing missing `.ts` syntax.

## Evaluation Thresholds
- **`PASS`**: `svelte-check` clean (`type_safety_coverage_pct >= 90%`), typed `$props()` / `$types`, and zero `@ts-ignore` / `any` abuse.
- **`WARN`**: Partial prop typing or isolated `any` at third-party DOM adapter seams.
- **`FAIL`**: Pervasive `any` / `@ts-ignore` or broken `svelte-check` template contracts.
