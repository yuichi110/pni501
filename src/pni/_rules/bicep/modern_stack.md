# Modern Bicep & Azure Verified Modules Idioms (`bicep/modern_stack`)

## Core Principles
1. **Native `.bicepparam` Files & Typed Imports**: Prefer `.bicepparam` over legacy JSON `parameters.json` files, `@export()` shared types/functions across `.bicep` files, and Azure Verified Modules (`br/public:avm/...`) over hand-rolled boilerplate (`AstFacts.modernization_hints`).
2. **Zero Raw ARM JSON Templates**: Migrate hand-edited ARM `azuredeploy.json` templates to clean Bicep with string interpolation (`'${prefix}-kv'`) instead of `concat(...)`.
3. **Key Vault Secret References & Private Endpoints**: Reference secrets via `kv.getSecret('...')` on module boundaries rather than passing plaintext values, and disable public network access on PaaS data stores where VNet integration applies.
4. **Clean Tagging & Naming Governance**: Apply consistent resource tags (`environment`, `owner`, `costCenter`) across deployed resources via shared `var` / user-defined types.
