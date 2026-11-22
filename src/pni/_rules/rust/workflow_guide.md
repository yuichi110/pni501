# Rust Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for Rust (`Cargo.toml`) repositories.

---

## 1. Mapping `targets` by Rust Crate / Workspace Layout

Inspect `Cargo.toml` (`[package]`, `[workspace]`) to configure `targets` accurately:

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Single Crate (Bin or Lib)** | `src/lib.rs`, `src/main.rs`, `tests/`, `README.md` | `source: ["src"]`<br>`tests: ["tests", "src"]`<br>`docs: ["README.md"]` |
| **Cargo Workspace (Multi-Crate)** | `crates/core/src`, `crates/api/src`, root `Cargo.toml` | List workspace crate dirs in `source` (e.g. `["crates/core/src", "crates/api/src"]`) or create per-crate `scope: component` workflows + one `category: rollup` workflow |
| **Polyglot Monorepo (e.g. Python/TS + Rust)** | `backend/`, `frontend/`, `native/Cargo.toml` | Create a `scope: component` workflow (`targets.root: "native"`) and include it in a `category: rollup` workflow |

---

## 2. Selecting Rust Actions & Rules

1. **Core Built-in Rust Actions**:
   - `repo_structure_audit` (`rust` scope): Auto-runs `project_inspect` for `Cargo.toml`, `Cargo.lock` (exempting pure library crates), edition/MSRV, dependency pinning, and supply-chain hygiene.
   - `rust_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="rust"`) to extract wildcard imports, rustdoc coverage, `.unwrap()`/`.expect()`/`unsafe` idioms, `static mut` globals, cognitive complexity, `danger_accept_invalid_certs` / SQL / command CWE sinks, and Axum/Actix/Rocket routes.
   - `architecture_analysis` (`needs: [ast_and_quality]`): Records crate boundaries, entry points (`main.rs`, HTTP routers, CLI commands), module layering, and data/async flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `rust_test_audit` (`needs: [ast_and_quality]`): Evaluates `#[cfg(test)]` unit tests, `tests/` integration suites, assertion density, and coverage alignment against `rust/testing`.
   - `container_runtime_audit` (`needs: [repo_and_deps]`, `when: "has_runtime_harness"`): Builds an isolated Rust harness image via `.pni/dockerfiles/rust/cargo.dockerfile`, runs `cargo test` offline (`--network=none`), and evaluates `common/runtime_verification`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against `Cargo.lock` / workspace files and correlates findings with AST `dangerous_sinks`.

---

## 3. Recommended `full_audit.yaml` DAG Template for Rust

```yaml
id: full_audit
category: audit
name: Full Project Health Audit & Report (Rust)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic Rust AST/Cargo analysis, container runtime verification, Trivy security scan, 3-aspect grounded architecture, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "src"
  tests:
    - "tests"
  docs:
    - "README.md"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: rust_ast_audit
    needs: [repo_and_deps]

  - id: runtime_verification
    uses: container_runtime_audit
    needs: [repo_and_deps]
    when: "has_runtime_harness"

  - id: security_audit
    uses: security_vulnerability_audit
    needs: [repo_and_deps]

  - id: arch_recording
    uses: architecture_analysis
    needs: [ast_and_quality]

  # Optional archetype audit: service_readiness_audit | cli_guidelines_audit | library_hygiene_audit
  - id: test_health
    uses: rust_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, runtime_verification, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
