# リリースノート (Release Notes)

**Project Nemesis Index (`pni501`)** のリリース履歴、アーキテクチャの拡張、および各バージョンの主な新機能一覧です。

---

## Version 0.1.4

*Release Date: 2026/11/10*

バージョン `0.1.4` では、Drawlib PDF レポート向けの公式 PNI501 ブランドアセットと表紙ロゴ描画ヘルパー、ローカルキャッシュおよびコンテナイメージを一括削除する `pni cache clean` CLI サブコマンド、さらに **Go**・**TypeScript**・**JavaScript** の静的解析・ランタイムハーネス機能（モノレポのロックファイルスコープ解決、`.d.ts` 型定義の自動認識、IIFE / ES2022 `#private` クラス解析、Playwright Headless Chromium の自動プロビジョニングなど）の大幅な強化が導入されました。

### 1. 公式ブランドアセットとレポートコンパイラの強化 (`pni._reporter`)

- **公式ブランドアセットの同梱と `draw_pni_logo()` 表紙ヘルパー**:
  - `pni report init` 実行時、Audit・Migration・Progress の全ブループリントで `<src_dir>/<target>_src/_assets/` に公式ブランドアセット (`logo.png`, `logo_dark.png`, `favicon.png`) が自動コピーされるようになりました。
  - スキャフォールドされる `utils.py` に `draw_pni_logo(xy=(135.0, 48.0), width=9.0, *, dark=True)` ヘルパーが追加され、`00_cover.md` のダーク／ライト表紙に PNI501 公式エンブレムを簡潔に配置できます。
- **`ClassDiagram` / `ClassNode` に対する Drawlib リンターチェック**:
  - `lint_drawlib_chapters()` (`pni report check` および `pni report build`) が、`ClassDiagram` や `ClassNode` での `Styles.White` の使用（白背景に白文字となり視認不能になる問題）を自動検出し、`Styles.Neutral` を推奨する警告を出力するようになりました。
- **マルチポータル環境向けの相対リンク検証 (`--link-check-root`)**:
  - `pni report build` / `compile_report_project()` に `--link-check-root <dir>` (`link_check_root`) オプションを追加し、複数ターゲットの HTML ポータル配下にネストされたレポートから親ポータル (`../index.html`) への相対リンクをルートディレクトリ基準で検証できるようになりました。

### 2. CLI の機能追加 (`pni cache clean` と `--version`)

- **`pni cache clean` サブコマンド**:
  - ローカルの `.pni/cache/` ディレクトリの削除に加え、`--docker` 指定時に一時生成された `pni-harness-*`、`pni-proj-*`、`pni-sec-*`、`pni-pentest-*` コンテナイメージやダングリングレイヤー、ビルドキャッシュを一括パージする `pni cache clean [--docker] [--container-engine auto|docker|podman]` を追加しました。
  ```bash
  uv run pni cache clean --docker
  ```
- **ルート `--version` / `-V` フラグ**:
  - `pni version` サブコマンドに加え、`pni --version` (`-V`) フラグで即座にバージョン (`pni501 v0.1.4`) を確認できるようになりました。
- **ワークフロー実行時の自動 Supersede（置き換え）**:
  - `start_workflow_run()` のデフォルトが `supersede=True` となり、同一ワークフローの新しい実行を開始した際、未完了の古い実行レコードを自動的に `CANCELLED` (`superseded_by_<run_id>`) として整理するようになりました。

### 3. TypeScript / JavaScript 解析およびランタイムハーネスの強化

- **AST 静的解析の精度向上 (`ast_analyze/ts_js/`)**:
  - **バレル再エクスポート循環と実装循環の分離**: `index.ts` などのバレルファイルを経由する意図的な再エクスポート循環 (`type_checking_cycles`) を、実際のモジュール間の実装循環 (`circular_dependencies`) から分離して計上します。
  - **IIFE / UMD クロージャの展開と ES2022 `#private` クラス対応**: トップレベルの IIFE/UMD ファクトリ (`var lib = (() => { ... })()`) 内部の関数や、ES2022 の `private_field_definition` / `#private` メソッドを展開してシンボル数・ドキュメントカバレッジを正確に算出します。
  - **コンパニオン `.d.ts` 型定義の自動認識**: `package.json` の `"types"` / `"typings"` または同梱の `*.d.ts` ファイルを検出し、JavaScript パッケージの `has_type_marker = True` 判定および公開 `.d.ts` 型シグネチャの型安全性評価を自動適用します。
  - **型レベルテストとカスタムアサーションの認識**: `expectTypeOf<T>()`、`assertType<T>()`、`// @ts-expect-error`、`test/`・`tests/` 配下のサフィックスなしテストファイル（非テストヘルパーを除外）、`assert*` / `verify*` / `check*` ヘルパー関数、`web-test-runner.config.*` の外部 CDN スクリプト依存を正確に認識します。
