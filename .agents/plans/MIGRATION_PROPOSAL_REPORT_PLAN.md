# マイグレーション計画・提案レポート機能 設計プラン (Migration Proposal & Execution Plan Feature)

## 1. ビジョンと位置づけ

PNI の開発目的は「現状把握（As-Is）すらできていないレガシーソフトウェアに対して、安全なマイグレーションの初手を与えること」にある。

現在の PNI は **「健康診断（カルテの作成：何が・どこで・なぜ壊れているか）」** として Python / Java / PHP（モダン・素 PHP・WordPress）の横断診断を実現している。次のステップとして、診断結果と **精査・確定された複数行フリーフォーマットの移行要件（`brief`）** を受け取り、言語・フレームワーク・DB・Cache 刷新からクリーンアーキテクチャ等の設計思想導入までをカバーして、エンジニアがそのまま PR（プルリクエスト）やチケットとして安全に着手できる **「手術計画書（マイグレーション実行計画レポート）」** を生成する機能を新設する。

### 設計の 5 大原則
1. **診断レポート（As-Is）と移行計画レポート（To-Be）の成果物分離**:
   - 1 つのレポートに混ぜると焦点がぼやけるため、`full_audit`（現状診断レポート）と `migration_plan`（移行提案レポート）は独立した成果物（`*_migration_plan.json` / `*_migration_plan.pdf`）として出力する。
2. **複数行フリーフォーマット要件（`brief` / `brief_file`）の第一級サポート**:
   - 実務の移行では「言語・FW 変更」だけでなく、「MySQL から PostgreSQL + JPA への移行」「プロセス内 `static Map` / `$_SESSION` から Redis キャッシュへの外部化」「クリーンアーキテクチャ（Port & Adapter）の導入」「一部 API の後方互換維持」など多軸のインフラ・設計思想・業務制約が絡み合う。
   - 固定キー列挙で縛るのではなく、**複数行の自然言語／Markdown（YAML `|` ブロック、または外部 `.md` ファイル）** をメイン入力とし、AI がそこから動的な変更軸リスト（`list[MigrationAxis]`）とターゲット層構造（`TargetArchitectureDesign`）へ構造化する。
3. **ワークフロー実行前の「マイグレーション要件精査・対話的確定プロトコル」のルール化**:
   - 曖昧な初期要望（例:「Java を新しくしてクリーンアーキテクチャにしたい、キャッシュも変えたい」）のまま `pni workflows start` を走らせると、AI が推測で技術選定や互換性方針を決め打ちし、手戻りの大きい計画書になってしまう。
   - PNI の公式ルール（`agent.md`, `common/workflow_guide`, `common/migration_planning`）において、**ワークフロー実行前に As-Is 診断結果と移行要望を突合して曖昧点を洗い出し、ユーザーへ質問して回答を得たうえで、確定的な内容に `.pni/workflows/*.yaml`（および `brief_file`）を更新してから実行するプロセス** を標準推奨ルールとして組み込む。
4. **「決定論的 As-Is 構造・境界接点解析 Action」＋「AI 移行設計 Action」の 2 段分離**:
   - AI に丸投げして「全部一気に最新化する理想論」を書かせるのを防ぐため、まず決定論的プリミティブ `migration_analyze` が現行コードから **①トポロジカル改修 Wave 順序、②暗黙の I/O データ契約、③状態・DB・Cache・外部通信の接点インベントリ、④自動変換ツール適用候補、⑤仕様 vs バグ確認候補** を JSON 化し、その実コード根拠の上に AI Action が移行設計（Port/Adapter 分割や PR WBS を含む）を組み立てる。
5. **3 つの移行類型（In-Place 刷新 / アーキテクチャ再編 / 異言語・異 FW 載せ替え）への適応**:
   - 同言語バージョンアップ（Java 8 → 21）だけでなく、**クリーンアーキテクチャ導入＋DB/Redis 刷新** や **素 PHP → Laravel 11 / Python FastAPI への段階リプレイス（Strangler Fig）** まで同一パイプラインで表現できるスキーマとする。

---

## 2. ワークフロー実行前の「要件精査・対話的確定プロトコル」（PNI ルール設計）

PNI のワークフローエンジンは `pni workflows start <workflow_id>` 実行時点でステップ定義と `with` パラメータを `.pni/cache/workflow_state.db` に固定する。したがって、**「実行前のワークフロー YAML こそが再現可能な唯一の確定仕様（Single Source of Truth）」** となるよう、以下の 4 ステップ・プリフライト手順を PNI ルールで強く推奨する。

