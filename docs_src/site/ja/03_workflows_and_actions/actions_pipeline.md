# アクションとプリミティブパイプライン: 182 テンプレート -> 16 プリミティブ

コード行数や複雑度、依存バージョン、テスト通過率、CVE 件数、モノレポ重み付け、リファクタリング影響範囲に対する LLM の憶測（ハルシネーション）を排除するため、`pni501` (`v0.2.0`) は**宣言的なワークフロー定義**と**実行メカニズム**を分離しています。**対応 55 言語 + `generic`** の全体にわたって、`src/pni/_actions/` は **182 個の組み込み複合 YAML アクションテンプレート**（`common/` 汎用アクション **15** + **55** 言語 × 各 **3** 言語別アクション + `generic/` フォールバック **2**）を同梱し、それらを **16 個の正規 `PrimitiveType` ステップ**（空の ACK ターンなしで並列ウェーブ自動実行される **7 個の決定論的 Python 解析器** + スキーマ検証・リポジトリ実在確認付きの **9 個の AI/ゲート/統合/レポートプリミティブ**）へとフラットに展開します。

```drawlib align=center code=fold file=two_tier_action_expansion.png caption="2層アクション展開アーキテクチャ (v0.2.0): 182個の組み込みアクションテンプレートが 7 個の並列決定論的解析器と 9 個の根拠検証付き AI/ゲートプリミティブへ展開される"
from drawlib.canvas import save, setup
from drawlib.diagrams.architecture import ArchitectureDiagram, Node, NodeGroup, PhosphorIcon
from drawlib.styles import Styles

setup(width=178, height=112, dpi=150)

diag = ArchitectureDiagram(
    node_style=Styles.PrimaryBold,
    node_text_style=Styles.DarkBold.patch(text_size=10.0),
    edge_style=Styles.DarkBold,
    edge_text_style=Styles.DarkBold.patch(text_size=10.0),
    node_card_style=Styles.WhiteBordered.patch(shape_r=1.6),
)

wf_node = diag.add(
    Node(
        "Workflow v2 YAML\n182 Built-in Actions\n(15 common + 55x3 + 2)",
        width=37.0,
        height=21.0,
        icon=PhosphorIcon.FILE_CODE,
        icon_size=6.0,
    ),
    xy=(21.5, 81.0),
)

mgr_node = diag.add(
    Node(
        "Action Manager\n(Cascade, DAG & Flatten)",
        width=37.0,
        height=19.5,
        icon=PhosphorIcon.STACK,
        icon_size=6.0,
        style=Styles.WhiteBold,
        text_style=Styles.WhiteBold.patch(text_size=10.2),
        card_style=Styles.PrimaryFlat.patch(shape_r=1.6),
    ),
    xy=(21.5, 31.0),
)

det_group = diag.add(
    NodeGroup(
        title="7 Deterministic Auto-Executed Python Primitives (Parallel Waves, 0 ACK)",
        width=121.0,
        height=47.0,
        style=Styles.Neutral.patch(shape_r=2.0),
        text_style=Styles.PrimaryBold.patch(text_size=10.5, halign="left", valign="top"),
    ),
    xy=(54.0, 61.0),
)

d1 = det_group.add(Node("project_inspect", width=25.0, height=13.5, icon=PhosphorIcon.FILE_MAGNIFYING_GLASS, icon_size=5.0), xy=(16.5, 30.5))
d2 = det_group.add(Node("ast_analyze", width=25.0, height=13.5, icon=PhosphorIcon.TREE_STRUCTURE, icon_size=5.0), xy=(45.5, 30.5))
d3 = det_group.add(Node("run_check", width=25.0, height=13.5, icon=PhosphorIcon.TERMINAL_WINDOW, icon_size=5.0), xy=(74.5, 30.5))
d4 = det_group.add(Node("security_scan", width=25.0, height=13.5, icon=PhosphorIcon.SHIELD_WARNING, icon_size=5.0), xy=(103.5, 30.5))

d5 = det_group.add(Node("web_pentest", width=25.0, height=13.5, icon=PhosphorIcon.BUG, icon_size=5.0), xy=(16.5, 11.5))
d6 = det_group.add(Node("migration_analyze", width=25.0, height=13.5, icon=PhosphorIcon.GIT_DIFF, icon_size=5.0), xy=(45.5, 11.5))
d7 = det_group.add(Node("progress_analyze", width=25.0, height=13.5, icon=PhosphorIcon.TREND_UP, icon_size=5.0), xy=(74.5, 11.5))
facts_node = det_group.add(
    Node(
        "facts.json +\n_facts/ Sync",
        width=25.0,
        height=13.5,
        icon=PhosphorIcon.DATABASE,
        icon_size=5.0,
        style=Styles.SecondaryBold,
        card_style=Styles.SecondaryNeutral.patch(shape_r=1.6),
    ),
    xy=(103.5, 11.5),
)

ai_group = diag.add(
    NodeGroup(
        title="9 Schema-Guided & Grounded AI / Gate / Synthesis Primitives",
        width=121.0,
        height=54.0,
        style=Styles.Neutral.patch(shape_r=2.0),
        text_style=Styles.SecondaryBold.patch(text_size=10.5, halign="left", valign="top"),
    ),
    xy=(54.0, 3.0),
)

a1 = ai_group.add(
    Node("confirm_plan", width=34.0, height=11.5, icon=PhosphorIcon.CHECK_CIRCLE, icon_size=4.6, card_style=Styles.WarningNeutral.patch(shape_r=1.5)),
    xy=(21.5, 38.5),
)
a2 = ai_group.add(Node("load_rules", width=34.0, height=11.5, icon=PhosphorIcon.BOOK_OPEN_TEXT, icon_size=4.6), xy=(60.5, 38.5))
a3 = ai_group.add(Node("record_architecture", width=34.0, height=11.5, icon=PhosphorIcon.BLUEPRINT, icon_size=4.6), xy=(99.5, 38.5))

a4 = ai_group.add(Node("ai_interpret", width=34.0, height=11.5, icon=PhosphorIcon.BRAIN, icon_size=4.6), xy=(21.5, 23.5))
a5 = ai_group.add(
    Node("emit_score", width=34.0, height=11.5, icon=PhosphorIcon.MEDAL, icon_size=4.6, style=Styles.PrimaryBold, card_style=Styles.PrimaryNeutral.patch(shape_r=1.5)),
    xy=(60.5, 23.5),
)
a6 = ai_group.add(
    Node("synthesize_rollup", width=34.0, height=11.5, icon=PhosphorIcon.STACK, icon_size=4.6, style=Styles.PrimaryBold, card_style=Styles.PrimaryNeutral.patch(shape_r=1.5)),
    xy=(99.5, 23.5),
)

a7 = ai_group.add(
    Node("emit_migration_plan", width=34.0, height=11.5, icon=PhosphorIcon.PATH, icon_size=4.6, style=Styles.PrimaryBold, card_style=Styles.PrimaryNeutral.patch(shape_r=1.5)),
    xy=(21.5, 8.5),
)
a8 = ai_group.add(
    Node("emit_progress", width=34.0, height=11.5, icon=PhosphorIcon.CHART_LINE_UP, icon_size=4.6, style=Styles.PrimaryBold, card_style=Styles.PrimaryNeutral.patch(shape_r=1.5)),
    xy=(60.5, 8.5),
)
a9 = ai_group.add(
    Node("write_drawlib_report", width=34.0, height=11.5, icon=PhosphorIcon.CHART_POLAR, icon_size=4.6, style=Styles.SuccessBold, card_style=Styles.SuccessNeutral.patch(shape_r=1.5)),
    xy=(99.5, 8.5),
)

diag.connect(wf_node, mgr_node, label="normalize", routing="orthogonal")
mgr_node.fork([det_group, ai_group], at_x=45.5, style=Styles.PrimaryBold)
diag.connect(d4, facts_node, routing="orthogonal", style=Styles.SecondaryBold)
diag.connect(d7, facts_node, routing="orthogonal", style=Styles.SecondaryBold)

diag.draw(xy=(0.0, 0.0))
save()
```

