# Dependency & Package Management Standards (JavaScript)

## Core Principles
1. **Standard `package.json` & Engines**: Declare project metadata, supported `engines.node` constraint (Node 20/22+ LTS), `"type": "module"` (ESM), and lint/test scripts cleanly in `package.json`.
2. **Committed Lockfile (Archetype-Aware)**: Commit a deterministic lockfile (`pnpm-lock.yaml`, `package-lock.json`, or `yarn.lock`; `ProjectFacts.lockfiles_found`) for applications and services, and avoid wildcard (`*`, `latest`) or unpinned git branch dependencies (`ProjectFacts.unpinned_dependencies`).
3. **Strict `dependencies` vs `devDependencies`**: Place linters (`eslint`, `@biomejs/biome`), bundlers (`vite`, `webpack`, `rollup`), and test runners (`vitest`, `jest`, `mocha`) in `devDependencies`, with zero undeclared/unused runtime imports (`AstFacts.undeclared_dependencies`, `AstFacts.unused_dependencies`).
4. **Supply Chain & Audit Hygiene**: Audit transitive npm packages regularly for CVEs and avoid unnecessary native postinstall scripts.

## Evaluation Thresholds
- **`PASS`**: Clean `package.json` with `engines.node`, committed lockfile (for apps/services), `unpinned_dependencies == 0`, and `undeclared_dependencies == 0`.
- **`WARN`**: Missing `engines.node` or minor unused dependencies.
- **`FAIL`**: Wildcard (`*`/`latest`) dependencies, missing lockfile on deployed apps, or undeclared runtime imports.
