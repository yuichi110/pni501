# VHDL Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for VHDL (`*.vhd`, `*.vhdl`, `rtl/`, `tb/`) repositories.

---

## 1. Mapping `targets` by VHDL Project Layout

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Standard RTL + Testbench Repo** | `rtl/*.vhd`, `tb/tb_*.vhd`, `run.py` or `Makefile` | `source: ["rtl"]`<br>`tests: ["tb", "sim"]`<br>`docs: ["README.md"]` |
| **Hardware + Software Monorepo** | `rtl/` (VHDL) + `sw/` (C/Python) | Create separate `scope: component` workflows + one `category: rollup` workflow (`includes:`) |

---

## 2. Selecting VHDL Actions & Rules

1. **Core Built-in VHDL Actions**:
   - `repo_structure_audit` (`vhdl` scope): Auto-runs `project_inspect` for RTL/TB layout, VUnit/FuseSoC/Makefile compile order, and IP pinning.
   - `vhdl_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="vhdl"`) to extract entity/architecture inventory, non-standard `std_logic_arith` usage, latch/sensitivity risks, shared variables, and complexity.
   - `architecture_analysis` (`needs: [ast_and_quality]`): Records top-level entities, hierarchy port maps, clock/reset domains, packages, and datapath flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `vhdl_test_audit` (`needs: [ast_and_quality]`): Evaluates self-checking `tb/` / VUnit / GHDL testbenches against `vhdl/testing`.
   - `container_runtime_audit` (`needs: [repo_and_deps]`, `when: "has_runtime_harness"`): Builds an isolated GHDL harness image via `.pni/dockerfiles/vhdl/ghdl.dockerfile`, analyzes and runs testbenches offline (`--network=none`), and evaluates `common/runtime_verification`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against workspace files/containers and correlates findings with AST issues.

---

## 3. Recommended `full_audit.yaml` DAG Template for VHDL

```yaml
id: full_audit
category: audit
name: Full RTL Health Audit & Report (VHDL)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic VHDL AST analysis, GHDL container simulation, security scan, grounded hardware architecture, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "rtl"
    - "src"
    - "hdl"
    - "."
  tests:
    - "tb"
    - "sim"
    - "tests"
  docs:
    - "README.md"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: vhdl_ast_audit
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

  - id: test_health
    uses: vhdl_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, runtime_verification, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
