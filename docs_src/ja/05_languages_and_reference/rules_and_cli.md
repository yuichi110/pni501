# ルール拡張と CLI リファレンス

`pni501` (`v0.1.4`) は、`common/*`（16 個の普遍的エンジニアリング規約とオーケストレーションガイド）および `<lang>/*`（6 言語・36 個の言語/フレームワーク規約）からなる **全 52 個の組み込み Markdown ルールファイル**を同梱しており、決定論的な `.pni/` ローカルオーバーライドカスケードと統合 `pni` CLI によってあらゆるプロジェクトの要件に柔軟に適応します。

```drawlib align=center code=fold file=rules_taxonomy_and_override.png caption="直交ルール体系（common/* + <lang>/*）と .pni/ ローカルオーバーライドカスケード"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import CardList, Panel
from drawlib.styles import Styles

setup(width=184, height=86, dpi=150)

tax_panel = Panel(
    "1. Built-in Rule Taxonomy (52 Markdown Files)",
    header_variant="filled",
    header_height=8.5,
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=11.2),
)
tax_panel.draw(xy=(4.0, 4.0), width=85.5, height=78.0)

tax_cards = CardList(
    style=Styles.WhiteBordered.patch(shape_r=1.5),
    text_style=Styles.DarkBold.patch(text_size=10.8),
    description_style=Styles.Dark.patch(text_size=10.0),
    badge_shape="rounded_rect",
    badge_style=Styles.PrimaryNeutral,
    badge_text_style=Styles.PrimaryBold.patch(text_size=10.0),
    icon_style=Styles.PrimaryBold,
    direction="vertical",
    spacing=2.8,
)
tax_cards.add(
    "Universal Standards & Guides (common/*)",
    "12 evaluation rules (Arch, SIG, OpenSSF, OWASP,\n"
    "12-Factor, SRE, CLI, Library) + 4 meta-guides\n"
    "(agent_instruction, workflow/migration/progress)",
    badge_text="16",
    icon=phosphor.globe,
)
tax_cards.add(
    "6-Language Core Standards (<lang>/*)",
    "code_quality, typing, dependencies, testing,\n"
    "modern_stack, workflow_guide across python,\n"
    "java, php, go, typescript, and javascript",
    badge_text="32",
    icon=phosphor.code,
)
tax_cards.add(
    "Framework Rules (<lang>/frameworks/*)",
    "python/frameworks/fastapi, java/frameworks/\n"
    "spring_boot, php/frameworks/laravel, and\n"
    "php/frameworks/wordpress",
    badge_text="4",
    icon=phosphor.stack,
)
tax_cards.draw(xy=(6.5, 6.5), width=80.5, height=64.5)

cas_panel = Panel(
    "2. Local .pni/ Override & Waiver Cascade",
    header_variant="filled",
    header_height=8.5,
    style=Styles.PrimaryNeutral.patch(shape_r=2.0),
    header_style=Styles.SecondaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=11.2),
)
cas_panel.draw(xy=(94.5, 4.0), width=85.5, height=78.0)

cas_cards = CardList(
    style=Styles.WhiteBordered.patch(shape_r=1.5),
    text_style=Styles.DarkBold.patch(text_size=10.8),
    description_style=Styles.Dark.patch(text_size=10.0),
    badge_shape="rounded_rect",
    badge_style=Styles.SecondaryNeutral,
    badge_text_style=Styles.SecondaryBold.patch(text_size=10.0),
    icon_style=Styles.SecondaryBold,
    direction="vertical",
    spacing=2.8,
)
cas_cards.add(
    "Priority 1: Local .pni/ Workspace Files",
    ".pni/rules/<scope>/<name>.md, .pni/actions/*.yaml,\n"
    ".pni/dockerfiles/, and .pni/instructions.md\n"
    "automatically shadow built-in package defaults",
    badge_text="P1",
    icon=phosphor.folder_open,
    badge_style=Styles.PrimaryFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=10.0),
    icon_style=Styles.WhiteBold,
)
cas_cards.add(
    "Priority 2: Active Language Scope (<lang>/*)",
    "Short names (e.g. 'pni rules show testing' or\n"
    "'repo_structure_audit') resolve to the active\n"
    "language before falling back to common/*",
    badge_text="P2",
    icon=phosphor.magnifying_glass,
)
cas_cards.add(
    "Priority 3: Built-in common/* & [[opt_out]]",
    "Canonical src/pni/_rules/ fallback paired with\n"
    "declarative .pni/pni.toml [[opt_out]] waivers\n"
    "(requires scoped paths + reason >= 10 chars)",
    badge_text="P3",
    icon=phosphor.shield_check,
)
cas_cards.draw(xy=(97.0, 6.5), width=80.5, height=64.5)

save()
```

