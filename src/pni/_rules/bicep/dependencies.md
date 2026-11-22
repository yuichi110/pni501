# Module Registry & API Version Pinning Standards (Bicep)

## Core Principles
1. **Recent Stable Azure Resource API Versions**: Pin every `resource` declaration to a recent stable (non-preview unless explicitly required) Azure Resource Manager API version (`@2023-05-01`+; `ProjectFacts.language_version_constraint`).
2. **Pinned Registry & Verified Modules (`br/public:avm/...`)**: Reference Azure Verified Modules (`br/public:avm/res/...:x.y.z`) or private ACR module registries (`br:<registry>/bicep/modules/...:x.y.z`) with exact immutable SemVer tags — never `:latest` (`ProjectFacts.unpinned_dependencies`).
3. **Zero-Lockfile Exemption & `bicepconfig.json`**: Bicep pins exact versions inline in `module` declarations and `bicepconfig.json` rather than using an npm-style lockfile — do **NOT** penalize Bicep repos for lacking a separate lockfile.
4. **Policy & Security Auditing**: Validate Bicep modules with `PSRule.Rules.Azure`, `checkov`, or `trivy config`.

## Evaluation Thresholds
- **`PASS`**: Stable non-EOL ARM API versions, exact SemVer registry module tags (`unpinned_dependencies == 0`), and `bicepconfig.json` configured.
- **`WARN`**: Aging API versions (> 3 years old) or preview APIs without documented justification.
- **`FAIL`**: `:latest` module registry tags or deprecated ARM API versions broken on modern Azure services.
