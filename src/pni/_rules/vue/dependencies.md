# Dependency & Package Management Standards (Vue)

## Core Principles
1. **Supported Vue 3 / Nuxt 3 & Node LTS**: Target Vue `3.4+` / `3.5+` (and Nuxt `3.x` when applicable) on a supported Node LTS (`>= 20` / `22`) declared via `engines.node` in `package.json` (`ProjectFacts.language_version_constraint`). Flag Vue 2 (`2.x`, EOL Dec 2023) as an urgent modernization/security risk.
2. **Committed Lockfile & Single Package Manager**: Commit exactly one lockfile (`pnpm-lock.yaml`, `package-lock.json`, or `yarn.lock`; `ProjectFacts.lockfiles_found`) and pin `packageManager` in `package.json`.
3. **Clean `dependencies` vs `devDependencies`**: Place build/test/lint tooling (`vite`, `vitest`, `vue-tsc`, `@vue/test-utils`, `eslint`, `prettier`) in `devDependencies`, avoid `*` or `latest` version specs (`ProjectFacts.unpinned_dependencies`), and avoid unused heavy UI libraries.
4. **Security Auditing**: Regularly audit npm packages with `pnpm audit` / `npm audit` and Trivy.

## Evaluation Thresholds
- **`PASS`**: Vue `3.x` on Node LTS, single committed lockfile, `unpinned_dependencies == 0`, and clean `dependencies` vs `devDependencies`.
- **`WARN`**: Missing `engines.node` or minor outdated build plugins.
- **`FAIL`**: EOL Vue `2.x` without migration plan, missing lockfile, `*`/`latest` dependencies, or high-severity unpatched CVEs.