---

## 1. 直交ルール体系（全 52 組み込みファイル）

`pni501` のすべてのルールは、`src/pni/_rules/` 配下に人間と LLM の双方が読みやすい Markdown として格納されており、AI が主観的な推測に頼ることなく評価できるよう、決定論的な静的解析・コンテナ実行・セキュリティスキャンの各シグナルと対になっています。

### 1.1 普遍的エンジニアリング規約とメタガイド (`common/*` — 16 ファイル)

`common/` スコープには、全プロジェクト共通およびアーキタイプ別（`Service / API`・`CLI Tool`・`Library / SDK`）の **12 個の評価ルール**と、エージェントおよびワークフロー設計用の **4 個のメタガイド**が含まれます。

| ルール識別子 | 準拠する業界標準・仕様 | 対象アーキタイプ | 決定論的グラウンディング指標 (`ProjectFacts` / `AstFacts` / `RuntimeFacts`) |
| :--- | :--- | :--- | :--- |
| `common/architecture` | Clean / Layered Arch | 全プロジェクト | `circular_dependencies`, `internal_import_graph`, `boundary_violations`, `ArchitectureRecord` |
| `common/maintainability` | SIG / ISO 25010 | 全プロジェクト | `complex_functions` (`McCabe > 7`, `cognitive > 15`), `LOC <= 50`, `params <= 6`, `global_state_usages` |
| `common/supply_chain` | OpenSSF Scorecard | 全プロジェクト | `lockfiles_found`, `unpinned_dependencies`, `ci_supply_chain_issues`, `has_license`, `has_security_md` |
| `common/security` | OWASP ASVS Baseline | 全プロジェクト | `committed_secret_files`, `hardcoded_secrets`, `bug_risk_idioms`, `dangerous_sinks` |
| `common/security_vulnerability` | Trivy + CWE Sinks | 全プロジェクト | `SecurityScanFacts` (App/OS CVE・IaC 設定ミス・秘匿情報) + AST `dangerous_sinks` & `api_endpoints` |
| `common/runtime_verification` | 隔離コンテナ実行検証 | 全プロジェクト | `RuntimeFacts` (Dockerfile ビルド・`--network=none` テスト通過率・行/分岐カバレッジ・Stage 3 スモークプローブ) |
| `common/git_workflow` | Conventional Repo | 全プロジェクト | `has_gitignore`、コミットされたキャッシュ・ビルド成果物（`__pycache__`, `node_modules`, `.venv`）、リポジトリ衛生 |
| `common/documentation` | Std Readme & Diataxis | 全プロジェクト | `readme_headings`, `readme_line_count`, `docs_inventory`, `docstring_coverage_pct`, `docstring_issues` |
| `common/twelve_factor` | 12 / 15-Factor App | Service / API | 設定モジュール外の `scattered_env_access`、`runtime_types`、ステートレスワーカー設計 |
| `common/production_readiness` | Google SRE PRR | Service / API | `missing_io_timeouts`、`unstructured_logging`、ヘルスチェックエンドポイント、非 root コンテナ設定 |
| `common/cli_guidelines` | clig.dev Guidelines | CLI Tool | CLI エントリポイント、`--help`/`--version`/`--json` 対応、`stdout` と `stderr` の分離、非ゼロ終了コード |
| `common/library_guidelines` | Public SDK Hygiene | Library / SDK | 明示的な公開エクスポート（`__all__`）、`py.typed` / `.d.ts` マーカー、import 時の副作用排除、ライブラリ内の `sys.exit()` 禁止 |
| `common/agent_instruction` | PNI Agent Protocol | メタガイド | 決定論的 Pull-Push 実行ループとゼロハルシネーション規約（`pni instructions`） |
| `common/workflow_guide` | PNI Authoring Spec | メタガイド | リポジトリ構造の調査手順と `.pni/workflows/*.yaml`・`.pni/actions/*.yaml` の設計仕様 |
| `common/migration_planning` | Modernization Spec | メタガイド | マイグレーション実行前の要件明確化チェックリスト、`based_on` 監査継承、5 フェーズゲート設計ガイド |
| `common/progress_tracking` | Schedule & Git Gov | メタガイド | `.pni/progress/<target>.yaml` のマイルストーン・タスク DAG 検証および Git ブランチ/コミットガバナンス規約 |

