# プロジェクト進行測定・Git メソドロジー監査機能 設計プラン (Project Progress & Git Governance Tracking Feature)

## 1. ビジョンと位置づけ

現在の PNI501 は以下の 2 つのワークフローカテゴリを備えている：
- **`audit`（現状品質診断）**: ある時点のコードベースの構造・品質・型・テスト・依存・セキュリティ・ドキュメントを 7 軸で採点する **静態スナップショット診断**（`reports/<target>_score.json`）。
- **`migration`（移行計画策定）**: 完了済み `audit` のファクトを継承（`based_on`）し、段階的なモダナイゼーション手順と PR 分割 WBS を設計する **将来移行計画**（`reports/<target>_migration_plan.json`）。

ここに第 3 の柱として **`category: progress`（プロジェクト進行・Git 統合健全性測定）** を新設する。

ソフトウェアそのものの詳細なコード品質診断は `audit` の責務とし、`progress` では `audit` の結果サマリ（スコア・重大指摘件数の推移）を軽量参照するにとどめる。その代わり、`progress` は **「時間軸（ヒストリー）」「計画に対する進行ギャップ」「Git メソドロジー適合性・ブランチ統合とコンフリクト状態」** に徹底フォーカスする。

### 設計の 5 大原則
1. **責務の明確な分離（コード品質は `audit`、進行と履歴は `progress`）**:
   - `progress` ワークフロー内で重い AST 全件レビューやコンテナセキュリティスキャンを再実行しない。ソフトウェア状態については `audit` の履歴サマリを引用するのみとし、開発速度・行数/テスト推移・ブランチ統合・マイルストーン達成度に集中する。
2. **`.gitignore` 対象（SQLite）に依存しない 2 層ヒストリー設計**:
   - `.pni/cache/workflow_state.db` はローカル実行ステート用の一時キャッシュであり Git 共有されないため、時系列データの根拠には一切使用しない。
   - ヒストリーは **① Git リポジトリ自体から決定論的に逆算できる時系列（コミット動態・ブランチ派生・実装/テスト行数遷移・静的テスト関数数遷移）** と、**② Git 管理下の `.pni/history/**/*.jsonl` に CLI が自動追記する計測スナップショット履歴（`audit` スコア推移・動的テスト通過/カバレッジ推移・`progress` 推移）** の 2 層で構成する。
3. **Git メソドロジーとブランチ運用ルールの `.pni` 明示定義**:
   - チームごとに異なる Git 運用方式（GitHub Flow / Trunk-Based / Git Flow / Release Flow）、基幹ブランチ（`main` / `develop`）、マージ方式（Squash / Rebase FF / Merge Commit `--no-ff`）、許容ブランチ乖離閾値を **`.pni/progress/<target>.yaml` 内の `git_policy` セクション**（機械判定用）および **`.pni/rules/common/git_workflow.md`**（AI 解釈規約）として明示定義する。
4. **非破壊のコンフリクト事前検知と統合リスク可視化**:
   - ワークツリー上の未解決コンフリクトや誤コミットされたコンフリクトマーカーの検出に加え、Git の非破壊プラミング機能（`git merge-tree --write-tree`）を用いて **未マージ派生ブランチを今 `main` に統合した場合のコンフリクト発生有無・競合ファイル群・ブランチ間重複変更ファイル** を決定論的にシミュレーションする。
5. **計画定義は「AI/人間の直接編集 ＋ CLI 厳格検証」、履歴台帳は「CLI 自動追記のみ」**:
   - `.pni/progress/<target>.yaml` は `pni progress init` で雛形生成し、AI または人間がエディタで直接編集したうえで `pni progress validate`（および `workflows start` 時の Fail-Closed プリフライト検証）で整合性を保証する。測定実行中は Read-Only 基準線として固定し、測定中の勝手な期日書き換え（ゴールポストずらし）を防止する。
   - `.pni/history/**/*.jsonl` は `pni` CLI のみが機械的に追記・更新し、AI による直接編集を禁止する。

---