---

## 1. 2層アクション展開 (`182` 組み込みテンプレート -> `16` プリミティブ)

`.pni/workflows/*.yaml`（`WorkflowDefinition`）の記述が簡潔に保たれるのは、`src/pni/_actions/base_model.py` が再利用可能なドメイン監査バンドルと低レベルの実行ステップを分離しているためです。

1. **Tier 1 — 複合アクション (`CompositeActionDefinition`、`182` 組み込みテンプレート)**: `uses: <action_id>` で呼び出されるドメイン特化型の YAML 仕様です。**登録済み 55 言語**のすべてに対して、**15 個の汎用 `common/` アクション**と **3 個の言語別 `<lang>/` アクション**（`repo_structure_audit`, `<lang>_ast_audit`, `<lang>_test_audit`）、および **2 個の `generic/` フォールバック**が組み込まれ、合計 `15 + (55 × 3) + 2 = 182` テンプレートを構成します。
2. **Tier 2 — 正規プリミティブ (`PrimitiveStep` & `PrimitiveType`、`16` プリミティブ)**: 複合 YAML の内部、またはワークフローステップの `action: <primitive_type>` で直接参照される `16` 個の実行プリミティブです。ステートフル Workflow v2 DAG 実行と単発の `run-action` はすべて、`needs`・`when`・`fact_views` を備えたフラットな `PrimitiveStep` 上で動作します。

