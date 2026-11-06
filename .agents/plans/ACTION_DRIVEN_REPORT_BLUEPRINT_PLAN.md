# アクション連動型データ提出・決定的ソート・レポート設計図（Blueprint）実装計画書

本ドキュメントは、ワークフローの各 Action 実行時（`get-action` → `push-action`）に**ステップ固有の構造化エビデンス（ルール別合否・監査軸スコア・指摘事項・改善案・3観点アーキテクチャ）を提出させ**、それらを **Python コード側で機械的に集約・重複排除・ソートして「レポート設計図（Report Blueprint）」を確定**させた上で、最終ステップ（`write_drawlib_report`）で AI に Drawlib レポートを描画させるための実装計画書です。

既存の多言語 AST 基盤（[CHECK_LANGUAGE_MATRIX_PLAN.md](./CHECK_LANGUAGE_MATRIX_PLAN.md)）および言語非依存エンジニアリング標準（[UNIVERSAL_ENGINEERING_STANDARDS_PLAN.md](./UNIVERSAL_ENGINEERING_STANDARDS_PLAN.md)）の検査結果を、**漏れなく・安定した順序と章構成で最終レポートへ反映させる**ことを目的とします。

---

## 1. 現状の課題と解決アーキテクチャ（Map → Deterministic Reduce/Sort → Render）

### 1.1. 現状の4つの課題
1. **中間ステップ提出物の揮発**: 各 `ai_interpret` で提出した内容が SQLite に保存されるものの、`emit_score` 時にコードでマージされず、AI の記憶頼みで再構成されている。また「検査して合格（`PASS`）したルール」の記録欄がないため、健全なプロジェクトほど新しい検査項目がレポートから消えて見える。
2. **3観点アーキテクチャ記録の欠落**: `record_architecture` で記録した `SystemProfile`・`StructureMap.layers`・`ExecutionFlowMap`（実行フロー・状態・例外モデル）が `ScoreResult` に丸ごと引き継がれていない。
3. **ソート順・優先度順の AI 依存**: 指摘事項（`findings`）、合格ルール一覧、改善計画（`action_plan`）、監査軸スコアの並び順が AI 任せになっている。
4. **旧4章固定テンプレートと過剰な差分維持制約**: [`drawlib_guide.py`](../../src/pni/_reporter/drawlib_guide.py) が旧4章・固定6軸のみを前提とし、「既存 `.md` の構成を変えない」制約により新しい監査軸や実行フロー図が描画されない。

### 1.2. 新パイプラインの全体像

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Phase 1: Map — 各 Action ごとの構造化提出 (get-action -> push-action)        │
│  ・project_inspect / ast_analyze : 確定ファクト抽出 + 確認応答               │
│  ・record_architecture (×3観点)  : SystemProfile / StructureMap / FlowMap    │
│  ・ai_interpret (各監査ステップ) :                                           │
│      1) active rules 全件に対する RuleCheckResult (pass/warn/fail + 根拠)    │
│      2) その監査ステップの step_score (0-100) と summary                     │
│      3) 実在パス検証済みの findings と action_items                          │
├──────────────────────────────────────────────────────────────────────────────┤
│ Phase 2: Reduce & Sort — Python コードによる決定的集約・重複排除・ソート     │
│  (新規モジュール: src/pni/_workflows/aggregator.py)                          │
│  ・監査ステップ別スコア (audit_dimensions) を弱点順 (score 昇順) にソート    │
│  ・全ルール適合表 (rule_compliance) を FAIL -> WARN -> PASS -> N/A 順にソート│
│  ・ファイル別リスク密度 (module_hotspots) を違反重要度重みから自動算出       │
│  ・全 findings を重複排除し CRITICAL -> HIGH -> MEDIUM -> LOW -> INFO 順整列 │
│  ・全 action_plan を重複排除し P0 -> P1 -> P2 順に整列                       │
│  ・3観点 ArchitectureRecord 全体を ScoreResult に完全統合                    │
├──────────────────────────────────────────────────────────────────────────────┤
│ Phase 3: Blueprint & Render — 確定設計図に基づく Drawlib レポート生成        │
│  (新規モジュール: src/pni/_reporter/blueprint.py + drawlib_guide.py 刷新)    │
│  ・Python コードが章番号・タイトル・各図表に載せる確定ソート済みデータを     │
│    ReportBlueprint (.pni/cache/<target>_report_blueprint.json) として出力    │
│  ・write_drawlib_report の get-action で確定済みテーブル/系列データを提示し、 │
│    AI は 5章構成の Drawlib 可視化と解説文執筆に専念する                      │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. データモデル拡張仕様 (`src/pni/_actions/base_model.py`)