## 2. `.pni/` ディレクトリ構成とデータ永続化アーキテクチャ

Git でチーム共有される定義・履歴資産と、`.gitignore` されるローカル実行キャッシュを以下のように厳密に分離する。

```text
.pni/
├── rules/                          # [既存・Git管理] 規約（git_workflow.md 拡充 + progress_tracking.md 新設）
├── actions/                        # [既存・Git管理] 複合アクション定義
├── workflows/                      # [既存・Git管理] audit / migration / progress ワークフロー定義
├── dockerfiles/                    # [既存・Git管理] 隔離テスト実行用 Dockerfile
├── pentests/                       # [既存・Git管理] 動的 Web ペネトレーションテスト
│
├── progress/                       # [新設・Git管理] 進行計画 & Git 運用ポリシー定義（人間/AIが直接編集）
│   └── <target>.yaml               #   マイルストーン・タスク期日・Gitメソドロジー・マージ/ブランチ基準
│
├── history/                        # [新設・Git管理] 軽量タイムシリーズ台帳（CLIのみが自動追記更新）
│   ├── audit/
│   │   └── <audit_wf_id>.jsonl     #   emit_score 完了時に 1 行記録（7軸スコア・LOC・テスト成否/カバレッジ）
│   └── progress/
│       └── <progress_wf_id>.jsonl  #   emit_progress 完了時に 1 行記録（進捗率・ブランチ健全性・コンフリクト数）
│
└── cache/                          # [既存・.gitignore対象] ローカル実行ステート（履歴参照には不使用）
    ├── workflow_state.db
    └── <workflow_id>/
        ├── facts.json
        └── progress_facts.json     #   progress_analyze 実行時の詳細中間キャッシュ
```

### 2-1. `.pni/history/**/*.jsonl`（JSON Lines 台帳）の更新ルール
- **1 行 = 1 コミット時点の軽量スナップショット（約 400〜600 Byte）**:
  - 配列 JSON と異なり末尾 1 行追加のみで済むため、`git diff` が最小化されブランチマージ時のコンフリクトが起きにくい。100 回計測しても約 50KB に収まりリポジトリを肥大化させない。
- **同一コミットでの重複汚染防止（Upsert 戦略）**:
  - ローカルで同一 `git_sha`（かつ `git_dirty == false`）のまま再計測した場合は、末尾レコードの `git_sha` と一致すれば **末尾 1 行を上書き更新** し、新しいコミットへ進んでいれば **新規行として末尾追記** する。
  - ワークツリーが未コミット変更あり（`git_dirty == true`）の場合は、デフォルトでは `.pni/history/` を汚さずスキップ（または明示オプション時のみ記録）とすることで、クリーンなコミット単位の履歴を保つ。

#### `audit` 履歴レコード例（`.pni/history/audit/full_audit.jsonl`）
```json
{"timestamp":"2026-10-25T09:00:00Z","workflow_id":"full_audit","git_sha":"a1b2c3d4","git_branch":"main","overall_score":86,"health_grade":"A","category_scores":{"architecture":90,"code_quality":85,"typing":92,"testing":80,"dependencies":88,"security":84,"documentation":83},"finding_counts":{"critical":0,"high":1,"medium":3,"low":4},"loc":{"source":4820,"tests":3910,"docs":640},"test_execution":{"passed":142,"failed":0,"skipped":2,"coverage_pct":87.4},"vuln_count":0}
```

#### `progress` 履歴レコード例（`.pni/history/progress/sprint_progress.jsonl`）
```json
{"timestamp":"2026-10-25T10:00:00Z","workflow_id":"sprint_progress","git_sha":"e5f6g7h8","git_branch":"main","delivery_status":"at_risk","verified_completion_pct":62.5,"schedule_variance_days":-3,"commits_7d":18,"net_source_loc":5410,"net_test_loc":4120,"static_test_cases":156,"active_branches":4,"stale_branches":1,"conflicting_branches":1,"policy_violations":2}
```

---