### 1.1 言語あたり 18 個の標準複合アクション一覧 (`common/` 15 + `<lang>/` 3)

対応 **55 言語**のいずれにおいても、ワークフローは以下の **18 個の複合 YAML アクション**（`common/` 15 個 + `<lang>/` 3 個）を組み合わせて構成します。

| # | 複合 `uses:` ID | スコープ | 展開される `PrimitiveType` シーケンス | デフォルト適用ルールと役割 |
| :---: | :--- | :--- | :--- | :--- |
| **`01`** | **`repo_structure_audit`** | `<lang>/` | `project_inspect` -> `ai_interpret` | `<lang>/dependencies`, `common/supply_chain`, `common/documentation`, `common/git_hygiene`, `common/security` |
| **`02`** | **`architecture_analysis`** | `common/` | `record_architecture` (`×3`: `purpose_and_stack`, `layers_and_modules`, `flows_and_state`) | `common/architecture` — 実在パス検証付きの 3 側面システム理解を `architecture.json` に保存 |
| **`03`** | **`<lang>_ast_audit`** | `<lang>/` | `ast_analyze` -> `ai_interpret` | `<lang>/code_quality`, `<lang>/typing`, `<lang>/modernization` および検出フレームワークルール（ネイティブ `tree-sitter`） |
| **`04`** | **`<lang>_test_audit`** | `<lang>/` | `ai_interpret` (`AstFacts` を参照) | `<lang>/testing` — テスト分離、ミラーディレクトリ構成、アサーション密度を評価 |
| **`05`** | **`supply_chain_audit`** | `common/` | `ai_interpret` (`ProjectFacts` を参照) | `common/supply_chain`, `common/git_hygiene`, `common/security` — OpenSSF & CI/CD ガバナンス監査 |
| **`06`** | **`library_hygiene_audit`** | `common/` | `ai_interpret` | `common/library_hygiene`, `common/documentation` — SemVer 公開 API 境界と最小依存関係の評価 |
| **`07`** | **`cli_guidelines_audit`** | `common/` | `ai_interpret` | `common/cli_guidelines`, `common/error_handling` — Clig.dev 操作性、`--help`、終了コード規約 |
| **`08`** | **`service_readiness_audit`** | `common/` | `ai_interpret` | `common/twelve_factor`, `common/production_readiness`, `common/observability`, `common/resilience` |
| **`09`** | **`container_runtime_audit`** | `common/` | `run_check` -> `ai_interpret` | `common/container_hygiene`, `common/production_readiness` — `--network=none` テスト実行と起動プローブ |
| **`10`** | **`security_vulnerability_audit`** | `common/` | `security_scan` -> `ai_interpret` | `common/security`, `common/supply_chain`, `common/container_hygiene` — ソケットレス Trivy FS + イメージ tar スキャン |
| **`11`** | **`web_penetration_audit`** | `common/` | `web_pentest` -> `ai_interpret` | `common/security`, `common/resilience` — ループバックコンテナ起動 + ライブ `httpx` セキュリティプローブ |
| **`12`** | **`emit_score`** | `common/` | `emit_score` | `finding_adjustments` トリアージ適用、実行済み DAG 記録、`pni_report_src/_facts/` 同期、スコア・サマリ・SARIF 出力 |
| **`13`** | **`synthesize_rollup`** | `common/` | `synthesize_rollup` | `includes` コンポーネントのハイブリッド重み付け集約 + 最弱リンク保護、統合スコア・SARIF 出力 |
| **`14`** | **`write_drawlib_report`** | `common/` | `write_drawlib_report` (`report_kind: audit \| rollup`) | `common/reporting` — `pni_report_src/_facts/` にブループリント出力し、`pni_report/<target>.pdf` を検証 |
| **`15`** | **`migration_proposal`** | `common/` | `migration_analyze` -> `ai_interpret` -> `emit_migration_plan` | `common/migration_planning`, `common/architecture` — Wave `1..4`、Tarjan SCC 切断、`pni_report/<target>_migration_plan.json` |
| **`16`** | **`write_migration_report`** | `common/` | `write_drawlib_report` (`report_kind: migration`) | `common/reporting`, `common/migration_planning` — 7章構成マイグレーション A4 PDF を `pni_report/` へコンパイル |
| **`17`** | **`progress_assessment`** | `common/` | `progress_analyze` -> `ai_interpret` -> `emit_progress` | `common/progress_tracking` — 複数スプリントの改修差分と Git ブランチ衛生を `pni_report/<target>_progress.json` へ出力 |
| **`18`** | **`write_progress_report`** | `common/` | `write_drawlib_report` (`report_kind: progress`) | `common/reporting`, `common/progress_tracking` — 改修進捗 A4 PDF を `pni_report/` へコンパイル |

