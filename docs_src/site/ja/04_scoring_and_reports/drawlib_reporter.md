# Drawlib ビジュアルレポーターと7章ブループリント

LLM にテーブルのソートやドキュメント構成の考案をゼロから任せるのではなく、`pni501`（`v0.2.0`）はすべての診断メトリクスを決定論的にエンリッチ・重複排除・事前ソートして `ReportBlueprint`（`blueprint.py`・`migration_blueprint.py`・`progress_blueprint.py`・`rollup_blueprint.py`）へ変換し、構造化エビデンス JSON を `<src_dir>/_facts/` へ自動同期したうえで、**フラットな自己完結型 Drawlib レポートプロジェクト**（`pni_report_src -> pni_report`）を `compiler.py` からベクター A4 PDF・バイリンガル HTML ポータル・Markdown・PNG へコンパイルします。

```drawlib align=center code=fold file=reporter_compilation_pipeline.png caption="v0.2.0 フラット自己完結型 Drawlib レポートパイプライン（pni_report_src -> pni_report と統合ポータルデプロイ）"
from drawlib.canvas import save, setup
from drawlib.diagrams.architecture import ArchitectureDiagram, Node, NodeGroup, PhosphorIcon
from drawlib.styles import Styles

setup(width=162, height=78, dpi=150)

diag = ArchitectureDiagram(
    node_style=Styles.PrimaryBold,
    node_text_style=Styles.DarkBold.patch(text_size=10.2),
    edge_style=Styles.DarkBold,
    edge_text_style=Styles.DarkBold.patch(text_size=10.0),
    node_card_style=Styles.WhiteBordered.patch(shape_r=1.5),
)

g_inputs = diag.add(
    NodeGroup(
        title="1. Enriched Inputs",
        width=34.5,
        height=70.0,
        style=Styles.Neutral.patch(shape_r=2.0),
        text_style=Styles.DarkBold.patch(text_size=10.8, halign="left", valign="top"),
    ),
    xy=(3.0, 4.0),
)
n_score = g_inputs.add(
    Node(
        "ScoreResult v2.0\n(JSON + SARIF 2.1.0)",
        width=30.0,
        height=16.0,
        icon=PhosphorIcon.MEDAL,
        icon_size=5.4,
        card_style=Styles.PrimaryNeutral.patch(shape_r=1.5),
    ),
    xy=(17.25, 51.5),
)
n_plan = g_inputs.add(
    Node(
        "Migration / Progress\n& Rollup Artifacts",
        width=30.0,
        height=16.0,
        icon=PhosphorIcon.GIT_PULL_REQUEST,
        icon_size=5.4,
    ),
    xy=(17.25, 31.5),
)
n_cache = g_inputs.add(
    Node(
        "_facts/ Evidence Sync\n(facts + arch + plan)",
        width=30.0,
        height=16.0,
        icon=PhosphorIcon.DATABASE,
        icon_size=5.4,
        style=Styles.SecondaryBold,
        card_style=Styles.SecondaryNeutral.patch(shape_r=1.5),
    ),
    xy=(17.25, 11.5),
)

g_bp = diag.add(
    NodeGroup(
        title="2. Blueprint Synthesis",
        width=34.5,
        height=70.0,
        style=Styles.Neutral.patch(shape_r=2.0),
        text_style=Styles.DarkBold.patch(text_size=10.8, halign="left", valign="top"),
    ),
    xy=(43.5, 4.0),
)
n_bp_eng = g_bp.add(
    Node(
        "blueprint.py /\nmig / prog / rollup",
        width=30.0,
        height=18.5,
        icon=PhosphorIcon.SLIDERS_HORIZONTAL,
        icon_size=5.6,
        style=Styles.WhiteBold,
        text_style=Styles.WhiteBold.patch(text_size=10.0),
        card_style=Styles.PrimaryFlat.patch(shape_r=1.5),
    ),
    xy=(17.25, 48.0),
)
n_bp_json = g_bp.add(
    Node(
        "_facts/blueprint.json\n(00_cover + 01..06)",
        width=30.0,
        height=18.5,
        icon=PhosphorIcon.LIST_NUMBERS,
        icon_size=5.6,
        card_style=Styles.PrimaryNeutral.patch(shape_r=1.5),
    ),
    xy=(17.25, 16.0),
)

g_author = diag.add(
    NodeGroup(
        title="3. Flat Source & QA",
        width=34.5,
        height=70.0,
        style=Styles.Neutral.patch(shape_r=2.0),
        text_style=Styles.DarkBold.patch(text_size=10.8, halign="left", valign="top"),
    ),
    xy=(84.0, 4.0),
)
n_src = g_author.add(
    Node(
        "pni_report_src/\nen/ja + _assets/_facts",
        width=30.0,
        height=18.5,
        icon=PhosphorIcon.FILE_CODE,
        icon_size=5.6,
    ),
    xy=(17.25, 48.0),
)
n_qa = g_author.add(
    Node(
        "drawlib rules show\n+ show -g Grid Check",
        width=30.0,
        height=18.5,
        icon=PhosphorIcon.MAGNIFYING_GLASS,
        icon_size=5.6,
        style=Styles.SecondaryBold,
        card_style=Styles.SecondaryNeutral.patch(shape_r=1.5),
    ),
    xy=(17.25, 16.0),
)

g_compile = diag.add(
    NodeGroup(
        title="4. compiler.py Build",
        width=34.5,
        height=70.0,
        style=Styles.Neutral.patch(shape_r=2.0),
        text_style=Styles.DarkBold.patch(text_size=10.8, halign="left", valign="top"),
    ),
    xy=(124.5, 4.0),
)
n_comp = g_compile.add(
    Node(
        "pni report build\n(lint + drawlib.tools)",
        width=30.0,
        height=16.0,
        icon=PhosphorIcon.GEAR_SIX,
        icon_size=5.4,
        style=Styles.WhiteBold,
        text_style=Styles.WhiteBold.patch(text_size=10.0),
        card_style=Styles.PrimaryFlat.patch(shape_r=1.5),
    ),
    xy=(17.25, 51.5),
)
n_pdf = g_compile.add(
    Node(
        "pni_report/<t>.pdf\n(A4 Vector + ToC)",
        width=30.0,
        height=16.0,
        icon=PhosphorIcon.FILE_PDF,
        icon_size=5.4,
        style=Styles.SuccessBold,
        card_style=Styles.SuccessNeutral.patch(shape_r=1.5),
    ),
    xy=(17.25, 31.5),
)
n_opt = g_compile.add(
    Node(
        "HTML / Portal Build\n(docs/reports/<slug>)",
        width=30.0,
        height=16.0,
        icon=PhosphorIcon.BROWSER,
        icon_size=5.4,
    ),
    xy=(17.25, 11.5),
)

diag.connect(n_bp_eng, n_bp_json, label="7 chapters", routing="orthogonal")
diag.connect(n_qa, n_src, label="self-heal", arrow="<->", routing="orthogonal")
diag.connect(n_comp, n_pdf, routing="orthogonal", style=Styles.SuccessBold)
diag.connect(n_pdf, n_opt, routing="orthogonal", style=Styles.MutedBold)

diag.connect(g_inputs, g_bp, routing="orthogonal", style=Styles.PrimaryBold)
diag.connect(g_bp, g_author, routing="orthogonal", style=Styles.PrimaryBold)
diag.connect(g_author, g_compile, routing="orthogonal", style=Styles.PrimaryBold)

diag.draw(xy=(0.0, 0.0))
save()
```