## 3. `.pni/progress/<target>.yaml` スキーマ設計（計画 ＋ Git メソドロジー定義）

`target_root` との対応規則は [`.pni/dockerfiles/`](../../src/pni/_cache.py) や [`.pni/pentests/`](../../src/pni/_cache.py) と統一しつつ、ルートプロジェクトでは `.pni/progress/<workflow_id_or_target>.yaml` としてシンプルに配置できるようにする。

```yaml
# .pni/progress/payment_v2.yaml
id: payment_v2
name: "決済基盤モダナイズ Phase 1 進行管理"
start_date: "2026-10-01"
target_date: "2026-11-30"

# ============================================================================
# 1. Git メソドロジー & ブランチ統合ポリシー定義 (git_policy)
# ============================================================================
git_policy:
  # 採用メソドロジー: github_flow | trunk_based | git_flow | release_flow | custom
  methodology: "github_flow"

  # 基幹ブランチ設定（git_flow の場合は integration_branch: "develop" を指定）
  trunk_branch: "main"
  integration_branch: null

  # 基幹ブランチへの統合マージ方式:
  #   - squash_only   : 線形履歴必須（2親マージコミット禁止・1機能1コミット統合）
  #   - rebase_ff     : 線形履歴必須（2親マージコミット禁止・リベースFast-Forward）
  #   - merge_commit  : --no-ff マージコミット必須（トピックブランチの統合境界を明示記録）
  #   - any           : 方式不問
  merge_strategy: "squash_only"

  # 履歴汚染・事故防止ガードレール
  forbid_foxtrot_merges: true         # feature 側へ main を逆マージして第1親がねじれる Foxtrot merge を禁止
  forbid_direct_trunk_commits: false  # true の場合、merge_commit モード時に main への直接単発コミットを警告
  forbid_wip_commits_on_trunk: true   # 基幹ブランチ上の "WIP", "fixup!", "squash!", "temp" コミットを警告

  # 派生ブランチ命名規則 & コミットメッセージ規約
  allowed_branch_patterns:
    - "feat/*"
    - "fix/*"
    - "refactor/*"
    - "docs/*"
    - "chore/*"
    - "hotfix/*"
  commit_convention: "conventional_commits"  # conventional_commits | freeform

  # ブランチ鮮度・乖離・肥大化の定量しきい値
  thresholds:
    stale_branch_days: 14             # 最終コミットから N 日以上経過した未マージブランチを放置警告
    max_behind_commits: 30            # trunk から N コミット以上遅れている派生ブランチを統合遅延警告
    max_ahead_commits: 25             # 未マージのまま N コミット以上積み上がった長寿命ブランチを肥大化警告
    max_unmerged_changed_lines: 800   # 未マージ差分 (+追加/-削除合計) が N 行超のブランチを巨大PR警告

# ============================================================================
# 2. マイルストーン & タスク進行計画 (milestones / tasks)
# ============================================================================
milestones:
  - id: M1
    name: "認証・コアドメイン基盤"
    due_date: "2026-10-20"
  - id: M2
    name: "決済API・結合検証"
    due_date: "2026-11-15"

tasks:
  - id: T-01
    milestone: M1
    name: "JWT認証・RBACミドルウェア実装"
    planned_start: "2026-10-01"
    planned_end: "2026-10-15"
    status: "done"                    # todo | in_progress | blocked | done（自己申告ステータス）
    declared_progress: 100            # 0〜100（省略時は status から自動補完）
    branch_pattern: "feat/auth-*"     # 対応する作業ブランチ名パターン（任意）
    expected_paths:                   # 対象コード・テストパス（任意・glob可）
      - "src/auth/"
      - "tests/auth/"
    acceptance_summary: "JWT検証ミドルウェアとロール権限テストの実装完了"
    depends_on: []

  - id: T-02
    milestone: M2
    name: "決済APIエンドポイント & 冪等キー制御"
    planned_start: "2026-10-16"
    planned_end: "2026-11-05"
    status: "in_progress"
    declared_progress: 60
    branch_pattern: "feat/payment-*"
    expected_paths:
      - "src/payment/"
      - "tests/payment/"
    acceptance_summary: "POST /charge の冪等性制御と異常系テストの実装"
    depends_on:
      - "T-01"
```