後方互換性を保ちつつ（新規フィールドはデフォルト値付き）、各ステップの提出物と最終 `ScoreResult` を拡張します。

### 2.1. ルール適合チェックと監査ステップスコア

```python
RuleComplianceStatus = Literal["pass", "warn", "fail", "not_applicable"]


class RuleCheckResult(BaseModel):
    """1つの適用ルールに対する合否判定と確定エビデンス（Cleanプロジェクトでも検査実績を残す）。"""

    rule_id: str                                   # 例: "common/supply_chain", "common/maintainability"
    status: RuleComplianceStatus                   # "pass" | "warn" | "fail" | "not_applicable"
    source_action: str = ""                        # 例: "supply_chain_audit"
    evidence: str                                  # 確定ファクトに基づく根拠（例: "uv.lock present, 0 unpinned"）
    summary: str                                   # 1行の判定要約


class AuditDimensionScore(BaseModel):
    """ワークフロー内で実行された各監査アクション単位のスコアカード。"""

    action_id: str                                 # 例: "act-03"
    audit_id: str                                  # 例: "supply_chain_audit" (source_action または action_id)
    title: str                                     # 例: "Evaluate Supply-Chain, CI Permissions & Secret Hygiene"
    score: int = Field(ge=0, le=100)
    grade: HealthGrade                             # Python 側で score から自動算出 (S>=90, A>=80, B>=70, C>=60, D<60)
    rules_evaluated: list[str] = Field(default_factory=list)
    pass_count: int = 0
    warn_count: int = 0
    fail_count: int = 0
    summary: str = ""
```

### 2.2. `InterpretationInput`（各 `ai_interpret` の `push-action` 提出スキーマ）の強化

```python
class InterpretationInput(BaseModel):
    """各 ai_interpret アクション完了時に AI が提出する構造化データ。"""

    summary: str
    step_score: Optional[int] = Field(default=None, ge=0, le=100)
    rule_checks: list[RuleCheckResult] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    category_rationales: dict[str, str] = Field(default_factory=dict)
    suggested_scores: dict[str, int] = Field(default_factory=dict)
    modules: list[ModuleSummary] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    action_items: list[ActionItem] = Field(default_factory=list)
```

### 2.3. ファイル別ホットスポット指標と `ScoreResult` への完全統合

```python
class ModuleHotspot(BaseModel):
    """Python コードで確定算出されるファイル単位の保守・障害リスク密度 (0.0〜1.0)。"""

    file_path: str
    loc: int = 0
    risk_score: float = Field(default=0.0, ge=0.0, le=1.0)
    finding_counts: dict[str, int] = Field(default_factory=dict)  # {"critical": 1, "high": 2, ...}
    top_rules: list[str] = Field(default_factory=list)


class ScoreResult(BaseModel):
    # ... 既存フィールドをすべて維持 ...
    architecture_record: Optional[ArchitectureRecord] = None
    audit_dimensions: list[AuditDimensionScore] = Field(default_factory=list)
    rule_compliance: list[RuleCheckResult] = Field(default_factory=list)
    module_hotspots: list[ModuleHotspot] = Field(default_factory=list)
```

---

## 3. 各ステップでの指示と検証 (`ai_actions.py` & `engine.py`)

