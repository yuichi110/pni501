# Dependency & Build System Standards (C)

## Core Principles
1. **Modern Reproducible Build System**: Prefer `CMakeLists.txt` (`cmake_minimum_required(VERSION 3.20+)`, modern target-based `target_include_directories`/`target_compile_options`) or `meson.build` (or clean POSIX `Makefile`) declaring an explicit C standard (`C11`, `C17`, or `C23`; `ProjectFacts.language_version_constraint`).
2. **Pinned External Libraries & Vendoring Hygiene**: Pin external C library versions via `pkg-config` version bounds, CMake `FetchContent` with pinned tag + `URL_HASH`, Meson `.wrap` checksums, or `vcpkg.json`/`conanfile.txt` (`ProjectFacts.unpinned_dependencies`). Note that pure zero-dependency C libraries legitimately have no package lockfile and must **NOT** be penalized for lacking one.
3. **Hardening & Sanitizer Build Targets**: Provide CI/debug flags for `-fsanitize=address,undefined` (ASan/UBSan) and release hardening (`-D_FORTIFY_SOURCE=2`, `-fstack-protector-strong`, `-fPIE`).
4. **Vulnerability Tracking**: Track bundled/vendored third-party C sources explicitly (SBOM / `THIRD_PARTY_LICENSES`) so Trivy/CVE scanners detect vulnerable embedded libraries.

## Evaluation Thresholds
- **`PASS`**: Explicit C11+ standard, reproducible CMake/Meson/Make build with warning & sanitizer flags, and pinned/tracked external libraries.
- **`WARN`**: Missing sanitizer target or implicit host-installed library discovery without version checks.
- **`FAIL`**: Unpinned/untracked vendored C libraries with known CVEs, legacy C89/K&R flags without justification, or broken non-portable build scripts.