### 3-1. Pydantic バリデーション仕様（`pni progress validate`）
`ProgressPlanDefinition` モデルにて以下を決定論的に検証し、違反時は明確なエラーメッセージで Fail-Closed とする：
1. `start_date <= target_date`、各タスクの `planned_start <= planned_end`。
2. `milestones[].id` および `tasks[].id` の一意性、`tasks[].milestone` の参照整合性。
3. `tasks[].depends_on` の存在確認および **有向非巡回グラフ（DAG：循環依存なし）** の検証。
4. `expected_paths` に絶対パス（`/` 始まり）や親ディレクトリ遡及（`..`）が含まれないこと。
5. `git_policy.methodology == "git_flow"` の場合に `integration_branch`（例: `"develop"`）が未設定であればプリフライトヒントを表示。

---

## 4. 決定論的進行・Git 解析エンジン設計（`src/pni/_actions/progress_analyze/`）

AI の推測を排除するため、新設プリミティブ `progress_analyze` が Git プラミングコマンドと履歴台帳を走査し、`ProgressFacts`（`.pni/cache/<workflow_id>/progress_facts.json`）を決定論的に生成する。

```text
src/pni/_actions/progress_analyze/
├── __init__.py
├── models.py               # GitPolicy, ProgressPlanDefinition, BranchHealthFact, ConflictFact, TrajectoryPoint, ProgressFacts
├── plan_loader.py          # .pni/progress/<target>.yaml のロード・Pydantic 検証・SHA256 ハッシュ計算
├── branch_topology.py      # ブランチ派生元 (merge-base)、ahead/behind、マージ戦略・Foxtrot・規約適合検査
├── conflict_detector.py    # ワークツリー未解決競合 + git merge-tree による対 main 非破壊コンフリクト検査
├── history_trajectory.py   # コミット動態・ソース/テスト/Docs 行数遷移・静的テスト関数数遷移の遡及集計
├── history_ledger.py       # .pni/history/{audit,progress}/*.jsonl の Read / Upsert 追記管理
└── runner.py               # 全体オーケストレーション（基準日 as_of_date 固定対応・Shallow clone 検知）
```

### 4-1. ブランチ派生トポロジ & Git メソドロジー適合検査（`branch_topology.py`）
1. **ブランチインベントリと派生関係（`git for-each-ref` / `git merge-base` / `git rev-list`）**:
   - 全ローカルブランチおよび `origin/*` リモート追跡ブランチを走査し、基準ブランチ（`git_policy.integration_branch or git_policy.trunk_branch`）との分岐点コミット（`merge_base_sha`, 分岐日）、`ahead_commits`、`behind_commits`、未マージ変更行数、最終コミット経過日数を算出する。
   - しきい値（`stale_branch_days`, `max_behind_commits`, `max_ahead_commits`, `max_unmerged_changed_lines`）超過ブランチと、`allowed_branch_patterns` に合致しないブランチ名を機械抽出する。
2. **マージ戦略 & 基幹ブランチ履歴検査（`git log --first-parent`）**:
   - `merge_strategy in {"squash_only", "rebase_ff"}` の場合：基幹ブランチ上の 2 親以上を持つマージコミット混入件数を検出する。
   - `merge_strategy == "merge_commit"` の場合：トピック統合が `--no-ff` マージコミットで行われているか、および `forbid_direct_trunk_commits: true` 時の直積み単発コミットを検出する。
   - **Foxtrot Merge 検知**: マージコミットの第 1 親（first-parent）がトピックブランチ側、第 2 親が `main` 側になってしまい `git log --first-parent` の本線履歴が乗っ取られている箇所を検出する。
   - **コミット衛生検査**: `commit_convention == "conventional_commits"` に対する適合率、および基幹ブランチ上の WIP 系コミット（`WIP`, `fixup!`, `squash!`）残存数を集計する。

