# Project Nemesis Index (PNI) 開発計画書 (Development Plan)

**Project Nemesis Index (PNI / パッケージ名: `pni501`)** は、生成 AI エージェントが参照する「ソフトウェア開発ベストプラクティス資料（Rules）」と「ハルシネーションを防ぐプログラム確定解析（AST 等）」を組み合わせ、AI エージェント自身にプロジェクトの評価・スコアリングおよび **drawlib** によるビジュアルレポート作成を行わせる AI ネイティブな診断ツールです。

本ドキュメントは、PNI の全体アーキテクチャ、ドメイン凝集（High Cohesion）パッケージ設計、Pydantic ベースの型・Action 設計、CLI インターフェース、およびフェーズ別の実装ロードマップを定義します。

---

## 1. ビジョン & コアコンセプト

```text
 ┌─────────────────────────────────────────────────────────────────────────┐
 │                               PNI (pni501)                              │
 └─────────────────────────────────────┬───────────────────────────────────┘
                                       │
       ┌───────────────────────────────┼───────────────────────────────┐
       ▼                               ▼                               ▼
【1. Rules (`_rules`)】     【2. Actions (`_actions`)】     【3. Workflows & Reporter】
 ・AIが読む設計・品質基準   ・AST解析 / 構造解析 (Python)   ・Step 1..N: ファクト解釈
 ・ベストプラクティス内包   ・ハルシネーションを完全排除    ・Step N+1: スコア出力 (JSON)
 ・.pni/rules で上書き      ・Composite → Primitive 変換    ・Final Step: drawlib レポート作成
```

1. **AI が参照するベストプラクティス (Rules as Knowledge)**:
   - アーキテクチャ、テスティング、依存関係管理、コード品質、ドキュメンテーションに関する標準規範をパッケージ内部（`pni._rules`）に Markdown 形式で内包。
   - プロジェクトごとに `.pni/rules/` を配置することで、標準ルールを透過的に上書き・カスタマイズ可能。
2. **ハルシネーションを排除するプログラム確定解析 (Deterministic Fact Extraction)**:
   - AI にコード行数や型ヒント付与率、複雑度、import 依存網を目視で数えさせると推測（ハルシネーション）が発生するため、**AST（抽象構文木）や設定ファイル解析などプログラムで解析可能なものは Python 側（`pni._actions` 内の確定解析プリミティブ）で処理**する。
   - 抽出された確定ファクト（数値・違反候補のファイル名と行番号・依存グラフ）はすべて **Pydantic モデル** として構造化され、AI には「その確定ファクトの解釈・定性判断」を行わせる。
3. **2階層 Action 構造と AI による中間スコア出力・最終 drawlib レポート作成**:
   - ワークフロー（`pni._workflows` および `.pni/workflows/`）は、ユーザー定義可能な複合 Action（`pni._actions`, `.pni/actions/`）を内部の **プリミティブ Action** に変換して処理する。
   - **中間ステップでスコア（`.pni/score.json`）を確定出力**し、**最終ステップ**で AI エージェントに以下を実行させる：
     1. **READ スコア**: 中間ステップで出力された `.pni/score.json`（および確定ファクト）を読み込む。
     2. **READ コードや資料**: 対象プロジェクトのソースコードや設計資料・ドキュメントを読み込み、ドメイン構造や文脈を把握する。
     3. **WRITE drawlib レポート**: プロジェクト固有のアーキテクチャ図・依存マップ・レーダーチャート・スコアカードを **drawlib** コードで描画し、リッチな HTML / PDF レポートを生成する。
4. **ドメイン凝集設計（High Cohesion）と Pydantic (`base_model.py`) の全面採用**:
   - `config/` や `runner/` のような技術レイヤー別の分散ディレクトリを廃止し、**`_instructions/`, `_rules/`, `_actions/`, `_workflows/`, `_reporter/` の各ドメインパッケージ配下に `base_model.py`（Pydantic モデル）・管理/実行ロジック・内包テンプレート（MD/YAML）を完全集約**する。
   - Pydantic の JSON Schema 生成機能（`model_json_schema()`）を活用し、AI エージェントへのプロンプトに厳密な入出力スキーマを自動埋め込みする。

---

## 2. CLI 体系 & ディレクトリ構造

