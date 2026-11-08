# Agent Bootstrap & Execution Instructions (Common)

This guide mirrors `pni instructions` so AI coding agents can access the complete PNI bootstrap procedure directly via `pni rules show common/agent_instruction` (or `pni rules show agent-instruction`).

## 1. Bootstrap & Workflow Setup

1. Run `pni init` if `.pni/` does not exist yet in the target workspace.
2. Read the general workflow design procedure:
   ```bash
   pni rules show common/workflow_guide
   ```
3. Detect the primary language(s) in the repository and read the corresponding language workflow guide:
   ```bash
   pni rules show python/workflow_guide
   pni rules show java/workflow_guide
   pni rules show php/workflow_guide
   ```
4. Tailor `.pni/workflows/*.yaml` (and `.pni/actions/*.yaml` if needed) to the repository's real source, test, and documentation paths, then verify step expansion with `pni workflows show <workflow_id>`.
5. **For Web Service Workflows (`uses: web_penetration_audit` / `web_pentest`)**: `pni workflows start <workflow_id>` fails closed if `.pni/pentests/<target>/` does not yet contain `conftest.py` and `test_*.py`. Implement and verify the target's penetration tests **first**:
   ```bash
   pni pentests init -w <workflow_id>
   # Inspect target endpoints/auth and add HTTP probes in .pni/pentests/<target>/test_*.py
   pni workflows run-action <workflow_id> web_pentest
   ```
6. **For Migration Planning Workflows (`category: migration`, `based_on: <audit_id>`)**: Read `pni rules show common/migration_planning`. Migration workflows inherit `targets` from `based_on` and require a `COMPLETED` run of `<audit_id>` in `.pni/cache/workflow_state.db`—if `pni workflows show` or `pni workflows start` reports a missing/unfinished prerequisite audit run, **execute and complete `<audit_id>` first**. **Before running `pni workflows start <migration_id>`**, ask the user concise clarifying questions (with recommended defaults) for any ambiguous target versions, DB/Cache middleware, Clean Architecture scope, API compatibility, or legacy bug policies, and write the deterministic answers back into `.pni/workflows/<migration_id>.yaml` (`with.brief: |` + pinned guardrail values).
7. **For Project Progress & Git Governance Workflows (`category: progress`)**: Read `pni rules show common/progress_tracking` and `pni rules show common/git_workflow`. Scaffold and validate `.pni/progress/<target>.yaml` (`pni progress init <target>` -> edit `git_policy`, `milestones`, and `tasks` -> `pni progress validate <target>`) **before** running `pni workflows start`, and keep `.pni/progress/<target>.yaml` strictly Read-Only during measurement runs.

## 2. Deterministic Pull-Push Execution Cycle (and Ad-Hoc Action Testing)

- **Ad-Hoc Single Action (Zero Prep)**: `pni workflows run-action <workflow_id> <action>` executes any specific step/action (e.g. `web_pentest`, `runtime_verification`, `security_audit`, `ast_and_quality`) directly without `workflow_state.db`.
- **Full Stateful Workflow**:
  1. **Start**: `pni workflows start <workflow_id> [--supersede]` -> receive `wf-<id>`.
  2. **Pull**: `pni workflows get-action <run_id>` -> inspect deterministic facts, active engineering rules, prior architecture records, and required JSON Schema.
  3. **Push**: `pni workflows push-action <run_id> <action_id> --file <payload.json>` -> validate against Pydantic + workspace grounding checks and advance state.
  4. **Repeat** until status is `COMPLETED`.
- **Progress Monitoring, Past-Run Inspection & Cleanup (Never Query SQLite Manually)**:
  - Check progress across workflows: `pni workflows status --latest [--json]` or `pni workflows status -s in_progress [--json]` (or `pni workflows status <run_id>` for step-level notes).
  - Inspect or export prior step payloads during re-audits: `pni workflows inspect-action <run_or_workflow> <action> [--agent-input | --deterministic] [-o <file.json>]`.
  - Re-run or rewind from an intermediate step after adjusting `.pni/pni.toml`, harness Dockerfiles, or `.pni/workflows/*.yaml`: `pni workflows rewind <run_or_workflow> <action> [--pull]` (alias: `retry-action`).
  - Clean up abandoned runs: `pni workflows cancel <run_id>` or `pni workflows cancel --superseded`.

## 3. Core Anti-Hallucination & Visual Report Rules

- **Never estimate counts manually**: Use the deterministic numbers in `ProjectFacts` and `AstFacts` (`import_hygiene_coverage_pct`, `type_safety_coverage_pct`, `docstring_coverage_pct`, `circular_dependencies`, etc.).
- **Never invent file paths or symbols**: Every module path, entry point, and flow step submitted during architecture recording or rule findings must exist in the repository's `module_inventory`.
- **Never guess `drawlib` APIs or coordinate anchors on report steps**: When entering `write_drawlib_report` / `write_migration_report`, query Drawlib's built-in CLI help and documentation on demand (prefix with `uv run` in `uv` workspaces):
  ```bash
  drawlib -h                                # CLI subcommands (init, build, show, serve, rules, styles, colors, cache)
  drawlib rules list                        # List all guideline & module API topics
  drawlib rules show agent-instruction      # 3-stage multimodal self-review workflow & component catalog
  drawlib rules show overview               # Bottom-left (0, 0) coordinate system & anchor conventions
  drawlib rules show project-doc            # Single-document cover/ToC, 720pt typography & A4 PDF rules
  drawlib rules show api                    # Full module/class signature cheat sheet
  drawlib rules show lib-smartarts-overview # Panel, KpiCards, Roadmap, Table, TreeNode, CardList APIs
  drawlib rules show lib-charts-overview    # RadarChart, BarChart, HeatmapChart, LineChart APIs
  drawlib rules show lib-diagrams-overview  # ClassDiagram, HeatmapOverlay, architecture/flow/sequence APIs
  drawlib rules show lib-icons-overview     # Phosphor, FontAwesome & cloud icon helpers
  ```
- **Verify diagrams visually with `-g` grid export & update non-destructively**: Keep Drawlib Markdown sources in `reports_src/<target>_src/<lang>/` (with `drawlib.toml` at `reports_src/<target>_src/drawlib.toml`) and update chapters in-place so `git diff` cleanly tracks report evolution; inspect rendered diagrams via `drawlib show <lang>/<chapter.md> <diagram.png> -s styles.py -u utils.py -g -o .drawlib/scratch/<unique_name>_grid.png` + image viewing to eliminate text clipping or collisions before compiling `reports/<target>.pdf` with `pni report build`.