---

## 1. フラットな自己完結型レイアウトと `_facts/` エビデンス自動同期

`pni501 v0.2.0` では、Drawlib レポートのディレクトリ構造をデフォルト `pni_report_src -> pni_report`（`DEFAULT_REPORT_SRC_DIR = "pni_report_src"`、`DEFAULT_REPORT_OUTPUT_DIR = "pni_report"`）とする **フラットな自己完結型レイアウト** に刷新しました。従来のような `<target>_src/` の二重ネストは廃止され、`src_dir` 直下に設定ファイル・共通スタイル・言語別チャプター・ブランドアセット・同期済みエビデンス JSON がすべて配置されます。

```text
pni_report_src/                     # src_dir 直下にフラット配置（<target>_src/ ネストなし）
├── drawlib.toml                    # [i18n] (en / ja / en,ja)・タイトル・テーマ設定
├── styles.py                       # Drawlib Colors & Styles プリセットトークン
├── utils.py                        # 共通ヘルパー + 自動注入された draw_pni_logo()
├── _assets/                        # 公式ロゴ (logo.png, logo_dark.png, favicon.png, ogp.png)
├── _facts/                         # 自動同期された構造化エビデンス JSON（Git 管理可能）
│   ├── project_facts.json          # マニフェスト・ロックファイル・依存メタデータ
│   ├── ast_facts.json              # Tree-sitter CST モジュール棚卸し・危険シンク・API 境界
│   ├── runtime_facts.json          # コンテナビルド・オフラインテスト・カバレッジ・スモーク検証
│   ├── security_facts.json         # Trivy FS/イメージ CVE・IaC 設定不備・マスク済み秘匿情報
│   ├── pentest_facts.json          # 動的 HTTP DAST プローブ結果・確認済み脆弱性
│   ├── architecture.json           # 3側面 ArchitectureRecord（プロファイル・層構造・実行フロー）
│   ├── score.json                  # 正規 ScoreResult v2.0（ベースライン・Δ・FPトリアージ・DAG）
│   ├── plan.json                   # Pre-Flight 実行計画・検証済み Mermaid DAG
│   └── blueprint.json              # 章別事前ソート済みブループリント（00..06）
├── en/                             # 英語チャプター (00_cover.md .. 06_*.md)
└── ja/                             # 任意の日本語チャプター (00_cover.md .. 06_*.md)
```