### 4-2. コンフリクト状態 & 非破壊マージシミュレーション（`conflict_detector.py`）
ワークツリーを一切変更せず（チェックアウト不要・完全 Read-Only）、以下の **3 段階のコンフリクト診断** を行う：
1. **Stage C1 — 現在の作業ツリー・インデックス異常検知**:
   - `git ls-files -u` による未解決コンフリクトファイル、`.git/MERGE_HEAD`・`REBASE_HEAD`・`CHERRY_PICK_HEAD` の中断状態残存、および対象ソースファイル内に誤ってコミットされているコンフリクトマーカー文字列（行頭 `<<<<<<< `, `=======`, `>>>>>>> `）を検出する。
2. **Stage C2 — 未マージ派生ブランチ vs 基幹ブランチの非破壊マージ検証（`git merge-tree --write-tree`）**:
   - アクティブな各未マージブランチ `<branch>` に対し、`git merge-tree --write-tree --name-only <base_branch> <branch>`（Git 2.38 以降標準搭載。インメモリ上で三方向マージを計算）を実行する。
   - 終了コード `0` なら **`clean_mergeable: true`**、非 `0` なら **`has_conflict: true` と具体的な競合ファイルパス一覧（`conflicting_files`）** を決定論的に記録する（※古い Git 環境向けのフォールバック処理も備える）。
3. **Stage C3 — 並行ブランチ間の潜在コンフリクト予備軍（Overlapping Touch Files）検知**:
   - 現在進行中の複数派生ブランチが「まだ `main` とは競合していないが、互いに同じファイルを変更しているため、片方を先にマージすると確実にコンフリクトするホットスポットファイル」を `git diff --name-only <merge_base>..<branch>` の集合積から事前特定する。

### 4-3. コミット・行数・テストの時系列遷移解析（`history_trajectory.py`）
1. **対象パス別の純粋 LOC 遷移 & Churn 解析**:
   - `WorkflowTargets`（`source` / `tests` / `docs`）に該当するパスのみを対象とし、Lockfile（`uv.lock`, `package-lock.json`, `composer.lock` 等）やバイナリ・自動生成物を除外して集計する。
   - 週次（またはマイルストーン境界）の代表コミットツリーを `git ls-tree` / `git show` で高速走査し、**初回導入時でも過去 N 週間分の「実装行数（Source LOC）・テスト行数（Test LOC）・ドキュメント行数（Docs LOC）・Test-to-Code 行数比」の時系列データ** を構築する。
   - 短期間（例：直近 7〜14 日）に同一ファイルで追加と削除が激しく繰り返されている **手戻りチャーン（Rework Churn）上位ファイル** と、期日直前の急激なコミットスパイクを抽出する。
2. **テスト状況の 2 面ヒストリー（静的テスト数推移 × 動的実行履歴）**:
   - **静的テスト推移（Git 遡及）**: 各時点コミットの `targets.tests` からテストファイル数およびテスト関数・メソッド数（Python `def test_*`、Java `@Test`、PHP `function test*` / `#[Test]`）の推移を算出する。
   - **動的テスト推移（`.pni/history/` 参照）**: `.pni/history/audit/<based_on>.jsonl`（および当ワークフロー内で任意実行された `run_check`）から、テスト通過数・失敗数・カバレッジ率（`coverage_pct`）の時系列推移を結合する。
3. **Shallow Clone 検知**:
   - CI 等で `git clone --depth 1` されている場合、`git rev-parse --is-shallow-repository` で検知し、`ProgressFacts.is_shallow_repository = True` と履歴取得制限の警告ヒントを出力する。