### 2-1. ルール配置先（3 箇所の同期整備）
1. **`src/pni/_instructions/agent.md` および `src/pni/_rules/common/agent_instruction.md`**:
   - エージェントが最初に読むブートストラップ手順（`Section 1. Authoring or Customizing Project Workflows`）に、マイグレーションワークフロー作成・実行前の **「Pre-Flight Migration Brief Scrutiny（実行前の曖昧性解消と YAML 確定化）」** を明記する（あわせて現行の章数表記 `00_cover.md`〜`06_*.md` も最新化する）。
2. **`src/pni/_rules/common/workflow_guide.md`**:
   - マイグレーション用ワークフロー（`migration_proposal` / `write_migration_report`）を作成する際の標準パイプライン構成と、実行前チェック手順を追記する。
3. **`src/pni/_rules/common/migration_planning.md`（新設）**:
   - `pni rules show common/migration_planning` で参照できる専用ルールとして、①実行前の 6 観点精査チェックリスト、②ユーザーへの質問フォーマット指針、③確定後の `brief` 構造化テンプレート、④5 段階フェーズゲート＆クリーンアーキテクチャ／DB・Cache 移行の設計基準を定義する。

### 2-2. 実行前 4 ステップ・プリフライト手順（Agent Workflow Rule）

1. **Step 1: As-Is 診断結果・対象コードと初期移行要望の突合**
   - 既存の診断成果物（`reports/<lang>/<target>_score.json`, `.pni/cache/<audit_wf>/facts.json`）またはリポジトリのマニフェスト・主要ソースを確認し、現行の言語バージョン、フレームワーク、DB 接続形態、インメモリ状態（`static Map`, `$_SESSION` 等）、外部通信箇所を把握する（未診断の場合は先に `full_audit` 系ワークフローの実行を推奨する）。
2. **Step 2: 6 つの観点での曖昧性・未決定事項の精査（Ambiguity Checklist）**
   - ユーザーの初期プロンプトやドラフト YAML に対し、以下の 6 観点で曖昧な点・欠落している制約がないかを精査する:
     1. **ターゲット技術スタックと具体的バージョン**: 「最新にする」等の曖昧表現ではなく、具体的なバージョン（例: Java 21 LTS か 17 か、Spring Boot 3.4、PHP 8.3 + Laravel 11 等）が定まっているか。
     2. **ステート・DB・Cache 基盤の選定**: As-Is コードにインメモリ状態や生 SQL が存在する場合、移行先のデータストア（PostgreSQL / MySQL、Redis / インプロセスキャッシュ、JPA / Eloquent / SQLAlchemy、マイグレーションツール等）が明確か。
     3. **設計思想・アーキテクチャの適用スコープ**: 「クリーンアーキテクチャ導入」等の要望に対し、レイヤー構成（`domain` / `usecase` / `port` / `adapter` 等）と適用範囲（全モジュール厳格分離か、DB・外部 API 等の境界 Port 抽出を優先するか）が明確か。
     4. **外部インターフェース互換性 (`api_compatibility`)**: 外部連携クライアントのために既存 URL・HTTP メソッド・JSON キー・認証ヘッダを完全維持（`strict`）する必要があるか、`/v2` 等の新スキーマ変更（`versioned_v2`）を許容するか。
     5. **既存コードの「仕様かバグか」の扱い方針 (`bug_handling_policy`)**: As-Is で検出された疑わしい挙動（例: `currency == "USD"` 参照比較や MD5 比較など）を、基盤移行フェーズでは現行維持して仕様確認票へ切り出す（`ask_human`）か、今回同時に修正するか。
     6. **移行方式・カットオーバー制約 (`migration_strategy` & Non-Goals)**: 同一リポジトリでの段階 PR 積み上げ（`phased_pr`）、新旧並行稼働（`strangler_fig`）、別リポジトリ刷新（`rewrite`）のどれを採るか、また「今回は対象外とするスコープ（Non-Goals）」は何か。
3. **Step 3: ユーザーへの対話的ヒアリング（曖昧なまま `start` しない）**
   - 計画の骨格を左右する未確定事項がある場合、エージェントは **`pni workflows start` を実行する前に立ち止まり**、As-Is コードの事実に基づいた **推奨選択肢（Recommended）付きの簡潔な質問** をユーザーに投げかける。
   - ※ユーザーが「推奨案でお任せ」と回答した場合は、エージェントが採用した推奨前提を明示して Step 4 へ進む。
4. **Step 4: 確定内容のワークフロー定義（`.pni/workflows/*.yaml`）への書き戻しと検証**
   - ユーザーの回答をチャット履歴だけに留めず、**必ず `.pni/workflows/<migration_id>.yaml` の `with.brief: |`（または管理下の `with.brief_file`）および明示的なガードレール設定値（`"auto"` を具体的な確定値 `"phased_pr"`, `"strict"`, `"ask_human"` 等へ更新）としてファイルに書き戻す**。
   - `pni workflows show <migration_id>` を実行して定義とプリフライト検査を確認した後に、`pni workflows start <migration_id>` を開始する。