### 1.2 3層カスケード・DAG 配線・パラメータ統合 (`_actions/manager.py`)

`normalize_workflow_steps()` が Workflow v2 YAML を展開する際、`expand_composite_action()` は `local (.pni/actions/) > <active_lang>/ > common/`（または `generic/`）の優先順で `uses:` を解決し、4 層の設定を統合します。

- **DAG 依存関係とガード (`needs`, `when`, `fact_views`)**: ステップ側の `needs:` と `when:` は複合アクションの先頭プリミティブに付与され、複合内部の後続プリミティブは自動的に直列依存（`act-02` が `act-01` に依存）で配線され、プロンプト射影用の `fact_views` を保持します。
- **パラメータ (`params`)**: フラットレポートの標準デフォルト（`src_dir: "pni_report_src"`, `output_dir: "pni_report"`）、`.pni/pni.toml [report]` 設定、ワークフローターゲット文脈、ステップの `with:` がプリミティブデフォルトを上書きします（`{**prim.with_params, **override_params}`）。
- **ルール (`rules`)**: 複合アクション、ワークフローステップ、プリミティブのルールを宣言順に連結・重複排除（`dict.fromkeys`）します。
- **由来追跡 ID (`Provenance IDs`)**: 複合ステップ ID（`{step_id}__{idx}_{prim.type.value}`）が `step_key` と `source_action=comp.id` を保持することで、`provenance.py` が SQLite の `act-01..NN` から見やすいステージ単位の実行済み監査 DAG を再構築できます。

---

## 2. 16 個の正規プリミティブ完全カタログ

`src/pni/_actions/ai_actions.py` および `src/pni/_workflows/engine.py` において、すべての AI/ゲートプロンプトはコンパクトスキーマ骨格（`get_expected_input_schema_json(..., compact=True)`、`--full-schema` で完全 JSON Schema）を注入し、すべての `push-action` は **Pydantic v2 検証**と**リポジトリパスの実在性**（`_verify_grounded_paths()`）を強制します。