### 1.2 言語別・フレームワーク別ルールカタログ (`<lang>/*` — 36 ファイル)

対応する 6 言語それぞれに、コア評価ルール（`code_quality`, `typing`, `dependencies`, `testing`）、エコシステム別 `workflow_guide`、および `modern_stack` や `frameworks/*` ルールが用意されています。

| 言語スコープ | ファイル数 | 組み込みルール識別子 | 主なエコシステム・フレームワーク評価基準 |
| :--- | :--- | :--- | :--- |
| **Python (`python/*`)** | `7` | `code_quality`, `typing`, `dependencies`, `modern_stack`, `testing`, `frameworks/fastapi`, `workflow_guide` | PEP 621 `pyproject.toml` + `uv.lock`、公開 API 型ヒント 100%、Google docstring、Python 3.11+ `pathlib` / `X \| Y`、`pytest` ミラー構成、FastAPI `lifespan` & `Depends()` DI |
| **Java (`java/*`)** | `6` | `code_quality`, `typing`, `dependencies`, `testing`, `frameworks/spring_boot`, `workflow_guide` | Maven/Gradle ラッパーとロックファイル、ジェネリクス安全性（生型の排除）、Javadoc `@param` 同期、Java 21 `record`/`sealed`、JUnit 5 `@Test`、Spring Boot コンストラクタ DI & `@ConfigurationProperties` |
| **PHP (`php/*`)** | `8` | `code_quality`, `typing`, `dependencies`, `modern_stack`, `testing`, `frameworks/laravel`, `frameworks/wordpress`, `workflow_guide` | `declare(strict_types=1)`、PSR-12 / PSR-4 オートロード、`$_GET`/`$GLOBALS` 直参照の排除、PHP 8.2+ `readonly`/`enum`、PHPUnit/Pest + `pcov`、Laravel FormRequest/Eloquent 安全性、WordPress `$wpdb->prepare` & nonce |
| **Go (`go/*`)** | `5` | `code_quality`, `typing`, `dependencies`, `testing`, `workflow_guide` | `gofmt`/`go vet`、エクスポートシンボルの GoDoc、明示的な `if err != nil`（`%w` ラップ、`_ = err` 禁止）、最小インターフェース（`any`/`unsafe.Pointer` 回避）、テーブル駆動 `t.Run` テスト |
| **TypeScript (`typescript/*`)** | `5` | `code_quality`, `typing`, `dependencies`, `testing`, `workflow_guide` | `tsconfig.json` `"strict": true` (`noImplicitAny`, `strictNullChecks`)、`: any` / `as any` の排除（`unknown` + Zod による絞り込み）、TSDoc コメント、Promise エラー処理、Vitest/Jest カバレッジ |
| **JavaScript (`javascript/*`)** | `5` | `code_quality`, `typing`, `dependencies`, `testing`, `workflow_guide` | ES Module (`import`/`export`)、JSDoc `@param {Type}` & `@returns {Type}` 型契約、`checkJs` / `// @ts-check`、`const`/`let` と厳密等価 `===`、Vitest/Jest/Node テストスイート |

