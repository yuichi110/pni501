# ドメインアーキテクチャと3層カスケード解決

`pni501` (`v0.2.0`) は `src/pni/` 配下の実装を、**8つの垂直ドメインパッケージ**（`_languages`、`_workflows`、`_actions`、`_reporter`、`_rules`、`_pentests`、`_dockerfiles`、`_instructions`）、プロジェクトマニフェストローダー（`_config.py`）、自己修復型キャッシュユーティリティ（`_cache.py`）、および軽量な Typer + Rich 製 CLI オーケストレーター（`cli.py`）に編成しています。各ドメインは **対応55言語 / 57 Tree-sitter 文法**（**組み込みルール 356 ファイル**、**アクションテンプレート 182 ファイル**、**ワークフローテンプレート 112 ファイル**、**コンテナハーネステンプレート 40 ファイル**）にわたる Pydantic v2 スキーマ、実行・解決ロジック、組み込みアセットを同一パッケージ内に同居（コロケーション）させ、モジュールレベルの厳密な有向非巡回グラフ（`circular_dependencies = []`）を維持しています。

```drawlib align=center code=fold file=domain_layer_hierarchy.png caption="src/pni/ における高凝集 8 ドメインパッケージ階層とモジュールレベル依存関係 DAG (v0.2.0)"
from drawlib.canvas import save, setup
from drawlib.diagrams.class_diagram import ClassDiagram, ClassNode
from drawlib.styles import Colors, Styles

setup(width=182, height=116, dpi=150)

diagram = ClassDiagram(
    node_style=Styles.Neutral.patch(text_size=10.0),
    header_style=Styles.PrimaryNeutral.patch(text_size=10.5),
    edge_style=Styles.DarkBold,
    edge_text_style=Styles.PrimaryBold.patch(text_size=10.0),
)

inst_node = ClassNode(
    "pni._instructions & _config",
    width=50.0,
    header_height=5.6,
    row_height=3.8,
)
inst_node.add_attribute("_config.py", ".pni/pni.toml & [[opt_out]]")
inst_node.add_attribute("manager.py", "agent.md cascade")
diagram.add(inst_node, xy=(30.0, 99.5))

cli_node = ClassNode(
    "pni.cli (CLI Orchestrator)",
    width=54.0,
    header_height=5.6,
    row_height=3.8,
    header_style=Styles.PrimaryFlat.patch(text_color=Colors.White, text_size=10.5),
)
cli_node.add_attribute("sub-apps (7)", "rules, workflows, report, grammars")
cli_node.add_attribute("commands", "init, validate-mermaid, validate-*")
diagram.add(cli_node, xy=(91.0, 99.5))

cache_node = ClassNode(
    "pni._cache (_cache.py)",
    width=50.0,
    header_height=5.6,
    row_height=3.8,
)
cache_node.add_attribute("self-healing", ".gitignore + CACHEDIR.TAG")
cache_node.add_attribute("workflow_state.db", "SQLite + trivy-cache/")
cache_node.add_attribute("cache/<wf>/", "plan, facts, arch, logs")
diagram.add(cache_node, xy=(152.0, 99.5))

pentest_node = ClassNode(
    "pni._pentests",
    width=50.0,
    header_height=5.6,
    row_height=3.8,
)
pentest_node.add_attribute("manager.py", ".pni/pentests/<target>/")
pentest_node.add_attribute("surface_codegen.py", "AST route probes")
pentest_node.add_attribute("templates (2)", "conftest & baseline .tmpl")
diagram.add(pentest_node, xy=(30.0, 71.0))

wf_node = ClassNode(
    "pni._workflows (v2 DAG)",
    width=54.0,
    header_height=5.6,
    row_height=3.8,
    style=Styles.PrimaryNeutral.patch(text_size=10.0),
)
wf_node.add_attribute("engine + planner", "needs/when DAG + Mermaid")
wf_node.add_attribute("4 categories", "audit, rollup, migration, progress")
wf_node.add_attribute("assets (112)", "55 langs + generic x 2")
diagram.add(wf_node, xy=(91.0, 71.0))

rep_node = ClassNode(
    "pni._reporter",
    width=50.0,
    header_height=5.6,
    row_height=3.8,
)
rep_node.add_attribute("facts_sync + sarif", "_facts/ sync & SARIF 2.1.0")
rep_node.add_attribute("blueprints (4)", "audit, rollup, mig, progress")
rep_node.add_attribute("compiler.py", "lazy drawlib -> pni_report/")
diagram.add(rep_node, xy=(152.0, 71.0))

docker_node = ClassNode(
    "pni._dockerfiles",
    width=50.0,
    header_height=5.6,
    row_height=3.8,
)
docker_node.add_attribute("manager.py", ".pni/dockerfiles/ harness")
docker_node.add_attribute("templates (40)", "35 langs (20 A + 15 B)")
diagram.add(docker_node, xy=(30.0, 42.0))

act_node = ClassNode(
    "pni._actions",
    width=54.0,
    header_height=5.6,
    row_height=3.8,
    style=Styles.SecondaryNeutral.patch(text_size=10.0),
    header_style=Styles.SecondaryNeutral.patch(text_size=10.5),
)
act_node.add_attribute("models + ai_actions", "16 canonical PrimitiveTypes")
act_node.add_attribute("ast_analyze/_cst.py", "native tree-sitter>=0.25.0")
act_node.add_attribute("assets (182)", "15 common + 55 langs x 3 + 2")
diagram.add(act_node, xy=(91.0, 42.0))

rules_node = ClassNode(
    "pni._rules",
    width=50.0,
    header_height=5.6,
    row_height=3.8,
)
rules_node.add_attribute("base_model.py", "RuleInfo (<scope>/<name>)")
rules_node.add_attribute("manager.py", "detect_active_language() (55)")
rules_node.add_attribute("assets (356)", "16 common + 55 langs + gen")
diagram.add(rules_node, xy=(152.0, 42.0))

lang_node = ClassNode(
    "pni._languages (SSOT Registry & ABI3 Grammar Downloader)",
    width=104.0,
    header_height=5.6,
    row_height=3.8,
    style=Styles.PrimaryNeutral.patch(text_size=10.0),
    header_style=Styles.PrimaryFlat.patch(text_color=Colors.White, text_size=10.5),
)
lang_node.add_attribute("registry.py", "55 langs / 57 grammars (20 Tier A, 20 Tier B, 15 Tier C)")
lang_node.add_attribute("_grammar_assets.py", "On-demand GitHub Releases ABI3 + SHA-256 pinning (5 extra)")
lang_node.add_attribute("cache fallback", "src/pni/_cached_grammars -> ~/.cache/pni501/grammars")
diagram.add(lang_node, xy=(91.0, 13.0))

diagram.connect(cli_node, inst_node, "dependency", start_side="left", end_side="right")
diagram.connect(cli_node, cache_node, "dependency", start_side="right", end_side="left")
diagram.connect(cli_node, wf_node, "dependency", start_side="bottom", end_side="top")
diagram.connect(wf_node, pentest_node, "dependency", start_side="left", end_side="right")
diagram.connect(wf_node, rep_node, "dependency", start_side="right", end_side="left")
diagram.connect(wf_node, act_node, "dependency", start_side="bottom", end_side="top")
diagram.connect(rep_node, cache_node, "dependency", start_side="top", end_side="bottom")
diagram.connect(act_node, docker_node, "dependency", start_side="left", end_side="right")
diagram.connect(act_node, rules_node, "dependency", start_side="right", end_side="left")
diagram.connect(act_node, lang_node, "dependency", start_side="bottom", end_side="top")
diagram.connect(rules_node, lang_node, "dependency", start_side="bottom", end_side="right")

diagram.draw(xy=(0.0, 0.0))
save()
```

