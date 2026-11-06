# Python Workflow Authoring Best Practices

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for Python repositories.

---

## 1. Mapping `targets` by Python Project Layout

Inspect `pyproject.toml` (`[project]`, `[tool.uv]`, `[tool.poetry]`, `[tool.hatch]`) and top-level directories to configure `targets` accurately:

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Standard `src/` Layout** *(Recommended PEP 621)* | `src/<pkg>/`, `tests/`, `README.md` | `source: ["src"]`<br>`tests: ["tests"]`<br>`docs: ["README.md"]` |
| **Flat Package Layout** | `<pkg>/__init__.py`, `tests/` | `source: ["<pkg>"]` *(list explicit package dirs, NOT `"."`, so `tests/` or `reports_src/` are not mixed into source AST)* |
| **FastAPI / Web Service (`app/` Layout)** | `app/`, `migrations/`, `scripts/`, `tests/` | `source: ["app"]` *(exclude auto-generated Alembic `migrations/versions` from source AST)*<br>`tests: ["tests"]` |
| **Library + Internal Dev CLI** | `src/<pkg>/`, `tools/<cli>/`, `tests/` | Either audit `source: ["src"]` for the published package or create a separate workflow for `tools/` |
| **`uv` / Poetry Workspace (Monorepo)** | `packages/core/`, `packages/api/` | Create one workflow per package (`core_audit.yaml` with `root: "packages/core"`, `api_audit.yaml` with `root: "packages/api"`) |

---

## 2. Selecting Python Actions & Framework/Modernization Rules

1. **Core Built-in Python Actions**:
   - `repo_structure_audit`: Runs `project_inspect` (`pyproject.toml`, lockfiles, `py.typed`, detected frameworks, legacy scripts) + evaluates `python/dependencies`, `common/documentation`, `common/git_workflow`, `common/security`.
   - `architecture_analysis`: Runs 3-aspect architecture comprehension & grounding validation (`purpose_and_stack` -> `layers_and_modules` -> `flows_and_state`), persisting `.pni/cache/<workflow_id>/architecture.json`.
   - `python_ast_audit`: Runs `ast_analyze` (`isort` import hygiene, type annotations & escape hatches, docstring coverage & `Args:` consistency, cognitive complexity, bug-risk idioms, circular & manifest dependencies, framework checks) + evaluates `common/architecture`, `python/code_quality`, `python/typing`, `python/modern_stack`.
   - `python_test_audit`: Runs test AST & structure evaluation (`assertion_free_tests`, module-to-test coverage) against `python/testing`.
   - `container_runtime_audit`: Builds an isolated Python harness image via `.pni/dockerfiles/.../Dockerfile`, runs `pytest` + `pytest-cov` offline (`--network=none`), probes `library`/`cli`/`web_api` startup health, and evaluates `common/runtime_verification`.
   - `security_vulnerability_audit`: Runs Trivy (`security_scan`) against project files and the resolved container image (using shared `.pni/cache/trivy-cache/`), evaluating CVEs, IaC misconfigs, redacted secrets, AST `dangerous_sinks`, and `api_endpoints` against `common/security_vulnerability`.

2. **Framework-Specific & Modernization Customization**:
   - **FastAPI / Pydantic / SQLAlchemy / Typer Projects**:
     Include `python/frameworks/fastapi` (when `fastapi` is in `pyproject.toml`) and `python/modern_stack` in your AST/architecture audit step's `rules:` list.
   - **Flask / Legacy `setup.py` / `argparse` / Fat `.sh` or `.pl` Repos**:
     Ensure `architecture_analysis` runs before `repo_structure_audit` or `python_ast_audit` interpretation so the system archetype (`rest_api` vs `web_ssr` vs `cli`) is established first—enabling accurate `Flask -> FastAPI` (for JSON APIs) and `argparse -> Typer` modernization recommendations without false positives.

---

## 3. Recommended `full_audit.yaml` Template for Python

```yaml
id: full_audit
name: Full Python Project Health Audit & Report
description: Complete deterministic Python AST/project inspection, 3-aspect architecture recording, rule evaluation, and Drawlib PDF report.

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

  - id: architecture_map
    uses: architecture_analysis

  - id: ast_and_quality
    uses: python_ast_audit

  - id: test_health
    uses: python_test_audit

  - id: runtime_verification
    uses: container_runtime_audit

  - id: security_audit
    uses: security_vulnerability_audit

  - id: output_score
    uses: emit_score
    with:
      target: "full_audit"

  - id: create_report
    uses: write_drawlib_report
    with:
      target: "full_audit"
      lang: "en"
      style: "google"
```

Verify with `pni workflows show full_audit` before running `pni workflows start full_audit`.