---

## 2. `.pni/` ローカルオーバーライドカスケードと `pni.toml` 特例承認 (`[[opt_out]]`)

`pni init` を実行するとワークスペース直下に `.pni/` ディレクトリが生成されます。PNI はルール・複合アクション・インストラクション・コンテナハーネスを非破壊の優先順位カスケードで解決するため、`pni501` 本体をフォークすることなくプロジェクト固有の閾値や Dockerfile を柔軟にカスタマイズできます。

| ワークスペースパス | カスケード解決順序 | 役割とカスタマイズ方法 |
| :--- | :--- | :--- |
| `.pni/pni.toml` | ワークスペースルート（または親ディレクトリの `.pni/pni.toml`） | `[project]`、デフォルト `[targets]`、`[scan]` 除外ルール、`[report]` 設定、および `[[opt_out]]` 特例承認を宣言します。 |
| `.pni/rules/<scope>/<name>.md` | `.pni/rules/` $\to$ 組み込み `<active_lang>/` $\to$ 組み込み `common/` | `.pni/rules/` 内の `.md` を編集すると組み込みルールより優先されます（`pni rules list` で `Local (.pni)` と表示）。メタガイド（`agent_instruction`, `workflow_guide`）は常に最新の組み込み版が参照されます。 |
| `.pni/actions/*.yaml` | `.pni/actions/` $\to$ 組み込み `<active_lang>/` $\to$ 組み込み `common/` | 複合アクションの適用ルール・パラメータ・プロンプトをプロジェクト単位で上書きします。 |
| `.pni/workflows/*.yaml` | `.pni/workflows/` 内で定義 | `audit`・`migration` (`based_on`)・`progress` ワークフローを定義します。 |
| `.pni/dockerfiles/` | `explicit_dockerfile` $\to$ `.pni/dockerfiles/_templates/<lang>/<tool>.dockerfile` $\to$ 組み込み `src/pni/_dockerfiles/` | ターゲット別の検証用 Dockerfile（`.pni/dockerfiles/<target>/Dockerfile` + `.dockerignore`）を実体化します。 |
| `.pni/pentests/<target>/` | `pni pentests init -w <workflow_id>` で生成 | 明示的な `Python + httpx` 動的ペネトレーションテストスイート（`conftest.py`, `test_*.py`）を保持します。 |
| `.pni/progress/<target>.yaml` | `pni progress init` で生成・`pni progress validate` で検証 | マイルストーン・タスク依存 DAG (`depends_on`)・`git_policy` ガバナンスルールを定義します。 |

また、CLI ツールにおける意図的なサブプロセス呼び出しや開発専用 Dockerfile ステージなど、設計上の正当なトレードオフをグローバルルールを緩めずに除外したい場合は、`.pni/pni.toml` の `[[opt_out]]` に対象パス (`scope`) と 10 文字以上の技術的理由 (`reason`) を明記します。

```toml
[project]
name = "order-dispatch"
language_version = "3.12"
archetypes = ["web_api"]

[targets]
root = "."
source = ["src"]
tests = ["tests"]
docs = ["README.md"]
exclude = ["src/generated/**"]

[scan]
respect_gitignore = true
include_gitignored = ["uv.lock", "composer.lock", "go.sum"]

[report]
src_dir = "reports_src"
output_dir = "reports"
formats = ["pdf"]
lang = "en"
style = "google"

[[opt_out]]
id = "CWE-78"
scope = ["src/cli/sandbox_runner.py"]
reason = "Command arguments are validated against an allowlist and executed with shell=False."
```

---

## 3. `pni` CLI 完全リファレンス

`pni` CLI（`src/pni/cli.py`）は、ワークスペース初期化、ルール参照、ステートフルワークフロー実行、ライブペネトレーションテスト、進捗・Git ガバナンス管理、Drawlib レポートコンパイル、ローカル/Docker キャッシュ削除、および Pydantic スキーマ検証を一貫したサブコマンドツリーとして提供します。