---

## 1. 高凝集な垂直ドメインパッケージ設計 (`src/pni/`)

従来の CLI コードベースでは、Pydantic モデルを `models/`、YAML/Markdown ローダーを `config/`、サブプロセス実行器を `executors/`、静的ファイルを `templates/` へと水平分割（レイヤー分割）しがちです。しかしこの構造では、1つの監査機能を追加・変更するたびに4つの離れたディレクトリを同時に編集する必要が生じ、人間のメンテナーにとっても AI コーディングエージェントにとってもコンテキスト負荷が増大します。

これに対し `pni501` は、`src/pni/` を **8つの自己完結型・垂直ドメインパッケージ** として構成しています。トップレベルの `src/pni/__init__.py` はパッケージ識別定数（`LIB_NAME = "pni501"`、`LIB_VERSION = "0.2.0"`、`__version__`）のみを公開し、各サブシステムが自身のスキーマ・オーケストレーションモジュール・組み込みテンプレートを単一の境界ディレクトリ内に同居させています。

| パッケージ / モジュール | 主要 Python モジュール | 主なスキーマと責務 | 同梱の組み込みアセット |
| :--- | :--- | :--- | :--- |
| **`cli.py`** | `cli.py` | Typer ルート `app` + 7 サブアプリ（`rules`, `workflows`, `report`, `pentests`, `progress`, `cache`, `grammars`）およびルートコマンド（`init`, `instructions`, `validate-score`, `validate-migration-plan`, `validate-progress`, `validate-mermaid`, `version`, `--version` / `-V`） | Rich CLI ヘルプエピローグ & AI ブートストラップ案内 |
| **`_languages/`** | `registry.py`, `_grammar_assets.py` | **55 言語 / 57 Tree-sitter 文法**の単一信頼源（`LANGUAGE_REGISTRY`, `GRAMMAR_PROVIDERS`、Tier A 20・Tier B 20・Tier C 15 の 3 階層）。SHA-256 ピン留め付き Drawlib スタイルのオンデマンド GitHub Releases ABI3 ダウンローダ（`_cached_grammars` -> `~/.cache/pni501/grammars` フォールバック） | PyPI 文法バインディング `52` 種 + オンデマンド ABI3 リリース文法 `5` 種（`cobol`, `dockerfile`, `protobuf`, `r`, `vue`） |
| **`_workflows/`** | `base_model.py`, `state_db.py`, `manager.py`, `planner.py`, `mermaid_validator.py`, `provenance.py`, `baseline.py`, `_projection.py`, `engine.py`, `_rollup_engine.py`, `_migration_engine.py`, `_progress_engine.py`, `aggregator.py`, `adhoc.py`, `inspector.py` | Workflow v2 条件付き DAG エンジン（`needs`, `when`, `fact_views`）、Phase 0 軽量偵察と検証済み Mermaid DAG 計画（`WorkflowExecutionPlan`）、`confirm_plan` ゲート、並列フロンティア（`get-actions`）、4 カテゴリ（`audit`, `rollup`, `migration`, `progress`）、`ExecutionDagSummary`、および誤検知トリアージ | **`112`** 個のスターターワークフロー YAML テンプレート（`55` 言語 + `generic` × 各 `full_audit.yaml` / `quick_check.yaml`） |
| **`_actions/`** | `base_model.py`, `manager.py`, `ai_actions.py`, `project_inspect.py`, `_extended_manifests.py`, `_repo_governance.py`、および `ast_analyze/`（`_cst.py`, `base/`, `declarative/`, `companion.py`, 6 専用スイート）, `runtime_check/`, `security_scan/`, `pentest/`, `migration_analyze/`, `progress_analyze/` | **`16` 個の正規 `PrimitiveType` ステップ**（決定論的自動解析器 `7` + 根拠検証付き AI/ゲート `9`）、ネイティブ **`tree-sitter>=0.25.0`** 1回パース CST ラッパー（`_cst.py`）、`ScoreResult`（7軸 + `triaged_adjustments` + `execution_dag`）、`ArchitectureRecord`、`MigrationPlanResult` | **`182`** 個の組み込み複合 YAML アクションテンプレート（`common/` 15 + 55 言語 × 各 3 + `generic/` 2） |
| **`_reporter/`** | `base_model.py`, `blueprint.py`, `rollup_blueprint.py`, `migration_blueprint.py`, `progress_blueprint.py`, `drawlib_guide.py`, `facts_sync.py`, `sarif.py`, `compiler.py` | フラットなレポートパス（**`pni_report_src -> pni_report`**）、`<src_dir>/_facts/` への自動証跡同期（`sync_workflow_facts_to_report`）、`*_summary.json` と SARIF 2.1.0 出力、4種ブループリント生成、および `drawlib.tools` 遅延コンパイル | 7章構成 Drawlib `doc` スキャフォールド、章リンター、および `_assets/{logo.png,logo_dark.png,favicon.png}` |
| **`_rules/`** | `base_model.py`, `manager.py` | `RuleInfo`、`_languages/registry.py` 由来の `SUPPORTED_LANGUAGES`、55 言語対応 `detect_active_language()`、および `<scope>/<name>` カスケード解決 | `common/`（16）、55 言語パック、`generic/` にわたる **`356`** 個の組み込み Markdown ルール |
| **`_pentests/`** | `manager.py`, `surface_codegen.py` | ターゲット別の `pytest + httpx` Web ペネトレーションテストを `.pni/pentests/<target>/` に生成・検証し、`AstFacts.api_endpoints` から `test_target_surface.py` を自動生成 | プローブテンプレート `2` 種: `conftest.py.tmpl`, `test_baseline_http.py.tmpl` |
| **`_dockerfiles/`** | `manager.py` | `.pni/dockerfiles/_templates/` オーバーライドまたは組み込みコンテナハーネスを解決し、分離 `.dockerignore` とともに `.pni/dockerfiles/` に展開（`prune_pni_container_artifacts()` も提供） | **35 言語**（Tier A `20/20` + Linux ネイティブ Tier B `15`）をカバーする **`40`** 個のコンテナハーネステンプレート |
| **`_instructions/` & `_config.py`** | `base_model.py`, `manager.py`, `_config.py` | `InstructionInfo`, `PniConfig`, `OptOutEntry`。`.pni/instructions.md` および `.pni/pni.toml` プロジェクトマニフェスト・`[[opt_out]]` 免除設定を解決 | `agent.md` およびデフォルト `.pni/pni.toml` テンプレート |
| **`_cache.py`** | `_cache.py` | 自己修復型 `.pni/cache/` 初期化（`ensure_cache_dir`, `ensure_cache_parent`）とワークスペース安全なパス解決（`normalize_target_subpath`） | 自動生成される `.pni/cache/.gitignore` (`*`) と `CACHEDIR.TAG` |