### 2-3. CLI 側の補助ガードレール（`pni workflows show` における曖昧性ヒント表示）
ルール（ドキュメント）だけでなく CLI 側でもこの運用を後押しするため、`pni workflows show <workflow_id>` が `migration_proposal` / `migration_analyze` を含むワークフローを表示する際、以下の決定論的レディネス検査（Preflight Readiness Hint）を表示する:
- `brief` / `brief_file` が未指定または極端に短い場合、あるいは曖昧キーワード（`"latest"`, `"最新"`, `"TBD"`, `"未定"`, `"いい感じ"` 等）を含む場合に警告ヒントを表示。
- `migration_strategy` 等が `"auto"` のままの場合に、「ユーザーと合意した確定値（`phased_pr` / `strangler_fig` / `rewrite`）への固定を推奨」と案内する（バッチ利用を妨げないようエラー停止ではなく Warning / Hint 表示とする）。

---

## 3. ワークフロー & 入力インターフェース設計

### 3-1. 新設するプリミティブと複合アクション

| 種別 | 識別子 | 役割 |
| :--- | :--- | :--- |
| **Primitive Action** | `migration_analyze` | 既存の診断キャッシュ（`facts.json`, `*_score.json`）または対象コードを走査し、①トポロジカル改修 Wave 順序、②暗黙の I/O・環境変数契約、③状態・DB・Cache・外部 HTTP 接点インベントリ、④Codemod 候補（`brief` ヒント照合）、⑤仕様 vs バグ確認候補を格納した **`migration_facts.json`** を決定論的に生成する。 |
| **Primitive Action** | `emit_migration_plan` | AI が作成した動的変更軸マトリクス・ターゲットアーキテクチャ設計（Clean Arch Port/Adapter 対応表等）・フェーズ別移行計画・Decision Log・PR 分割 WBS を Pydantic スキーマ（`MigrationPlanResult`）で厳密検証し、決定論データとマージして **`reports/<lang>/<target>_migration_plan.json`** を出力する。 |
| **Composite Action** | `migration_proposal` | `migration_analyze` → `ai_interpret`（`common/migration_planning` ルール＋確定済み `brief` 適用）→ `emit_migration_plan` を束ねた標準複合アクション。 |
| **Composite Action** | `write_migration_report` | `MigrationBlueprint`（移行専用の 7 ファイル構成 `00_cover.md`〜`06_*.md`）を生成し、Drawlib で **`reports/<lang>/<target>_migration_plan.pdf`** をコンパイルする。 |

### 3-2. 再現性を担保する 2 つの確定仕様記述方法（YAML SSOT 原則）

ユーザーとの対話で確定した複数行の移行要件は、一時的な CLI 引数ではなくリポジトリに永続化できる以下の 2 方式でワークフローに定義する:

1. **ワークフロー YAML 内の複数行リテラルブロック (`with.brief: |`)【推奨・標準】**: ワークフロー定義と確定した移行要件（ゴール・設計思想・互換制約・対象外範囲）を 1 ファイルで自己完結させる方式。
2. **外部 Markdown ファイル参照 (`with.brief_file: "docs/migration_brief.md"`)**: 背景・非機能要件・目標パッケージ構成図などを長文の設計書 Markdown として Git 管理し、ワークフロー YAML から参照する方式（`brief` と併用時は結合）。

### 3-3. 対話的精査を経て確定したワークフロー YAML の記述イメージ

