# Agent Bootstrap & Execution Instructions (Common — Workflow v2)

This guide provides the concise PNI Workflow v2 bootstrap and execution procedure via `pni rules show common/agent_instruction` (or `pni rules show agent-instruction`). Run `pni instructions` for the full CLI command reference.

## 1. Bootstrap & Workflow Setup

1. Run `pni init` if `.pni/` does not exist yet in the target workspace (scaffolds `.pni/pni.toml`, `rules/`, `actions/`, `workflows/`, `instructions.md`, and `.pni/cache/.gitignore`).
2. Read the general workflow design procedure:
   ```bash
   pni rules show common/workflow_guide
   ```
3. Detect the primary language(s) in the repository and read the corresponding language workflow guide(s):
   ```bash
   pni rules show python/workflow_guide
   pni rules show java/workflow_guide
   pni rules show php/workflow_guide
   pni rules show go/workflow_guide
   pni rules show typescript/workflow_guide
   pni rules show javascript/workflow_guide
   pni rules show generic/workflow_guide
   ```
4. Tailor `.pni/workflows/*.yaml` (using DAG `needs:` edges and safe `when:` predicates) to the repository's real source, test, and documentation paths, then preview Phase 0 Recon & validated Mermaid DAG:
   ```bash
   pni workflows show <workflow_id>
   pni workflows plan <workflow_id> [--mermaid | --json]
   ```
5. **For Multi-Language / Monorepo Repositories (`scope: component` + `category: rollup`)**:
   - Define per-component audit workflows with `scope: component` (skips duplicate root governance penalties and omits redundant per-component PDFs unless requested).
   - Define a single `category: rollup` workflow declaring `includes:` (`synthesize_rollup` -> `write_drawlib_report`, default `report_mode: unified`) to aggregate 7-axis scores via `log1p(LOC)` weighting + `security`/`testing` weakest-link guardrails (`min_primary + 15`) into one unified executive + per-component deep-dive report.
6. **For Web Service Workflows (`uses: web_penetration_audit` / `web_pentest`)**: `pni workflows start <workflow_id>` fails closed if `.pni/pentests/<target>/` does not yet contain `conftest.py` and `test_*.py`. Implement and verify penetration tests **first**:
   ```bash
   pni pentests init -w <workflow_id>
   # Inspect target endpoints/auth and add HTTP probes in .pni/pentests/<target>/test_*.py
   pni workflows run-action <workflow_id> web_pentest
   ```
7. **For Migration Planning Workflows (`category: migration`, `based_on: <audit_id>`)**: Read `pni rules show common/migration_planning`. Migration workflows inherit `targets` from `based_on` and require a `COMPLETED` run of `<audit_id>` in `.pni/cache/workflow_state.db`. Clarify ambiguous target versions, DB/Cache middleware, architecture boundaries, API compatibility, and legacy bug policies with the user, then pin them in `.pni/workflows/<migration_id>.yaml` (`with.brief: |` + guardrail options) before `pni workflows start`.
8. **For Project Progress & Git Governance Workflows (`category: progress`)**: Read `pni rules show common/progress_tracking` and `pni rules show common/git_workflow`. Scaffold and validate `.pni/progress/<target>.yaml` (`pni progress init <target>` -> edit -> `pni progress validate <target>`) **before** starting, and keep it Read-Only during runs.

## 2. Workflow v2 Execution Cycle (Plan-First DAG + Zero Empty ACKs)

- **Auto-Approval Friendly CLI Discipline (Zero Shell Metacharacters)**: Always invoke `pni` / `drawlib` as a **single simple command** (NEVER use pipes `|`, redirects `>`, heredocs `<<EOF`, `$(...)`, `$VAR`, `&&`/`;`, `jq`/`head`/`python -c`, or inline multi-line JSON). Write JSON payloads with your file-writing tool to `.pni/cache/<workflow_id>/input_<action_id>.json`, pass `--file <path> --next` (or `start --pull`), use `-o <path>` + your file-reading tool for long outputs/JSON inspection, and validate Mermaid from files (`pni validate-mermaid <file>`).
- **Ad-Hoc Single Action (Zero Prep)**: `pni workflows run-action <workflow_id> <action>` executes any individual step/action directly without `workflow_state.db`.
- **Full Stateful DAG Workflow**:
  1. **Start**:
     - Interactive (default): `pni workflows start <workflow_id> --pull [--supersede]` -> starts and pulls `act-01: confirm_plan` (`AWAITING_APPROVAL`) in one command.
     - CI / Batch: `pni workflows start <workflow_id> --auto-approve --pull` (or `--plan <approval.json> --pull`).
  2. **Phase 1 — Human Alignment Gate (`confirm_plan`)**:
     - Show the user the validated Mermaid Execution DAG, detected scope/languages/harness table, and alignment questions; once aligned, write `PlanApprovalInput` to `.pni/cache/<workflow_id>/input_act-01.json` via your file-writing tool and submit with `--next`.
  3. **Auto-Advance Parallel Collection & Step-Scoped Pull**:
     - `pni workflows get-action <run_id> [--json] [--full-schema] [-o <path>]` (or `pni workflows get-actions <run_id> --ready [--json] [-o <path>]` for parallel AI subagents).
     - PNI automatically executes all DAG-ready deterministic analyzers (`project_inspect`, `ast_analyze`, `run_check`, `security_scan`, `web_pentest`, `migration_analyze`, `progress_analyze`) in parallel without requiring empty `{"acknowledged": true}` pushes, writes `.pni/cache/<workflow_id>/facts.json`, and projects only step-relevant fact slices (`fact_views`) with compact input skeletons.
  4. **Push & Auto-Pull Next**:
     - Write the JSON payload via your file-writing tool and run a single command: `pni workflows push-action <run_id> <action_id> --file .pni/cache/<workflow_id>/input_<action_id>.json --next [-o <path>]` (DAG-ready AI actions may be pushed out-of-order).
     - On `ai_interpret`: triage deterministic `det-*` pre-findings via `finding_adjustments` (`waive`/`reclassify`, `reason >= 10 chars`) and bounded `baseline_delta` (`-10..+10`).
     - On `emit_score`: submit compact `ScoreSubmissionInput` -> PNI validates `±10pt` anchoring and writes `*_score.json` (`schema_version="2.0"`), `*_summary.json`, and `*_findings.sarif` (SARIF 2.1.0).
  5. **Repeat** until status is `COMPLETED`.
