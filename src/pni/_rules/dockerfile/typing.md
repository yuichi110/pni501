# Schema, Syntax & Build-Arg Contract Standards (Dockerfile)

## Core Principles
1. **Explicit BuildKit Syntax Directive & Typed `ARG` Defaults**: Declare `# syntax=docker/dockerfile:1` at line 1 to enable BuildKit mounts (`--mount=type=cache`, `--mount=type=secret`), provide safe explicit `ARG` defaults without secrets, and scope `ARG` declarations cleanly per build stage.
2. **DSL Exemption (Avoid False Positives)**: Dockerfiles are declarative container build recipes — do **NOT** apply software type-annotation or OOP rules. Evaluate structural clarity via explicit `AS <stage>` naming, OCI standard `LABEL` metadata (`org.opencontainers.image.*`), and exact `WORKDIR` absolute paths.
3. **Shell `pipefail` Discipline**: When using pipes (`|`) in `RUN` commands on Debian/Ubuntu/Alpine, set `SHELL ["/bin/bash", "-o", "pipefail", "-c"]` (or `set -o pipefail`) so upstream failures do not succeed silently (`AstFacts.bug_risk_idioms`).
4. **Explicit `EXPOSE` & Exec-Form Contracts**: Declare listening ports explicitly with `EXPOSE` and pass JSON-array exec form `["bin", "arg"]` to `ENTRYPOINT`/`CMD`.

## Evaluation Thresholds
- **`PASS`**: Explicit `# syntax=`, named stages, `SHELL` pipefail discipline, absolute `WORKDIR`, and exec-form `ENTRYPOINT`/`CMD`.
- **`WARN`**: Missing OCI `LABEL` metadata or shell-form `ENTRYPOINT`.
- **`FAIL`**: Broken multi-stage references, relative `WORKDIR` ambiguity, or silent pipe errors masking failed installs.
