# Code Quality Standards (CUDA)

## Core Principles
1. **Mandatory CUDA Error Checking After Every API Call & Kernel Launch**: Check `cudaError_t` on every `cudaMalloc`/`cudaMemcpy`/`cudaStream*` call via a `CUDA_CHECK(...)` macro, AND immediately check `cudaGetLastError()` after every `<<<grid, block>>>` kernel launch (asynchronous launches silently fail otherwise; `AstFacts.bug_risk_idioms`).
2. **Thread Bounds Guards & Warp-Divergence Synchronization Safety**: Guard global thread indices (`if (idx >= n) return;`) at kernel entry to prevent GPU out-of-bounds memory corruption (CWE-787), and **never** call `__syncthreads()` inside a thread-divergent conditional branch (causes permanent GPU deadlock!).
3. **RAII Device Memory Ownership**: Wrap `cudaMalloc` / `cudaMallocHost` / `cudaStream_t` / `cudaEvent_t` inside RAII wrappers (`thrust::device_vector`, `rmm::device_buffer`, or custom `std::unique_ptr` deleters) so host exceptions never leak GPU VRAM (`AstFacts.bug_risk_idioms`).
4. **Header Hygiene, Documentation & Zero Mutable Device Globals**: Document `__global__` kernels (grid/block assumptions, shared memory usage, alignment requirements) with Doxygen comments (`AstFacts.docstring_coverage_pct`), avoid mutable `__device__` globals (`AstFacts.global_state_usages`), and keep kernels modular (`AstFacts.complex_functions`).

## Evaluation Thresholds
- **`PASS`**: Checked `cudaError_t` + `cudaGetLastError()`, explicit kernel bounds checks, non-divergent `__syncthreads()`, RAII device memory management, and kernel doc comments.
- **`WARN`**: Missing kernel launch-grid documentation or isolated raw `cudaMalloc`/`cudaFree` pairs without exception safety.
- **`FAIL`**: Unchecked `cudaMalloc`/kernel launches, divergent `__syncthreads()` deadlock hazards, missing kernel bounds checks, or leaked VRAM allocations.
