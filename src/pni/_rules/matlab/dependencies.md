# Toolbox & Dependency Management Standards (MATLAB)

## Core Principles
1. **Explicit MATLAB Release & Toolbox Dependencies**: Document the minimum MATLAB release (e.g., `R2022b+` / `R2024a+`) and required MathWorks toolboxes (verifiable via `matlab.codetools.requiredFilesAndProducts`) in `README.md` or `.prj` / `.mltbx` packaging metadata (`ProjectFacts.language_version_constraint`).
2. **Zero-Lockfile Exemption (Avoid False Positives)**: MATLAB repositories do **not** use npm/Cargo-style lockfiles — do **NOT** penalize MATLAB projects for lacking a lockfile. Evaluate reproducibility via MATLAB Project (`.prj`), pinned File Exchange / Git submodule dependencies, and documented GNU Octave compatibility when targeted.
3. **Clean Path Management**: Never hardcode developer machine paths (`addpath('C:\Users\...')`) in source files; resolve paths relative to `fileparts(mfilename('fullpath'))` or MATLAB Project path setup.
4. **MEX / External Binary Hygiene**: Track C/C++ MEX sources and external libraries explicitly for build reproducibility and security auditing.

## Evaluation Thresholds
- **`PASS`**: Documented MATLAB release and required toolboxes, zero hardcoded absolute `addpath` calls, and reproducible `.prj` or relative path setup.
- **`WARN`**: Missing explicit toolbox list or undocumented Octave compatibility status.
- **`FAIL`**: Hardcoded developer absolute paths (`C:\Users\...`), undocumented third-party `.p` obfuscated binaries, or broken MEX build steps.