### 2.1. コマンド体系の分離
- **`pni` (エンドユーザー & AI エージェント向け CLI / パッケージ: `pni501`)**:
  - `pni init`: 被測定プロジェクトに `.pni/`（`rules/`, `actions/`, `workflows/`, `instructions.md`）を初期展開し、`.gitignore` に一時アーティファクト（`.pni/workflow_state.db` 等）を追加。
  - `pni instructions`: AI エージェント向けの初期指示・行動規範（Markdown）を標準出力（エイリアス: `pni instruction`）。
  - `pni rules [list|show]`: 内包・ローカルのベストプラクティスルールの一覧表示・参照。
  - `pni workflows [list|show|start|get-action|push-action|status]`:
    - `list` / `show`: `.pni/workflows/` の一覧およびプリミティブ Action 展開構成を表示。
    - `start <workflow_id>`: `.pni/workflow_state.db`（SQLite）に実行セッションを作成し `workflow_run_id` を発行。
    - `get-action <run_id>`: 現在の対象 `action_id` と指示詳細を取得（プログラム解析ステップは確定実行の上 `facts.json` と DB に保存して通知）。
    - `push-action <run_id> <action_id> [INPUT] [--file <path>]`: AI の出力 JSON を Pydantic スキーマで厳密検証して DB に記録し、次ステップへ確定遷移（`emit_score` 時は `outputs.score` を自動書き出し）。
    - `status [run_id]`: SQLite 上のワークフロー実行履歴・各アクション進捗を表示。
  - `pni validate-score [score_path]`: スコア JSON を `ScoreResult` スキーマで検証。
  - `pni report`: AI エージェントが作成した drawlib スクリプト・図表とスコアデータを統合し、最終的な HTML / PDF レポートをビルド・検証。
  - `pni version`: バージョン表示。
- **`./pcli` (当リポジトリ内製開発 CLI / `tools/pcli`)**:
  - `./pcli code-check [lint|type|lines|all]`: Ruff, Ty による品質保証。
  - `./pcli test [all|pni|pcli|target]`: pytest による単体テスト・カバレッジ計測。
  - `./pcli pypi [check-version|deps|latest|publish]`: PyPI リリース管理。

### 2.2. パッケージ構造設計（ドメイン凝集アーキテクチャ）

各ドメインパッケージ（`_instructions`, `_rules`, `_actions`, `_workflows`, `_reporter`）が自身の `base_model.py`（Pydantic モデル）、`manager.py`（または実行エンジン）、および内包アセット（`.md` / `.yaml`）を一体管理します。

