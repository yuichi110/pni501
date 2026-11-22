# Module Manifest & Dependency Management Standards (PowerShell)

## Core Principles
1. **Explicit Module Manifests (`.psd1`) & `#Requires`**: For modules (`.psm1`), provide a complete `.psd1` manifest (`ModuleVersion`, `PowerShellVersion`, `RequiredModules` with pinned `ModuleVersion`/`RequiredVersion`, explicit `FunctionsToExport` — never `'*'`; `ProjectFacts.language_version_constraint`). For standalone scripts, declare `#Requires -Version 7.2` and `#Requires -Modules @{ ModuleName='...'; ModuleVersion='...' }`.
2. **Zero-Lockfile Exemption (Avoid False Positives)**: PowerShell repos typically pin module versions in `.psd1` / `RequiredModules.psd1` (PSDepend / PSResourceGet) rather than npm-style lockfiles — do **NOT** penalize lacking a separate lockfile when versions are pinned in `.psd1`.
3. **Clean Module Pinning**: Avoid unpinned `Install-Module -Force` without `-RequiredVersion` (`ProjectFacts.unpinned_dependencies`) or `AllowClobber` blind overrides.
4. **Security Auditing**: Verify PSGallery modules are signed/maintained and audit scripts/containers with `PSScriptAnalyzer` and Trivy.

## Evaluation Thresholds
- **`PASS`**: Supported PowerShell `7.2+` / `7.4` (or documented Windows PowerShell 5.1 compat), explicit `FunctionsToExport`, pinned `RequiredModules`, and `#Requires` headers.
- **`WARN`**: Wildcard `FunctionsToExport = '*'` in `.psd1` or missing `#Requires -Version`.
- **`FAIL`**: Unpinned runtime `Install-Module` calls inside production scripts, EOL PowerShell `< 5.1`, or unverified remote script execution.
