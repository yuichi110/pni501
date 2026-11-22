# Verilog / SystemVerilog Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for Verilog / SystemVerilog (`*.sv`, `*.v`, `rtl/`, `tb/`) repositories.

---

## 1. Mapping `targets` by RTL Project Layout

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Standard RTL + Testbench Repo** | `rtl/*.sv`, `tb/tb_*.sv`, `Makefile` | `source: ["rtl"]`<br>`tests: ["tb", "sim"]`<br>`docs: ["README.md"]` |
| **Hardware + Firmware/Software Monorepo** | `rtl/` (SV) + `fw/` (C/Rust) + `sim/` (Python/cocotb) | Create separate `scope: component` workflows + one `category: rollup` workflow (`includes:`) |

---

## 2. Selecting Verilog / SystemVerilog Actions & Rules

1. **Core Built-in Verilog Actions**:
   - `repo_structure_audit` (`verilog` scope): Auto-runs `project_inspect` for RTL/TB layout, filelists/FuseSoC/Makefile, and IP pinning.
   - `verilog_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="verilog"`) to extract module inventory, blocking/non-blocking hazards, inferred latch risks, width/CDC issues, and complexity.
   - `architecture_analysis` (`needs: [ast_and_quality]`): Records top-level modules, hierarchy instantiations, clock/reset domains, bus interfaces (AXI/Wishbone/valid-ready), and datapath flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `verilog_test_audit` (`needs: [ast_and_quality]`): Evaluates self-checking `tb/` / `cocotb` testbenches and assertions against `verilog/testing`.
   - `container_runtime_audit` (`needs: [repo_and_deps]`, `when: "has_runtime_harness"`): Builds an isolated Verilator / Icarus Verilog harness image via `.pni/dockerfiles/verilog/`, lints and simulates testbenches offline (`--network=none`), and evaluates `common/runtime_verification`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against workspace files/containers and correlates findings with AST issues.

---

## 3. Recommended `full_audit.yaml` DAG Template for Verilog / SystemVerilog

```yaml
id: full_audit
category: audit
name: Full RTL Health Audit & Report (Verilog / SystemVerilog)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic SystemVerilog AST analysis, Verilator/Icarus container simulation, security scan, grounded hardware architecture, score+SARIF emission, and Drawlib report.

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
    uses: verilog_ast_audit
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
    uses: verilog_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, runtime_verification, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