```drawlib align=center code=fold file=cli_command_tree.png caption="pni CLI コマンド階層と .pni/ ワークスペース成果物の対応関係"
from drawlib.canvas import save, setup
from drawlib.smartarts import MindMapNode
from drawlib.styles import Styles

setup(width=204, height=90, dpi=150)

txt_root = Styles.WhiteBold.patch(text_size=11.0)
txt_group = Styles.DarkBold.patch(text_size=10.0)
txt_leaf = Styles.Dark.patch(text_size=9.8)

root = MindMapNode(
    "pni CLI\n(pni501 v0.1.4)",
    shape="rectangle",
    width=26.0,
    height=13.0,
    style=Styles.PrimaryFlat.patch(shape_r=2.0),
    text_style=txt_root,
    line_style=Styles.DarkBold,
    line_length=6.0,
    horizontal_margin=3.0,
    vertical_margin=2.4,
    children=[
        MindMapNode(
            "Workspace & Rules",
            branch="left",
            shape="rectangle",
            width=31.0,
            height=8.0,
            style=Styles.PrimaryNeutral.patch(shape_r=1.5),
            text_style=txt_group,
            children=[
                MindMapNode(
                    "pni init [--lang] [--force]",
                    shape="rectangle",
                    width=36.0,
                    height=6.2,
                    style=Styles.Neutral.patch(shape_r=1.2),
                    text_style=txt_leaf,
                ),
                MindMapNode(
                    "pni rules list [--all]",
                    shape="rectangle",
                    width=36.0,
                    height=6.2,
                    style=Styles.Neutral.patch(shape_r=1.2),
                    text_style=txt_leaf,
                ),
                MindMapNode(
                    "pni rules show <id> [-p]",
                    shape="rectangle",
                    width=36.0,
                    height=6.2,
                    style=Styles.Neutral.patch(shape_r=1.2),
                    text_style=txt_leaf,
                ),
                MindMapNode(
                    "pni instructions | version",
                    shape="rectangle",
                    width=36.0,
                    height=6.2,
                    style=Styles.Neutral.patch(shape_r=1.2),
                    text_style=txt_leaf,
                ),
            ],
        ),
        MindMapNode(
            "Cascaded .pni/ Assets",
            branch="left",
            shape="rectangle",
            width=31.0,
            height=8.0,
            style=Styles.SecondaryNeutral.patch(shape_r=1.5),
            text_style=txt_group,
            children=[
                MindMapNode(
                    "actions (.pni/actions/)",
                    shape="rectangle",
                    width=36.0,
                    height=6.2,
                    style=Styles.Neutral.patch(shape_r=1.2),
                    text_style=txt_leaf,
                ),
                MindMapNode(
                    "dockerfiles (.pni/)",
                    shape="rectangle",
                    width=36.0,
                    height=6.2,
                    style=Styles.Neutral.patch(shape_r=1.2),
                    text_style=txt_leaf,
                ),
                MindMapNode(
                    "validate-score | plan",
                    shape="rectangle",
                    width=36.0,
                    height=6.2,
                    style=Styles.Neutral.patch(shape_r=1.2),
                    text_style=txt_leaf,
                ),
            ],
        ),
        MindMapNode(
            "pni workflows",
            branch="right",
            shape="rectangle",
            width=31.0,
            height=8.0,
            style=Styles.PrimaryNeutral.patch(shape_r=1.5),
            text_style=txt_group,
            children=[
                MindMapNode(
                    "list [-c] | show <wf_id>",
                    shape="rectangle",
                    width=36.0,
                    height=6.2,
                    style=Styles.Neutral.patch(shape_r=1.2),
                    text_style=txt_leaf,
                ),
                MindMapNode(
                    "start <wf_id> [--supersede]",
                    shape="rectangle",
                    width=36.0,
                    height=6.2,
                    style=Styles.Neutral.patch(shape_r=1.2),
                    text_style=txt_leaf,
                ),
                MindMapNode(
                    "get-action | push-action",
                    shape="rectangle",
                    width=36.0,
                    height=6.2,
                    style=Styles.Neutral.patch(shape_r=1.2),
                    text_style=txt_leaf,
                ),
                MindMapNode(
                    "run-action <wf_id> <step>",
                    shape="rectangle",
                    width=36.0,
                    height=6.2,
                    style=Styles.Neutral.patch(shape_r=1.2),
                    text_style=txt_leaf,
                ),
                MindMapNode(
                    "status | inspect | rewind",
                    shape="rectangle",
                    width=36.0,
                    height=6.2,
                    style=Styles.Neutral.patch(shape_r=1.2),
                    text_style=txt_leaf,
                ),
            ],
        ),
        MindMapNode(
            "Report & Governance",
            branch="right",
            shape="rectangle",
            width=31.0,
            height=8.0,
            style=Styles.SecondaryNeutral.patch(shape_r=1.5),
            text_style=txt_group,
            children=[
                MindMapNode(
                    "pni report init | build",
                    shape="rectangle",
                    width=36.0,
                    height=6.2,
                    style=Styles.Neutral.patch(shape_r=1.2),
                    text_style=txt_leaf,
                ),
                MindMapNode(
                    "pni pentests init | run",
                    shape="rectangle",
                    width=36.0,
                    height=6.2,
                    style=Styles.Neutral.patch(shape_r=1.2),
                    text_style=txt_leaf,
                ),
                MindMapNode(
                    "pni progress | cache clean",
                    shape="rectangle",
                    width=36.0,
                    height=6.2,
                    style=Styles.Neutral.patch(shape_r=1.2),
                    text_style=txt_leaf,
                ),
            ],
        ),
    ],
)

root.draw(xy=(102.0, 45.0))
save()
```