```text
src/pni/
├── __init__.py
├── cli.py                        # pni CLI メインエントリポイント
├── py.typed                      # PEP 561 型マーカー
├── _instructions/                # 【Instructions ドメイン】AI エージェント初期指示
│   ├── __init__.py
│   ├── base_model.py             # Pydantic モデル (InstructionInfo 等)
│   ├── manager.py                # カスケード解決 (.pni/instructions.md > agent.md) & 展開
│   └── agent.md                  # AI エージェント向けメタ指示・行動規範 (Builtin)
├── _rules/                       # 【Rules ドメイン】ベストプラクティス規範 (2階層スコープ)
│   ├── __init__.py
│   ├── base_model.py             # Pydantic モデル (RuleInfo 等)
│   ├── manager.py                # 言語自動判定・カスケード解決 (.pni/rules/ > _rules/) & 展開
│   ├── common/                   # 言語非依存の普遍的ベストプラクティス
│   │   ├── architecture.md       # 設計規範（レイヤリング、責務分離、疎結合、高凝集）
│   │   ├── git_workflow.md       # Git運用規範（ブランチ戦略、コミット規約、PRサイズ）
│   │   ├── documentation.md      # ドキュメンテーション・仕様書・コメント規範
│   │   └── security.md           # 認証情報管理、最小権限、ログ方針
│   └── python/                   # Python 固有のベストプラクティス
│       ├── code_quality.md       # PEP 8, Ruff, 命名規約, Docstring
│       ├── typing.md             # 型ヒント徹底 (PEP 484/585/604), Any 最小化
│       ├── testing.md            # pytest, 境界値テスト, カバレッジ基準
│       └── dependencies.md       # pyproject.toml, uv, ロックファイル必須
├── _actions/                     # 【Actions ドメイン】確定解析 (AST等) + AI Action 定義 & 変換
│   ├── __init__.py
│   ├── base_model.py             # Pydantic モデル (PrimitiveType, ScoreResult, 各 push 入力スキーマ等)
│   ├── manager.py                # カスケード解決 (.pni/actions/ > _actions/) & Composite → Primitive 正規化
│   ├── ast_analyze.py            # [Primitive] Python AST 確定解析モデル (AstFacts) & 解析ロジック
│   ├── project_inspect.py        # [Primitive] pyproject.toml, ロックファイル, 構造, Git 確定解析ロジック
│   ├── ai_actions.py             # [Primitive] アクション別 AI タスク指示・入力 JSON Schema 生成
│   ├── repo_structure_audit.yaml # 内包 Composite Action 定義 (リポジトリ・依存関係・Git)
│   ├── python_ast_audit.yaml     # 内包 Composite Action 定義 (AST解析 + コード品質・型・設計解釈)
│   ├── python_test_audit.yaml    # 内包 Composite Action 定義 (テスト構造・網羅性解釈)
│   ├── emit_score.yaml           # 内包 Composite Action 定義 (中間ステップ: ScoreResult JSON 出力)
│   └── write_drawlib_report.yaml # 内包 Composite Action 定義 (最終ステップ: READ スコア & 資料 → WRITE drawlib)
├── _workflows/                   # 【Workflows ドメイン】ワークフロー定義 & SQLite ステートフル実行エンジン
│   ├── __init__.py
│   ├── base_model.py             # Pydantic モデル (WorkflowDefinition, WorkflowRunRecord, ActionRunRecord 等)
│   ├── manager.py                # .pni/workflows/ 解決・テンプレート展開 & プリミティブ正規化
│   ├── state_db.py               # SQLite (.pni/workflow_state.db) ステートマシン永続化層
│   ├── engine.py                 # start / get-action / push-action ステートフル実行・検証エンジン
│   ├── full_audit.yaml           # 総合診断テンプレート（AST/構造解析 → AI解釈 → スコア出力 → drawlibレポート作成）
│   └── quick_check.yaml          # 高速診断テンプレート（AST/構造解析 → AI解釈 → スコア出力）
└── _reporter/                    # 【Reporter ドメイン】drawlib ビジュアルレポート生成支援 & ビルド
    ├── __init__.py
    ├── base_model.py             # Pydantic モデル (ReportConfig, ReportManifest 等)
    ├── drawlib_guide.py          # AI が drawlib コードを記述するための API ガイド・スニペット生成
    ├── compiler.py               # AI が生成した drawlib 図表・スコア・解説から HTML / PDF をビルド
    └── templates/                # レポート用 HTML / CSS テンプレート
```

### 2.3. ドメイン間の依存関係階層（Layer Hierarchy）
自身の [`common/architecture.md`](../../src/pni/_rules/common/architecture.md) の規範通り、単一方向の明確なレイヤー階層を維持し、循環依存を禁止します。

```text
[cli.py] (Entrypoint)
   ├──> [_workflows] ──> [_actions] ──> [_rules]
   ├──> [_reporter]  ──> [_actions.base_model]
   └──> [_instructions]
```

---

## 3. Workflows & Actions の詳細設計（AI ネイティブ設計）

### 3.1. 2階層の Action アーキテクチャ
ユーザーやプロジェクトごとのカスタマイズ性と、内部処理の厳密性を両立するため、`_actions/` 内にて **「1. 内部プリミティブ Action (`PrimitiveStep`)」** と **「2. 複合 Action 定義 (`CompositeAction`: `.pni/actions/` / `_actions/*.yaml`)」** の2階層を管理します。

```text
[Workflow YAML (.pni/workflows/full_audit.yaml)]
   │  uses: python_ast_audit (複合 Action 参照) または action: <primitive> (直接指定)
   ▼
[Action Manager (pni._actions.manager)]
   │  .pni/actions/*.yaml (Local) > _actions/*.yaml (Builtin) を解決し、
   │  内部の Pydantic `PrimitiveStep` リストへ一意に展開・正規化
   ▼
[Workflow Engine (pni._workflows.engine)]
   ├─ (A) プログラム解析プリミティブ → Python が即時実行し `.pni/cache/facts.json` に確定値を保存
   └─ (B) AI 誘導プリミティブ        → 確定ファクト + Rules + Pydantic JSON Schema を統合した AI 指示を生成
```

### 3.2. 内部プリミティブ Action 一覧（`_actions/base_model.py` の `PrimitiveType`）

