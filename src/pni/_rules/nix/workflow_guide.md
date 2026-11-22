# Nix Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when auditing Nix / NixOS / Flake repositories (`flake.nix`, `flake.lock`, `*.nix`).

---

## 1. Mapping `targets` by Nix Repository Layout

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **NixOS / Home-Manager Flake Repo** | `flake.nix`, `hosts/`, `modules/`, `pkgs/` | `source: ["."]`<br>`docs: ["README.md"]` |
| **App Repo with `flake.nix` DevShell** | `src/` (App) + `flake.nix` | Audit the primary app language (`scope: repo`) so `flake.nix` is scanned automatically as a Companion DSL |

---

## 2. Selecting Nix Actions & Rules

1. **Core Built-in Nix Actions**:
   - `repo_structure_audit` (`nix` scope): Auto-runs `project_inspect` for `flake.nix`, `flake.lock`, channel versions, and supply-chain hygiene.
   - `nix_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="nix"`) to detect `<nixpkgs>` impurity, `/nix/store` secret exposure, `with` shadowing, `rec` recursion traps, and module option typing.
   - `nix_test_audit` (`needs: [ast_and_quality]`): Evaluates `nix flake check`, `statix`/`deadnix`, and `runNixOSTest` gates against `nix/testing`.
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against workspace files/secrets and correlates findings with AST issues.

---

## 3. Recommended `full_audit.yaml` DAG Template for Nix

```yaml
id: full_audit
category: audit
name: Full Nix / NixOS Flake Audit & Report (Nix)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic Nix AST & security analysis, grounded module topology, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "."
  tests: []
  docs:
    - "README.md"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: nix_ast_audit
    needs: [repo_and_deps]

  - id: security_audit
    uses: security_vulnerability_audit
    needs: [repo_and_deps]

  - id: arch_recording
    uses: architecture_analysis
    needs: [ast_and_quality]

  - id: test_health
    uses: nix_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