Python モジュールと静的アセットを同一パッケージ内に配置することで、開発時の editable インストールでも pure-Python（`py3-none-any`）wheel パッケージでも `BUILTIN_*_DIR = Path(__file__).resolve().parent` が常に決定論的に解決されます。

---

## 2. モジュールレベル依存関係階層・`_languages` SSOT・オンデマンド ABI3 文法

`src/pni/` 内のすべての import は厳密な **モジュールレベル有向非巡回グラフ（DAG）** を形成しており、`pni501` 自身の `src/pni/` ツリーに対する `ast_analyze` によって継続的に検証されています（`circular_dependencies = []`）。

1. **CLI オーケストレーター (`src/pni/cli.py`)**: ユーザー引数をパースし、Rich テーブルや Markdown パネルを整形して、`_workflows`、`_actions`、`_reporter`、`_rules`、`_pentests`、`_languages`、`_instructions`、`_config`、`_cache` へコマンドをディスパッチします。内部モジュールが `pni.cli` を逆インポートすることは一切ありません。
2. **Workflow v2 条件付き DAG オーケストレーション (`src/pni/_workflows/`)**:
   - `planner.py` と `mermaid_validator.py` が Phase 0 軽量偵察（`pni workflows plan <id>`）、`when:` 条件ガードの安全な AST 評価、および 2 層 Mermaid 検証（Layer 1 純 Python 静的チェック + Layer 2 `--browser` Playwright `mermaid.parse()`）を担います。
   - `engine.py`、`_rollup_engine.py`、`_migration_engine.py`、`_progress_engine.py` が SQLite 永続化（`state_db.py`）、Pre-Flight 前提条件ゲート、並列決定論的フロンティア実行、ステップ別 `fact_views` 射影（`_projection.py`）、パスグラウンディング検証、実行済み DAG 来歴（`provenance.py`）、および `aggregator.py` による 7 軸スコア統合・誤検知トリアージ（`finding_adjustments`）を統括します。詳細は [ステートフル Pull-Push エンジン](stateful_engine.md) を参照してください。
   - `adhoc.py`（`pni workflows run-action` / `run-step`）は SQLite に一切書き込まず単一アクションをインメモリ実行し、`inspector.py` は `pni workflows status` や `inspect-action` を提供します。