### 3.1. `get-action` での明確な提出指示 (`src/pni/_actions/ai_actions.py`)
`PrimitiveType.AI_INTERPRET` の `get-action` 出力に、そのステップ固有の **`Active Rule Checklist`** セクションを自動生成します。
- 例（`supply_chain_audit` の場合）:
  - **必須提出項目 1 (`step_score`)**: この監査ステップ単体の評価点（`0〜100`）を算出して提出すること。
  - **必須提出項目 2 (`rule_checks`)**: 適用ルール `["common/supply_chain", "common/security", "common/git_workflow"]` の**全件**について、`pass` / `warn` / `fail` / `not_applicable` と `ProjectFacts` / `AstFacts` 上の確定数値を `evidence` に記載して提出すること。
  - **必須提出項目 3 (`findings` & `action_items`)**: `warn` / `fail` となった項目について、実在する `file_path`・`line` 付きの `Finding` と、改善のための `ActionItem`（`P0` / `P1` / `P2`）を提出すること。

### 3.2. `push-action` での検証とハルシネーション防止 (`src/pni/_workflows/engine.py`)
1. **パス実在検証の横展開**:
   - `record_architecture` だけでなく、`ai_interpret` と `emit_score` でも `findings[].file_path`（指定時）および `action_items[].target_files[]` がリポジトリまたは `AstFacts.module_inventory` に実在するかを `_verify_grounded_paths` で検証し、架空ファイルパスの混入をブロックします。
2. **適用ルールの網羅チェック（警告・自動補完）**:
   - `action.rules` が存在する `ai_interpret` ステップで `rule_checks` が提出された際、`source_action` を自動刻印します。

---

## 4. Python コードによる決定的集約・重複排除・ソート仕様 (`src/pni/_workflows/aggregator.py`)

新規モジュール `src/pni/_workflows/aggregator.py` を作成し、SQLite 内の全完了アクションから以下を **100% 決定論的アルゴリズム** で組み立てます。

| 集約対象 | 重複排除キー | Python コードによる決定的ソート順（優先キー → 副キー） |
| :--- | :--- | :--- |
| **`audit_dimensions`**<br>(監査ステップ別スコア) | `action_id` | **`(score ASC, -fail_count ASC, -warn_count ASC, seq ASC)`**<br>→ **スコアが低い（弱点）監査軸が先頭**に来るよう整列（`step_score` 未指定時は `suggested_scores` 平均または違反減点式から自動算出） |
| **`rule_compliance`**<br>(全ルール合否マトリクス) | `rule_id`<br>(複数ステップで評価された場合は最も厳しい判定 `fail > warn > pass > not_applicable` を採用し根拠を結合) | **`(STATUS_RANK[status], rule_id ASC)`**<br>→ **`FAIL (0) → WARN (1) → PASS (2) → NOT_APPLICABLE (3)`** の順、同一ステータス内は `rule_id` 辞書順 |
| **`findings`**<br>(全ルール違反・提案) | `(rule_id, file_path or "", line or 0, symbol or "")` | **`(SEVERITY_RANK[severity], category ASC, rule_id ASC, file_path or "~", line or 0)`**<br>→ **`CRITICAL (0) → HIGH (1) → MEDIUM (2) → LOW (3) → INFO (4)`** の順 |
| **`action_plan`**<br>(改善ロードマップ) | `(priority, normalized_title)` | **`(PRIORITY_RANK[priority], category ASC, title ASC)`**<br>→ **`P0 (0) → P1 (1) → P2 (2)`** の順 |
| **`module_hotspots`**<br>(ファイル別リスク密度) | `file_path`<br>(`AstFacts.module_inventory` 全ファイル + 指摘対象ファイル) | **`(-risk_score ASC, -loc ASC, file_path ASC)`**<br>→ 各ファイルの違反重み合計（`critical=0.45, high=0.28, medium=0.15, low=0.06, info=0.02` + 複雑関数/Global状態ペナルティ、上限 `1.0`、無違反モジュールはベース値 `0.06`）で算出・降順ソート |
| **`strengths`**<br>(プロジェクトの強み) | 正規化テキスト一致 | 実行ステップ順 (`seq ASC`) にマージし重複を除去 |
| **`architecture_record`** | 3観点マージ | `SystemProfile` + `StructureMap` + `ExecutionFlowMap` を完全保持 |