```drawlib align=center code=fold file=primitive_catalog_table.png caption="16個の正規 PrimitiveType アクション完全カタログ (v0.2.0): 実行モード、Push 検証スキーマ、および実在検証・トリアージ・フラット出力"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=168, height=154, dpi=150)

headers_and_rows = [
    ["Primitive (16)", "Mode", "Validated Push Schema", "Grounding, Triage & Flat Output Side Effects"],
    [
        "confirm_plan",
        "Plan Gate",
        "PlanApprovalInput",
        "Confirms Phase 0 Recon & Mermaid DAG; applies targets,\ndisabled_steps (-> skipped) & extra_opt_outs",
    ],
    [
        "project_inspect",
        "Auto (Parallel)",
        "Auto-Completed (0 ACK)",
        "Parses 55-lang manifests, lockfiles & OpenSSF governance\n-> .pni/cache/<wf>/facts.json",
    ],
    [
        "ast_analyze",
        "Auto (Parallel)",
        "Auto-Completed (0 ACK)",
        "Runs native tree-sitter CST (55 langs + 15 Tier C DSLs)\n-> .pni/cache/<wf>/facts.json",
    ],
    [
        "run_check",
        "Auto (Parallel)",
        "Auto-Completed (0 ACK)",
        "Materializes .pni/dockerfiles/ (40 tmpl / 35 langs),\nruns --network=none unit tests & coverage",
    ],
    [
        "security_scan",
        "Auto (Parallel)",
        "Auto-Completed (0 ACK)",
        "Runs socketless Trivy FS + image tar scan\n-> security_facts.json & facts.json",
    ],
    [
        "web_pentest",
        "Auto (Parallel)",
        "Auto-Completed (0 ACK)",
        "Boots 127.0.0.1 loopback container & runs\n.pni/pentests/<target>/ httpx probes",
    ],
    [
        "migration_analyze",
        "Auto (Parallel)",
        "Auto-Completed (0 ACK)",
        "Computes Waves 1..4, Tarjan SCC cuts, contracts\n& DEC-XX -> migration_facts.json",
    ],
    [
        "progress_analyze",
        "Auto (Parallel)",
        "Auto-Completed (0 ACK)",
        "Inspects Git branches, commits & baseline history\n-> progress_facts.json & facts.json",
    ],
    [
        "load_rules",
        "AI / Gate",
        "DeterministicAckInput",
        "Resolves & injects cascaded Markdown engineering\nrules (356 built-in) into prompt context",
    ],
    [
        "record_architecture",
        "AI / Grounded",
        "SystemProfile | StructureMap |\nExecutionFlowMap",
        "Verifies paths against module_inventory\n-> .pni/cache/<wf>/architecture.json",
    ],
    [
        "ai_interpret",
        "AI / Grounded",
        "InterpretationInput",
        "Grounds findings/action_items & runs\nnormalize_step_rule_checks() per active rule",
    ],
    [
        "emit_score",
        "AI + Aggregator",
        "ScoreSubmissionInput\n(incl. finding_adjustments)",
        "Applies triage, records Executed DAG, syncs _facts/\n-> pni_report/<t>_score.json, summary & SARIF",
    ],
    [
        "synthesize_rollup",
        "AI + Rollup",
        "RollupSynthesisInput",
        "Hybrid log1p(LOC) weights + weakest-link guardrail\n-> unified pni_report/<t>_score.json & SARIF",
    ],
    [
        "emit_migration_plan",
        "AI + Grounded",
        "MigrationPlanResult",
        "Grounds As-Is paths + attaches MigrationFacts & DAG\n-> pni_report/<t>_migration_plan.json",
    ],
    [
        "emit_progress",
        "AI + Delta",
        "ProgressAssessmentInput",
        "Combines Git ProgressFacts with sprint remediation\n-> pni_report/<t>_progress.json",
    ],
    [
        "write_drawlib_report",
        "AI + Compiler",
        "ReportCompletionInput",
        "Writes blueprint to pni_report_src/_facts/ & checks\nnon-empty pni_report/<t>.pdf on disk",
    ],
]

tbl = Table(
    cell_style=Styles.White,
    text_style=Styles.Dark.patch(text_size=9.8),
    header_cell_style=Styles.PrimaryFlat,
    header_text_style=Styles.WhiteBold.patch(text_size=10.5),
    border_style=Styles.MutedThin,
    has_header=True,
)

tbl.set_style_cell_evenodd(
    even_color=Styles.Neutral.shape_fill_color,
    even_text_style=Styles.Dark.patch(text_size=9.8),
    odd_color=Styles.White.shape_fill_color,
    odd_text_style=Styles.Dark.patch(text_size=9.8),
)
tbl.set_style_cell(
    background_color=Styles.PrimaryFlat.shape_fill_color,
    text_style=Styles.WhiteBold.patch(text_size=10.5),
    rows=[0],
)
tbl.set_style_cell(
    background_color=Styles.WarningNeutral.shape_fill_color,
    text_style=Styles.DarkBold.patch(text_size=9.8),
    rows=[1],
    columns=[0],
)
tbl.set_style_cell(
    background_color=Styles.SecondaryNeutral.shape_fill_color,
    text_style=Styles.SecondaryBold.patch(text_size=9.8),
    rows=[2, 3, 4, 5, 6, 7, 8],
    columns=[0],
)
tbl.set_style_cell(
    background_color=Styles.PrimaryNeutral.shape_fill_color,
    text_style=Styles.PrimaryBold.patch(text_size=9.8),
    rows=[9, 10, 11, 12, 13, 14, 15, 16],
    columns=[0],
)

col_widths = [32.0, 24.0, 39.0, 67.0]
row_heights = [8.2] + [8.4] * 16

tbl.draw_flexible(
    xy=(3.0, 148.5),
    column_widths=col_widths,
    row_heights=row_heights,
    data=headers_and_rows,
    align="top_left",
)
save()
```

