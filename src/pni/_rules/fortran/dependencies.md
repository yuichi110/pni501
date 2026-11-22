# Dependency & Build Management Standards (Fortran)

## Core Principles
1. **Modern `fpm.toml` or Target-Based `CMakeLists.txt`**: Prefer Fortran Package Manager (`fpm.toml`) or modern `CMakeLists.txt` (or Meson) declaring compiler standard flags (`-std=f2018`, `-Wall -Wextra -fcheck=all`) cleanly (`ProjectFacts.language_version_constraint`).
2. **Zero-Lockfile Exemption (Avoid False Positives)**: Scientific Fortran libraries frequently depend only on BLAS/LAPACK/MPI or stdlib without an npm-style lockfile — do **NOT** penalize Fortran repos for lacking a lockfile when `fpm.toml` / CMake tags are pinned (`ProjectFacts.unpinned_dependencies`).
3. **Pinned External Dependencies**: Pin `fpm.toml` git dependencies to explicit `tag` or `rev` commits (never unpinned `branch = "main"`) and document BLAS/LAPACK/OpenMP/MPI system requirements.
4. **Compiler Bounds-Check Debug Builds**: Provide debug build flags enabling `-fcheck=bounds,mem,recursion -finit-real=snan -ffpe-trap=invalid,zero,overflow` to catch numerical and array bugs early.

## Evaluation Thresholds
- **`PASS`**: Reproducible `fpm.toml` / CMake build, pinned git tags/revs (`unpinned_dependencies == 0`), and debug bounds/FPE check flags documented.
- **`WARN`**: Missing compiler bounds-check debug profile or undocumented BLAS/MPI version requirements.
- **`FAIL`**: Unpinned mutable branch dependencies or broken non-portable hardcoded compiler path Makefiles.