3. **アクションサブシステムとフラットレポートコンパイラ (`_actions/`, `_reporter/`, `_pentests/`, `_dockerfiles/`)**:
   - `_actions/ast_analyze/_cst.py` は従来の `ast-grep-py` を **ネイティブ `tree-sitter>=0.25.0` 1回パース CST ラッパー**（`CstNode` + 遅延1パス `TreeCursor` 種別インデックス）へ置き換え、6つの専用スイート（`python/`, `java/`, `php/`, `go/`, `ts_js/`）、49の宣言的文法プロファイル（`declarative/`）、および 15 の Tier C コンパニオン DSL スキャナ（`companion.py`）を支えています。
   - `_reporter/facts_sync.py` が構造化証跡（`plan.json`, `facts.json`, `architecture.json`, `blueprint.json`）をフラットな `<src_dir>/_facts/`（デフォルト `pni_report_src/_facts/`）へ自動同期し、`_reporter/compiler.py` は `importlib.import_module("drawlib.tools")` を **遅延ロード** してフラットな `pni_report_src -> pni_report` をコンパイルします。
4. **兄弟依存ゼロの基盤パッケージ (`_languages/`, `_rules/`, `_instructions/`, `_cache.py`)**:
   - **`_languages/registry.py`** は **55 言語の `LanguageSpec`** と **57 個の `GrammarProviderSpec`**（`php`/`php_only` や `typescript`/`tsx` 等のデュアル文法を含む）を単一信頼源（SSOT）として定義します。
   - **`_languages/_grammar_assets.py`** は、3 OS 向けの PyPI wheel が提供されていない MIT ライセンスの 5 文法（**COBOL、Dockerfile、Protocol Buffers、R、Vue**）を、GitHub Releases（`grammars-v0.2.0`）から **SHA-256 ピン留め検証済み**の ABI3 バイナリとしてオンデマンド取得することで、`pni501` 本体を軽量な pure-Python wheel に保ちます。スレッドロックと `fcntl` ファイルロックの下で書き込み可能なキャッシュ先を `PNI_GRAMMAR_CACHE_DIR` -> パッケージ内 `src/pni/_cached_grammars` -> OS ユーザーキャッシュ（`~/.cache/pni501/grammars` または `%LOCALAPPDATA%\pni501\grammars`）-> `<tmp>/pni501_grammars` の順で自動フォールバックし、`pni grammars status` / `prefetch --all` / `clear` で管理できます。