### 3.1 ワークスペース初期化・ルール参照・キャッシュ削除・スキーマ検証コマンド

トップレベルコマンド、`pni rules`、および `pni cache` サブコマンドを使用して、`.pni/` の初期化、エンジニアリングルールの閲覧、AI エージェントのブートストラップ、ローカル/Docker キャッシュの一括削除、および出力 JSON のスキーマ検証を行います。

| コマンド | 主な引数・オプション | 概要と用途 |
| :--- | :--- | :--- |
| `pni init` | `[--lang/-l <lang>] [--force/-f]` | プロジェクトの主要言語（`python`, `java`, `php`, `go`, `typescript`, `javascript`）を自動検出し、`.pni/`（`pni.toml`, `rules/`, `actions/`, `workflows/`, `instructions.md`, `cache/.gitignore`）を生成します。 |
| `pni instructions` | *(別名: `pni instruction`)* | AI コーディングエージェント向けのブートストラップ手順とステートフル Pull-Push 実行ループガイドを標準出力に表示します。 |
| `pni rules list` | `[--all/-a]` | `common` と検出言語 `<lang>` の有効ルール一覧（`--all` 指定時は全 6 言語・52 ルールすべて）を、`Builtin` / `Local (.pni)` のステータス付きで表示します。 |
| `pni rules show` | `<name> [--pretty/-p]` | 指定したルールまたはワークフローガイド（`common/workflow_guide`, `python/testing`, または短縮名 `testing`）を Markdown（`--pretty` 指定時は Rich パネル）で出力します。 |
| `pni cache clean` | `[--docker] [--container-engine auto\|docker\|podman]` | `.pni/cache/` を削除し、`--docker` 指定時は一時生成された `pni-harness-*`, `pni-proj-*`, `pni-sec-*`, `pni-pentest-*` コンテナイメージやダングリングレイヤー、ビルドキャッシュを一括パージします。 |
| `pni validate-score` | `[score_path]` | `reports/<target>_score.json` を Pydantic の `ScoreResult` スキーマに対して検証します。 |
| `pni validate-migration-plan` | `[plan_path]` | `reports/<target>_migration_plan.json` を Pydantic の `MigrationPlanResult` スキーマに対して検証します。 |
| `pni validate-progress` | `[progress_path]` | `reports/<target>_progress.json` を Pydantic の `ProgressResult` スキーマに対して検証します。 |
| `pni version` | *(または `pni --version` / `-V`)* | インストールされている `pni501` のパッケージ名とバージョン（`pni501 v0.1.4`）を表示します。 |

