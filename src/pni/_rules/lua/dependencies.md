# Dependency & LuaRocks Management Standards (Lua)

## Core Principles
1. **Explicit `*.rockspec` & Runtime Compatibility**: Declare the target Lua runtime version (`lua >= 5.1, < 5.5` or `LuaJIT 2.1`) and dependencies cleanly in `*.rockspec` (`ProjectFacts.language_version_constraint`), noting Lua 5.1/LuaJIT vs Lua 5.4 incompatibilities (`table.unpack` vs `unpack`, bitwise operators).
2. **Zero-Lockfile Exemption (Avoid False Positives)**: Embedded Lua plugins (Neovim, OpenResty, game engines) and standalone LuaRocks libraries commonly omit lockfiles — do **NOT** penalize lacking a lockfile unless a deployed OpenResty/app service has external LuaRocks dependencies without pinned versions (`ProjectFacts.unpinned_dependencies`).
3. **Pinned Rock Versions**: Specify bounded SemVer constraints (`>= 1.0, < 2.0` or exact pins) for production rocks and separate test-only rocks (`busted`, `luacov`, `luacheck`).
4. **Security & Host Sandbox Hygiene**: Audit C-binding rocks and OpenResty modules for maintenance and CVEs (Trivy).

## Evaluation Thresholds
- **`PASS`**: Explicit Lua/LuaJIT runtime target, bounded `*.rockspec` versions (`unpinned_dependencies == 0`), and clean runtime vs test tooling split.
- **`WARN`**: Missing explicit Lua version range in `*.rockspec` or unpinned dev rocks.
- **`FAIL`**: Unpinned external C-rock downloads in production OpenResty/server builds or broken Lua 5.1/5.4 runtime assumptions.