```yaml
id: java_legacy_billing_migration
name: Migration Plan - legacy-billing Modernization & Clean Architecture
description: Generate a phased PR-by-PR migration plan incorporating Java 21, Spring Boot 3.4, PostgreSQL, Redis, and Clean Architecture.

targets:
  root: "examples/java/api_spring_messy"
  source:
    - "src/main/java"
  tests:
    - "src/test/java"
  docs:
    - "README.md"

steps:
  # 既存キャッシュ (.pni/cache/java_api_spring_messy/facts.json) があれば再利用、なければ自動収集
  - id: gap_and_order
    uses: migration_proposal
    with:
      base_audit_workflow: "java_api_spring_messy"
      # ▼ ユーザーへのヒアリングを経て曖昧さを排除・確定させた複数行移行仕様 (brief / brief_file)
      brief: |
        【移行ゴール・技術スタック（確定）】
        - 言語・FW: Java 8 から Java 21 LTS + Spring Boot 3.4.x (Jakarta EE 10 / JUnit 5) へ刷新する。
        - DB 永続化: 請求履歴の永続化に向け PostgreSQL 16 + Spring Data JPA + Flyway を導入する。
        - Cache / 状態管理: BillingManager 内の public static HashMap (INVOICE_CACHE) や
          Controller のフィールド状態は全廃し、Redis 7 (Spring Data Redis, TTL 24h) へ外部化して水平スケール可能にする。

        【設計思想・アーキテクチャ方針（確定）】
        - クリーンアーキテクチャ (domain / usecase / port / adapter) を導入する。
        - domain 層および usecase 層は Spring / JPA / Redis / HTTP クライアントに一切依存させない純粋 Java とする。
        - 外部決済通信 (現 GatewayClient) は PaymentGatewayPort インターフェースとして抽象化し、
          adapter/out/payment 配下にタイムアウト(接続3秒/読取5秒)付き RestClient 実装として分離する。

        【運用・互換性制約 & スコープ境界（確定）】
        - 既存の POST /charge の URL・JSON リクエスト/レスポンスキー ("customerId", "amountCents" 等) は外部連携中のため完全維持する。
        - BillingManager の currency == "USD" 比較等の疑わしい既存挙動は、基盤移行フェーズでは勝手に変更せず仕様確認票(Decision Log)へ切り出す。
        - 認証基盤 (OAuth2/OIDC 導入) は別プロジェクトで API Gateway 側にて対応するため本計画のスコープ外 (Non-Goal) とする。
        - コンテナは Eclipse Temurin 21 JRE の非 root マルチステージビルドとする。

      # ▼ ヒアリング結果に基づき "auto" から確定値へピン留めされたガードレール
      migration_strategy: "phased_pr"     # phased_pr | strangler_fig | rewrite | auto
      api_compatibility: "strict"         # strict (JSONキー・URL完全維持) | versioned_v2 | flexible
      bug_handling_policy: "ask_human"    # ask_human (仕様確認票へ分離) | preserve_behavior | fix_in_phase3
      codemod_tool: "openrewrite"         # openrewrite | rector | ruff | manual_only | auto
      output_dir: "reports/java"
      target: "api_spring_messy_migration"

  - id: create_migration_pdf
    uses: write_migration_report
    with:
      src_dir: "reports_src/java"
      output_dir: "reports/java"
      target: "api_spring_messy_migration"
      lang: "ja"
      style: "google"
```

同様に、異言語リプレイスやレガシー PHP 刷新も、事前ヒアリングで確定させた要件を `brief` に書き込むだけで一貫して表現できる:
- **例（レガシー素 PHP → Laravel + Redis + モジュラー設計）**:
  - ヒアリングで「既存 MySQL スキーマは維持するか」「MD5 パスワードをログイン時に段階再ハッシュするか」「URL 互換（`.php` パス）を Nginx リライトで吸収するか」を確認後、`migration_strategy: "strangler_fig"` として YAML を確定。
- **例（異言語リプレイス：レガシー PHP → Python FastAPI + SQLAlchemy 2.0）**:
  - ヒアリングで「共有 DB 期間を設けるか」「認証トークン互換方式」「JSON レスポンスキー互換」を確認後、`brief` とガードレールに明記して YAML を確定。

---

## 4. フリーフォーマット要件と安全弁ガードレールの協調モデル

### 4-1. 入力モデル (`MigrationOptions`)
`brief` に自然言語で書かれた個別指示を最優先しつつ、境界条件を明示的にロックするためのガードレールパラメータ（デフォルト値あり・事前精査時に確定値への更新を推奨）を組み合わせる。

1. **`brief: str` / `brief_file: Optional[str]`**:
   - 移行先スタック（言語・FW・DB・Cache・インフラ）、導入したい設計思想（クリーンアーキテクチャ、DDD、モジュラーモノリス等）、非機能要件、業務制約、および対象外範囲（Non-Goals）を記述する複数行フリーフォーマット本文（両方指定時は結合）。
2. **`migration_strategy` (`"auto"` [default] | `"phased_pr"` | `"strangler_fig"` | `"rewrite"`)**:
   - `phased_pr`: 同一リポジトリ内で依存リーフから順番に小さな PR を積み上げる方式。
   - `strangler_fig`: フロントプロキシ／ルーターでエンドポイント単位に新実装へ段階移管する方式。
   - `rewrite`: 新規ディレクトリ／リポジトリに新スタックを構築し契約テストで一括または段階切替する方式。
   - `auto`: 未指定時のフォールバック（`brief` の内容から自動判定するが、事前精査ルールでは確定値への明示を推奨）。