| カテゴリ | プリミティブ名 | 実装ファイル (`_actions/`) | 実行主体 | 処理内容 |
| :--- | :--- | :--- | :---: | :--- |
| **プログラム解析**<br>*(Deterministic)* | **`ast_analyze`** | `ast_analyze.py` | Python (`pni`) | Python 標準 `ast` モジュール等でソース・テストコードを静的走査し、以下を確定算出：<br>・ファイル数、総行数(LOC)、関数・クラス定義数<br>・引数・戻り値の型ヒント付与率、未付与箇所（ファイル:行番号）、`Any` 使用箇所<br>・公開モジュール・クラス・関数の Docstring 付与率と欠落箇所<br>・関数ごとの行数・分岐複雑度（McCabe 相当）の異常値リスト<br>・モジュール間 `import` 依存グラフと循環依存の検出 |
| | **`project_inspect`** | `project_inspect.py` | Python (`pni`) | プロジェクト構成・メタデータの確定解析：<br>・`pyproject.toml` 等のパース、依存パッケージ一覧、ロックファイル（`uv.lock` 等）有無<br>・`src/` と `tests/` のミラー構造一致状況、テストファイル比率<br>・Git リポジトリ状態（ブランチ、直近コミット履歴、`.gitignore` 設定状況） |
| | **`run_check`** | `run_check.py` | Python (`pni`) | 指定された検証コマンド（テストや Linter 等）をサブプロセス実行し、終了コード・標準出力サマリを確定ファクトとして記録 |
| **AI 解釈・出力**<br>*(Cognitive)* | **`load_rules`** | `ai_actions.py` | `pni` → AI | ステップで参照するルール（例: `common/architecture`, `python/typing`）を `_rules.manager` で解決して AI コンテキストに展開 |
| | **`ai_interpret`** | `ai_actions.py` | **AI Agent** | プログラム解析プリミティブが出力した **確定ファクト（数値・該当行リスト・import 網）** を受け取り、AI がルールに照らして設計妥当性・責務分離・例外の正当性を解釈し、カテゴリ評価と改善指摘（Findings）をまとめる |
| | **`emit_score`** | `ai_actions.py` | **AI Agent**<br>*(中間ステップ)* | ここまでの確定ファクトと AI 解釈を統合し、Pydantic `ScoreResult` スキーマに準拠した **`.pni/score.json`** をファイル出力する |
| | **`write_drawlib_report`** | `ai_actions.py` | **AI Agent**<br>*(最終ステップ)* | ワークフローの最後で AI エージェントに以下の3アクションを遂行させる：<br>1. **READ スコア**: `.pni/score.json`（および `.pni/cache/facts.json`）を読み込む<br>2. **READ コードや資料**: リポジトリの主要コード・README・設計書を読み込む<br>3. **WRITE drawlib レポート**: `drawlib` を用いてスコアのレーダーチャート・プロジェクト固有のアーキテクチャ図・課題マップを描画し、レポート（`.pni/report/`）を生成する |

### 3.3. ワークフロー定義の役割と具体例 (`.pni/workflows/full_audit.yaml`)

GitHub Actions（`.github/workflows/`）と同様に、ワークフローはプロジェクト側の `.pni/workflows/*.yaml` に定義します（`pni init` で初期生成）。
ワークフローファイルは以下の **3つの要素** をシンプルに定義する役割を持ちます：
1. **`targets`（どのコード・資料を対象にやるか）**: `source`, `tests`, `docs` の対象パス
2. **`outputs`（スコアとレポートはどこに出すか）**: `facts`, `score`, `report` の出力先パス
3. **`steps`（具体的なアクションの列挙）**: 実行する Action（`uses:` または `action:`）の順序リスト

```yaml
id: full_audit
name: Full Project Health Audit & Report
description: Deterministic AST/project analysis, AI rule interpretation, score emission, and drawlib report creation.

# 1. どのコード・資料を対象にやるか
targets:
  source:
    - "src"
  tests:
    - "tests"
  docs:
    - "README.md"

# 2. スコアとレポートはどこに出すか
outputs:
  facts: ".pni/cache/facts.json"
  score: ".pni/score.json"
  report: ".pni/report"

# 3. 具体的なアクションの列挙
steps:
  - id: repo_and_deps
    uses: repo_structure_audit

  - id: ast_and_quality
    uses: python_ast_audit

  - id: test_health
    uses: python_test_audit

  - id: output_score
    uses: emit_score

  - id: create_report
    uses: write_drawlib_report
```