### 4-4. スケジュール突合 & `audit` 軽量サマリ連携
- **基準日（`as_of_date`）の決定論固定**: デフォルトは実行当日（ISO 日付）とし、ワークフロー `with.as_of_date: "YYYY-MM-DD"` 指定時はその日付を基準に遅延日数・期日超過を算出する（単体テストの完全再現性を担保）。
- **タスク別エビデンス束ね**: 各タスクの `branch_pattern`（ブランチ存在・マージ済みか・コンフリクト有無）と `expected_paths`（実在ファイル数・最終コミット日・スタブ `TODO/FIXME` 残存数・対応テスト有無）を紐付ける。
- **`audit` サマリ参照**: `based_on: <audit_workflow_id>` が設定されている場合、`audit` を再実行せず `.pni/history/audit/<audit_workflow_id>.jsonl` と最新の `reports/<target>_score.json`（存在時）から **総合スコア・7 軸スコア推移・Critical/High 件数サマリのみ** を `ProgressFacts.audit_summary` に格納する。

---

## 5. ワークフロー・CLI・レポート統合設計

### 5-1. `WorkflowCategory` と `based_on` 仕様の拡張
[`src/pni/_workflows/base_model.py`](../../src/pni/_workflows/base_model.py) の `WorkflowCategory` を以下のように拡張する：
- `AUDIT = "audit"`：`based_on` 指定不可。`emit_score` 実行時に `.pni/history/audit/<workflow_id>.jsonl` へ自動記録するフックを追加。
- `MIGRATION = "migration"`：`based_on` 必須（完了済み `audit` が前提）。
- **`PROGRESS = "progress"`（新設）**：**`based_on` は任意（Optional）**。指定されていれば該当 `audit` の `.jsonl` 履歴と最新スコアサマリを自動リンクし、未指定でも Git ヒストリー＋計画 YAML だけで単独実行可能とする。

### 5-2. 新設するプリミティブ・複合アクション・CLI コマンド

| 種別 | 識別子 / コマンド | 役割 |
| :--- | :--- | :--- |
| **CLI** | `pni progress init [target] [-w <wf_id>] [--force]` | `.pni/progress/<target>.yaml` に `git_policy`・`milestones`・`tasks` のコメント付きテンプレートを生成する（既存ファイル保護）。 |
| **CLI** | `pni progress validate [target_or_path]` | `.pni/progress/<target>.yaml` のスキーマ・日付整合性・DAG 循環・Git ポリシー設定を検証する。 |
| **CLI** | `pni validate-progress <path>` | 生成された `reports/<target>_progress.json` を `ProgressResult` スキーマで検証する。 |
| **Primitive** | `progress_analyze` | `.pni/progress/*.yaml`・Git トポロジ・`git merge-tree` コンフリクトシミュレーション・LOC/テスト推移・`.pni/history/` を走査し、`ProgressFacts` を生成する。 |
| **Primitive** | `emit_progress` | AI が提出した `ProgressResult` JSON を検証（実在パス・タスクID・ブランチ名照合）し、決定論 `ProgressFacts` を統合して `reports/<target>_progress.json` 出力 ＋ `.pni/history/progress/<wf_id>.jsonl` へ自動記録する。 |
| **Composite** | `progress_assessment` | `progress_analyze` → `ai_interpret`（`common/progress_tracking` + `common/git_workflow` 適用）→ `emit_progress` を束ねた標準複合アクション。 |
| **Composite** | `write_progress_report` | `ProgressBlueprint`（進行・Git 監査専用ブループリント）を生成し、Drawlib でベクター PDF レポートをビルドする。 |

### 5-3. ワークフロー YAML の記述イメージ（`.pni/workflows/project_progress.yaml`）

```yaml
id: project_progress
category: progress
based_on: full_audit   # 任意：指定時は full_audit のスコア推移サマリを自動参照
name: Sprint Progress & Git Integration Health Check
description: Evaluate milestone schedule adherence, Git branch/merge methodology compliance, merge conflicts, and LOC/test historical trajectories.

targets:
  source:
    - "src"
  tests:
    - "tests"
  docs:
    - "README.md"
    - "docs"

steps:
  - id: measure_progress_and_git
    uses: progress_assessment
    with:
      plan_file: ".pni/progress/project_progress.yaml"
      lookback_weeks: 12
      output_dir: "reports"
      target: "project_progress"

  - id: compile_progress_report
    uses: write_progress_report
    with:
      src_dir: "reports_src"
      output_dir: "reports"
      target: "project_progress"
      lang: "ja"
      style: "google"
```

