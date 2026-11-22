# Copybook, Compiler & Dependency Management Standards (COBOL)

## Core Principles
1. **Standard COBOL Dialect & Compiler Flags**: Document the target COBOL dialect (`COBOL-85`, `COBOL-2002`, `COBOL-2014`, IBM Enterprise COBOL, or GnuCOBOL `-std=cobol2014`) and build commands (`Makefile` / JCL / compile scripts) explicitly (`ProjectFacts.language_version_constraint`).
2. **Zero-Lockfile Exemption (Avoid False Positives)**: COBOL repositories typically do **not** use npm/Cargo-style package lockfiles — do **NOT** penalize a COBOL repository for lacking a package manager lockfile. Instead evaluate reproducibility via pinned copybook paths (`-I copybooks/`), deterministic build scripts, and explicit DB/CICS precompiler versions.
3. **Canonical Copybook (`.cpy`) Governance**: Centralize shared record layouts under `copybooks/` (or `cpy/`) without duplicate divergent copies of the same record across programs, and avoid circular `COPY` inclusions.
4. **Static Analysis & Toolchain Hygiene**: Enable compiler diagnostics (`cobc -Wall -Wextra -fdebugging-line` or IBM `FLAG(I,W)` / `SSRANGE` bounds checking during testing) and track any C/Java/SQL external subprogram libraries explicitly.

## Evaluation Thresholds
- **`PASS`**: Documented compiler dialect & reproducible build script, centralized copybooks without duplication, and compiler warning/bounds-check flags enabled.
- **`WARN`**: Missing explicit `-std=` dialect declaration or scattered duplicate copybooks.
- **`FAIL`**: Broken/undocumented build steps, divergent copybooks causing record corruption, or disabled compiler diagnostics hiding truncation warnings.