### `emit_score` の省力化と一貫性保証
- `emit_score` の `get-action` 実行時点で、すでに `aggregator.py` が計算した **事前集約サマリー（推奨カテゴリ点数・ソート済み Findings 一覧・ソート済み Rule Compliance・ソート済み Action Plan）** をプロンプトに提示します。
- `emit_score` の `push-action` 実行時、`_enrich_score_result` が先行ステップの全 `findings`・`rule_checks`・`action_items`・`audit_dimensions`・`module_hotspots`・`architecture_record` を機械的にマージ＆再ソートして `<target>_score.json` に書き出します。これにより **「途中のステップで見つけた違反や PASS 記録が `score.json` から抜け落ちる」事象が構造上ゼロ** になります。

---

## 5. レポート設計図 (`ReportBlueprint`) の自動生成 (`src/pni/_reporter/blueprint.py`)

新規モジュール `src/pni/_reporter/blueprint.py` を作成し、`ScoreResult` と `WorkflowFactsBundle` から **章ごとの描画仕様・確定データ配列・削除すべき旧章ファイル** を定義した `ReportBlueprint` を生成し、`.pni/cache/<target>_report_blueprint.json` に保存するとともに `write_drawlib_report` の `get-action` プロンプトへ埋め込みます。

### 標準 5 章構成（ワークフローの実行内容を余さず可視化）

| 章ファイル名 | 章テーマ | Python 側で事前確定・ソートして AI に渡す描画データ | 必須 Drawlib 図表（各章 2 図） |
| :--- | :--- | :--- | :--- |
| **`00_cover.md`** | エグゼクティブサマリー＆総合健全性 | ・総合スコア/Grade (`overall_score`, `grade`)<br>・ルール合格率 (`pass_count / evaluated_rules_count`)<br>・固定6軸スコア + 監査ステップ弱点トップ3 | 1. エグゼクティブ KPI カード (`KpiCards`)<br>2. 6軸健全性レーダー + 要約カード (`RadarChart` + `CardList`) |
| **`01_architecture_flows.md`** | システムプロファイル・レイヤー境界・実行フロー | ・`SystemProfile`（目的・技術スタック・実行形態）<br>・`StructureMap`（レイヤー・モジュール依存）<br>・`module_hotspots`（コード算出済み `risk_score`）<br>・`ExecutionFlowMap`（エントリポイント・実行ステップ・状態/例外モデル） | 1. モジュール/レイヤー依存図 × 空間リスクオーバーレイ (`ClassDiagram` + `HeatmapOverlay`、値は `module_hotspots` 確定値)<br>2. 実行フロー＆状態・例外ガバナンス図 (`Roadmap` / `TreeNode` + `CardList`) |
| **`02_standards_compliance.md`** | 横断エンジニアリング標準＆監査軸適合マトリクス | ・ソート済み `audit_dimensions`（実行された全監査ステップの点数、弱点順）<br>・ソート済み `rule_compliance`（`FAIL → WARN → PASS` 順のルール別合否と確定エビデンス） | 1. 監査ステップ別スコア比較グラフ (`BarChart`: Supply Chain / AST / Library・Service・CLI / Testing 等)<br>2. エンジニアリング標準・ルール適合エビデンス表 (`Table`: OpenSSF, SIG, OWASP, Library/CLI/12-Factor, Diátaxis 等) |
| **`03_metrics_heatmap.md`** | 定量 AST・サプライチェーン・運用メトリクス分析 | ・モジュール別 LOC / カバレッジ / 複雑度 / 違反密度マトリクス<br>・`metrics_snapshot` の主要確定指標（型・Doc・テスト・SIG複雑度/引数・OpenSSF・12-Factor運用衛生） | 1. モジュール × 品質ディメンション適合ヒートマップ (`HeatmapChart`)<br>2. 確定メトリクス内訳チャート / スコア比較 (`BarChart` または `Table`) |
| **`04_findings_roadmap.md`** | 重要度順ルール違反エビデンス＆優先度順ロードマップ | ・重要度順ソート済み `findings`（0件の場合は上位 PASS/改善余地項目）<br>・優先度順ソート済み `action_plan`（`P0 → P1 → P2`） | 1. 重要度順ルール監査指摘一覧表 (`Table`)<br>2. `P0 → P1 → P2` 段階的改善ロードマップ (`Roadmap`) |