### 2.1 ゼロ ACK 並列決定論的自動実行 (`7` 解析器)

`pni workflows get-action` / `get-actions`（または `start --pull` / `push-action --next`）が **7 個の決定論的プリミティブ**（`project_inspect`, `ast_analyze`, `run_check`, `security_scan`, `web_pentest`, `migration_analyze`, `progress_analyze`）のいずれかに到達すると、`_advance_deterministic_actions()` が DAG 上で実行可能な全解析器を `ThreadPoolExecutor` で並列実行します。

- **空の ACK ターンを排除**: 決定論的ステップは `action_runs.deterministic_output_json` と `.pni/cache/<workflow_id>/facts.json`（`repo` スコープでは 15 種の Tier C コンパニオン DSL スキャンも 1 回実行）を永続化した直後に自動完了し、そのまま次の AI/ゲートプロンプトへ進みます。
- **再取得時のゼロ再計算**: `pni workflows rewind <run_id> <selector>` で明示的に巻き戻さない限り、キャッシュ済み JSON が SQLite から即座に再利用されます。

### 2.2 グラウンディングゲート・誤検知トリアージ・フラットレポート同期 (`9` AI/ゲートプリミティブ)

- **計画承認ゲート (`confirm_plan` -> `PlanApprovalInput`)**: 人間または CI（`--auto-approve`）が Phase 0 偵察ターゲットを確認し、不要なステップのスキップ（`disabled_steps`）、`focus_areas`、セッション限定 `extra_opt_outs` を確定します。
- **3側面分離アーキテクチャ理解 (`record_architecture` -> `architecture.json`)**: `SystemProfile`・`StructureMap`・`ExecutionFlowMap` の 3 スキーマに分割し、全パスを `AstFacts.module_inventory` および実ワークスペースと照合します。
- **ルール別準拠判定と根拠付き推論 (`ai_interpret` -> `InterpretationInput`)**: 実在パス検証済みの `findings[].file_path` / `action_items[].target_files` と、ルールごとの正規化判定（`pass`, `warn`, `fail`, `not_applicable`）を要求します。
- **スコア刻印・誤検知トリアージ・実行済み DAG (`emit_score` / `synthesize_rollup`)**: 簡潔な v2 `ScoreSubmissionInput`（監査理由付きの **`finding_adjustments`**: `action: "waive" | "reclassify"`, `new_severity`, `reason` を含む）を受け付け、`ExecutionDagSummary`（`provenance.py`）を生成、構造化 JSON 証跡を **`pni_report_src/_facts/`** へ自動同期した上で **`pni_report/<target>_score.json`**・**`*_summary.json`**・**`*_findings.sarif.json`** を出力します。
- **マイグレーション・進捗・ブループリント連動レポートゲート (`emit_migration_plan`, `emit_progress`, `write_drawlib_report`)**: 全 As-Is パスと Git 差分証跡を検証し、ブループリントを `pni_report_src/_facts/` へ書き出し、`ReportCompletionInput.generated_files`（例: `pni_report/<target>.pdf`）が `st_size > 0` で実在することを検証します。

続いて、**55 言語 / 57 文法**を支えるネイティブ `tree-sitter>=0.25.0` CST エンジンと隔離コンテナサンドボックスの詳細については [決定論的解析器とペネトレーションテスト](analyzers_and_pentest.md) を、アンカー付きグレード算出とトリアージの詳細は [7軸品質スコアリングモデル](../04_scoring_and_reports/scoring_model.md) を参照してください。