---

## 3. 直交タクソノミー：普遍的アーキタイプ vs. 55言語・コンパニオンパック

静的解析ツールチェーンで陥りがちなアンチパターンは、アーキテクチャ・セキュリティ・運用ルールをプログラミング言語ごとに重複して書き直すことです。`pni501` では、ルール（`src/pni/_rules/`）と複合アクション（`src/pni/_actions/`）を 3 つの直交する層で分離しています。

1. **普遍的エンジニアリング標準 (`common/*` — 16 ルール・15 アクション)**: 実装言語に依存しない不変条件を規定します。レイヤー間の依存方向（`common/architecture`）、SIG 単位複雑度上限（`common/maintainability`）、OpenSSF ロックファイル・CI トークン衛生（`common/supply_chain`）、OWASP シークレット・インジェクション防御（`common/security`）、12-Factor ステートレス性（`common/twelve_factor`）、Google SRE I/O タイムアウト（`common/production_readiness`）、`clig.dev` CLI 人間工学（`common/cli_guidelines`）、公開ライブラリ API 契約（`common/library_hygiene`）、Diátaxis ドキュメント標準（`common/documentation`）、およびロールアップ・移行・進捗レポート規約が含まれます。
2. **3 階層 55 言語パック (`<lang>/*` — 55 言語 / 57 文法)**:
   - **Tier A — フルエンジニアリング監査 (20 言語)**: `python`, `java`, `php`, `go`, `typescript`, `javascript`, `csharp`, `rust`, `ruby`, `kotlin`, `swift`, `c`, `cpp`, `scala`, `dart`, `elixir`, `vue`, `perl`, `cobol`, `r` — フル AST 解析、組み込みコンテナハーネス Dockerfile、言語別 3 アクション、6 以上のルールを標準装備。
   - **Tier B — 静的監査 (20 言語)**: `bash`, `powershell`, `groovy`, `objc`, `lua`, `haskell`, `fsharp`, `ocaml`, `zig`, `julia`, `fortran`, `matlab`, `svelte`, `solidity`, `cuda`, `verilog`, `vhdl`, `ada`, `odin`, `commonlisp` — Tree-sitter 静的 AST 監査に対応し、うち 15 言語には Linux ネイティブコンテナハーネスも同梱。
   - **Tier C — コンパニオン DSL / IaC / スキーマ / 設定 (15 言語)**: `dockerfile`, `hcl`, `bicep`, `nix`, `make`, `starlark`, `protobuf`, `sql`, `html`, `css`, `scss`, `yaml`, `json`, `toml`, `xml` — アプリケーションコードと併せてポリグロット・コンパニオンとして自動スキャンされます（`companion.py`）。
