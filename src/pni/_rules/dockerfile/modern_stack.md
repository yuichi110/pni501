# Modern BuildKit & Distroless Container Idioms (`dockerfile/modern_stack`)

## Core Principles
1. **BuildKit Native Mounts**: Use `RUN --mount=type=cache,target=...` for package manager caches (`pip`/`uv`/`npm`/`cargo`/`go`), `--mount=type=bind` for lockfiles, and `--mount=type=secret` for private registries instead of `ARG TOKEN` (`AstFacts.modernization_hints`).
2. **Distroless / Chainguard / Slim Multi-Stage Final Images**: Ship compiled binaries (Go, Rust, C/C++) on `gcr.io/distroless/static:nonroot` or `scratch`, and interpreted runtimes on minimal `-slim` / Alpine non-root images.
3. **Graceful Signals & Read-Only Rootfs Readiness**: Design images to run with `--read-only` root filesystems and `--cap-drop=ALL`, writing ephemeral state strictly to `/tmp` or mounted volumes.
4. **SBOM & Provenance Attestations**: Generate SPDX/CycloneDX SBOMs and SLSA provenance (`docker buildx build --sbom=true --provenance=true`) in release pipelines.
