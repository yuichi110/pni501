# Python Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for Python repositories.

---

## 1. Mapping `targets` by Python Project Layout

Inspect `pyproject.toml` (`[project]`, `[tool.uv]`, `[tool.poetry]`, `[tool.hatch]`) and top-level directories to configure `targets` accurately:

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Standard `src/` Layout** *(Recommended PEP 621)* | `src/<pkg>/`, `tests/`, `README.md` | `source: ["src"]`<br>`tests: ["tests"]`<br>`docs: ["README.md"]` |
| **Flat Package Layout** | `<pkg>/__init__.py`, `tests/` | `source: ["<pkg>"]` *(list explicit package dirs, NOT `"."`, so `tests/` or `reports_src/` are not mixed into source AST)* |
| **FastAPI / Web Service (`app/` Layout)** | `app/`, `migrations/`, `scripts/`, `tests/` | `source: ["app"]` *(exclude auto-generated Alembic `migrations/versions` from source AST)*<br>`tests: ["tests"]` |
| **Library + Internal Dev CLI** | `src/<pkg>/`, `tools/<cli>/`, `tests/` | Either audit `source: ["src"]` for the published package or create a separate `scope: component` workflow for `tools/` |
| **`uv` / Poetry Workspace or Multi-Language Monorepo** | `packages/core/`, `packages/api/`, `frontend/` | Create one `scope: component` workflow per package (`root: "packages/core"`) + one `category: rollup` workflow (`includes:`) for a unified report |

---

## 2. Selecting Python Actions & Framework/Modernization Rules

1. **Core Built-in Python Actions**:
   - `repo_structure_audit`: Auto-runs `project_inspect` (`pyproject.toml`, lockfiles, `py.typed`, detected frameworks, legacy scripts) + evaluates `python/dependencies`, `common/documentation`, `common/git_workflow`, `common/security`.
   - `python_ast_audit`: Auto-runs `ast_analyze` (`isort` import hygiene, type annotations & escape hatches, docstring coverage & `Args:` consistency, cognitive complexity, bug-risk idioms, circular & manifest dependencies, framework checks) + evaluates `common/architecture`, `python/code_quality`, `python/typing`, `python/modern_stack`.
   - `architecture_analysis` (`needs: [ast_and_quality]`): Runs 3-aspect architecture comprehension & grounding validation (`purpose_and_stack` -> `layers_and_modules` -> `flows_and_state`), persisting `.pni/cache/<workflow_id>/architecture.json`.
   - `python_test_audit` (`needs: [ast_and_quality]`): Evaluates test AST & structure (`assertion_free_tests`, module-to-test coverage) against `python/testing`.
   - `container_runtime_audit` (`needs: [repo_and_deps]`, `when: "has_runtime_harness"`): Builds an isolated Python harness image via `.pni/dockerfiles/.../Dockerfile`, runs `pytest` + `pytest-cov` offline (`--network=none`), probes `library`/`cli`/`web_api` startup health, and evaluates `common/runtime_verification`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against project files and the resolved container image (using shared `.pni/cache/trivy-cache/`), evaluating CVEs, IaC misconfigs, redacted secrets, AST `dangerous_sinks`, and `api_endpoints` against `common/security_vulnerability`.

2. **Framework-Specific & Archetype Customization**:
   - **FastAPI / Pydantic / SQLAlchemy / Typer Projects**: `python_ast_audit` automatically includes `python/modern_stack` and `python/frameworks/fastapi` (which marks `not_applicable` on non-FastAPI projects).
   - **Archetype & Security Extensions**: Add the matching archetype action (`service_readiness_audit` + `web_penetration_audit` for Web APIs/services, `cli_guidelines_audit` for CLIs, or `library_hygiene_audit` for libraries) with `needs: [ast_and_quality]`.
   - **DAG Parallelism**: Placing `ast_and_quality`, `runtime_verification`, and `security_audit` with `needs: [repo_and_deps]` lets Workflow v2 run all three deterministic analyzers in parallel via Auto-Advance.

---

## 3. Recommended `full_audit.yaml` DAG Template for Python

```yaml
id: full_audit
category: audit
name: Full Project Health Audit & Report (Python)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic Python AST, container runtime verification, Trivy security scan, 3-aspect grounded architecture, score+SARIF emission, and Drawlib report.

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
    uses: python_ast_audit
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
    uses: python_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, runtime_verification, security_audit]
    with:
      target: "full_audit"

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
    with:
      target: "full_audit"
      lang: "en"
      style: "google"
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