### `drawlib_guide.py` の更新ポリシー改善
- 旧ポリシー（「既存の章構成を変更しない」）を廃止し、**「Blueprint 章構成への同期ポリシー」** に変更します。
  - `styles.py`, `utils.py`, `style.css`, `template.html` は非破壊で維持する。
  - 章ファイル（`00_cover.md` 〜 `04_findings_roadmap.md`）は **Python が生成した `ReportBlueprint` の章リスト・ソート順データに厳密に従って作成・上書き** し、Blueprint に含まれない旧名の `.md` ファイルが残っていれば整理する。
- さらに `write_drawlib_report` の `push-action` バリデーションで、PDF の存在確認に加えて **`reports_src/<target>_src/` 内の章ファイル群が Blueprint の期待章リストと一致しているか** も検証可能にします。

---

## 6. 実装フェーズ計画

### Phase 1: スキーマ拡張と Action 提出指示の強化
1. [`src/pni/_actions/base_model.py`](../../src/pni/_actions/base_model.py) に `RuleComplianceStatus`, `RuleCheckResult`, `AuditDimensionScore`, `ModuleHotspot` を追加し、`InterpretationInput` と `ScoreResult` を拡張（後方互換デフォルト付き）。
2. [`src/pni/_actions/ai_actions.py`](../../src/pni/_actions/ai_actions.py) と [`src/pni/_workflows/engine.py`](../../src/pni/_workflows/engine.py) を更新し、`ai_interpret` の `get-action` で適用ルール全件に対する `rule_checks`・`step_score`・`findings`・`action_items` の提出指示を明示する。
3. `push-action` で `findings[].file_path` と `action_items[].target_files` の実在パス検証を追加する。

### Phase 2: Python アグリゲータ＆ソータ (`aggregator.py`) の実装
1. `src/pni/_workflows/aggregator.py` を新規作成し、`audit_dimensions`・`rule_compliance`・`findings`・`action_plan`・`module_hotspots`・`architecture_record` の決定的集約・重複排除・ソートロジックを実装する。
2. `engine.py` の `emit_score` プロンプト生成（事前集約データの提示）および `_enrich_score_result`（自動マージ＆決定的ソート刻印）に統合する。

### Phase 3: `ReportBlueprint` 生成器と `drawlib_guide.py` の刷新
1. `src/pni/_reporter/blueprint.py` を新規作成し、`ScoreResult` から 5 章構成の確定描画データ（ソート済みテーブル行・グラフ系列・ホットスポット値・フロー情報）を持つ `ReportBlueprint` を生成・保存する機能を実装する。
2. [`src/pni/_reporter/drawlib_guide.py`](../../src/pni/_reporter/drawlib_guide.py) を `ReportBlueprint` 駆動に刷新し、`write_drawlib_report` の `get-action` で確定ソート済みデータを AI にそのまま渡すようにする。

### Phase 4: 単体テスト追加・サンプルワークフロー再実行＆レポート上書き検証
1. `tests/pni/test_aggregator_and_blueprint.py` を作成し、重複排除・ソート順序（`CRITICAL→INFO`, `FAIL→PASS`, `P0→P2`, `score` 昇順）・ホットスポット算出・Blueprint 生成・後方互換性を網羅的にテストする。
2. `./pcli code-check all` および `./pcli test all` で品質・型安全・カバレッジを検証する。
3. 新パイプライン上で `example_clean` / `example_messy` を再実行し、5 章構成に進化した `reports/python_clean.pdf` と `reports/python_messy.pdf`（および `*_score.json`）を上書き生成する。