- **`_facts/` 自動同期の意義**: `pni report init`・ワークフローレポート合成・`pni report build` の実行時に（`src/pni/_reporter/facts_sync.py`）、構造化エビデンス JSON（`project_facts.json`、`ast_facts.json`、`runtime_facts.json`、`security_facts.json`、`pentest_facts.json`、`architecture.json`、`score.json`、`plan.json`、および統合 `facts.json`・`blueprint.json`）が `<src_dir>/_facts/` へ自動同期されます。一方、一時的な SQLite ステート DB（`workflow_state.db`）や Trivy キャッシュ、生コンテナログは `.pni/cache/` に厳格に留められるため、レポートソース一式をそのまま Git コミットして別環境でも完全に再現ビルドできます。
- **事前計算された章別ペイロード**: `blueprint.py`・`migration_blueprint.py`・`progress_blueprint.py`・`rollup_blueprint.py` が事前ソート済みテーブル・チャート系列・KPI カード値・推奨 Drawlib コンポーネントを `<src_dir>/_facts/` に書き出すため、ファインディングの抜け漏れやソート崩れが発生しません。

---

## 2. 2系統の7章構成 ReportBlueprint アーキテクチャ

健全性監査ワークフロー（`category: audit`）とモダナイゼーションワークフロー（`category: migration`）はいずれも、英語（`en`）・日本語（`ja`）・バイリンガル（`en,ja`）に対応した同一の **7ファイル線形 `doc` レイアウト（`00_cover.md` + `01..06.md`）** に標準化されています。Drawlib は `00_cover.md` の直後にハイパーリンク付き目次（Table of Contents）を自動挿入します。（なお、進捗ワークフローは `progress_blueprint.py` による 5 ファイル構成 `00_cover.md` + `01..04.md`、マルチ言語ロールアップは `rollup_blueprint.py` による 6 ファイル構成 `00_cover.md` + `01..05.md` を採用します。）