3. **`api_compatibility` (`"strict"` [default] | `"versioned_v2"` | `"flexible"`)**:
   - `strict` 指定時、内部をクリーンアーキテクチャの Entity / UseCase Input・Output DTO に再設計しても、**Web Adapter 境界での公開 URL・HTTP メソッド・JSON フィールド名・デフォルト値（例: `"customerId"`, `"anon"`）を 100% 維持** するマッピング層を強制する。
4. **`bug_handling_policy` (`"ask_human"` [default] | `"preserve_behavior"` | `"fix_in_phase3"`)**:
   - レガシーコードのバグ（例: `currency == "USD"` で税加算がスキップされる、PHP の緩い `==` 比較等）に外部システムが依存しているリスク（ハイラムの法則）に対処する。
   - `ask_human` 指定時、基盤移行フェーズでは現行挙動を壊さず固定し、プロダクトオーナー向けの **「仕様かバグか確認票（Decision Log）」** を第 3 章に出力したうえで業務ロジック改修フェーズへ分離させる。
5. **`codemod_tool` (`"auto"` [default] | `"openrewrite"` | `"rector"` | `"ruff"` | `"manual_only"`)**:
   - 同言語アップグレード要素（`javax -> jakarta`, JUnit 4 → 5, PHP 8 型補完等）があれば決定論的 Codemod レシピを割り当て、クリーンアーキテクチャ分割や異言語移行・DB/Redis アダプタ実装などの構造変更は手動/AI PR タスクへ切り分ける。

### 4-2. 出力スキーマにおける動的変更軸 (`MigrationAxis`) とターゲット設計 (`TargetArchitectureDesign`)
フリーフォーマットの多様な要求を受け止めるため、`MigrationPlanResult` は固定カラムではなく以下の構造を持つ:

- **`confirmed_assumptions: list[str]` & `non_goals: list[str]`（確定前提条件とスコープ外事項）**:
  - 実行前ヒアリングおよび `brief` で確定した前提条件と、「本計画ではあえて触らない範囲（Non-Goals）」を明示的に記録し、スコープクリープを防止する。
- **`target_axes: list[MigrationAxis]`（動的な As-Is → To-Be 変更軸リスト）**:
  - `category`: `"language_runtime"` | `"framework"` | `"architecture_pattern"` | `"database_persistence"` | `"cache_state"` | `"auth_security"` | `"messaging_async"` | `"container_cicd"` | `"custom"`
  - `title`（例: `"Cache / State Management"`, `"Architecture Philosophy"`）
  - `as_is`（例: `"BillingManager.INVOICE_CACHE (public static HashMap) + BillingController.channel"`）
  - `to_be`（例: `"Spring Data Redis (InvoiceCachePort / RedisInvoiceCacheAdapter, TTL 付きステートレス構成)"`）
  - `migration_approach` / `risk_level` / `affected_files: list[str]`
- **`target_architecture: TargetArchitectureDesign`（設計思想・レイヤー＆Port/Adapter マッピング）**:
  - `pattern_name`（例: `"Clean Architecture (Domain / UseCase / Interface Adapters / Infrastructure)"`）
  - `dependency_rules: list[str]`（例: `"domain・usecase 層は org.springframework.* / jakarta.persistence.* の import を禁止"`）
  - `target_layers: list[TargetLayerSpec]`（新設するパッケージ／ディレクトリ階層と責務）
  - `component_mappings: list[ComponentMigrationMapping]`（現行ファイル／クラス・接点を、移行後のどの層・どの Port / Adapter / Entity / UseCase へ分割・移設するかの具体的な対応表）

---

## 5. `migration_analyze` が決定論的に抽出する 5 つのコアデータ (`MigrationFacts`)

移行先がフリーフォーマットであっても、**「現行コード（As-Is）のどこに依存・契約・状態・外部 I/O があるか」は 100% 決定論的に抽出できる**。`src/pni/_actions/migration_analyze/` パッケージを新設し、以下の 5 モジュールを実装する。

### 5-1. トポロジカル改修順序 & 循環切断プランナ (`graph_waves.py`)
- `AstFacts.internal_import_graph` に対して **Tarjan の強連結成分分解（SCC）＋ Kahn の葉優先トポロジカルソート** を適用する。
- 出力データ (`refactoring_waves: list[RefactoringWave]`):
  - **Wave 1 (Leaf Nodes)**: 他モジュールへの内部依存が `0` の DTO・モデル・ユーティリティ（例: `InvoiceRecord.java`, `LegacyDateHelper.java` → クリーンアーキテクチャの `domain` 抽出の最優先候補）。
  - **Wave 2 (Infrastructure / Outbound Clients)**: Wave 1 のみに依存する外部通信・DB 層（例: `GatewayClient.java`, `includes/db.php` → Outbound Port + Adapter 化候補）。
  - **Wave 3 (Cycle Cut Targets)**: 双方向循環（SCC サイズ `>= 2`）を形成しているモジュール群と、**最小影響で切断すべき逆方向エッジの候補**（例: `BillingManager -> BillingController` の逆参照削除）。
  - **Wave 4 (Application Services & Entrypoints)**: 上位ユースケース・Web コントローラ層。

