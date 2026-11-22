# Dependency & Package Management Standards (Svelte)

## Core Principles
1. **Supported Svelte 4/5, SvelteKit 2 & Node LTS**: Target Svelte `5.x` (or `4.x` with migration plan) and SvelteKit `2.x` on a supported Node LTS (`>= 20` / `22`) declared in `package.json` `engines.node` (`ProjectFacts.language_version_constraint`). Flag Svelte 3 (EOL) as modernization debt.
2. **Single Committed Lockfile**: Commit exactly one lockfile (`pnpm-lock.yaml`, `package-lock.json`, or `yarn.lock`; `ProjectFacts.lockfiles_found`) and pin `packageManager`.
3. **Clean `dependencies` vs `devDependencies`**: Place `svelte`, `@sveltejs/kit`, `vite`, `svelte-check`, `vitest`, and `@testing-library/svelte` in `devDependencies` (Svelte compiles components at build time; `ProjectFacts.unpinned_dependencies == 0`).
4. **Security Auditing**: Regularly audit npm dependencies via `pnpm audit` / `npm audit` and Trivy.

## Evaluation Thresholds
- **`PASS`**: Svelte `4.x`/`5.x` on Node LTS, single committed lockfile, `unpinned_dependencies == 0`, and clean dev/runtime separation.
- **`WARN`**: Missing `engines.node` or Svelte 4 project without Svelte 5 migration path.
- **`FAIL`**: EOL Svelte `3.x`, missing lockfile, `*`/`latest` specs, or unpatched high-severity CVEs.
