# Dependency & Cabal/Stack Management Standards (Haskell)

## Core Principles
1. **Supported GHC & PVP Version Bounds**: Declare explicit Haskell PVP bounds (`base >= 4.16 && < 5`, `text >= 2.0 && < 2.2`) in `*.cabal` or `package.yaml` targeting a supported GHC (`9.4+` / `9.6` / `9.8` / `9.10`; `ProjectFacts.language_version_constraint`, `ProjectFacts.unpinned_dependencies`).
2. **Reproducible Snapshots / Freeze Files**: Commit `stack.yaml` (with pinned LTS resolver) + `stack.yaml.lock` OR `cabal.project.freeze` for deployed applications/services (`ProjectFacts.lockfiles_found`). Pure Hackage libraries legitimately omit freeze files and must **NOT** be penalized.
3. **Clean Component Separation**: Separate `library`, `executable`, and `test-suite` stanzas in `*.cabal` so test dependencies (`hspec`, `QuickCheck`, `hedgehog`) never leak into library consumers.
4. **Security & Maintenance Auditing**: Track Hackage deprecation/security advisories (`cabal-audit` / `security-advisories` / Trivy).

## Evaluation Thresholds
- **`PASS`**: Supported GHC (`>= 9.2`), PVP bounds on library dependencies, clean `test-suite` stanza, and pinned Stack LTS / Cabal freeze file on apps.
- **`WARN`**: Unbounded upper versions on Hackage dependencies or missing `cabal.project`.
- **`FAIL`**: EOL GHC (`< 8.10`) without migration plan, missing resolver/freeze pin on production services, or vulnerable dependencies.
