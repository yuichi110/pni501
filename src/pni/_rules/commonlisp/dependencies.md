# Dependency & ASDF / Qlot Management Standards (Common Lisp)

## Core Principles
1. **Clean ASDF System Definitions (`*.asd`)**: Declare `:version`, `:license`, `:depends-on`, `:serial t` (or explicit component dependencies), and `:in-order-to ((test-op ...))` cleanly in `*.asd` targeting a supported implementation (SBCL `2.3+`, CCL, ECL; `ProjectFacts.language_version_constraint`).
2. **Reproducible Locking (`qlfile.lock` / `ocicl.csv` — App vs. Library Distinction)**:
   - **Deployed Services / Applications**: Pin Quicklisp dists/git commits via Qlot (`qlfile` + `qlfile.lock`) or `ocicl` (`ProjectFacts.lockfiles_found`).
   - **Pure Quicklisp / ASDF Libraries**: Omitting `qlfile.lock` is standard Common Lisp convention and must **NOT** be penalized.
3. **Separate Test System (`<sys>/tests`)**: Define a distinct secondary system (`defsystem "my-pkg/tests"`) in `*.asd` so test frameworks (`fiveam`, `rove`, `parachute`) never enter the primary system's `:depends-on`.
4. **CFFI & Security Auditing**: Document native C libraries loaded via `cffi:define-foreign-library` explicitly for reproducible builds and Trivy CVE auditing.

## Evaluation Thresholds
- **`PASS`**: Clean `*.asd` with separate `<sys>/tests` system, zero runtime test-framework leakage, and `qlfile.lock` on deployed apps (exempt for pure libraries).
- **`WARN`**: Missing `:in-order-to ((test-op ...))` wiring or unpinned Qlot git sources.
- **`FAIL`**: Broken/circular ASDF system definitions, undocumented external CFFI shared libs, or unpinned remote code loads.