3. **フレームワークオーバーレイ (`<lang>/frameworks/*`)**: `python/frameworks/fastapi`、`java/frameworks/spring_boot`、`php/frameworks/laravel`、`php/frameworks/wordpress` など、フレームワーク固有のライフサイクルや DI パターンを規定します。

```drawlib align=center code=fold file=scope_orthogonality_composition.png caption="3層ルール＆アクション合成：普遍的ガバナンス・ランタイムアーキタイプ・55言語＆コンパニオンパック（Tier A/B/C）"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import CardList, Panel
from drawlib.styles import Styles

setup(width=164, height=66, dpi=150)

panel = Panel(
    "Composable Audit Formula = Universal Core + Runtime Archetype + 55-Language / Companion Pack",
    header_variant="filled",
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=11.0),
)
panel.draw(xy=(3.0, 3.0), width=158.0, height=60.0)

layers = CardList(
    style=Styles.PrimaryNeutral.patch(shape_r=1.6),
    text_style=Styles.DarkBold.patch(text_size=11.0),
    description_style=Styles.Dark.patch(text_size=10.0),
    badge_shape="rounded_rect",
    badge_style=Styles.PrimaryFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=10.0),
    icon_style=Styles.WhiteBold,
    direction="horizontal",
    show_arrows=True,
    arrow_style=Styles.PrimaryBold,
    spacing=4.5,
)
layers.add(
    "Layer 1: Universal Core",
    "16 common/ rules & 15 actions\narchitecture, maintainability,\nsupply_chain, security, docs",
    icon=phosphor.shield_check,
)
layers.add(
    "Layer 2: Runtime Archetype",
    "Library -> library_hygiene\nCLI Tool -> cli_guidelines\nService -> twelve_factor +\nproduction_readiness",
    style=Styles.Neutral.patch(shape_r=1.6),
    badge_style=Styles.SecondaryFlat,
    icon=phosphor.cube,
)
layers.add(
    "Layer 3: 55 Langs & FW",
    "20 Tier A + 20 Tier B +\n15 Tier C Companion DSLs\n+ FastAPI, Spring Boot,\nLaravel, WordPress (356 rules)",
    style=Styles.SecondaryNeutral.patch(shape_r=1.6),
    badge_style=Styles.SuccessFlat,
    icon=phosphor.brackets_curly,
)
layers.draw(xy=(7.0, 8.0), width=150.0, height=45.0)
save()
```

---

## 4. `.pni/` ワークスペース構成・フラットレポートパス・3層カスケード解決

`pni init [--lang/-l <language_id>] [--force/-f]` を実行すると、`src/pni/cli.py` の `init_project()` が呼び出され、**登録済み 55 言語**（または `generic` フォールバック）に応じた透明性の高い `.pni/` 設定ディレクトリと自己修復型 `.pni/cache/` 階層を初期化します。レポート出力は従来のネスト構造を廃し、自動 `<src_dir>/_facts/` 同期を伴うフラットな **`pni_report_src -> pni_report`** レイアウトをデフォルトとしています。