- **Playwright ブラウザハーネスとカバレッジパーサーの拡充 (`runtime_check/`)**:
  - `typescript/node.dockerfile` および `javascript/node.dockerfile` に `@vitest/coverage-v8` をプリインストールし、`@playwright/test`、`playwright`、または `@vitest/browser` が検出された場合は **Playwright Headless Chromium** (`PLAYWRIGHT_BROWSERS_PATH=/ms-playwright`) と OS 共有ライブラリを自動プロビジョニングします。
  - `lcov.info` (`parse_lcov_info`)、`@web/test-runner` (WTR)、Mocha (`parse_node_test_output`) の出力パーサー、複数スイート実行時の Vitest カバレッジマージ (`--coverage.clean=false`)、およびモノレポのサブパッケージ単位の `tsc --noEmit -p <subpkg>/tsconfig.json` スコープ実行に対応しました。
- **モノレポのロックファイルとコンテナ脆弱性スコープの精緻化 (`security_scan/`)**:
  - `discover_non_core_packages()` が `pnpm-lock.yaml`、`package-lock.json`、`yarn.lock` のワークスペース構成を解析し（ゼロ依存ターゲットにおける docs/workspace パッケージの分離を含む）、コンテナ内のグローバルツールチェーンパス (`/usr/local/lib/node_modules` 等) を `harness_os` / `os_package` として分類します。

### 4. Go AST 解析の改善と非 root コンテナハーネス (`go`)

- **Go AST 解析の改善 (`ast_analyze/go/`)**:
  - `check_exception_hygiene()` で部分的に無視されたエラー戻り値 (`val, _ := ...`) を検出します。
  - `check_complexity()` で複数行の raw バッククォート文字列（SQL・HTML・テンプレート等）を関数 LOC 肥大化のペナルティから除外します。
  - `check_type_safety()` で `format string` 引数を伴う `fmt.Printf` スタイルの可変長引数 (`...any` / `...interface{}`) を weak-type ペナルティから除外します。
  - `check_test_quality()` で `t.Run` のメソッド値デリゲーションおよびヘルパー関数内のアサーションを認識します。
- **堅牢化された Go コンテナテンプレート (`go/go.dockerfile`)**:
  - Go `1.22` Bookworm イメージを下限 (`1.22`〜`1.24`) とし、非 root ユーザー `USER pni` (`UID 10001`) でのテスト実行と、ビルド時の `/go/cache` 事前ウォームアップによる `--network=none` オフライン実行の安定化を実現しました。
  - デフォルトの `.pni/pni.toml` の `include_gitignored` に `"go.sum"` を追加し、`exclude_patterns` に `"docs/**"` と `"docs_src/**"` を追加しました。

---

## Version 0.1.3

*Release Date: 2026/11/10*

バージョン `0.1.3` では、従来の 3 言語から **6 つのターゲット言語** へと対応範囲を拡大し、**Go (`go`)**・**TypeScript (`typescript`)**・**JavaScript (`javascript`)** 向けの Tree-sitter AST アナライザー、カスケードルール、オフライン Docker ハーネス、テスト／カバレッジパーサー、マイグレーション解析器を追加するとともに、**Java** および **PHP** の解析精度を強化しました。

### 1. Go・TypeScript・JavaScript のフルサポート（計 6 言語対応）

- **Tree-Sitter AST アナライザー（計 27 個の新規チェッカー）**:
  - `go`、`typescript`、`javascript` の各言語に 9 個ずつの決定論的 AST チェッカー（`complexity`, `type_safety`, `doc_coverage`, `architecture`, `code_hygiene`, `exception_hygiene`, `test_quality`, `security_patterns`, `resource_safety`）を実装しました。
- **ビルトイン言語ルールカスケード（計 15 個の新規ルールファイル）**:
  - `rules/go/`、`rules/typescript/`、`rules/javascript/` 配下に `coding_convention.md`、`architecture_design.md`、`test_strategy.md`、`security_policy.md`、`audit_rubric.md` を追加しました。