- **Progress Monitoring, Past-Run Inspection & Cleanup (Never Query SQLite Manually)**:
  - Check progress: `pni workflows status --latest [--json]` or `pni workflows status <run_id>`.
  - Inspect recorded payloads: `pni workflows inspect-action <run_or_workflow> <action> [--agent-input | --deterministic] [-o <file.json>]`.
  - Rewind from an intermediate step: `pni workflows rewind <run_or_workflow> <action> [--pull]` (alias: `retry-action`).
  - Clean up abandoned runs: `pni workflows cancel <run_id>` or `pni workflows cancel --superseded`.

## 3. Core Anti-Hallucination, Mermaid Verification & Visual Report Rules

- **Never estimate counts manually**: Rely strictly on deterministic numbers in `ProjectFacts`, `AstFacts`, `RuntimeFacts`, `SecurityFacts`, and `RollupFacts` (drill into `.pni/cache/<workflow_id>/facts.json` when needed).
- **Never invent file paths or symbols**: Every module path, entry point, and finding location must exist in the repository's `module_inventory`.
- **Always validate Mermaid before presenting to users**: Run `pni validate-mermaid <file.md_or_mmd> [--browser] [--json]` on every AI-authored or edited Mermaid diagram (Layer 1 static validator + optional Layer 2 Playwright `mermaid.parse()`).
- **Never guess `drawlib` APIs or coordinate anchors on report steps**: When entering `write_drawlib_report` / `write_migration_report` / `write_progress_report`, query Drawlib's built-in CLI help and documentation on demand (prefix with `uv run` in `uv` workspaces):
  ```bash
  drawlib -h                                # CLI subcommands (init, build, show, serve, rules, styles, colors, cache)
  drawlib rules list                        # List all guideline & module API topics
  drawlib rules show agent-instruction      # 3-stage multimodal self-review workflow & component catalog
  drawlib rules show overview               # Bottom-left (0, 0) coordinate system & anchor conventions
  drawlib rules show project-doc            # Single-document cover/ToC, 720pt typography & A4 PDF rules
  drawlib rules show api                    # Full module/class signature cheat sheet
  drawlib rules show lib-smartarts-overview # Panel, KpiCards, Roadmap, Table, TreeNode, CardList APIs
  drawlib rules show lib-charts-overview    # Radar, Bar, Box, Heatmap, Line, Gantt Chart APIs
  drawlib rules show lib-diagrams-overview  # ClassDiagram, HeatmapOverlay, architecture/flow/sequence APIs
  drawlib rules show lib-icons-overview     # Phosphor, FontAwesome & cloud icon helpers
  ```
- **Place the PNI501 logo badge on `00_cover.md` & Audit Pipeline Provenance in Ch. 4**: `pni report init` scaffolds directly into `<src_dir>/` (default `pni_report_src/`, or custom flat paths like `docs_src/pni/`), copies `_assets/logo.png`, `_assets/logo_dark.png`, and `_assets/favicon.png` into `<src_dir>/_assets/`, and injects `draw_pni_logo(xy=(135.0, 48.0), width=9.0, *, dark=True)` into `<src_dir>/utils.py`. Structured evidence JSONs (`plan.json`, `facts.json`, `architecture.json`, `blueprint.json`) are synchronized into `<src_dir>/_facts/` so the report project is self-contained. Always render the PNI501 logo badge on `00_cover.md`, and in Chapter 4 render the logical action-level Executed DAG (`drawlib.graph` / `drawlib.diagrams.flow`), 7-axis Deterministic Baseline vs. AI Δ table, triage/waiver log, and a compact Machine-Readable Artifact Reference Table (never paste raw JSON into the PDF).
- **Verify diagrams visually with `-g` grid export & update non-destructively**: Keep Drawlib Markdown sources directly in `<src_dir>/<lang>/` (default `pni_report_src/<lang>/`, with `drawlib.toml` at `<src_dir>/drawlib.toml` and evidence JSONs at `<src_dir>/_facts/`) and update chapters in-place so `git diff` cleanly tracks report evolution; inspect rendered diagrams via `drawlib show <src_dir>/<lang>/<chapter.md> <diagram.png> -s <src_dir>/styles.py -u <src_dir>/utils.py -g -o .drawlib/scratch/<unique_name>_grid.png`, resolve any `[Geometry Warning]` diagnostics, and eliminate text clipping or collisions before compiling `<output_dir>/<target>.pdf` (default `pni_report/<target>.pdf`) with `pni report build`.
