# Code Quality & Container Hardening Standards (Dockerfile)

## Core Principles
1. **Non-Root Runtime User & Minimal Attack Surface**: Always drop root privileges before `CMD`/`ENTRYPOINT` via an explicit non-root `USER` (AVD-DS-0002; `AstFacts.bug_risk_idioms`), prefer multi-stage builds (`FROM ... AS builder` -> slim/distroless/scratch final stage), and provide a `.dockerignore` excluding `.git`, `.env`, caches, and credentials.
2. **Eliminate `:latest` Tags & Unverified Remote Execution**: Pin explicit base-image version tags or immutable `@sha256:...` digests — never `FROM image:latest` (AVD-DS-0001; `AstFacts.bug_risk_idioms`). Forbid `curl ... | sh` / `wget ... | bash` without SHA-256 verification (CWE-829; `AstFacts.dangerous_sinks`), and prefer `COPY` over `ADD` (prevents unintended remote URL fetches and tar-slip extraction).
3. **Zero Secrets in Build Layers**: Never bake credentials into `ENV`, `ARG`, or `COPY .env` (they persist permanently in `docker history` / image layers; `AstFacts.hardcoded_secrets`) — use BuildKit `--mount=type=secret` for build-time tokens.
4. **Layer Efficiency & Hadolint Hygiene**: Combine `apt-get update && apt-get install -y --no-install-recommends ... && rm -rf /var/lib/apt/lists/*` in a single `RUN` layer, use exec-form `ENTRYPOINT ["..."]` / `CMD ["..."]` so PID 1 receives `SIGTERM` cleanly, and lint with `hadolint`.

## Evaluation Thresholds
- **`PASS`**: Pinned base images, non-root `USER`, multi-stage/clean layers, zero `curl | sh` or baked secrets, and `hadolint` cleanliness.
- **`WARN`**: Missing `.dockerignore` or `HEALTHCHECK`, or shell-form `CMD`.
- **`FAIL`**: Root runtime container (`USER root` / missing `USER`), `:latest` base image, `curl | sh` remote code execution, or secrets committed in `ENV`/`ARG`.
