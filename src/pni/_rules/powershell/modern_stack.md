# Modern PowerShell 7+ & Automation Idioms (`powershell/modern_stack`)

## Core Principles
1. **PowerShell 7.4+ Cross-Platform Idioms**: Prefer PowerShell 7+ (`pwsh`) features (ternary `? :`, null-coalescing `??`, `Join-Path` over hardcoded `\` backslashes, `Microsoft.PowerShell.PSResourceGet` over legacy `PowerShellGet` v2; `AstFacts.modernization_hints`).
2. **Hardened HTTP & TLS**: Always pass `-TimeoutSec` to `Invoke-RestMethod` / `Invoke-WebRequest` (`AstFacts.missing_io_timeouts`) and never pass `-SkipCertificateCheck` in production (`AstFacts.dangerous_sinks`).
3. **Avoid Quadratic Array Concatenation**: Never accumulate objects in loops via `$arr += $item` (O(N^2) allocations); emit to pipeline or use `[System.Collections.Generic.List[object]]::new()`.
4. **Structured Output & Logging**: Use `Write-Verbose`, `Write-Warning`, `Write-Error`, and `Write-Information` streams instead of `Write-Host` (`AstFacts.unstructured_logging`).
