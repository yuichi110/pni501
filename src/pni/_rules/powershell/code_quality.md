# Code Quality Standards (PowerShell)

## Core Principles
1. **Strict Mode, Error Handling & PSScriptAnalyzer**: Enforce `Set-StrictMode -Version Latest`, explicit `$ErrorActionPreference = 'Stop'` (or per-cmdlet `-ErrorAction Stop`), approved PowerShell Verb-Noun naming (`Get-Verb`), zero short aliases (`%`, `?`, `gci`, `cd`) in scripts, and `PSScriptAnalyzer` cleanliness (`AstFacts.bug_risk_idioms`, `AstFacts.unscoped_type_ignores == 0`).
2. **Eliminate Code Injection & Plaintext Secret Sinks**: Forbid `Invoke-Expression` (`iex`; CWE-94), never pass plaintext passwords instead of `[PSCredential]` / `[SecureString]` (`ConvertTo-SecureString -AsPlainText -Force` with hardcoded literals; CWE-798), and avoid `Write-Host` inside reusable functions (pollutes host stream instead of pipeline output; `AstFacts.dangerous_sinks`, `AstFacts.unstructured_logging`).
3. **Comment-Based Help**: Document every public function/script with Comment-Based Help (`.SYNOPSIS`, `.DESCRIPTION`, `.PARAMETER`, `.EXAMPLE`; `AstFacts.docstring_coverage_pct`).
4. **Scoped Variables & SupportsShouldProcess**: Avoid mutating `$global:` variables (`AstFacts.global_state_usages`), declare `[CmdletBinding(SupportsShouldProcess)]` on state-mutating functions, and keep functions modular (`AstFacts.complex_functions`, `AstFacts.excessive_parameters`).

## Evaluation Thresholds
- **`PASS`**: `Set-StrictMode -Version Latest`, zero `Invoke-Expression`/plaintext credentials/aliases, Comment-Based Help on public commands, and zero `$global:` state abuse.
- **`WARN`**: Missing `.EXAMPLE` / `.PARAMETER` help sections or isolated `Write-Host` in helper scripts.
- **`FAIL`**: `Invoke-Expression` on untrusted input, hardcoded plaintext secrets, empty `catch {}`, or unguarded `$global:` mutations.
