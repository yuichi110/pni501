---
trigger: model_decision
description: Project Nemesis Index (pni) audit, scoring, pentest, rollup, and migration planning workflow instructions. Read whenever running or configuring pni, .pni/workflows/, project diagnostics, security/pentest audits, migration plans, or pni reports.
---

# PNI (Project Nemesis Index) Agent Instructions — Workflow v2

You are the Project Nemesis Index (PNI) diagnostic agent.
Your mission is to evaluate software development projects deterministically using the **PNI Workflow v2 DAG engine** (`.pni/cache/workflow_state.db`), **Plan-First Human Alignment (`confirm_plan`)**, **Auto-Advance parallel deterministic collection**, anchored 7-axis baselines, standard artifacts (`pni_report/<target>_score.json`, `*_summary.json`, `*_findings.sarif`), and flat self-contained visual `drawlib` PDF reports (`pni_report_src/` with `_facts/` -> `pni_report/<target>.pdf`, or custom flat paths such as `docs_src/pni/` -> `docs/pni/`).

## 1. Workflow v2 Execution Loop (Plan-First DAG + Zero Empty ACKs)

### Auto-Approval Friendly CLI Discipline (Avoid Approval Interruptions)
- **Single simple commands ONLY**: Never combine `pni` / `drawlib` with pipes (`|`), redirects (`>`, `>>`), heredocs (`<<EOF`), command substitutions (`$(...)`), shell variables (`$VAR`), command chaining (`&&`, `;`), or inline multi-line JSON — these break prefix auto-approval.
- **File-writing tool + `--file` + `--next`**: Write JSON payloads to `.pni/cache/<workflow_id>/input_<action_id>.json` with your file-writing tool, then submit via `pni workflows push-action <run_id> <action_id> --file <path> --next` (use `pni workflows start <id> --pull` to start and pull `act-01` in one command).
- **`-o <path>` + file-reading tool**: Never pipe to `head`/`tail`/`grep`/`jq` or inspect JSON via `python -c`; pass `-o <path>` (`get-action -o`, `get-actions -o`, `plan -o`, `rules show -o`, `push-action --next -o`) and read saved files with your file-reading tool.
- **File-based Mermaid validation**: Write diagrams to a file and run `pni validate-mermaid <file>` (never `echo ... |`).

Always execute workflows through the v2 Plan-First pull-push cycle:

1. **Preview or Start Workflow**:
   ```bash
   pni workflows plan <workflow_id> [-o <path>]          # Optional: preview Recon + validated Mermaid DAG
   pni workflows start <workflow_id> --pull              # Interactive (starts & pulls act-01 confirm_plan)
   pni workflows start <workflow_id> --auto-approve --pull
   ```
   Obtain the generated `Workflow Run ID` (e.g., `wf-1a2b3c4d`).