```bash
# Initialize .pni/ workspace and inspect active + language-specific rules
pni init
pni rules list --all
pni rules show common/workflow_guide
pni rules show python/testing --pretty

# Validate emitted JSON deliverables and clean local + Docker cache artifacts
pni validate-score reports/full_audit_score.json
pni validate-migration-plan reports/migration_plan.json
pni validate-progress reports/project_progress.json
pni cache clean --docker
```

### 3.2 ステートフルワークフロー実行・デバッグコマンド (`pni workflows`)

`pni workflows` は SQLite ステートマシン（`.pni/cache/workflow_state.db`）の実行管理に加え、事前準備不要の単一ステップ直接実行（`run-action`）や非破壊のステップ巻き戻し（`rewind`）を提供します。

| コマンド | 主な引数・オプション | 概要と用途 |
| :--- | :--- | :--- |
| `pni workflows list` | `[--category/-c audit\|migration\|progress]` | `.pni/workflows/` 内のワークフロー一覧をカテゴリ・`based_on` 前提監査・ステップ数・対象パス・出力先とともに表示します。 |
| `pni workflows show` | `<workflow_id>` | 複合アクションを正規化プリミティブステップ（`1..N`）に展開し、ペネトレーションテスト・移行計画・進捗計画の Pre-Flight チェックを実行します。 |
| `pni workflows start` | `<workflow_id> [--supersede]` | `.pni/cache/workflow_state.db` に新しい実行セッション（`wf-...`）を開始します（デフォルトの `supersede=True` で同一ワークフローの未完了セッションを自動キャンセル）。 |
| `pni workflows get-action` | `<run_id>` | 未実行の決定論的解析器（`project_inspect`, `ast_analyze`, `run_check`, `security_scan`, `web_pentest`, `migration_analyze`, `progress_analyze`）を自動実行し、次の `act-XX` プロンプトと JSON スキーマを出力します。 |
| `pni workflows push-action` | `<run_id> <action_id> [json] [--file/-f <path>]` | エージェントの JSON 出力を Pydantic スキーマおよび実在ファイルパスに対して検証・保存し、次のステップへ進めます。 |
| `pni workflows run-action` | `<workflow_id> <action> [--base-url <url>] [--force-pentests] [--fail-on-findings]` | SQLite セッション準備なしで特定のステップや解析器を単体実行します（Dockerfile 調整・ペネトレーションテスト・CI ゲートに最適）。 |
| `pni workflows status` | `[run_or_wf] [-w <wf>] [-s <status>] [--latest] [-n <limit>] [--json]` | SQLite を直接クエリすることなく、実行履歴や各ステップの進捗状況（`done/total`、現在のステップ）を確認します。 |
| `pni workflows inspect-action` | `<run_or_wf> <action> [--agent-input \| --deterministic] [--json] [-o <path>]` | 記録済みの決定論的解析結果 JSON やエージェント入力 JSON を SQLite から抽出・ファイル保存します。 |
| `pni workflows rewind` | `<run_or_wf> <action> [--pull/-p]` *(別名: `retry-action`)* | 実行セッションを指定ステップまで巻き戻し、`.pni/workflows/<id>.yaml` の設定変更を再同期して後続ステップをクリアします。 |
| `pni workflows cancel` | `<run_id> \| --superseded [-w <wf>]` | 中断された `in_progress` セッションのキャンセル、または古い未完了セッションの一括整理を行います。 |

