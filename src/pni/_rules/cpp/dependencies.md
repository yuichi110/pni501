# Dependency & Build System Standards (C++)

## Core Principles
1. **Modern CMake / Meson & Explicit C++ Standard**: Use modern target-based `CMakeLists.txt` (`target_compile_features(... cxx_std_20)` or `cxx_std_17`/`cxx_std_23`) or `meson.build` declaring an explicit C++ standard (`ProjectFacts.language_version_constraint`).
2. **Reproducible Dependency Pinning**: Manage third-party libraries via `vcpkg.json` (manifest mode with `builtin-baseline`), `conanfile.txt`/`conanfile.py` + `conan.lock`, CMake `FetchContent` with pinned tag/commit + hash, or Meson `.wrap` checksums (`ProjectFacts.unpinned_dependencies`). Note that header-only or zero-dependency C++ libraries legitimately lack a package lockfile and must **NOT** be penalized.
3. **Sanitizer & Hardening Presets**: Define CMake presets (`CMakePresets.json`) or targets enabling ASan/UBSan/TSan for CI testing and compiler hardening flags for releases.
4. **SBOM & Vendored Source Auditing**: Track vendored third-party headers/sources explicitly so Trivy / CVE checks cover embedded dependencies.

## Evaluation Thresholds
- **`PASS`**: Explicit `C++17`/`C++20`/`C++23` standard, modern target-based build system, and pinned external dependencies (`unpinned_dependencies == 0`).
- **`WARN`**: Missing `CMakePresets.json` / sanitizer preset or minor unpinned test-only deps.
- **`FAIL`**: Legacy `C++98`/`C++11` without justification, unpinned mutable git fetches in production builds, or untracked vulnerable vendored libs.
