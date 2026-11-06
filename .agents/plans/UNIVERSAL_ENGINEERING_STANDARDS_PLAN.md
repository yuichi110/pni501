# 言語非依存エンジニアリング指標（12-Factor / SRE PRR / OpenSSF / SIG / CLI / Diátaxis）実装計画書

本ドキュメントは、**Twelve-Factor App (15-Factor)**、**Google SRE Production Readiness Review (PRR)**、**OpenSSF Scorecard**、**OWASP ASVS**、**SIG Maintainability Model**、**Command Line Interface Guidelines (`clig.dev`)**、**Diátaxis** といった**言語非依存（Language-Agnostic）の国際・業界標準指標**を `pni501` に組み込むための実装設計書です。

既存の多言語 AST 基盤（[CHECK_LANGUAGE_MATRIX_PLAN.md](./CHECK_LANGUAGE_MATRIX_PLAN.md)）および Python 詳細設計（[PYTHON_HEALTH_CHECKS_PLAN.md](./PYTHON_HEALTH_CHECKS_PLAN.md)）と直交するレイヤーとして設計します。

---

## 1. 基本アーキテクチャ：「言語 (`language`) × 実行形態 (`runtime_type`) × 全共通 (`universal`)」の3軸合成

言語非依存の指標を導入する際の最大の落とし穴は、**「Web サービス用の基準（ポートバインディングや `/healthz`）をライブラリや CLI に要求してノイズ（誤検知）を出すこと」**です。
これを防ぐため、言語非依存指標を **「全プロジェクト共通（Universal）」** と **「実行形態別（Runtime-Archetype Scoped）」** の2層に分離します。

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 1. Universal Standards (すべてのリポジトリに無条件適用)                  │
│   ・SIG Maintainability (関数長・複雑度・引数数・結合度)                 │
│   ・OpenSSF Scorecard / Supply Chain (Lockfile, CI権限, 依存更新, 秘密鍵) │
│   ・OWASP ASVS Code Baseline (ハードコード秘密情報・危険API・入力検証)    │
│   ・Diátaxis & Standard Readme (README必須章・docsの4象限整理)           │
├─────────────────────────────────────────────────────────────────────────┤
│ 2. Runtime-Archetype Standards (runtime_type に応じて選択適用)          │
│   ├─ [web_api / worker] 12-Factor (15-Factor) + Google SRE PRR          │
│   ├─ [cli]              CLI Guidelines (clig.dev)                       │
│   └─ [library]          Library API Hygiene (SemVer, 上限固定回避, 純粋性)│
├─────────────────────────────────────────────────────────────────────────┤
│ 3. Language & Framework Standards (既存の <lang>/*, frameworks/*)       │
│   ・Python (isort, typing, docstring, FastAPI/Pydantic)                 │
│   ・Java (Checkstyle import, Generics, Javadoc, Spring Boot)            │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 導入指標の有効性 × 実装難易度ランク付け

| ランク | 指標 / フレームワーク | スコープ | 決定論的抽出手段 (`project_inspect` / `ast_analyze`) | 有効性 | 実装難易度 |
| :---: | :--- | :--- | :--- | :---: | :---: |
| **Tier S** | **OpenSSF Scorecard (リポジトリ・CI衛生)** | 全共通 | `.github/workflows/*.yml` 権限・ピン留め検査、`dependabot`/`renovate`、`SECURITY.md`、`LICENSE`、`.env`/鍵ファイル誤コミット検出 | **極高** | **低** (YAML/Path検査) |
| **Tier S** | **SIG Maintainability (Unit Interfacing 追加)** | 全共通 | 既存の Unit Size / Cognitive Complexity / Coupling に加え、**引数過多 (`MAX_CALLABLE_PARAMS > 6`)** を決定論的 AST 検査 | **極高** | **低** (`BaseQualityChecker`拡張) |
| **Tier S** | **12-Factor / 15-Factor + SRE PRR** | `web_api` / `worker` | AST で **外部通信タイムアウト欠落**・**散在する環境変数直参照**・**非構造化標準出力ログ**・**Dockerfile root/`:latest`** を検出し AI が総合判定 | **極高** | **中** (`BaseOperationalChecker`新設) |
| **Tier A** | **OWASP ASVS (コード・シークレット衛生)** | 全共通 | AST でハードコードされた API キー/パスワードリテラル・危険デシリアライズ/SQL 文字列連結を検出 | **高** | **中** |
| **Tier A** | **CLI Guidelines (`clig.dev`)** | `cli` | `project_inspect` で CLI エントリポイントを特定し、`-h`/`--help`・終了コード・`stderr` 分離・非対話オプションをルール検査 | **高** | **低〜中** |
| **Tier A** | **Library Packaging & SemVer Hygiene** | `library` | `dependencies` での過剰な上限ピン留め（`==` / `<` 乱用）警告、トップレベル副作用・`sys.exit()` 使用の AST 検出 | **高** | **低** |
| **Tier B** | **Diátaxis / Standard Readme** | 全共通 | `README.md` の Markdown 見出し一覧と `docs/` ファイル一覧を決定論抽出し、AI が Tutorials / How-to / Reference / Explanation の充足度を評価 | **中〜高** | **低** |

---

## 3. コンポーネント別の詳細実装仕様

### 3.1. `project_inspect.py` の拡張（100% 言語非依存のリポジトリ・サプライチェーン検査）

[`ProjectFacts`](../../src/pni/_actions/project_inspect.py) に以下のフィールドを追加し、どの言語のリポジトリに対しても同一ロジックで確定ファクトを抽出します。

```python
class ProjectFacts(BaseModel):
    # ... 既存フィールド ...

    # 1. アーキタイプ自動推定ヒント ("cli" | "web_api" | "library" | "worker" | "hybrid")
    runtime_type_hint: str = "library"

    # 2. OpenSSF Scorecard / Supply Chain & Repo Governance
    has_license: bool = False
    has_security_policy: bool = False          # SECURITY.md / .github/SECURITY.md
    has_dependency_automation: bool = False    # dependabot.yml / renovate.json
    ci_workflows_found: list[str] = Field(default_factory=list)
    ci_supply_chain_issues: list[str] = Field(default_factory=list)
    committed_secret_files: list[str] = Field(default_factory=list)  # .env, *.pem, *.key 等

    # 3. Container / 12-Factor Build-Run Hygiene (Dockerfile 存在時のみ)
    has_dockerfile: bool = False
    container_hygiene_issues: list[str] = Field(default_factory=list)

    # 4. Diátaxis / Standard Readme 見出し・ドキュメント棚卸し
    readme_headings: list[str] = Field(default_factory=list)
    docs_inventory: list[str] = Field(default_factory=list)
```

#### 決定論的チェック内容
1. **`runtime_type_hint` の自動推定**:
   - `pyproject.toml` の `[project.scripts]` や `typer`/`click`/`argparse`/`picocli`/`cobra` 依存があれば `"cli"`
   - `fastapi`/`flask`/`django`/`spring-boot`/`gin`/`express` 依存があれば `"web_api"`（両方あれば `"hybrid"`、どちらも無ければ `"library"`）
2. **GitHub Actions / CI サプライチェーン検査 (`ci_supply_chain_issues`)**:
   - `.github/workflows/*.yml` を `yaml.safe_load` で解析（外部通信ゼロ）:
     - ワークフローまたはジョブに `permissions:` ブロックが無い → *OpenSSF Token-Permissions 違反（最小権限未設定）*
     - `uses: owner/repo@main` / `@master` / `@HEAD` のような可変ブランチ参照 → *Unpinned CI Action 警告*
     - `pull_request_target` トリガーの使用 → *特権昇格リスク注意喚起*
3. **誤コミット機密ファイル検査 (`committed_secret_files`)**:
   - ワークスペース内の `.env`（`.env.example` / `.env.template` は除外）、`*.pem`, `*.key`, `id_rsa`, `*credentials*.json` の存在を検出。
4. **Dockerfile 衛生検査 (`container_hygiene_issues`)**:
   - `Dockerfile` が存在する場合、`FROM ...:latest`（タグ未固定）、`USER` 命令の欠落（root 実行）、`.dockerignore` 欠如を検出。
5. **ドキュメント構造棚卸し (`readme_headings`, `docs_inventory`)**:
   - `README.md` から `#`〜`###` 見出しテキストを抽出（コードフェンス内は除外）。`docs/` 配下の `.md`/`.rst` 一覧を収集。

---

### 3.2. `ast_analyze` の拡張（SIG 引数検査 + `BaseOperationalChecker` 新設）

#### A. `BaseQualityChecker` への SIG Unit Interfacing 追加
- [`models.py`](../../src/pni/_actions/ast_analyze/models.py) に既定義の定数 `MAX_CALLABLE_PARAMS = 6` を活用し、`AstFacts.excessive_parameters: list[CodeLocation]` を追加。
- Python（`self`/`cls` 除外）および Java の全関数・メソッド・コンストラクタで引数数 `> 6` を決定論的に検出し、DTO / Config オブジェクトへの集約を促します。

#### B. 新規抽象クラス `BaseOperationalChecker` (`src/pni/_actions/ast_analyze/base/operational.py`)
12-Factor・SRE PRR・OWASP ASVS のうち、ソースコードの AST から確定抽出できる**運用・セキュリティシグナル**を言語横断で統一スキーマに正規化します。

| `AstFacts` 追加フィールド | 対応する指標・原則 | Python 実装 (`PythonOperationalChecker`) | Java 実装 (`JavaOperationalChecker`) |
| :--- | :--- | :--- | :--- |
| **`missing_io_timeouts`** | **SRE PRR** (外部通信の無限ハング防止) | `requests.{get,post,put,delete,patch,request}(...)` や `httpx.{get,post}(...)` で `timeout=` 引数が未指定の箇所 | `URL.openConnection()` 直使用や `HttpClient.newHttpClient()`（`connectTimeout` 未設定） |
| **`scattered_env_access`** | **12-Factor III: Config** (設定の集約と型検証) | `config`/`settings`/`cli` 以外の一般モジュールに散在する `os.environ[...]` / `os.getenv(...)` 直参照 | `@ConfigurationProperties` / `@Value` を使わずドメイン/サービス層で `System.getenv(...)` / `System.getProperty(...)` を直参照 |
| **`unstructured_logging`** | **12-Factor XI: Logs / CLI 衛生** | CLI 表示層以外での生の `print(...)` 呼び出し（`logging` / `structlog` 推奨） | `System.out.print*` / `System.err.print*` / `e.printStackTrace()` |
| **`hardcoded_secrets`** | **OWASP ASVS / 12-Factor III** | 非テストコードでの `password` / `secret` / `api_key` / `access_token` 変数への固定文字列リテラル代入（空文字・ダミープレースホルダ除外） | 非テストコードでの `PASSWORD` / `SECRET` / `API_KEY` 定数・フィールドへの固定文字列リテラル代入 |

---

### 3.3. 組込みルール (`src/pni/_rules/common/`) の拡充

すべて**言語非依存の `common/` スコープ**として以下の Markdown ルールを新設します。

| ルール ID | ベースとなる業界指標 | 主な評価基準（AI 解釈およびスコア根拠） |
| :--- | :--- | :--- |
| **`common/supply_chain`** | **OpenSSF Scorecard / SLSA** | ロックファイル必須、未ピン留め依存ゼロ、GitHub Actions `permissions:` 最小化・タグ固定、`dependabot`/`renovate`、`SECURITY.md`、`.env` 非コミット |
| **`common/maintainability`** | **SIG Maintainability / ISO 25010** | Unit Size (`<=50` LOC)、Cognitive Complexity (`<=15`)、Unit Interfacing (`<=6` 引数)、モジュール間疎結合・循環依存ゼロ |
| **`common/security`** | **OWASP ASVS (Code Baseline)** | ハードコード秘密情報ゼロ、SQL/OSコマンドインジェクション防止、安全なデシリアライズ、境界でのスキーマ入力検証 |
| **`common/documentation`** | **Diátaxis + Standard Readme** | `README` の必須要素（概要・インストール・最小実行例・開発手順）、規模に応じた Tutorials / How-to / Reference / Explanation の分離 |
| **`common/twelve_factor`** | **12-Factor / 15-Factor App** | 設定とコードの分離＆起動時型検証（III）、バックエンドサービスの疎結合化（IV）、ステートレスプロセス（VI）、ポートバインディング（VII）、Graceful Shutdown（IX）、構造化ログ出力（XI）、API First |
| **`common/production_readiness`** | **Google SRE PRR** | 全外部 I/O のタイムアウト設定、リトライ＋バックオフ戦略、Health/Readiness エンドポイント、例外握り潰し禁止とエラーコンテキスト保持、テレメトリ考慮 |
| **`common/cli_guidelines`** | **`clig.dev` (CLI Guidelines)** | `-h`/`--help` と `--version`、適切な終了コード（0 / 非0）、人間向け装飾とパイプ/機械可読出力（`--json` 等）の両立、`stdout`（結果）と `stderr`（ログ/エラー）の分離、非対話実行フラグ |
| **`common/library_guidelines`** | **SemVer / SDK Best Practices** | 公開 API 境界（`__all__` / `public` パッケージ）の明確化、Import 時の副作用（I/O・グローバル状態変更）ゼロ、ライブラリ内での `sys.exit()` / `System.exit()` 禁止、依存バージョンの過剰な上限固定回避 |

---

### 3.4. コンポジットアクション & AI ワークフロー構築ガイド (`workflow_guide`) の連携

#### 新規コンポジットアクション (`src/pni/_actions/common/`)
1. **`supply_chain_audit.yaml`**: `project_inspect` のサプライチェーン・CI・コンテナ・シークレット検査結果に対し、`common/supply_chain` + `common/security` ルールで AI 解釈を行う。
2. **`service_readiness_audit.yaml`** (*Web API / Worker / Microservice 向け*): `AstFacts`（`missing_io_timeouts`, `scattered_env_access`, `unstructured_logging`）と `ArchitectureRecord` を基に、`common/twelve_factor` + `common/production_readiness` ルールで評価する。
3. **`cli_guidelines_audit.yaml`** (*CLI ツール向け*): エントリポイント実装を読み、`common/cli_guidelines` ルールでヘルプ・終了コード・入出力ストリーム設計を評価する。
4. **`library_hygiene_audit.yaml`** (*ライブラリ / SDK 向け*): `common/library_guidelines` + `common/documentation`（Diátaxis）ルールで公開 API 設計とパッケージ境界を評価する。

#### `common/workflow_guide.md` の意思決定手順アップデート
AI にワークフロー（`.pni/workflows/*.yaml`）を作成させる際、以下の決定木でプロジェクトに最適なアクションを自動編成させます。

1. **全プロジェクト共通で必ず含めるステップ**:
   - `repo_structure_audit` + `supply_chain_audit`（OpenSSF / OWASP）
   - `<lang>_ast_audit`（言語別 AST + SIG Maintainability）
   - `architecture_analysis`（3観点アーキテクチャ記録）
   - `<lang>_test_audit`
2. **`runtime_type_hint` に応じて追加するステップ**:
   - `web_api` / `worker` → **`service_readiness_audit`**（12-Factor + SRE PRR）を追加
   - `cli` → **`cli_guidelines_audit`**（`clig.dev`）を追加
   - `library` → **`library_hygiene_audit`**（SemVer / SDK 純粋性 / Diátaxis）を追加
   - `hybrid`（例: CLI 兼 ライブラリである `pni501` 自身など）→ 両方を組み合わせ可能

---

### 3.5. 既存 6 カテゴリスコア (`CategoryScores`) との互換マッピング

[`ScoreResult`](../../src/pni/_actions/base_model.py#L204-L226) の JSON スキーマ後方互換性を維持したまま、新しい指標の検査結果を以下の 6 カテゴリへ自然に統合します。

| `CategoryScores` 軸 | 統合される言語非依存指標 |
| :--- | :--- |
| **`architecture`** | Architectural Fitness Functions、12-Factor (III Config 分離, IV Backing Services, VI Stateless) |
| **`code_quality`** | SIG Maintainability (Unit Size / Complexity / Interfacing)、SRE PRR (Timeouts, Error Handling, Logging)、OWASP ASVS コード安全性、`clig.dev` / Library 純粋性 |
| **`typing`** | 型注釈率・Generics 安全性・設定スキーマの型検証 (`pydantic-settings` / `@ConfigurationProperties`) |
| **`testing`** | テストカバレッジ・Assertion 実効性・CI 自動テスト実行構成 |
| **`dependencies`** | **OpenSSF Scorecard**（ロックファイル・ピン留め・CI 権限・自動更新設定・`.env` 管理）、`deptry` 過不足検査 |
| **`documentation`** | API Docstring / Javadoc 率 ＋ **Diátaxis / Standard Readme** 構造評価 |

---

## 4. 段階的実装フェーズ

### Phase 1: `project_inspect` の OpenSSF / Container / Diátaxis / `runtime_type_hint` 拡張
- [`src/pni/_actions/project_inspect.py`](../../src/pni/_actions/project_inspect.py) に GitHub Actions YAML 安全性検査（`permissions:`, 未ピン留め Action）、`SECURITY.md` / `LICENSE` / `dependabot` 検出、`.env`/秘密鍵誤コミット検出、`Dockerfile` 検査、`README` 見出し抽出、`runtime_type_hint` 推定を実装。
- [`src/pni/_workflows/engine.py`](../../src/pni/_workflows/engine.py) のプロンプト描画と `metrics_snapshot` に新ファクトを反映。

### Phase 2: SIG 引数過多チェック & `BaseOperationalChecker` (Python / Java) の実装
- [`BaseQualityChecker`](../../src/pni/_actions/ast_analyze/base/quality.py) に `excessive_parameters` (`> 6` 引数) を追加。
- `src/pni/_actions/ast_analyze/base/operational.py` (`BaseOperationalChecker`) を新設し、[`PythonOperationalChecker`](../../src/pni/_actions/ast_analyze/python/) と [`JavaOperationalChecker`](../../src/pni/_actions/ast_analyze/java/) で `missing_io_timeouts` / `scattered_env_access` / `unstructured_logging` / `hardcoded_secrets` を実装（[runner.py](../../src/pni/_actions/ast_analyze/runner.py) に接続）。

### Phase 3: 言語非依存ルール (`common/*.md`)・コンポジットアクション・`workflow_guide` 更新
- `src/pni/_rules/common/` に 8 本の言語非依存ルール（`supply_chain.md`, `maintainability.md`, `security.md`, `documentation.md`, `twelve_factor.md`, `production_readiness.md`, `cli_guidelines.md`, `library_guidelines.md`）を作成。
- `src/pni/_actions/common/` に `supply_chain_audit.yaml`, `service_readiness_audit.yaml`, `cli_guidelines_audit.yaml`, `library_hygiene_audit.yaml` を追加し、[common/workflow_guide.md](../../src/pni/_rules/common/workflow_guide.md) のワークフロー編成ガイドを更新。

### Phase 4: ユニットテスト & `pni501` ドッグフーディング検証
- GitHub Actions 権限不備・未ピン留め、`.env` 誤コミット、`requests.get` タイムアウト欠落、散在 `os.environ`、ハードコード API キー、6 引数超え関数、`clig.dev` / 12-Factor ワークフロー編成の網羅的テストを追加。
- `./pcli code-check all` および `./pcli test all --cov --cov-report --parallel` で全チェック・全テスト通過を確認。