### 3.4. ステートフル Pull-Push 実行ループ（`.pni/workflow_state.db`）

AI エージェントがステップを飛ばしたり出力形式を逸脱したりするのを完全に防ぐため、SQLite（`.pni/workflow_state.db` / `.gitignore` 対象）をステートマシンとした Pull-Push プロトコルを採用します：

```text
1. pni workflows start <workflow_id>      ─▶ SQLite に Run と全 Primitive Action を登録し <run_id> を返却
2. pni workflows get-action <run_id>      ─▶ 現在の未完了 <action_id> と詳細指示・必須 JSON Schema を出力
                                             （※ AST/構造解析ステップはここで確定実行され facts.json と DB に保存）
3. [AI Agent Work]                        ─▶ ファクト解釈 / スコア算出 / drawlib レポート作成
4. pni workflows push-action <run_id> <action_id> INPUT
                                          ─▶ Pydantic スキーマで INPUT を厳密検証して DB に保存し次ステップへ遷移
                                             （※ emit_score 時は outputs.score へ自動書き出し）
5. COMPLETED になるまで Step 2〜4 を反復
```

---

## 4. フェーズ全体構成 (Roadmap)

| フェーズ | 区分 | 対象領域 | 主な開発内容 | 完了目安 |
| :--- | :---: | :--- | :--- | :---: |
| **Phase 1: ドメイン凝集リファクタリング (`_rules`, `_instructions`) と Pydantic 化** | 基盤構築 | `_rules/`, `_instructions/`, `cli.py` | ・`config/` を廃止し、`_rules/` と `_instructions/` に `base_model.py` (Pydantic) と `manager.py` を集約<br>・`pni init` / `pni rules` / `pni instructions` の新構造対応 | v0.2.0 ✅ |
| **Phase 2: `_actions` (AST 確定解析・Action 変換) と `_workflows` (SQLite ステートフル実行)** | 実行基盤 | `_actions/`, `_workflows/`, `cli.py` | ・`_actions/base_model.py`（Primitive/Composite/ScoreResult/入力スキーマ）実装<br>・`_actions/ast_analyze.py`（Python AST 解析）と `project_inspect.py` 実装<br>・`_workflows/state_db.py`（`.pni/workflow_state.db`）と `engine.py` 実装<br>・`pni workflows [list\|show\|start\|get-action\|push-action\|status]` 実装 | v0.3.0 ✅ |
| **Phase 3: `_reporter` (AI 主導の drawlib レポート作成基盤 & `pni report`)** | レポート機能 | `_reporter/`, `_actions/`, `pyproject.toml`, `cli.py` | ・`drawlib` (`doc` プロジェクト形式) 統合と `_reporter/drawlib_guide.py` 整備<br>・ワンセット型ワークフローでの `emit_score` → `write_drawlib_report` 連携構築<br>・HTML / A4 Vector PDF / Markdown / PNG 一括ビルド (`_reporter/compiler.py`, `pni report [init\|build]`) 実装 | v0.4.0 ✅ |
| **Phase 4: 多言語拡張・Dogfooding・CI 連携** | 統合・品質 | `docs/`, `_rules/`, `_actions/`, GitHub Actions | ・他言語向け AST/構造アナライザーとルール拡充<br>・`pni501` 自体の PNI セルフ診断 (Dogfooding)<br>・GitHub Actions CI 連携 | v1.0.0 |

---

## 5. 各フェーズの詳細仕様

### 5.1. Phase 1: ドメイン凝集リファクタリング (`_rules`, `_instructions`) と Pydantic 化
1. **Pydantic & PyYAML の導入**:
   - `pyproject.toml` の `dependencies` に `pydantic>=2.0.0` と `pyyaml>=6.0.0` を追加。
2. **`config/` の廃止と各ドメインへの集約**:
   - **`src/pni/_rules/`**:
     - `base_model.py`: Pydantic `BaseModel` による `RuleInfo` 定義。
     - `manager.py`: 言語自動判定（`detect_active_language`）、カスケード解決（`list_rules`, `get_rule_content`）、`.pni/rules/` へのテンプレートコピー。
   - **`src/pni/_instructions/`**:
     - `base_model.py`: Pydantic `BaseModel` による `InstructionInfo` 定義。
     - `manager.py`: `.pni/instructions.md` > `_instructions/agent.md` のカスケード解決とテンプレートコピー。

