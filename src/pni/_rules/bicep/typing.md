# Parameter Typing, User-Defined Types & Decorators Standards (Bicep)

## Core Principles
1. **User-Defined Types (`type ... = { ... }`) & Union Literals**: Replace untyped `object` / `array` parameters with Bicep user-defined types (`type NetworkConfig = { vnetName: string, subnetPrefix: string }`) and string literal unions (`'dev' | 'staging' | 'prod'`) instead of opaque `object` bags (`AstFacts.type_safety_coverage_pct`, `AstFacts.weak_type_usages`).
2. **Constraint Decorators**: Apply `@minLength()`, `@maxLength()`, `@minValue()`, `@maxValue()`, and `@allowed([...])` (or literal unions) on public module parameters so invalid SKUs or names fail at compile/validate time.
3. **Explicit `targetScope` & `existing` Resources**: Declare `targetScope` explicitly (`'resourceGroup'`, `'subscription'`, `'managementGroup'`) and reference pre-existing resources via `resource kv 'Microsoft.KeyVault/vaults@...' existing` instead of untyped ID strings.
4. **Safe Null-Forgiving Discipline**: Minimize unchecked `!` non-null assertions in Bicep expressions (`AstFacts.type_safety_issues`).

## Evaluation Thresholds
- **`PASS`**: User-defined types / literal unions, constraint decorators, explicit `targetScope`, and zero untyped `object` bags on public modules.
- **`WARN`**: Isolated untyped `object` params on internal sub-modules.
- **`FAIL`**: Pervasive untyped `object`/`array` parameters masking schema errors or broken ARM property paths.
