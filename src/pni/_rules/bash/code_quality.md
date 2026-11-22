# Code Quality Standards (Bash / Shell)

## Core Principles
1. **Strict Mode & Shebang Discipline**: Start executable scripts with a portable shebang (`#!/usr/bin/env bash` or `#!/bin/sh`) and enable strict error handling (`set -euo pipefail`; `AstFacts.bug_risk_idioms`). Format with `shfmt` and lint with `shellcheck`, scoping `# shellcheck disable=SCxxxx` directives with inline rationale (`AstFacts.unscoped_type_ignores == 0`).
2. **Double-Quote Every Variable Expansion**: Quote all variable and command expansions (`"$var"`, `"${arr[@]}"`, `"$(cmd)"`) to prevent word-splitting, globbing, and argument injection (CWE-78); avoid `eval`, unquoted `rm -rf $dir/*`, and parsing `ls` output (`AstFacts.dangerous_sinks`).
3. **Deterministic Temp Files & Signal Traps**: Create temporary files/directories with `mktemp` / `mktemp -d` and guarantee cleanup with `trap 'rm -rf "$tmp"' EXIT` rather than predictable `/tmp/foo` paths (CWE-377).
4. **Local Variables, Cohesion & Usage Docs**: Use `local` inside functions to prevent mutating global script state (`AstFacts.global_state_usages`), keep functions concise (`AstFacts.complex_functions`), and include top-of-file header comments plus `--help` usage output (`AstFacts.docstring_coverage_pct`).

## Evaluation Thresholds
- **`PASS`**: `set -euo pipefail` (or POSIX `set -eu`), zero `eval`/unquoted-expansion injection risks, `mktemp` + `trap` cleanup, `local` function variables, and ShellCheck cleanliness.
- **`WARN`**: Missing `local` on minor helpers, missing header comments, or isolated ShellCheck style warnings.
- **`FAIL`**: Missing strict mode combined with unsafe `eval`/`rm -rf $var`/predictable `/tmp` paths, or pervasive unquoted expansions on untrusted input.