```bash
# Inspect workflow pipeline and execute the stateful Pull-Push loop
pni workflows show full_audit
pni workflows start full_audit --supersede
pni workflows get-action wf-1a2b3c4d
pni workflows push-action wf-1a2b3c4d act-02 --file payload.json

# Debug a single step ad-hoc or rewind an existing run to re-run runtime verification
pni workflows run-action full_audit runtime_verification
pni workflows status wf-1a2b3c4d
pni workflows inspect-action full_audit emit_score --agent-input -o last_score.json
pni workflows rewind wf-1a2b3c4d runtime_verification --pull
```

### 3.3 ビジュアルレポート・ペネトレーションテスト・進捗ガバナンスコマンド

専用サブコマンドグループとして、Drawlib レポート生成（`pni report`）、ライブ HTTP ペネトレーションテスト管理（`pni pentests`）、および進捗・Git ガバナンス計画検証（`pni progress`）が提供されています。

| コマンド | 主な引数・オプション | 概要と用途 |
| :--- | :--- | :--- |
| `pni report init` | `[target] [--src-dir reports_src] [-l en\|ja] [-s google\|default\|monochrome] [--keep-samples] [-f]` | 既存の執筆済み `*.md` チャプターを保持したまま、`reports_src/<target>_src/`（`drawlib.toml`, `styles.py`, `utils.py`, `_assets/`, `<lang>/`）を非破壊で初期化・更新します。 |
| `pni report check` | `[target] [--src-dir reports_src]` | 出力ファイルをビルドせずに `lint_drawlib_chapters` による事前チェック（複数系列凡例、`ClassDiagram` 等高線・`Styles.White` ガード）のみを実行します。 |
| `pni report build` | `[target] [--src-dir reports_src] [-o reports] [-f pdf\|html\|markdown\|images] [--toc/--no-toc] [--no-cache] [--link-check-root <dir>]` | `lint_drawlib_chapters` による事前チェックを実行し、`reports/<target>.pdf`（A4 ベクター PDF・目次付き）をコンパイルします（`-f html` 時はリンク切れ検査も自動実行）。 |
| `pni pentests init` | `[-w <wf>] [-t <root>] [-s <src>] [-l <lang>] [--force/-f]` | AST 解析結果から API エンドポイントを抽出し、`.pni/pentests/<target>/` に `Python + httpx` ベースの DAST スイート（`conftest.py`, `test_*.py`）を生成します。 |
| `pni pentests run` | `[-w <wf>] [-t <root>] [-s <src>] [--base-url <url>] [--container-engine auto\|docker\|podman] [-f]` | 隔離されたループバックコンテナを起動（または `--base-url` をプローブ）して `.pni/pentests/<target>/` を実行し、`PentestFacts` を出力します。 |
| `pni progress init` | `[target] [-w <wf>] [--force/-f]` | マイルストーン・タスク・`git_policy` を備えた `.pni/progress/<target>.yaml` の初期テンプレートを生成します。 |
| `pni progress validate` | `[target_or_path]` | 進捗ワークフロー開始前に、`.pni/progress/<target>.yaml` のスキーマ・ISO-8601 日付・`git_policy`・非巡回 `depends_on` タスク DAG を検証します。 |

```bash
# Scaffold, lint, and compile a 7-chapter Drawlib visual PDF report
pni report init full_audit --src-dir reports_src --lang en --style google
pni report check full_audit --src-dir reports_src
pni report build full_audit --src-dir reports_src --output-dir reports

# Materialize and execute live HTTP penetration tests for a web service workflow
pni pentests init -w full_audit
pni pentests run -w full_audit

# Initialize and validate a project progress & Git governance plan
pni progress init project_progress -w full_audit
pni progress validate project_progress
```

各コマンドの実践的なワークフロー手順については、[クイックスタートガイド](../01_getting_started/quickstart.md)、[ワークフローと Pre-Flight ゲート](../03_workflows_and_actions/workflows_guide.md)、および [Drawlib ビジュアルレポーター](../04_scoring_and_reports/drawlib_reporter.md) を参照してください。