- **複合アクション・ワークフロー・オフライン Docker ハーネス**:
  - `go.audit_analyze`、`typescript.audit_analyze`、`javascript.audit_analyze` 複合アクション、`full_audit` / `quick_check` ワークフロー、および `go-cover`・`istanbul-summary` カバレッジパーサーを備えた Docker テンプレート (`go/go.dockerfile`, `typescript/node.dockerfile`, `javascript/node.dockerfile`) を追加しました。
- **マイグレーション解析器**:
  - Go、TypeScript、JavaScript 向けに外部依存タッチポイントスキャナー、公開 API コントラクト抽出器、AST コードモッド候補検出器を追加しました。

### 2. Java および PHP アナライザーの強化

- **Java (`java`)**:
  - JUnit 4 の `@Test(expected=...)`、AssertJ、Hamcrest、Spring `MockMvc` アサーションの認識、Javadoc コメントのメソッド LOC 除外、カスタム Maven ビルド引数のサポート、および `pom.xml` の `test` / `provided` / `optional` スコープの自動フィルタリングを追加しました。
- **PHP (`php`)**:
  - 無名クラスシンボルの整形、PSR-3 ロガー呼び出しと生の `error_log()` デバッグ出力の区別、および `composer.json` の PSR-4 マッピングからの対象ソースディレクトリ自動検出を追加しました。

---

## Version 0.1.2

*Release Date: 2026/11/08*

バージョン `0.1.2` では、`security_scan` における **4 段階の脆弱性スコープ分類**、Python AST アナライザーの精緻化、およびワークフロー状態管理コマンド (`rewind` と `cancel`) を導入しました。

### 1. 4 段階の脆弱性スコープ分類 (`security_scan`)

- **`dep_scopes.py` による依存関係スコープ自動分類**:
  - 開発・ドキュメント用依存関係やコンテナベースイメージ由来の誤検知ペナルティを排除するため、Trivy および OSV の検出結果を以下の 4 スコープに自動分類します。
    1. `runtime_core`: 本番ランタイムのコア依存パッケージ（スコア評価の主対象）。
    2. `dev_or_optional`: テスト・リンター・ドキュメント生成ツールやオプション依存。
    3. `os_package`: アプリケーションコンテナ内の Debian/Alpine OS パッケージ。
    4. `harness_os`: 監査用コンテナハーネス (`pni-sec-*` / `pni-harness-*`) の OS パッケージ。

### 2. ワークフローの巻き戻し・キャンセル CLI と Python AST の改善

- **ワークフロー状態リカバリ (`pni workflows rewind` & `cancel`)**:
  - 指定したアクションまでワークフローを巻き戻して後続アーティファクトをクリアする `pni workflows rewind <action_id>`（エイリアス `retry-action`）と、古い実行を整理する `pni workflows cancel` (`--superseded` / `--supersede`) を追加しました。
- **Python AST 解析の改善**:
  - `ast_analyze/python/` における `TYPE_CHECKING` 条件付きインポートの扱い、`@overload` / `@abstractmethod` スタブの除外、および docstring カバレッジ算出ロジックを改善しました。

---

## Version 0.1.1

*Release Date: 2026/11/06*

- **PyPI パッケージングおよびメタデータの改善**:
  - パッケージ分類情報、`pni` CLI エントリポイント、同梱ルール／ワークフローのパッケージデータ構成、およびリリース検証ワークフローを改善しました。

---

## Version 0.1.0

*Release Date: 2026/11/06*

AI オーケストレーション型ソフトウェアエンジニアリング監査・セキュリティ検証・マイグレーション計画・ビジュアルレポートフレームワーク **Project Nemesis Index (`pni501`)** の初回パブリックリリースです。

- **コアアーキテクチャ**:
  - 決定論的アクション実行と LLM 審査ゲートを統合したステートフルな **Pull-Push 型 SQLite ワークフローエンジン** (`.pni/state.db`)。
  - **3 層カスケードルールシステム** (`common/` → `<language>/` → `.pni/rules/`) と **2 層設定ローダー** (`.pni/pni.toml`)。
  - **Python**・**Java**・**PHP** 向けの決定論的アナライザー群 (`project_inspect`, `ast_analyze`, `run_check`, `security_scan`, `web_pentest`, `migration_analyze`, `progress_analyze`)。
  - **7 軸 `ScoreResult`**（100 点満点の重み付けルーブリックおよび `S`/`A`/`B`/`C`/`D` グレード判定）と **`MigrationPlanResult`**。
  - 7 章構成の 16:9 ベクター PDF および HTML スライドデッキを生成する **Drawlib ビジュアル PDF レポーター** (`pni report init`, `pni report check`, `pni report build`)。