```drawlib align=center code=fold file=blueprint_chapter_comparison.png caption="健全性監査レポートとマイグレーション実行計画の7章構成 ReportBlueprint アーキテクチャ比較"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import CardList, Panel
from drawlib.styles import Styles

setup(width=170, height=112, dpi=150)

audit_panel = Panel(
    "Health Audit Blueprint (blueprint.py)",
    header_variant="filled",
    header_height=8.5,
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=11.2),
)
audit_panel.draw(xy=(3.0, 3.0), width=79.5, height=106.0)

audit_cards = CardList(
    style=Styles.WhiteBordered.patch(shape_r=1.4),
    text_style=Styles.DarkBold.patch(text_size=10.2),
    description_style=Styles.Dark.patch(text_size=10.0),
    badge_shape="rounded_rect",
    badge_style=Styles.PrimaryNeutral,
    badge_text_style=Styles.PrimaryBold.patch(text_size=10.0),
    icon_style=Styles.PrimaryBold,
    direction="vertical",
    spacing=2.0,
)
audit_cards.add(
    "00_cover.md — Diagnostic Cover",
    "Panel + KpiCards (Score/Grade, Rules) -> Auto ToC",
    badge_text="00",
    icon=phosphor.medal,
    badge_style=Styles.PrimaryFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=10.0),
    icon_style=Styles.WhiteBold,
)
audit_cards.add(
    "01_executive_summary.md",
    "7-Axis RadarChart + KpiCards + Strengths/Top Risks",
    badge_text="01",
    icon=phosphor.chart_polar,
)
audit_cards.add(
    "02_architecture_and_structure.md",
    "TreeNode/Table + ClassDiagram & HeatmapOverlay",
    badge_text="02",
    icon=phosphor.tree_structure,
)
audit_cards.add(
    "03_remediation_roadmap.md",
    "Phased P0 -> P1 -> P2 Roadmap + Traceability Table",
    badge_text="03",
    icon=phosphor.git_commit,
)
audit_cards.add(
    "04_standards_and_findings.md",
    "Executed DAG + Baseline Δ + FP Triage + Findings",
    badge_text="04",
    icon=phosphor.list_checks,
)
audit_cards.add(
    "05_code_and_runtime_analysis.md",
    "Module HeatmapChart + Runtime/Coverage Bars",
    badge_text="05",
    icon=phosphor.cpu,
)
audit_cards.add(
    "06_security_and_supply_chain.md",
    "App/OS CVE Table + CWE Sinks & API Auth Surface",
    badge_text="06",
    icon=phosphor.shield_check,
)
audit_cards.draw(xy=(5.5, 5.5), width=74.5, height=92.5)

mig_panel = Panel(
    "Migration Plan Blueprint (migration_blueprint.py)",
    header_variant="filled",
    header_height=8.5,
    style=Styles.PrimaryNeutral.patch(shape_r=2.0),
    header_style=Styles.SecondaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=11.2),
)
mig_panel.draw(xy=(87.5, 3.0), width=79.5, height=106.0)

mig_cards = CardList(
    style=Styles.WhiteBordered.patch(shape_r=1.4),
    text_style=Styles.DarkBold.patch(text_size=10.2),
    description_style=Styles.Dark.patch(text_size=10.0),
    badge_shape="rounded_rect",
    badge_style=Styles.SecondaryNeutral,
    badge_text_style=Styles.SecondaryBold.patch(text_size=10.0),
    icon_style=Styles.SecondaryBold,
    direction="vertical",
    spacing=2.0,
)
mig_cards.add(
    "00_cover.md — Migration Cover",
    "Panel + KpiCards (Mode, Strategy, PRs) -> Auto ToC",
    badge_text="00",
    icon=phosphor.compass,
    badge_style=Styles.SecondaryFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=10.0),
    icon_style=Styles.WhiteBold,
)
mig_cards.add(
    "01_migration_strategy_summary.md",
    "Assumptions/Non-Goals + As-Is->To-Be Gap Table",
    badge_text="01",
    icon=phosphor.arrows_left_right,
)
mig_cards.add(
    "02_architecture_waves_and_contracts.md",
    "Port/Adapter ClassDiagram + Wave 1..4 Roadmap",
    badge_text="02",
    icon=phosphor.graph,
)
mig_cards.add(
    "03_spec_vs_bug_decision_log.md",
    "Hyrum's Law Decision Matrix + Sign-Off Workflow",
    badge_text="03",
    icon=phosphor.scales,
)
mig_cards.add(
    "04_five_phase_gate_roadmap.md",
    "Phase 0..4 Gated Timeline + Exit/Rollback Matrix",
    badge_text="04",
    icon=phosphor.flag_checkered,
)
mig_cards.add(
    "05_codemod_and_refactoring_design.md",
    "Codemod vs Manual Chart + Touchpoint->Port Table",
    badge_text="05",
    icon=phosphor.wrench,
)
mig_cards.add(
    "06_pr_wbs_and_verification_gates.md",
    "Topological PR-01..NN WBS Table + Gate Summary",
    badge_text="06",
    icon=phosphor.git_pull_request,
)
mig_cards.draw(xy=(90.0, 5.5), width=74.5, height=92.5)

save()
```