### 5.2. Phase 2: `_actions` (AST 確定解析・Action 変換) と `_workflows` (SQLite ステートフル実行)
1. **`src/pni/_actions/` の構築**:
   - **`base_model.py`**:
     - `PrimitiveType` (`Enum`): `ast_analyze`, `project_inspect`, `run_check`, `load_rules`, `ai_interpret`, `emit_score`, `write_drawlib_report`。
     - `PrimitiveStep`, `CompositeActionDefinition`: Action 定義と正規化ステップの Pydantic モデル。
     - `DeterministicAckInput`, `InterpretationInput`, `ScoreResult`, `ReportCompletionInput`: 各 `push-action` 時に検証される厳密な入力 Pydantic モデル。
   - **`ast_analyze.py`**:
     - Python `ast.parse` による確定解析（ファイル数、LOC、関数/クラス数、型アノテーション付与率と未付与箇所の行番号、`Any` 使用行、Docstring 付与率と欠落行、長大・高複雑度関数、内部 `import` 依存グラフと循環依存検出）を実行し、Pydantic モデル `AstFacts` を返却。
   - **`project_inspect.py`**:
     - `pyproject.toml` / `requirements.txt` パース、ロックファイル有無、ソース/テスト構成、Git 状態を解析し、Pydantic モデル `ProjectFacts` を返却。
   - **`manager.py`**:
     - `.pni/actions/*.yaml` と `_actions/*.yaml` をカスケード解決し、Composite Action を `list[PrimitiveStep]` に変換。
2. **`src/pni/_workflows/` の構築**:
   - **`base_model.py`**: `WorkflowStepSpec`, `WorkflowDefinition`, `WorkflowRunRecord`, `ActionRunRecord` 等の Pydantic モデル。
   - **`manager.py`**: `.pni/workflows/*.yaml` の一覧取得・ロードとプリミティブ正規化。
   - **`state_db.py`**: `.pni/workflow_state.db`（SQLite）の `workflow_runs` / `action_runs` テーブル管理と状態遷移永続化。
   - **`engine.py`**:
     - `start_workflow_run`: ワークフローを正規化し SQLite セッション（`wf-xxxxxxxx`）を開始。
     - `get_workflow_action`: 未完了アクションを取得し、プログラム解析ステップなら即時実行して `facts.json` と SQLite に保存した上で、ルール・確定ファクト・Pydantic JSON Schema 付きの指示を返却。
     - `push_workflow_action`: `action_id` の順序整合性と JSON ペイロードの Pydantic スキーマを検証し、`emit_score` 時は `outputs.score` への書き出し、`write_drawlib_report` 時は生成ファイルの存在検証を行って次ステップへ進める。

### 5.3. Phase 3: `_reporter` (AI 主導の drawlib レポート作成基盤 & `pni report`)
1. **`src/pni/_reporter/drawlib_guide.py`**:
   - AI が最終ステップ（`write_drawlib_report`）で `drawlib`（`doc` プロジェクト形式）を正確に構築できるよう、`KpiCards`、`RadarChart`、`HeatmapChart`（2D品質マトリクス）、`ClassDiagram` + `HeatmapOverlay`（空間リスクホットスポット）、`Roadmap` の座標アンカー規範と `lang` / `style` 指定を埋め込んだガイドを生成。
2. **`src/pni/_reporter/compiler.py` (`pni report [init|build]`)**:
   - `scaffold_report_project` (`pni report init`): `drawlib.tools.init_project("doc", ...)` により `<report_dir>/report_src/` を多言語フォント・テーマ付きで初期化し、サンプル章を自動クリーンアップ。
   - `compile_report_project` (`pni report build`): `<report_dir>/report_src/*.md` から単一結合 HTML (`report_html/index.html`)、目次・改ページ付き A4 ベクター PDF (`report.pdf`)、GitHub 用 Markdown (`report_markdown/`)、単体図版 PNG (`report_images/`) を一括ビルドし、`scan_broken_links` によるリンク切れゼロ検証を実行。

---

## 6. 品質保証 & 開発規律

- すべてのコードは **`./pcli code-check all`**（Ruff リント・フォーマット、Ty 静的型チェック）を 100% パスすること。
- テストは **`./pcli test all`** で実行し、新規モジュールに対するカバレッジ 90% 以上を維持すること。
- 公開前のバージョンチェックは **`./pcli pypi check-version`**、公開は **`./pcli pypi publish`** を通じて安全に行うこと。
