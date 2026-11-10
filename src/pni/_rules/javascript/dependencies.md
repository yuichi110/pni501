# Dependency & Package Management Standards (JavaScript)

## Core Principles
1. **Standard `package.json` & Engines**: Declare project metadata, `engines.node` constraint, `"type": "module"` (ESM), and lint/test scripts cleanly in `package.json`.
2. **Committed Lockfile**: Commit a deterministic lockfile (`pnpm-lock.yaml`, `package-lock.json`, or `yarn.lock`) and avoid wildcard (`*`, `latest`) or unpinned git branch dependencies.
3. **Strict `dependencies` vs `devDependencies`**: Place linters (`eslint`, `@biomejs/biome`), bundlers (`vite`, `webpack`, `rollup`), and test runners (`vitest`, `jest`, `mocha`) in `devDependencies`.
4. **Supply Chain & Audit Hygiene**: Audit transitive npm packages regularly for CVEs and avoid unnecessary native postinstall scripts.