### 2.1 健全性監査 7章ブループリント（`blueprint.py`）

`src/pni/_reporter/blueprint.py` は、`ScoreResult` v2.0、`WorkflowFactsBundle`、および `ArchitectureRecord` を以下の 7 章へマッピングします。

| 章ファイル | 主なブループリントデータスライス | 標準 Drawlib ビジュアルコンポーネント |
| :--- | :--- | :--- |
| **`00_cover.md`** | `overall_score`、`grade`、`workflow_id`、`evaluated_at`、ルール準拠サマリ、ファインディング件数 | フルブリード表紙 `Panel` + `draw_pni_logo()` + `KpiCards`（直後に PDF/HTML 目次を自動生成） |
| **`01_executive_summary.md`** | `category_scores`（`7` 軸）、`category_rationales`、`strengths`、主要 Critical/High リスク、`approved_plan_summary` | 7軸 `RadarChart` + `KpiCards` + `CardList` / サマリテーブル |
| **`02_architecture_and_structure.md`** | `architecture_record`（`layers_and_modules`、`flows_and_state`）、`internal_import_graph`、`module_hotspots` | `TreeNode` / `Table` + UML `ClassDiagram` と `HeatmapOverlay(show_contour_lines=False)` |
| **`03_remediation_roadmap.md`** | `action_plan`（`P0 -> P1 -> P2` 改善アクション、対象ファイル、工数、関連ルール ID） | フェーズ別 `Roadmap` / `ChevronProcess` + 改善トレーサビリティ `Table` |
| **`04_standards_and_findings.md`** | `execution_dag`（`AUTO`/`AI`/`HYBRID`/`SKIP` + `audit_scope`）、7軸 `baseline_scores` 対 AI Δ（`±10 pt`）、`audit_dimensions`、`rule_compliance`、`consolidated_findings`、`triaged_adjustments`、`opt_outs`、軽量 `artifact_manifest` | 実行済み監査 DAG（`drawlib.graph` / `flow`）+ ベースライン対最終 `Table` + 弱点順 `BarChart` + 位置統合ファインディング & FP トリアージ `Table` |
| **`05_code_and_runtime_analysis.md`** | `modules`（`loc`、複雑度、型注釈、docstring、`risk_score`）、`runtime_facts`（テスト、カバレッジ、スモーク） | モジュール品質 `HeatmapChart` + 複数系列ランタイム・カバレッジ `BarChart` |
| **`06_security_and_supply_chain.md`** | `security_facts`（Trivy アプリ/OS CVE、秘密情報、IaC）、`dangerous_sinks`、`api_endpoints`、`pentest_facts` | アプリ/OS CVE・CWE シンク内訳 + 動的 HTTP ペネトレーションテスト判定 `Table` |

### 2.2 マイグレーション実行計画 7章ブループリント（`migration_blueprint.py`）