```drawlib align=center code=fold file=cascade_resolution_layout.png caption=".pni/ ワークスペース・自己修復キャッシュ・フラットレポート階層と 3 層カスケード解決フロー (v0.2.0)"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import CardList, Panel, TreeNode
from drawlib.styles import Styles

setup(width=168, height=86, dpi=150)

left_panel = Panel(
    ".pni/ Workspace, Cache & Flat pni_report",
    header_variant="filled",
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=11.0),
)
left_panel.draw(xy=(3.0, 3.0), width=82.0, height=80.0)

root = TreeNode(
    "Workspace (.pni/ + Flat Report Output)",
    text_style=Styles.PrimaryBold.patch(text_size=10.5),
    line_style=Styles.DarkBold,
    line_horizontal_margin=2.0,
    line_horizontal_length=2.2,
    line_vertical_margin=4.7,
)
root.add(".pni/pni.toml & instructions.md", text_style=Styles.DarkBold.patch(text_size=10.0))
root.add(".pni/rules/{common,<lang>}/  (356 built-in)", text_style=Styles.DarkBold.patch(text_size=10.0))
root.add(".pni/actions/*.yaml  (182 built-in templates)", text_style=Styles.DarkBold.patch(text_size=10.0))
root.add(".pni/workflows/*.yaml  (v2 DAG: needs/when)", text_style=Styles.DarkBold.patch(text_size=10.0))
root.add(".pni/dockerfiles/ (40) & pentests/<target>/", text_style=Styles.DarkBold.patch(text_size=10.0))
cache_dir = root.add(
    ".pni/cache/  (.gitignore: '*' + CACHEDIR.TAG)",
    text_style=Styles.SecondaryBold.patch(text_size=10.0),
)
cache_dir.add("workflow_state.db & trivy-cache/", text_style=Styles.Dark.patch(text_size=10.0))
cache_dir.add("<wf>/  (plan, facts, arch, logs)", text_style=Styles.Dark.patch(text_size=10.0))
rep_dir = root.add(
    "pni_report_src/ -> pni_report/  (Flat Layout)",
    text_style=Styles.SuccessBold.patch(text_size=10.0),
)
rep_dir.add("_facts/ (synced JSONs) & PDF/SARIF/Score", text_style=Styles.Dark.patch(text_size=10.0))
root.draw(xy=(6.0, 71.5))

cascade_cards = CardList(
    style=Styles.PrimaryNeutral.patch(shape_r=1.8),
    text_style=Styles.DarkBold.patch(text_size=11.0),
    description_style=Styles.Dark.patch(text_size=10.0),
    badge_shape="circle",
    badge_style=Styles.PrimaryFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=10.5),
    icon_style=Styles.WhiteBold,
    direction="vertical",
    spacing=3.8,
    show_arrows=True,
    arrow_style=Styles.DarkBold,
)
cascade_cards.add(
    "1. Local .pni/ Override",
    "Checks .pni/{pni.toml, instructions.md, rules/,\nactions/, dockerfiles/_templates/} first.",
    icon=phosphor.folder_open,
)
cascade_cards.add(
    "2. 55-Language Scope (<lang>/)",
    "_languages/registry.py resolves built-in Tier A,\nTier B, or Tier C packs (3 actions, 6+ rules).",
    style=Styles.Neutral.patch(shape_r=1.8),
    icon=phosphor.code,
)
cascade_cards.add(
    "3. Universal Fallback (common/)",
    "Falls back to 16 common/ rules, 15 universal\ncomposite actions, and generic/ templates.",
    style=Styles.SecondaryNeutral.patch(shape_r=1.8),
    badge_style=Styles.SecondaryBold,
    icon=phosphor.globe,
)
cascade_cards.draw(xy=(89.0, 3.0), width=76.0, height=80.0)
save()
```

### 自己修復型キャッシュ・フラットレポート・ターゲット別ハーネス

ホストプロジェクトのルート `.gitignore` を直接書き換える代わりに、`src/pni/_cache.py`（`ensure_cache_dir()` および `ensure_cache_parent()`）は `.pni/cache/` を **自己修復型（Self-Healing）** として管理し、`src/pni/_reporter/facts_sync.py` がポータブルな構造化証跡をレポートソース配下へ自動同期します。