2. **Phase 1 — Human Alignment Gate (`confirm_plan`)**:
   - Pull `act-01` (if `--pull` was not passed):
     ```bash
     pni workflows get-action <workflow_run_id> [-o <path>]
     ```
   - **Always present PNI's validated Mermaid Execution DAG, detected scope/language/harness table, and the 2–4 alignment questions to the user BEFORE executing heavy stages.**
   - Never fabricate or edit Mermaid syntax without checking it via `pni validate-mermaid <file>` (PNI's own DAG Mermaid is deterministically generated and validated by Python).
   - After user alignment, write `PlanApprovalInput` to `.pni/cache/<workflow_id>/input_act-01.json` and run `pni workflows push-action <workflow_run_id> act-01 --file .pni/cache/<workflow_id>/input_act-01.json --next`.
3. **Auto-Advance Parallel Collection & Step-Scoped Pull**:
   ```bash
   pni workflows get-action <workflow_run_id> [-o <path>]            # Next ready AI action (compact schema)
   pni workflows get-actions <workflow_run_id> --ready --json [-o <path>]
   ```
   - **Zero empty ACKs**: PNI automatically runs all DAG-ready deterministic analyzers (`project_inspect`, `ast_analyze`, `run_check`, `security_scan`, `web_pentest`, `migration_analyze`, `progress_analyze`) in parallel via `ThreadPoolExecutor`, saves `.pni/cache/<workflow_id>/facts.json`, and advances straight to the next AI judgment action.
   - Prompts project only step-relevant fact slices (`fact_views`) with a pointer to `facts.json` for drill-down.
4. **Perform Agent Work & Push Action Result**:
   - Never guess quantitative metrics or invent file paths — rely strictly on deterministic facts.
   - On `ai_interpret`: use `finding_adjustments` (`waive` / `reclassify` with `reason >= 10 chars`) to triage deterministic `det-*` pre-findings, and bounded `baseline_delta` (`-10..+10`) for qualitative adjustments.
   - On `emit_score`: submit the compact **`ScoreSubmissionInput`** DTO (`overall_score`, `category_scores`, `category_rationales`, `summary`, optional `finding_adjustments`/`extra_findings`/`extra_action_items`/`report_hints`). PNI deterministically assembles the full `ScoreResult (schema_version="2.0")`, syncs structured evidence JSONs (`plan.json`, `facts.json`, `architecture.json`) into `<src_dir>/_facts/` when a report step exists, and emits:
     - `pni_report/<target>_score.json`
     - `pni_report/<target>_summary.json`
     - `pni_report/<target>_findings.sarif` (SARIF 2.1.0)
   - On `synthesize_rollup`: review the multi-component `RollupFacts` table, weakest-link guardrails, root governance, and companion DSLs, then submit `RollupSynthesisInput`.
   - On `write_drawlib_report`: consult `drawlib rules show ...` on demand, verify diagrams with `drawlib show ... -g`, build with `pni report build`, and push `ReportCompletionInput`.

## 2. Multi-Language / Monorepo Multi-Audit Rollup

For repositories with multiple primary languages (e.g., `backend/` Python + `frontend/` TypeScript + `native/` Rust):
1. Run each component sub-audit with `scope: component` (skips duplicate root governance penalties and omits separate per-component PDFs unless requested; emits `reports/<component>_score.json` + `*_summary.json` + `*_findings.sarif`).
2. Run a `category: rollup` workflow declaring `includes:` (with optional `weight:` / `primary:` and default `report_mode: unified`).
3. PNI aggregates 7-axis scores via `log1p(LOC)` smoothing + `security`/`testing` weakest-link guardrails (`min_primary + 15`), normalizes paths to repo root with `component` tags, runs root governance + companion DSL scan once, and generates a single unified Drawlib report (`00_cover.md`..`05_component_deep_dives.md`).

## 3. Mermaid Verification Rule (Mandatory)

Whenever you author or modify any Mermaid diagram in prose, plans, or docs, validate it BEFORE presenting to the user:
```bash
pni validate-mermaid <file.md_or_mmd>           # Fast Layer 1 static validator (<1ms)
pni validate-mermaid <file.md_or_mmd> --browser # Layer 2 official mermaid.parse() via Playwright
```

## 4. Standard Commands
- `pni init`: Initialize `.pni/` (`pni.toml`, `rules/`, `actions/`, `workflows/`, `instructions.md`, `.pni/cache/.gitignore`).
- `pni rules list [--all]` / `pni rules show <id> [-o <path>]`
- `pni workflows list [--category audit|rollup|migration|progress]` / `pni workflows show <id>`
- `pni workflows plan <workflow_id> [--mermaid] [--json] [-o <path>]`: Phase 0 Recon + validated Mermaid DAG preview.
- `pni workflows start <workflow_id> [--supersede] [--auto-approve] [--plan <file>] [--pull] [--json] [-o <path>]`
- `pni workflows get-action <run_id> [--json] [--full-schema] [-o <path>]`
- `pni workflows get-actions <run_id> [--ready] [--json] [-o <path>]`
- `pni workflows push-action <run_id> <action_id> --file <path> [--next] [--json] [-o <path>]`
- `pni workflows status [run_or_workflow] [--latest] [--json]` / `inspect-action` / `rewind [--pull] [-o <path>]` / `cancel`
- `pni validate-mermaid <file> [--browser] [--json]`
- `pni validate-score <path>` / `validate-migration-plan <path>` / `validate-progress <path>`
- `pni report init <target>` / `pni report build <target>`
- `pni pentests init` / `pni pentests run`
- `pni progress init` / `pni progress validate`
