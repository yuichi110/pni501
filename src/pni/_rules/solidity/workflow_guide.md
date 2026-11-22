# Solidity Workflow Authoring Best Practices (Workflow v2)

Use this guide alongside `common/workflow_guide` when designing or customizing `.pni/workflows/*.yaml` and `.pni/actions/*.yaml` for Solidity (`foundry.toml`, `hardhat.config.*`, `*.sol`) repositories.

---

## 1. Mapping `targets` by Solidity Project Layout

| Layout Archetype | Typical Directory Structure | Recommended `targets` Configuration |
| :--- | :--- | :--- |
| **Foundry Project** | `src/*.sol`, `test/*.t.sol`, `script/*.s.sol`, `foundry.toml` | `source: ["src"]`<br>`tests: ["test"]`<br>`exclude: ["lib/**"]` |
| **Hardhat Project** | `contracts/*.sol`, `test/*.ts`, `hardhat.config.ts` | `source: ["contracts"]`<br>`tests: ["test"]`<br>`exclude: ["node_modules/**", "artifacts/**"]` |
| **Full-Stack Web3 Monorepo (Contracts + TS Frontend)** | `contracts/`, `web/` | Create separate `scope: component` workflows (`solidity` + `typescript`) + one `category: rollup` workflow (`includes:`) |

---

## 2. Selecting Solidity Actions & Rules

1. **Core Built-in Solidity Actions**:
   - `repo_structure_audit` (`solidity` scope): Auto-runs `project_inspect` for `foundry.toml`/`hardhat.config.*`, compiler version, OpenZeppelin pinning, and supply-chain hygiene.
   - `solidity_ast_audit` (`needs: [repo_and_deps]`): Auto-runs `ast_analyze` via `tree-sitter` (`lang="solidity"`) to detect `tx.origin` auth (CWE-287), `delegatecall` (CWE-829), `selfdestruct`, unchecked low-level calls, NatSpec coverage, and complexity.
   - `architecture_analysis` (`needs: [ast_and_quality]`): Records contract inheritance trees, proxy/upgradeability patterns, external protocol/oracle calls, and asset flows into `.pni/cache/<workflow_id>/architecture.json`.
   - `solidity_test_audit` (`needs: [ast_and_quality]`): Evaluates Foundry/Hardhat unit, fuzz, and invariant test suites against `solidity/testing`.
   - `container_runtime_audit` (`when: "has_runtime_harness"`): Automatically skipped cleanly when no built-in Solidity container harness is configured (`has_runtime_harness=False`).
   - `security_vulnerability_audit` (`needs: [repo_and_deps]`): Runs Trivy (`security_scan`) against workspace dependencies and correlates findings with AST `dangerous_sinks`.

---

## 3. Recommended `full_audit.yaml` DAG Template for Solidity

```yaml
id: full_audit
category: audit
name: Full Smart-Contract Health Audit & Report (Solidity)
description: Workflow v2 DAG — Plan-First alignment, parallel deterministic Solidity AST/security analysis, grounded contract architecture, score+SARIF emission, and Drawlib report.

targets:
  root: "."
  source:
    - "contracts"
    - "src"
  tests:
    - "test"
    - "tests"
  docs:
    - "README.md"
  exclude:
    - "lib/**"
    - "node_modules/**"

steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: solidity_ast_audit
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
    uses: solidity_test_audit
    needs: [ast_and_quality]

  - id: output_score
    uses: emit_score
    needs: [arch_recording, test_health, runtime_verification, security_audit]

  - id: create_report
    uses: write_drawlib_report
    needs: [output_score]
```

Verify with `pni workflows show full_audit` and preview the validated Mermaid DAG with `pni workflows plan full_audit` before running `pni workflows start full_audit`.