- **Git およびバックアップからの自動除外**: `.pni/cache/` への書き込みが行われるたびに、`.pni/cache/.gitignore`（`*`）と標準 `CACHEDIR.TAG` シグネチャ（`8a477f597d28d172789f06886806bc55`）の存在が自動的に保証されます。SQLite データベース、Trivy 脆弱性 DB キャッシュ（`trivy-cache/`）、JUnit XML、コンテナログが Git ステータスに混入しません。
- **ワークフロー単位で分離された一時状態 (`.pni/cache/<workflow_id>/`)**: 各ワークフローは Phase 0 実行計画を `plan.json`、集約スナップショットを `facts.json`、グラウンディング検証済みの 3 側面アーキテクチャモデルを `architecture.json` に書き出し、各ステージの生ログを `runtime/`、`security/`、`pentest/` に格納します。
- **フラットレポートパス (`pni_report_src -> pni_report`) と自動 `_facts/` 同期**: 従来の `reports_src/<target>_src -> reports/` 階層に代わり、v0.2.0 ではフラットな `pni_report_src/` から `pni_report/` へ直接コンパイルします（`pni_report/<target>_score.json`、`pni_report/<target>_summary.json`、`pni_report/<target>_findings.sarif.json`、`pni_report/<target>.pdf` を出力）。`write_drawlib_report` を含むワークフローでは、`sync_workflow_facts_to_report()` が構造化 JSON 証跡（`plan.json`, `facts.json`, `architecture.json`, `blueprint.json`）を `pni_report_src/_facts/` へ自動コピーするため、`.pni/cache/` 削除後もレポートの再ビルドが可能です。
- **パストラバーサル防止付きマルチターゲットハーネス (`.pni/dockerfiles/` & `.pni/pentests/`)**: `normalize_target_subpath()` が絶対パスや `..` トラバーサルを拒否しつつ、モノレポ内のサブターゲットを安全にマッピングします（例: `targets.root: services/order_api` -> `.pni/dockerfiles/services/order_api/Dockerfile` および `.pni/pentests/services/order_api/`）。

### 3層カスケードと55言語解決ルール

チームは `pni init` で生成された `.pni/` ファイル一式をそのままコミットして管理することも、未変更のファイルを削除してカスタマイズしたいオーバーライドファイルのみを残すことも可能です。

1. **アクティブ言語の自動検出 (`_rules/manager.py` + `_languages/registry.py`)**: `detect_active_language(project_root)` は登録済み全言語のマニフェスト（`pyproject.toml`, `pom.xml`/`build.gradle*`, `composer.json`, `go.mod`, `tsconfig.json`/`package.json` のほか `Cargo.toml`, `*.csproj`, `Gemfile`, `Package.swift`, `build.sbt`, `pubspec.yaml`, `mix.exs`, `*.tf` 等）を優先検査し、該当しない場合は 55 言語にわたる深さ制限付きソース拡張子ヒューリスティクスへフォールバックし、最終的に `"python"` をデフォルトとします。詳細は [対応 55 言語マトリクス](../05_languages_and_reference/supported_languages.md) を参照してください。
2. **エンジニアリングルール (`local > <lang> > common`)**: `list_rules()` は組み込みの `src/pni/_rules/`（`356` ファイル）とローカルの `.pni/rules/` から `("common", active_lang)`（`--all` 指定時は全 55 言語の `SUPPORTED_LANGUAGES`）の候補を統合し、`.pni/rules/<scope>/<name>.md`（`is_local=True`）を優先します。`get_rule_content()` はハイフンとアンダースコアを正規化した上で、完全一致 `<scope>/<name>` -> `<active_lang>/<name>` -> `common/<name>` -> 任意スコープ一致の 4 段階で解決します。
3. **複合アクション (`local > <lang> > common`)**: `load_composite_action()` は `.pni/actions/<id>.yaml`（または `.pni/actions/<scope>/<id>.yaml`）を最優先で解決し、次に組み込みの `<active_lang>/<id>.yaml`（55 言語または `generic/` へ自動ディスパッチ）、最後に `common/<id>.yaml`（汎用 15 アクション）へフォールバックします。全カタログは [アクションとプリミティブパイプライン](../03_workflows_and_actions/actions_pipeline.md) を参照してください。
4. **コンテナハーネス・文法・マニフェスト・エージェント指示書**: `resolve_template_dockerfile()` は `.pni/dockerfiles/_templates/<lang>/<tool>.dockerfile` を 35 言語・40 種の組み込み `src/pni/_dockerfiles/` より優先し、`_grammar_assets.py` が 5 種のオンデマンド ABI3 文法を管理します。`load_pni_config()` は `.pni/pni.toml` を読み込み、`get_instructions_info()` は `.pni/instructions.md` を `src/pni/_instructions/agent.md` より優先します。

```bash
# アクティブなルール、オンデマンド ABI3 文法状態、Phase 0 DAG 計画を確認
pni rules list --all
pni grammars status
pni workflows plan full_audit
```