### 5-2. 暗黙の I/O スキーマ & 環境契約エクストラクタ (`contracts.py`)
レガシーコードに埋め込まれた「型定義のない入出力キー」を AST（`ast-grep-py`）で全言語横断抽出する:
- **Java**: `Map.get("k")`, `Map.getOrDefault("k", "default")`, `Map.put("k", v)`, `HttpServletRequest.getParameter("k")`, `System.getenv("ENV")`, `@Value("${prop:default}")`。
- **PHP**: `$_GET['k']`, `$_POST['k']`, `$_REQUEST['k']`, `$_COOKIE['k']`, `$request->input('k', 'default')`, `json_encode(['k' => ...])`, `getenv('ENV')`, `env('ENV', 'default')`, `define('CONST', ...)`。
- **Python**: `dict.get("k", default)`, `payload["k"]`, `request.args.get("k")`, `request.form.get("k")`, `os.getenv("ENV", default)`, `os.environ.get("ENV")`。
- 出力データ:
  - `implicit_contracts: list[ImplicitEndpointContract]`（入力キー名・推測型・デフォルト値・出力キー名・参照行番号）
  - `env_contracts: list[EnvVarContract]`（必要な環境変数・設定キー一覧と現在のデフォルト値／ハードコード箇所）

### 5-3. 状態・DB・Cache・外部通信の境界接点インベントリ (`touchpoints.py`) 【多軸・Clean Arch 対応の要】
`brief` で「DB 変更」「Redis キャッシュ導入」「クリーンアーキテクチャ（Port/Adapter 分離）」が指示された際、AI が抽象論ではなく **実コードの正確な行番号に紐づく分割設計** を書けるよう、現行コードの境界接点を決定論的に分類抽出する:
- **`in_memory_state`（Cache / ステートレス化対象）**: `static Map` / `Collection`（例: `BillingManager.INVOICE_CACHE`）、シングルトン Bean の可変フィールド（`BillingController.channel`）、PHP `$_SESSION` / `global` 変数、Python モジュールグローバル辞書。
- **`persistence_db`（DB / Repository Port 抽出対象）**: 生 SQL 文字列、JDBC / `@Transactional` / JPA Repository、PHP `mysqli_*` / `PDO` / `$wpdb` / Eloquent、Python `sqlite3` / `psycopg` / `SQLAlchemy` 呼び出し箇所。
- **`external_http_rpc`（Outbound Gateway Port 抽出対象）**: Java `HttpClient` / `RestTemplate` / `WebClient`、PHP `curl_*` / `file_get_contents(http)` / `Guzzle`、Python `requests` / `urllib` / `httpx` 呼び出し箇所。
- 出力データ: `boundary_touchpoints: list[BoundaryTouchpoint]`（種別・ファイル・行番号・シンボル・現在の結合形態）。

### 5-4. `brief` 連動の変換モード判定 & Codemod レシピマッパ (`codemods.py`)
現行スタック（`ProjectFacts` + `AstFacts`）と `MigrationOptions`（`brief` 内のターゲット言語・FW・設計キーワードを含む）を照合し、変換モードと適用可能な自動変換レシピを抽出する:
- **変換モード判定 (`transformation_mode`)**:
  - `"same_lang_upgrade"`（同言語・同系統 FW アップグレード）
  - `"architectural_restructure"`（同言語＋クリーンアーキテクチャ再編・DB/Redis 刷新など構造変更を伴う移行）
  - `"cross_stack_replacement"`（素 PHP → Laravel、または PHP → Python/Go 等のフレームワーク載せ替え・異言語移行）
- **定型 Codemod カタログ照合**（同言語要素がある場合に自動提案）:
  - **Java (`OpenRewrite`)**: `MigrateToJava21`, `UpgradeSpringBoot_3_4` (`javax -> jakarta`), `JUnit4to5Migration`, `ConstructorInjection`。
  - **PHP (`Rector` + `Composer`)**: `composer.json` PSR-4 初期化、`LevelSetList::UP_TO_PHP_83`、`DeclareStrictTypesRector`。
  - **Python (`Ruff` + `pyupgrade` / `bump-pydantic`)**: `UP` ルール群、Pydantic v1 → v2。
- 出力データ: `mechanical_codemods: list[CodemodRecipeMatch]`, `manual_blockers: list[MigrationBlocker]`（コンパイル阻害要因・循環依存・未宣言依存等の先行解消リスト）。