### 5-4. 出力データモデル（`ProgressResult`）とビジュアルレポート構成（5 章構成）
進行管理はスプリントごと等の高頻度運用が想定されるため、レポートは意思決定に直結する **5 ファイル構成（`00_cover.md` + 4 章）** とする：

1. **`00_cover.md` — エグゼクティブカバー & 4 軸進捗ヘルス KPI**:
   - 総合デリバリー判定（`on_track` / `at_risk` / `delayed` / `blocked`）＋ `KpiCards` 4 軸スコア（① Schedule Adherence 計画遵守度、② Git & Merge Hygiene ブランチ・統合健全性、③ Momentum & Churn 開発速度・安定性、④ Test & Quality Trajectory テスト追随・`audit` サマリ）。
2. **`01_schedule_and_milestones.md` — マイルストーン計画 vs 実績診断**:
   - Drawlib `GanttChart` による計画期間 vs 検証済み実質進捗率（自己申告との乖離ハイライト、停滞タスク、クリティカルパス遅延）。
3. **`02_git_methodology_and_conflicts.md` — Git メソドロジー適合・ブランチ派生・コンフリクト診断**:
   - 基幹ブランチに対する未マージ派生ブランチの分岐トポロジ（`ahead / behind` 分布）、`git merge-tree` による **対 `main` コンフリクト発生ブランチ＆競合ファイル一覧**、並行ブランチ間の重複変更ホットスポット、マージ戦略（Squash / Rebase / `--no-ff` / Foxtrot）適合状況。
4. **`03_code_and_test_trajectories.md` — コミット・行数（LOC）・テスト履歴の遷移分析**:
   - Drawlib `LineChart` / `BarChart` による週次コミット推移、実装行数 vs テスト行数の成長曲線、テストケース数・カバレッジ推移、および `audit` 品質スコア履歴サマリ（連携時）。
5. **`04_risks_and_next_actions.md` — 進行ボトルネック & 次スプリント優先アクション（P0〜P2）**:
   - コンフリクト解消優先順序、放置・肥大化ブランチの統合/整理手順、駆け込み実装によるテスト不足箇所の補強、現実的なリスケジュール・スコープ調整提案。

---

## 6. 実行前の対話的セットアップ & ガードレール（PNI ルール設計）

1. **`src/pni/_rules/common/git_workflow.md` の拡充**:
   - 現行の簡易原則に加え、代表的な Git メソドロジー（GitHub Flow / Trunk-Based / Git Flow）、マージ戦略の選択基準、Foxtrot マージ回避、長寿命ブランチによるコンフリクト爆発防止基準を体系化する。
2. **`src/pni/_rules/common/progress_tracking.md` の新設**:
   - 初回セットアップ時にエージェントがユーザーへ確認すべき項目（①採用している Git ブランチ/マージ運用方式、②マイルストーンと主要タスク期日）と、**測定実行中は `.pni/progress/<target>.yaml` を勝手に書き換えて遅延を隠蔽してはならない（Baseline Immutability 原則）** ことを明文化する。
3. **`pni workflows show` / `start` の Fail-Closed プリフライト検査**:
   - `category: progress` のワークフロー開始時に対象の `.pni/progress/<target>.yaml` が存在しない、またはスキーマエラーがある場合は実行をブロックし、`pni progress init -w <workflow_id>` からの計画作成を案内する。

---

## 7. 段階的実装ロードマップ

- **Phase 1: Git 管理ヒストリー基盤（`.pni/history/`）の導入と `audit` 連携**
  - `history_ledger.py`（JSONL Read / SHA 単位 Upsert 追記）を実装し、既存の `emit_score` 完了時に `.pni/history/audit/<workflow_id>.jsonl` が自動記録されるようにする。
