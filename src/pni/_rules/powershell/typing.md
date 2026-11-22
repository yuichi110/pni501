# Typing, Parameter Contracts & Validation Standards (PowerShell)

## Core Principles
1. **Explicit `[CmdletBinding()]` & Typed `param(...)` Blocks**: Annotate every function/script parameter with concrete .NET types (`[string]`, `[int]`, `[switch]`, `[PSCredential]`, `[System.IO.FileInfo]`) and `[Parameter(Mandatory)]` / validation attributes (`[ValidateNotNullOrEmpty()]`, `[ValidateSet(...)]`, `[ValidateRange(...)]`; `AstFacts.type_safety_coverage_pct`).
2. **Declared `[OutputType(...)]` & Structured `[PSCustomObject]`**: Declare `[OutputType([PSCustomObject])]` (or concrete `class` / .NET type) on exported functions and emit rich objects instead of pre-formatted `Format-Table` strings (never return formatted text from data functions).
3. **Avoid Untyped `[object]` / `$args` Bags**: Replace positional `$args` inspection and untyped hashtables with named typed parameters (`AstFacts.weak_type_usages`, `AstFacts.excessive_parameters`).
4. **Strict Null & Array Safety**: Guard empty/single-item pipeline returns with `@(...)` when array indexing is required and place `$null` on the left of equality comparisons (`$null -eq $val`).

## Evaluation Thresholds
- **`PASS`**: `[CmdletBinding()]` + typed `param(...)` with validation attributes on public functions, `[PSCustomObject]` outputs, and `$null -eq` discipline.
- **`WARN`**: Missing `[OutputType]` or isolated untyped internal helper parameters.
- **`FAIL`**: Untyped `$args` parsing across public functions, `Format-Table` returned from library functions, or `$val -eq $null` array-filtering bugs.