### 5-5. 「仕様かバグか（Spec vs. Bug）」意思決定候補の抽出 (`ambiguities.py`)
`AstFacts.bug_risk_idioms`、`dangerous_sinks`（`CWE-697` 緩い比較等）、および条件分岐内のハードコード定数・空 `catch` から、**「勝手に修正すると外部クライアントや課金・認証挙動が変わる恐れがある箇所」** を `SpecVsBugCandidate` として自動抽出する:
- 例（Java）: `BillingManager.java:55` の `currency == "USD"` 参照比較、`forceRetry` 時の固定 `100L` セント課金、レスポンスの `"controllerPing"` キー。
- 例（PHP）: `login.php:17` の `md5() == $expected_hash`（既存 DB の MD5 パスワードハッシュをどう段階移行するか）、無認証エンドポイントの公開範囲。

---

## 6. 適応型 5 段階フェーズゲート方式（移行パイプライン骨格）

`emit_migration_plan` およびレポートでは、インフラ刷新・アーキテクチャ再編・バグ修正を一度に混ぜてデグレを起こすアンチパターンを防ぐため、**5 段階フェーズゲート方式** を標準骨格としつつ、`transformation_mode`（同言語刷新 / Clean Arch 再編 / 異言語リライト）に応じて各フェーズのタスク内容を適応させる。

1. **Phase 0: 最小ビルド復旧 & 仕様固定テスト（Characterization / Golden Master Test）構築**
   - 構造変更やフレームワーク刷新の前に、最小変更でビルドまたはテストハーネスを通し、抽出した `ImplicitEndpointContract` に基づいて現行 API 入出力をスナップショット固定するテスト（異言語リライト時は HTTP E2E 契約テスト）を構築する。
2. **Phase 1: 構造的ブロッカー解消 & ドメイン／境界インターフェース（Port）の抽出**
   - `refactoring_waves` と `boundary_touchpoints` に従い、循環依存を切断する。
   - クリーンアーキテクチャや DB/Cache 変更を含む場合は、ここで `domain` / `usecase` と外部境界インターフェース（例: `PaymentGatewayPort`, `InvoiceCachePort`, `InvoiceRepositoryPort`）を切り出し、現行の `HashMap` や `HttpClient` を一時的な In-Memory / Legacy Adapter として包み込む（挙動はまだ変えない）。
3. **Phase 2: ランタイム・FW 引き上げ（Codemod 適用）& 新インフラ Adapter（DB / Redis 等）実装**
   - 同言語刷新要素には OpenRewrite / Rector / Ruff を適用して言語・FW を引き上げる（異言語移行時は新スタックの骨格と UseCase 移植を実施）。
   - Phase 1 で定義した Port に対し、移行先の **PostgreSQL (JPA/SQLAlchemy) Adapter** や **Redis Cache Adapter** を実装し、Testcontainers / 統合テストおよび Phase 0 の契約テスト PASS をゲート条件とする。
4. **Phase 3: Web API 境界の型安全 DTO 化 & 承認済み業務ロジック改修**
   - `api_compatibility` 制約を守りながら生 `Map` / `$_POST` / `dict` を型付き Request/Response DTO + Validation へ置き換え、第 3 章の **Decision Log（仕様確認票）** で承認されたバグ修正・SQL プリペアド化・認証認可付与を実施する。
5. **Phase 4: コンテナ・CI/CD ハードニング・段階切替（Cutover）と検収**
   - シークレット外部化、HTTP タイムアウト・耐障害設定、非 root マルチステージ `Dockerfile`、最小権限・SHA 固定 CI ワークフロー、Strangler Fig ルーティング切替（該当する場合）、および Trivy / PNI 再診断で完了検収を行う。

---

## 7. 移行計画レポート（Drawlib PDF）の章構成 (`MigrationBlueprint`)

`reports_src/<lang>/<target>_migration_src/` に以下の 7 ファイル構成で専用ビジュアルレポートを生成する（プラン 1 で導入した Drawlib Preflight リンター：複数系列凡例必須・等高線衝突防止・テーブル列幅ガードレールを標準適用）。

- **`00_cover.md` — PNI マイグレーション実行計画書（表紙）**:
  - 確定した移行シナリオ概要（`brief` 要約）、変更軸数（Language / FW / Arch / DB / Cache 等）、総 PR 分割数、要仕様確認件数（Decision Log 件数）の KPI カード。
- **`01_migration_strategy_summary.md` — 1. 移行戦略サマリー・確定前提条件と多軸 As-Is / To-Be ギャップマトリクス**:
  - 事前精査で確定した前提条件・対象外スコープ（`confirmed_assumptions` / `non_goals`）、`target_axes` に基づく **多軸 As-Is vs To-Be ギャップ比較表（`Table`：言語・FW・アーキテクチャ思想・DB・Cache・コンテナ等）**、および移行リスク・工数配分チャート（`BarChart`）。
