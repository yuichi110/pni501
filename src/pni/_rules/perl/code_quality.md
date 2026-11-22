# Code Quality Standards (Perl)

## Core Principles
1. **Mandatory `strict` & `warnings` Pragmas**: Every `.pl` and `.pm` file MUST enable `use strict; use warnings;` (or `use v5.36;` / `use Moo;` / `use Moose;` which implicitly enable both; `AstFacts.bug_risk_idioms`), formatted with `perltidy` and linted with `Perl::Critic`.
2. **Eliminate Classic Perl Security & I/O Sinks**: Always use lexical filehandles and **3-argument `open`** (`open my $fh, '<:encoding(UTF-8)', $path or die ...`) instead of vulnerable 2-argument `open($fh, "|$cmd")` (CWE-78); forbid string `eval $str` (CWE-94; block `eval { ... }` for exception trapping is acceptable) and single-string `system($cmd)` / backticks on untrusted input (`AstFacts.dangerous_sinks`).
3. **Lexical Scope & Zero Package Globals**: Declare variables with `my` rather than package-global `our` / `use vars` (`AstFacts.global_state_usages`), avoid bareword filehandles and indirect object notation (`new Foo`), and keep subroutines modular (`AstFacts.complex_functions`, `AstFacts.excessive_parameters`).
4. **POD Documentation**: Document public `.pm` modules and exported subroutines with POD (`=head1`, `=head2`, `=cut`; `AstFacts.docstring_coverage_pct`).

## Evaluation Thresholds
- **`PASS`**: `use strict; use warnings;` (or `use v5.36+`) everywhere, 3-arg `open` with lexical handles, zero string `eval`/shell-injection sinks, and POD documentation on public modules.
- **`WARN`**: Missing POD on helper modules or isolated `Perl::Critic` complexity/style warnings.
- **`FAIL`**: Missing `use strict`/`use warnings`, 2-argument `open` pipe injection, string `eval` RCE, or pervasive mutable package globals.
