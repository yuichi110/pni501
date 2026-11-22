# Modern CUDA (12.x) & GPU Programming Idioms (`cuda/modern_stack`)

## Core Principles
1. **Modern CUDA 12 & Cooperative / Async Primitives**: Prefer `cuda::std::*` (libcu++), `CUB` / `Thrust` block/warp primitives over hand-rolled error-prone reductions, `cudaMemcpyAsync` on explicit non-default `cudaStream_t` streams (avoid unnecessary `cudaDeviceSynchronize()` global stalls), and `cooperative_groups` / explicit sync warp masks (`__shfl_sync`, `__ballot_sync` instead of deprecated maskless `__shfl`; `AstFacts.modernization_hints`).
2. **Coalesced Global Memory & Shared-Memory Bank Safety**: Ensure adjacent threads in a warp access contiguous memory addresses, avoid shared-memory bank conflicts, and eliminate unnecessary host-device round trips.
3. **No Silent Warp-Synchronous Assumptions**: Never assume lockstep warp execution without `__syncwarp(mask)` (Volta+ Independent Thread Scheduling breaks implicit warp-sync code; `AstFacts.bug_risk_idioms`).
4. **Clean Host Diagnostics**: Avoid `printf` inside hot production kernels (`AstFacts.unstructured_logging`).