- **`02_architecture_waves_and_contracts.md` — 2. ターゲットアーキテクチャ設計・改修 Wave 順序・データ契約**:
  - **To-Be レイヤー & Port/Adapter 構造図（`ClassDiagram`：クリーンアーキテクチャ等の新パッケージ境界と依存方向）**、**Wave 1（葉）→ Wave 4（根）改修順序ロードマップ（循環切断ポイント・DB/Cache 接点明示）**、および暗黙 I/O 契約 → 互換 DTO 設計表。
- **`03_spec_vs_bug_decision_log.md` — 3. 仕様確認票（Decision Log: 仕様かバグか）**:
  - プロダクトオーナー／業務担当者が Phase 3 着手前に判断すべき挙動リスト（該当コード・現行挙動・修正時の影響・推奨移行オプション）。
- **`04_five_phase_gate_roadmap.md` — 4. 5段階フェーズゲート実行ロードマップ**:
  - Phase 0〜Phase 4 のタイムライン／ゲート図（`Roadmap`）、各フェーズの完了条件（Exit Criteria）とロールバック／並行稼働基準。
- **`05_codemod_and_refactoring_design.md` — 5. 自動変換レシピと境界アダプタ（DB / Cache / Port）実装設計**:
  - 自動 Codemod vs 手動アーキテクチャ再編の比率チャート、適用レシピ（OpenRewrite / Rector / Ruff 等）、およびコア箇所（循環切断・Port/Adapter 抽出・Redis/DB 移行）の Before/After 設計表。
- **`06_pr_wbs_and_verification_gates.md` — 6. PR 分割 WBS（チケット一覧）と検収テスト計画**:
  - そのまま GitHub Issues / Jira に起票できるトポロジカル順 PR リスト（`PR #1`〜`PR #N`：対象フェーズ・変更軸・対象ファイル・変更内容・検証コマンド・推定規模）。

---

## 8. 実装フェーズ案

1. **Phase A（コアデータモデル & 決定論的 `migration_analyze` 実装）**:
   - `MigrationOptions`（`brief` / `brief_file` 対応）、`MigrationAxis`、`TargetArchitectureDesign`、`BoundaryTouchpoint`、`MigrationFacts`、`MigrationPlanResult`（`confirmed_assumptions` / `non_goals` 含む）の Pydantic モデル定義。
   - Python / Java / PHP 対応の `graph_waves.py`（SCC + トポロジカルソート）、`contracts.py`（暗黙 I/O 契約抽出）、`touchpoints.py`（インメモリ状態・DB・外部 HTTP 接点抽出）、`codemods.py`（`brief` 連動モード判定）、`ambiguities.py` の実装と単体テスト。
2. **Phase B（ワークフロー実行前精査ルールの整備・エンジン統合 & `MigrationBlueprint` 実装）**:
   - **実行前要件精査・対話的確定ルールの整備**:
     - `src/pni/_instructions/agent.md` および `src/pni/_rules/common/agent_instruction.md` へのマイグレーション実行前プリフライト手順（6 観点精査 → ユーザー質問 → YAML 確定化）の追加。
     - `src/pni/_rules/common/workflow_guide.md` の更新、および新設ルール `src/pni/_rules/common/migration_planning.md` の作成（`.pni/` テンプレート側とも同期）。
     - `pni workflows show <workflow_id>` におけるマイグレーション `brief` 曖昧性・未確定パラメータの Preflight Readiness Hint 表示の実装。
   - `PrimitiveType.MIGRATION_ANALYZE` / `EMIT_MIGRATION_PLAN` の `engine.py` 統合、`migration_proposal.yaml` / `write_migration_report.yaml` の追加。
   - `src/pni/_reporter/migration_blueprint.py` による専用 7 章 Blueprint 生成。
3. **Phase C（複合移行シナリオでの実証レポート生成）**:
   - シナリオ 1: `examples/java/api_spring_messy` に対し、確定済み複数行 `brief` で **「Java 21 + Spring Boot 3.4 + PostgreSQL + Redis キャッシュ化 + クリーンアーキテクチャ（Port & Adapter）導入」** を定義したワークフロー YAML を作成し、マイグレーション計画 PDF レポートを生成・検証する。
   - シナリオ 2: `examples/php/legacy_shop_messy` に対し、確定済み複数行 `brief` で **「素 PHP から PHP 8.3 + Laravel 11 + PDO/Eloquent + Redis セッションへの Strangler Fig 段階移行」** を定義したワークフロー YAML を作成し、マイグレーション計画 PDF レポートを生成・検証する。