完了した健全性監査実行を起点とするモダナイゼーションワークフロー（`based_on` 指定）では、`src/pni/_reporter/migration_blueprint.py` が `MigrationPlanResult` と `MigrationFacts` を並列の 7 章構成実行ブループリントへ合成します。

| 章ファイル | 主なブループリントデータスライス | 標準 Drawlib ビジュアルコンポーネント |
| :--- | :--- | :--- |
| **`00_cover.md`** | `transformation_mode`、`migration_strategy`、`api_compatibility`、`bug_handling_policy`、PR・フェーズ数 | フルブリード移行計画表紙 `Panel` + `draw_pni_logo()` + `KpiCards`（直後に目次を自動生成） |
| **`01_migration_strategy_summary.md`** | `confirmed_assumptions`、`non_goals`、`target_axes`（`As-Is -> To-Be` スタック・リスク軸） | 移行戦略 `CardList` + `As-Is -> To-Be` ギャップ変換マトリクス `Table` |
| **`02_architecture_waves_and_contracts.md`** | `target_architecture`（`target_layers`、`component_mappings`）、`refactoring_waves`、`cycle_cuts`、`implicit_contracts` | To-Be Port/Adapter `ClassDiagram` / `ArchitectureDiagram` + Wave `1..4` 依存トポロジ |
| **`03_spec_vs_bug_decision_log.md`** | `decision_log`（`DEC-01..NN`）、`spec_vs_bug_candidates`（PO 承認を要する Hyrum の法則の挙動） | 意思決定ワークフロー図 + `DEC-01..NN` サインオフマトリクス `Table` |
| **`04_five_phase_gate_roadmap.md`** | `phase_gates`（`Phase 0` 特性テストから `Phase 4` カットオーバーまでの完了条件・ロールバック手順） | 5フェーズゲート付き `Roadmap` / `GanttChart` + 完了・ロールバック基準 `Table` |
| **`05_codemod_and_refactoring_design.md`** | `mechanical_codemods`、`manual_blockers`、`boundary_touchpoints`（`db`、`http`、`cache`、`auth` ポート） | 自動 Codemod 対 手動リファクタリング `BarChart` + 境界タッチポイント変換 `Table` |
| **`06_pr_wbs_and_verification_gates.md`** | `pr_wbs`（`PR-01..NN` トポロジカル順 PR チケット、`depends_on_prs`、`verification_cmd`） | PR 依存 DAG / フェーズ内訳 + `PR-01..NN` 作業分解構成（WBS）`Table` |

---

## 3. 非破壊スキャフォールディング・組み込みプリフライト・統合ポータル運用

`src/pni/_reporter/compiler.py` と `src/pni/_reporter/drawlib_guide.py` は、`pni report` 配下の 2 つのサブコマンド（`pni report init` と `pni report build`）を通じて、スキャフォールディングからビルド・リンク検証まで一貫した品質ゲートを提供します。

### 3.1 非破壊 `pni report init` と `pni report build`

前半の CST 解析やルール解釈ステップでシステムプロンプトが肥大化するのを防ぐため、エージェントは `pni_report_src/<lang>/*.md` を執筆する直前に Drawlib ルールをオンデマンドで読み込み、`-g` 座標グリッドで各図を検証したうえで `pni_report/` へ最終成果物をコンパイルします。

```bash
# 1. 非破壊で pni_report_src/ を初期化（既存 *.md を保持しつつ _assets/ を配置）
pni report init full_audit --src-dir pni_report_src --lang en --style google

# 2. Drawlib API・コンポーネント仕様をオンデマンド参照（引数推測を防止）
uv run drawlib rules show overview
uv run drawlib rules show project-doc
uv run drawlib rules show api

# 3. ビルド前に Stage 2 座標グリッド視覚検査（-g）を実施
uv run drawlib show pni_report_src/en/01_executive_summary.md \
  -s pni_report_src/styles.py -u pni_report_src/utils.py \
  -g -o .drawlib/scratch/exec_summary_grid.png

# 4. 組み込み lint_drawlib_chapters() を自動実行し pni_report/full_audit.pdf を生成
pni report build full_audit --src-dir pni_report_src --output-dir pni_report
```

