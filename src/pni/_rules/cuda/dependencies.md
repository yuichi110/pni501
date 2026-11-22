# Dependency & CUDA Build Standards (CUDA)

## Core Principles
1. **Modern CMake CUDA Support & Explicit SM Architectures**: Use native CMake CUDA language support (`project(... LANGUAGES CXX CUDA)`, `CMAKE_CUDA_STANDARD 17/20`) and declare explicit `CMAKE_CUDA_ARCHITECTURES` (e.g., `80;86;89;90` or `native` for local builds) rather than deprecated `FindCUDA` (`ProjectFacts.language_version_constraint`).
2. **Pinned CUDA Toolkit & Library Versions**: Document minimum CUDA Toolkit version (`>= 12.0`) and required NVIDIA libraries (`cuBLAS`, `cuDNN`, `NCCL`, `CUTLASS`, `CUB`/`Thrust`), pinning external headers/submodules explicitly (`ProjectFacts.unpinned_dependencies`). Pure CUDA kernel repos legitimately omit npm-style lockfiles and must **NOT** be penalized.
3. **Compiler Diagnostics & Line-Info Flags**: Enable `-Xcompiler=-Wall,-Wextra` and `-lineinfo` (debug/profiling) in CMake build presets (`CMakePresets.json`).
4. **Cross-Architecture Portability**: Avoid hardcoding warp size `32` as a magic constant (use `warpSize`) or sm-specific intrinsics without `#if __CUDA_ARCH__ >= ...` guards.

## Evaluation Thresholds
- **`PASS`**: Native CMake CUDA with explicit `CMAKE_CUDA_ARCHITECTURES`, documented CUDA `>= 12.x` requirement, and pinned library/submodule deps.
- **`WARN`**: Missing `#if __CUDA_ARCH__` guards or deprecated `FindCUDA.cmake`.
- **`FAIL`**: Hardcoded legacy `sm_35`/`sm_50` targets removed from modern toolkits, unpinned mutable external fetches, or broken build scripts.
