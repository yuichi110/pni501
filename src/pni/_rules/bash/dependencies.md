# External Tooling & Runtime Dependency Standards (Bash / Shell)

## Core Principles
1. **Explicit Command Preflight Checks**: Verify required external binaries (`jq`, `curl`, `git`, `awk`) up front via `command -v <tool> >/dev/null 2>&1 || { echo "..."; exit 1; }` instead of failing mid-script with cryptic `command not found` errors.
2. **Zero-Lockfile Exemption (Avoid False Positives)**: Shell script repositories do **not** use npm/Cargo-style lockfiles — do **NOT** penalize Bash repositories for lacking a package lockfile. Evaluate reproducibility via documented minimum Bash/tool versions, containerized tooling, or pinned Nix/Dockerfile images.
3. **Zero `curl | bash` Remote Execution**: Never download and pipe unverified remote scripts straight into `sh`/`bash` (CWE-829; `AstFacts.dangerous_sinks`); verify SHA-256 checksums or install from signed OS/package registries.
4. **POSIX vs Bash Portability**: Match shebang (`#!/bin/sh` vs `#!/usr/bin/env bash`) strictly to syntax used (no bashisms in `#!/bin/sh` scripts) and avoid GNU-only flags (`sed -i`) without guarding macOS/BSD differences when cross-platform support is expected.

## Evaluation Thresholds
- **`PASS`**: Explicit `command -v` dependency checks, matched shebang/syntax, zero `curl | sh` remote code execution, and documented runtime prerequisites.
- **`WARN`**: Undocumented non-core CLI dependencies (`jq`/`yq`) without preflight verification.
- **`FAIL`**: Unverified `curl | bash` remote execution, broken shebang/bashism mismatches, or undocumented host mutations.