- **Phase 2: `.pni/progress/` スキーマと `pni progress init / validate` CLI の実装**
  - `GitPolicy`・`ProgressPlanDefinition` Pydantic モデルと CLI サブコマンド（雛形展開・DAG/日付/パス検証）を実装する。
- **Phase 3: 決定論的 `progress_analyze` エンジンの実装**
  - ブランチ派生トポロジ解析、`git merge-tree --write-tree` 非破壊コンフリクト検出、LOC/テスト遡及時系列集計、`audit` 履歴サマリ結合を実装する。
- **Phase 4: `WorkflowCategory.PROGRESS`・`emit_progress`・レポート Blueprint の統合**
  - ステートフルエンジン（`engine.py` / `adhoc.py`）、複合アクション、`ProgressBlueprint`（5 章構成）、`pni validate-progress`、およびインストラクション／ルール群を統合する。

---

## Verification Plan

### Engineering & Functional Verification
- `./pcli code-check all` による Ruff lint/format および Ty 静的型検査の完全パスを確認する。
- `./pcli test all --parallel` による単体・統合テストを実行する：
  - 一時ディレクトリ上に実際のテスト用 Git リポジトリをプログラム構築（複数コミット履歴、`main` と派生 `feat/*` ブランチ、意図的に競合させたブランチ、Foxtrot マージ、Stale ブランチ等を再現）し、以下を検証する：
    1. `git merge-tree --write-tree` によりワーキングツリーを一切汚さずにコンフリクト発生ブランチと競合ファイル名が正確に特定されること。
    2. `squash_only` / `merge_commit` 等の `git_policy` 違反、放置ブランチ、`ahead/behind` 超過が決定論的に検出されること。
    3. Lockfile ノイズを除外した週次 Source LOC / Test LOC / 静的テスト関数数の推移が正確に算出されること。
    4. `.pni/history/{audit,progress}/*.jsonl` において、同一 `git_sha` 再実行時は末尾行が Upsert 更新され、新規コミット時は追記されること。
    5. `.pni/progress/<target>.yaml` 未作成時または循環 `depends_on` 定義時に `pni workflows start` が Fail-Closed で拒否すること。

### Security Guidelines Validation
- **Git Subprocess Hardening**: すべての `git` コマンド呼び出しは `run_safe_command`（`shell=False`、引数リスト渡し）で行い、ブランチ名やパス引数の先頭ハイフンによるオプションインジェクション（例: `--upload-pack=...`）を防ぐため、正規表現によるブランチ参照名バリデーションおよび `--` セパレータ付与を徹底する。
- **Non-Destructive Read-Only Git Inspection**: コンフリクト検査は `git merge-tree` 等の読み取り専用プラミングコマンドのみを使用し、`git checkout` / `git merge` / `git reset` 等のワークツリー・インデックス破壊操作を一切実行しない。
- **Path Traversal Boundary Enforcement**: `plan_file`、`expected_paths`、`.pni/history/` 出力先はすべてワークスペースルート配下（`Path.is_relative_to(workspace_root.resolve())`）であることを検証する。
- **Safe Deserialization & Local CLI Scope**: YAML パースには必ず `yaml.safe_load` のみを使用する。本機能はローカル Python CLI ツール（Web フロントエンド・HTTP セッション・Cookie・ファイルアップロード・RDBMS サーバ非該当）として動作するため、Web 固有項目（XSS/CSP/CSRF/OAuth/Cookie/SQL サーバ設定）は対象外であり、CLI 入力検証・サブプロセス実行安全性・ファイル境界保護・機密非露出ログを重点検証する。

### Automated Security Check
- **Security Scanner**: Run a scan on all newly created files to identify common vulnerabilities (e.g., XSS, SQL injection, command injection, path traversal). If findings are detected, auto-apply the fix and document the results.
- **Security Audit**: Audit the new code for design-level security issues (input validation, secrets handling, subprocess & path boundary checks). Document findings and remediations in the `walkthrough.md` artifact using the `generate_security_audit_report` skill.