### 3.2 組み込みプリフライトリンター（`lint_drawlib_chapters`）とリンク検証

`pni report build` はビルド直前に `lint_drawlib_chapters()` と各種品質ガードレールを自動実行します（個別のチェックコマンドを実行する必要はありません）。

- **非破壊な再スキャフォールディングとブランドアセット（`scaffold_report_project`）**: 初回作成時にスターターサンプル（`00_cover.md`・`01_overview.md`・`02_design.md`）を削除し、印刷向けワイドテーブル CSS（`@media print`）を追記し、公式ブランドアセット（`_assets/{logo.png,logo_dark.png,favicon.png,ogp.png}`）をコピーして `utils.py` に `draw_pni_logo()` を注入します。`--force` を指定した再実行でも執筆済みの `<lang>/*.md` はすべて保護されます。
- **未マスクトークン検出ガード**: Markdown 本文中の生 GitHub/AWS/Slack/OpenAI トークン文字列（`ghp_`、`github_pat_`、`AKIA`、`xox*`、`sk-live-` 等）を検出し、GitHub Push Protection によるプッシュ遮断を未然に防ぎます。
- **複数系列チャート凡例・UML 等高線/コントラストガード**: `.add_series(...)` を 2 回以上呼ぶ `BarChart` / `LineChart` の `.draw_legend(...)` 漏れ、`ClassDiagram` と `HeatmapOverlay(..., show_contour_lines=True)` の等高線衝突、および `ClassDiagram` / `ClassNode` での `Styles.White` 使用（白背景に白文字で視認不能になるため `Styles.Neutral` を使用）をプリフライト検出します。
- **出力正規化とリンク切れスキャン（`_verify_links`）**: `pni report build` は `<target>_<default_lang>.pdf` を `<output_dir>/<target>.pdf`（`page_break=True`、`generate_index=True`）へ正規化します（多言語ビルド時は `<target>_en.pdf` / `<target>_ja.pdf` も保持）。`-f html` 指定時は `_verify_links()` が `drawlib.tools.scan_broken_links()`（マルチポータル相対リンク検証用 `--link-check-root <dir>` 対応）を実行し、リンク切れや画像欠損があればフェイルクローズ（`strict_links=True`）で停止します。

### 3.3 統合ポータルデプロイ（`docs_src/` -> `docs/`）

`pni report build` はフラットな `src_dir` をそのままビルドし、`--html-output-dir` と `--link-check-root` に対応しているため、公式サイトと複数のバイリンガル監査・移行レポートを単一の静的 GitHub Pages ポータル（`docs/`）へ統合デプロイできます。

- **公式ドキュメントサイト**: `docs_src/site/` を `docs/`（`docs/{en,ja}/` + ルート `index.html`）へビルド。
- **埋め込みプロジェクトレポート**: `docs_src/reports/<slug>/` 配下の各自己完結型レポートを `docs/reports/<slug>/` へ HTML + A4 PDF 出力し、`docs/` ルート基準でポータル横断の相対リンクを検証。

```bash
# バイリンガルレポートを統合ポータル配下へコンパイル
pni report build my_service \
  --src-dir docs_src/reports/my_service \
  --output-dir docs/reports/my_service \
  --html-output-dir docs/reports/my_service \
  --link-check-root docs \
  -f pdf -f html

# ポータル全体（サイト + 全レポート）のリンク整合性を一括検証
uv run drawlib serve docs/ --check
```

上流の JSON スキーマ・ベースラインアンカリング・FP トリアージの詳細は [7軸品質スコアリングモデル](scoring_model.md) を、実際のバイリンガル生成例は [サンプルレポートギャラリー](sample_reports.md) を、`pni report` の全 CLI フラグは [ルール拡張と CLI リファレンス](../05_languages_and_reference/rules_and_cli.md) を参照してください。
