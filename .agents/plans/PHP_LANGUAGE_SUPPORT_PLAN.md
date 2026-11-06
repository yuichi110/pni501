# PHP 言語サポート（モダン Composer/Laravel 系 ＆ レガシー素PHP / WordPress 系 デュアル診断基盤）実装計画書

本ドキュメントは、`pni501` に第 3 の対応言語として **PHP (`lang="php"`)** を追加し、**「① Composer / PSR-4 / Laravel / Symfony を用いたモダン PHP アプリケーション」** から **「② `composer.json` すら存在しないレガシー素PHP（HTML・SQL・スーパーグローバル混在スクリプト）および WordPress プラグイン／テーマ」** までを一貫した 7 軸スコア・6 章構成 Drawlib レポートで精密診断するための詳細実装計画書です。

> **スコープ定義**:
> - **本計画の対象**:
>   1. **デュアルモード言語検出・構造検査 (`_rules/manager.py`, `project_inspect.py`)**: `composer.json` / `composer.lock` の解析に加え、マニフェスト無しの素PHP・`wp-config.php`・WordPress プラグインヘッダーの自動認識とレガシー度診断
>   2. **PHP AST 解析スイート (`ast_analyze/php/`)**: `ast-grep-py` 組み込みの `"php"` パーサー（追加 Python 依存ゼロ）による 8 種の基本チェッカー ＋ **PHP 特有の CWE 危険シンク（SQLi / XSS / LFI / `eval` / `unserialize` / 型ジャグリング `==`）＆ Attack Surface 抽出** ＋ **Laravel / WordPress フレームワーク専用チェッカー**
>   3. **コンテナ実行検証＆セキュリティスキャン (`runtime_check`, `_dockerfiles/php/`, `security_scan`)**: `composer.dockerfile` と `raw.dockerfile` の 2 系統ハーネス、`php -l` 全ファイル構文ゲート、`pcov` + PHPUnit カバレッジ（`clover.xml`）解析、アーキタイプ別スモーク検証、Trivy による `composer.lock` ＆ PHP ベースイメージ CVE 検査
>   4. **PHP ルール体系・複合アクション・標準ワークフロー (`_rules/php/`, `_actions/php/`, `_workflows/php/`)**
>   5. **3 種の対照的サンプルプロジェクト (`examples/php/*`) とワークフロー定義 (`.pni/workflows/php_*.yaml`)**
> - **対象 OS**: Linux / macOS（コンテナ実行部は既存の `runtime_check` / `security_scan` と同じく Docker / Podman 対応）

---

## 1. 背景・PHP エコシステムの二極化と 6 つの設計原則

### 1.1. なぜ PHP 診断では「二極化（Dual-Mode）」への対応が不可欠か
Python や Java と比較して、実務で監査対象となる PHP ソフトウェアには極端な二極化が存在します。

1. **モダン PHP 層（PHP 8.2〜8.4 + Composer + Laravel / Symfony）**:
   - `declare(strict_types=1);`、引数・戻り値型宣言、`readonly class`、Enum、PSR-4 オートロード、PHPUnit / Pest テストを備える。
   - 一方で Laravel 特有のアンチパターン（`$guarded = []` による Mass Assignment 脆弱性、`config/*.php` 以外での `env()` 直接呼び出し、Controller 直書きの `DB::raw()`、認可ミドルウェア漏れ）が頻発する。
2. **レガシー素PHP・WordPress 層（Composer 不使用 / PHP 5.x〜7.x 時代からの継ぎ足し / 素人実装）**:
   - `composer.json` が無く、`include` / `require_once` の相対パス連鎖とグローバル変数・`$_GET` / `$_POST` / `$_SESSION` の直接参照で動く。
   - 1 ファイル内に DB 接続・生 SQL 文字列連結（`CWE-89`）・ビジネスロジック・エスケープ無し HTML `echo`（`CWE-79`）・動的 `include $_GET['page']`（`CWE-98` LFI）が同居する「スパゲッティスクリプト」が多い。
   - WordPress プラグイン／テーマでは、`register_rest_route` の `'permission_callback' => '__return_true'`、`wp_ajax_nopriv_*` の未認証公開、`wp_verify_nonce()` / `current_user_can()` 欠如、`$wpdb->prepare()` 未使用による SQLi が実被害の大半を占める。

モダン前提のツール（Composer 必須・PSR-4 必須）では後者が解析不能になり、逆に単純な grep ツールでは前者のアーキテクチャ境界やフレームワーク固有リスクを評価できません。`pni501` はこの両極を **同一の評価パイプライン上でシームレスに扱える設計** とします。

### 1.2. 6 つの設計原則

1. **追加 Python 依存パッケージ「ゼロ」の高速 CST 解析**
   - 導入済みの `ast-grep-py` は標準で `tree-sitter-php`（`SgRoot(src, "php")`）を内包しており、`<?php ...` 単体ファイルも HTML 混在 PHP テンプレートもそのまま高速パースできることを確認済み。
   - `composer.json` / `composer.lock` は標準ライブラリ `json`、PHPUnit JUnit XML / Clover カバレッジ XML は既存のセキュア XML パーサー（`_safe_parse_xml`）で解析する。
2. **`composer` モードと `raw_php`（Composer 無し）モードのファーストクラス両立**
   - `composer.json` が無いリポジトリでもエラーや `unknown` 扱いにせず、`build_system="raw_php"`（または WordPress 検出時 `"wordpress_raw"`）として正式認識し、「パッケージ管理・ロックファイル欠如」自体を `ProjectFacts.tooling_modernization_issues` の構造化ファクトとして減点・改善提案に繋げる。
3. **Web 脆弱性の本丸（XSS `CWE-79`・ファイルインクルード `CWE-98`・型ジャグリング `CWE-697`）を AST 危険シンクへ拡張**
   - Python / Java 向けに構築した `SecuritySinkCategory` を拡張し、PHP で致命的となる反射型/出力時 XSS、動的 `include`/`require`（LFI/RFI）、パスワードやトークンに対する緩い比較 `==`（Type Juggling）を決定論的に検出する。
4. **Laravel・Symfony・WordPress・素PHP エントリスクリプトの 4 系統 Attack Surface 抽出**
   - ルーティング定義が無く `.php` ファイル自体が URL エンドポイントになる素PHP（`public/login.php` 等で `$_GET`/`$_POST` を読むスクリプト）や、WordPress の `wp_ajax_nopriv_*` / `register_rest_route` も `ApiEndpointFact` として統一抽出し、レポート第 6 章の Attack Surface テーブルに可視化する。
5. **テストゼロのレガシー PHP でも価値を出す 3 段階コンテナ検証 (`php -l` 構文ゲート ＋ PHPUnit/PCOV ＋ スモーク起動)**
   - 単体テストが 1 件も無い素PHP や WordPress プラグインでも、コンテナ内で全 `.php` ファイルに対する `php -l`（構文・廃止構文チェック）と `php -S` ビルトインサーバー（または WP スタブローダー）スモーク検証を実行し、「PHP 8.3 環境へ移行した際に致命的構文エラーで即死する箇所」を機械的に炙り出す。
6. **既存の 7 軸スコア・6 章レポート・キャッシュ基盤との 100% 互換**
   - `CategoryScores`（7 軸）、`HotspotModule`、`00_cover.md`〜`06_security_and_supply_chain.md` のレポートブループリントをそのまま活用し、Python / Java と完全に横並びで比較可能なスコアと PDF レポートを出力する。

---

## 2. 詳細設計 — 柱1: 言語自動判定と `project_inspect` の拡張

### 2.1. 言語自動判定 (`src/pni/_rules/manager.py`)
- `SUPPORTED_LANGUAGES` を `("python", "java", "php")` に拡張。
- `_MANIFEST_LANGUAGE_RULES` に以下を追加:
  - `"composer.json"` -> `"php"`
  - `"wp-config.php"` / `"wp-config-sample.php"` -> `"php"`
  - `"artisan"` -> `"php"`
  - `"phpunit.xml"` / `"phpunit.xml.dist"` -> `"php"`
- マニフェストが存在しない「素PHP」および「単一ディレクトリ型 WordPress プラグイン／テーマ」のため、`detect_active_language(project_root)` のフォールバック走査を拡張:
  - ルート直下、または `src/`・`app/`・`public/`・`includes/` 直下に `*.php` ファイルが存在する場合に `"php"` と判定する。

### 2.2. マニフェスト・ロックファイル・フレームワーク検査 (`src/pni/_actions/project_inspect.py`)

1. **除外ディレクトリとロックファイル定義の追加**:
   - `IGNORED_PATH_PARTS`（および `ast_analyze/models.py` の `IGNORED_DIR_NAMES`、`security_scan/trivy_runner.py` の除外対象外確認）に `"vendor"` を追加:
     - **重要**: `project_inspect` と `ast_analyze` では Composer の外部パッケージ群 `vendor/` を走査除外して純粋な自社コードのみを計測対象とする（ただし、素PHP プロジェクトで手動コピーされた `lib/` や `includes/` 内の `.php` は検出し、ベンダリング警告を出す）。
     - 一方、`security_scan`（Trivy `fs`）ではルート直下の `composer.lock` から全推移的依存の CVE を正確に検出する。
   - `LOCKFILE_CANDIDATES` に `"composer.lock"` を追加。

2. **`composer.json` / `composer.lock` パーサー (`_inspect_composer_json`)**:
   - `build_system = "composer"` を設定。
   - `require.php`（または `config.platform.php`）から要求 PHP バージョン制約を抽出し、**EOL バージョン（PHP `< 8.1`: `5.*`, `7.*`, `8.0.*`）** が許容されている場合は `tooling_modernization_issues` に警告を記録。
   - `require` / `require-dev` から宣言パッケージ一覧（`declared_dependencies`）を抽出し、`*`・`dev-master`・上限なし緩い制約を `unpinned_dependencies` に記録。
   - `autoload.psr-4` / `autoload.classmap` / `autoload.files` の有無を検査（`autoload.files` の多用や PSR-4 未定義はモダナイゼーション課題として記録）。

3. **Composer 無し（素PHP / WordPress）検査 (`_inspect_raw_php_project`)**:
   - `composer.json` が無く `.php` ファイル群が存在する場合、`build_system = "raw_php"` を設定。
   - WordPress シグナル検出:
     - `wp-config.php`、`style.css`（`Theme Name:` ヘッダー）、またはルート `*.php` 先頭コメントの `Plugin Name:` ヘッダーを検出し、`detected_frameworks` に `"wordpress"`（プラグインの場合はアーキタイプヒントも付与）を追加。
   - `tooling_modernization_issues` に以下を記録:
     - `composer.json` 不在（依存関係・オートローダ未管理）
     - `phpunit.xml` / `phpunit.xml.dist` 不在（自動テスト基盤欠如）

4. **PHP フレームワーク・ツール検出マップ**:
   - `laravel/framework` / `artisan` -> `"laravel"`
   - `symfony/framework-bundle` / `symfony/http-kernel` -> `"symfony"`
   - `slim/slim` -> `"slim"`
   - `cakephp/cakephp` -> `"cakephp"`
   - `codeigniter4/framework` -> `"codeigniter"`
   - `wordpress`（`johnpbloch/wordpress` / `wpackagist-*` / ヘッダー検出） -> `"wordpress"`
   - `phpunit/phpunit` -> `"phpunit"`, `pestphp/pest` -> `"pest"`
   - `phpstan/phpstan` / `vimeo/psalm` / `laravel/pint` / `friendsofphp/php-cs-fixer` -> 静的解析・フォーマッタ導入シグナルとして記録

---

## 3. 詳細設計 — 柱2: `ast_analyze/php/` フル解析スイート

`src/pni/_actions/ast_analyze/php/` パッケージを新設し、`runner.py` の `_SUITES["php"]` に `LanguageAnalyzerSuite(ast_grep_lang="php", source_extensions=(".php", ".phtml"), ...)` を登録します。

### 3.1. モジュール構成 (`src/pni/_actions/ast_analyze/php/`)

```text
src/pni/_actions/ast_analyze/php/
├── __init__.py          # Php*Checker クラス群のエクスポート
├── helpers.py           # PHP CST 共通ヘルパー（namespace/class/method/function 抽出、PHPDoc 取得、スーパーグローバル判定）
├── imports.py           # PhpImportChecker (BaseImportChecker)
├── quality.py           # PhpQualityChecker (BaseQualityChecker)
├── typing.py            # PhpTypingChecker (BaseTypingChecker)
├── docs.py              # PhpDocChecker (BaseDocChecker)
├── dependencies.py      # PhpDependencyChecker (BaseDependencyChecker)
├── testing.py           # PhpTestChecker (BaseTestChecker)
├── operational.py       # PhpOperationalChecker (BaseOperationalChecker)
├── security.py          # PhpSecurityChecker (BaseSecurityChecker)
└── frameworks.py        # LaravelFrameworkChecker, WordPressFrameworkChecker (BaseFrameworkChecker)
```

### 3.2. 各チェッカーの決定的抽出仕様

| チェッカー | モダン PHP (Composer / Laravel) での検査内容 | レガシー素PHP / WordPress での検査内容 |
| :--- | :--- | :--- |
| **`PhpImportChecker`** | `namespace` 宣言後の `use ...;` ブロックの辞書順ソート、グループ `use Foo\{Bar, Baz}` 整理、クラス/関数内部での遅延 `use`/動的ロード検出 | **`require` / `include` / `require_once` / `include_once` の乱用・条件分岐内遅延読み込み** を `late_imports` としてピンポイント検出 |
| **`PhpTypingChecker`** | ファイル先頭 `declare(strict_types=1);` の有無、関数・メソッドの引数型ヒント＆戻り値型ヒント率（マジックメソッド `__construct`, `__destruct` 等の戻り値除外考慮）、`mixed` 型の乱用（`weak_type_usages`）、`@phpstan-ignore-next-line` / `@psalm-suppress` の無制限抑制 | 型ヒントゼロの関数群による `type_safety_coverage_pct = 0.0%` と `declare(strict_types=1)` 欠如を定量化 |
| **`PhpDocChecker`** | 公開 `class` / `interface` / `trait` / `enum` / `function` / `public method` 直前の PHPDoc (`/** ... */`) 有無と、`@param $name` タグと実仮引数リストの乖離（`doc_signature_mismatches`） | 長大な手続き関数・クラスにおけるドキュメント欠如・空コメントの特定 |
| **`PhpQualityChecker`** | 関数・メソッド行数（`> 50`）、分岐数（`> 7`）、認知的複雑度（`> 15`）、過剰引数（`> 6`） | **① スーパーグローバル直接参照（`$_GET`, `$_POST`, `$_REQUEST`, `$_SESSION`, `$_COOKIE`, `$_FILES`, `$GLOBALS`）および `global $var` 文** を `global_state_usages` に記録<br>**② エラー握り潰し演算子 `@expr`（`error_suppression_expression`）、空 `catch`、ドメイン層での `die()`/`exit()`、HTML と PHP ロジックの過度な混在（1 ファイル内に SQL/ループと複数 `?>...<?php` ブロックが同居）** を `bug_risk_idioms` に記録 |
| **`PhpDependencyChecker`** | `use App\...` による内部名前空間グラフ構築と循環依存（Cycle）検出、`composer.json` の `autoload.psr-4` ＆ `require` と実コード `use Vendor\...` の突き合わせによる未使用依存・未宣言依存の特定、Controller -> Repository 直接参照等の境界違反 | `include` / `require_once` の相対パス解決による **ファイル間インクルード依存グラフと循環インクルード** の構築 |
| **`PhpTestChecker`** | PHPUnit（`extends TestCase`、`test*` メソッド、`#[Test]` 属性、`@test` アノテーション）および Pest（`test('...', fn() => ...)` / `it(...)`）の検出、`$this->assert*()` / `expect()` 無しのゼロアサーションテスト検出 | テストファイル不在時は `test_functions_count = 0`, `module_test_coverage_pct = 0.0%` を明確に出力 |
| **`PhpOperationalChecker`** | Guzzle (`new Client()`) / Laravel `Http::get()` / Symfony `HttpClient` のタイムアウト未指定、設定ファイル（`config/*.php`）外での `getenv()` / `$_ENV` 散在、構造化ロガー（PSR-3 `$logger->info` / `Log::info`）を使わない `var_dump()` / `print_r()` / `error_log()`、ハードコード API キー・パスワード | **`curl_init()` で `CURLOPT_TIMEOUT` 未設定、`file_get_contents('http://...')` での `stream_context_create` タイムアウト無し**、`define('DB_PASSWORD', '...')` や `$db_pass = '...'` の平文埋め込み、`echo` デバッグ出力の検出 |

### 3.3. `PhpSecurityChecker` — PHP 特有 CWE 危険シンクと Attack Surface 抽出

#### (A) `SecuritySinkCategory` の拡張 (`src/pni/_actions/ast_analyze/models.py`)
既存の 7 カテゴリに Web / PHP で不可欠な 3 カテゴリを追加し、計 10 カテゴリとします（既存レポート・集計コードは任意の文字列ラベルとして透過処理するため破壊的変更なし）：
- `"xss"` (`CWE-79`: Cross-Site Scripting)
- `"file_inclusion_or_traversal"` (`CWE-98` / `CWE-22`: Local/Remote File Inclusion & Path Traversal)
- `"loose_comparison_or_auth"` (`CWE-697` / `CWE-287`: PHP Type Juggling / Mass Variable Extraction)

#### (B) `find_dangerous_sinks` で検出する PHP CWE シンク一覧

| カテゴリ (`SecuritySinkCategory`) | CWE | 検出対象 AST パターン（決定的ルール） | 深刻度 |
| :--- | :--- | :--- | :---: |
| `sql_injection` | `CWE-89` | - `$pdo->query(...)` / `$pdo->exec(...)` / `mysqli_query(...)` / レガシー `mysql_query(...)` に変数補間文字列（`"SELECT ... $id"`）または文字列連結（`.`）を渡している箇所<br>- Laravel `DB::raw(...)` / `whereRaw(...)` / `selectRaw(...)` / `orderByRaw(...)` への変数連結・補間<br>- WordPress `$wpdb->query(...)` / `$wpdb->get_results(...)` / `$wpdb->get_row(...)` / `$wpdb->get_var(...)` で `$wpdb->prepare(...)` を介さず変数を埋め込んでいる箇所 | `high` |
| `xss` | `CWE-79` | - `echo` / `print` / 短縮出力タグ `<?= ... ?>` で `$_GET` / `$_POST` / `$_REQUEST` / `$_COOKIE` / `$_SERVER['PHP_SELF']` 等を `htmlspecialchars(..., ENT_QUOTES)` や `esc_html()` / `esc_attr()` 無しに直接出力している箇所<br>- Blade テンプレート構文または PHP 出力における非エスケープ出力 | `high` |
| `command_injection` | `CWE-78` | - `system(...)`, `exec(...)`, `shell_exec(...)`, `passthru(...)`, `popen(...)`, `proc_open(...)`, およびバッククォート実行演算子 `` `...` ``（`shell_command_expression`） | `high` |
| `code_execution` | `CWE-94` | - `eval(...)`, `assert($str)`（文字列評価）, `create_function(...)`（廃止済みの動的関数生成）, `preg_replace('/.../e', ...)` 修飾子 | `high` |
| `file_inclusion_or_traversal` | `CWE-98` / `CWE-22` | - 変数やスーパーグローバルを伴う動的 `include $x` / `require $_GET[...]` / `include_once`（`__DIR__ . '/fixed.php'` のような定数連結のみの場合は除外し、変数混入時のみ検出）<br>- `file_get_contents` / `readfile` / `unlink` / `move_uploaded_file` へのスーパーグローバル直接渡し | `high` |
| `unsafe_deserialization` | `CWE-502` | - `unserialize(...)` の呼び出しで第 2 引数 `['allowed_classes' => false]` が明示されていない箇所 | `high` |
| `weak_cryptography` | `CWE-327` / `CWE-338` | - `md5(...)` / `sha1(...)`（特にパスワード・トークン変数への適用、`password_hash()` 未使用）、暗号用途での非暗号論的乱数 `rand()` / `mt_rand()` / `uniqid()` | `medium`〜`high` |
| `insecure_transport` | `CWE-295` | - `curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false)` / `CURLOPT_SSL_VERIFYHOST => 0`、Guzzle `['verify' => false]`、Laravel `Http::withoutVerifying()` | `high` |
| `loose_comparison_or_auth` | `CWE-697` / `CWE-621` | - `$password`, `$token`, `$hash`, `$hmac`, `$secret`, `$api_key` 等の名称を含む式に対する緩い等価比較 `==` / `!=`（PHP マジックハッシュ `0e...` による認証バイパス、`hash_equals()` または `===` 必須）<br>- グローバル名前空間を汚染する `extract($_REQUEST / $_POST / $_GET)` および第 2 引数無しの `parse_str(...)` | `high` |
| `permissive_cors_or_debug` | `CWE-489` / `CWE-942` | - `ini_set('display_errors', '1')`、本番コード内の `phpinfo()`、`header('Access-Control-Allow-Origin: *')` | `medium` |

#### (C) `find_api_endpoints` による 4 系統の Attack Surface 抽出

1. **Laravel ルーティング (`routes/*.php`, Controller)**:
   - `Route::get('/users/{id}', [UserController::class, 'show'])` / `Route::post(...)` / `Route::any(...)` / `Route::apiResource(...)` を抽出。
   - チェーンまたは親 `Route::middleware(['auth:sanctum', 'can:...'])` グループから `has_auth_hint` と `auth_mechanisms` を判定。
2. **Symfony / PHP 8 Attribute ルーティング**:
   - メソッド・クラスの `#[Route('/api/orders', methods: ['POST'])]` 属性と `#[IsGranted('ROLE_ADMIN')]` 属性から抽出。
3. **WordPress REST API ＆ Admin-AJAX エンドポイント**:
   - `register_rest_route('myplugin/v1', '/items', ['methods' => 'POST', 'callback' => ..., 'permission_callback' => ...])` を抽出し、**`'permission_callback' => '__return_true'` または未指定の場合は `has_auth_hint = False`（未認証公開 API）**、`current_user_can` 等を含むコールバックの場合は `has_auth_hint = True` と記録！
   - `add_action('wp_ajax_nopriv_<action>', $handler)` を `POST /wp-admin/admin-ajax.php?action=<action>`（`has_auth_hint = False`, 未認証公開）として抽出、`add_action('wp_ajax_<action>', $handler)` を認証済みエンドポイント候補として抽出。
4. **レガシー素PHP エントリスクリプト**:
   - クラス定義のみのファイルではなく、トップレベル実行コードで `$_GET` / `$_POST` / `$_REQUEST` / `$_FILES` / `php://input` を直接読み取っている `.php` スクリプト（例: `login.php`, `admin/delete_user.php`）を `ANY /login.php` として抽出。ファイル内で `$_SESSION['user_id']` チェック等のガード節が見当たらない場合は `has_auth_hint = False` として可視化する。

### 3.4. フレームワーク専用チェッカー (`src/pni/_actions/ast_analyze/php/frameworks.py`)

1. **`LaravelFrameworkChecker` (`framework_name = "laravel"`)**:
   - **Eloquent Mass Assignment 無防備**: Model クラスでの `protected $guarded = [];` 定義（`$fillable` 明示を推奨）。
   - **Config キャッシュ破壊**: `config/*.php` 以外のファイル（`app/` や `routes/`）での `env('...')` 直接呼び出し（本番 `php artisan config:cache` 時に `null` になる定番バグ）。
   - **Fat Controller / クエリ直書き**: `Controller` クラス内での `DB::table(...)` 直接構築や `Request::all()` の無検証一括渡し。
   - **モダナイゼーションヒント**: レガシーな配列属性定義（`$casts = [...]` メソッド化前や古い Accessor `getFooAttribute`）や PHP 8 コンストラクタプロモーション活用余地。

2. **`WordPressFrameworkChecker` (`framework_name = "wordpress"`)**:
   - **CSRF Nonce 検証欠如**: `$_POST` を処理するフック関数（`admin_post_*`, `wp_ajax_*`, `save_post` 等）内で `wp_verify_nonce()` または `check_admin_referer()` / `check_ajax_referer()` が呼ばれていない箇所。
   - **認可（Capability）チェック欠如**: 更新・削除処理を行うフック内で `current_user_can('...')` が確認されていない箇所。
   - **未サニタイズ入力取得**: `$_POST[...]` / `$_GET[...]` を `sanitize_text_field()` / `absint()` / `wp_unslash()` 無しに変数代入している箇所。
   - **アセット直接出力**: `wp_enqueue_script()` / `wp_enqueue_style()` を使わず `<script src="...">` を直接 `echo` している箇所。
   - **ABSPATH 直接アクセス防止ガード欠如**: プラグイン PHP ファイル先頭に `if (!defined('ABSPATH')) { exit; }` ガードが無いファイル（直接 URL 叩きによる情報漏洩・エラー誘発リスク）。

---

## 4. 詳細設計 — 柱3: コンテナ実行検証 (`runtime_check`) ＆ セキュリティスキャン (`security_scan`)

### 4.1. PHP 用ビルトイン Dockerfile テンプレート 2 種 (`src/pni/_dockerfiles/php/`)

[`src/pni/_dockerfiles/manager.py`](../../src/pni/_dockerfiles/manager.py) の `_FALLBACK_TOOL_BY_LANG` に `"php": "composer"` を追加し、プロジェクトの `build_system` に応じて以下の 2 テンプレートを自動選択します。

1. **`src/pni/_dockerfiles/php/composer.dockerfile`**（Composer / Laravel / Symfony / PSR-4 プロジェクト用）:
   - ベースイメージ: `php:${PHP_VERSION}-cli-bookworm`（デフォルト `8.3`、`composer.json` の `require.php` に応じて `8.1`, `8.2`, `8.3`, `8.4` を自動選択。もし `require.php` が `^7.4` 等の EOL 指定であっても、まずサポート対象の `8.1` または対象自身の `Dockerfile` を優先利用しつつ、互換性破綻有無を Stage 2 `php -l` で実証する）。
   - 軽量カバレッジ拡張 **`pcov`**（Xdebug より 5〜10 倍高速）、`zip` / `unzip`、`pdo_sqlite`、公式 `composer:2` バイナリ、およびプロジェクト側に `phpunit/phpunit` が未導入でもテスト実行可能なフォールバック `phpunit` PHAR を同梱。
   - ステージ構成: `composer install --no-interaction --no-progress --prefer-dist` をキャッシュ効率良く実行し、非特権ユーザーで動作。

2. **`src/pni/_dockerfiles/php/raw.dockerfile`**（`composer.json` 無しの素PHP・WordPress プラグイン用）:
   - ベースイメージ: `php:${PHP_VERSION}-cli-bookworm` + `pcov` + `mysqli` / `pdo_sqlite` + スタンドアロン `phpunit`。
   - `composer install` をスキップし、そのままソースツリーをコピーして Stage 2 の全ファイル `php -l` 構文検査と Stage 3 の起動スモークを実行できる超軽量ハーネス。

3. **`.dockerignore` デフォルト (`_DEFAULT_DOCKERIGNORE_CONTENT`)**:
   - `vendor/` を追加し、ホスト側の汚れた `vendor/` がコンテナへ混入するのを防ぎクリーンビルドを保証する。

### 4.2. `runtime_check` 3 ステージの PHP 対応 (`selector.py`, `parsers.py`, `smoke.py`, `runner.py`)

1. **Stage 1 (Build & Dependency Resolution)**:
   - 対象プロジェクトに `Dockerfile`（例: レガシーな `FROM php:7.4-apache` 等）が存在する場合はまずそれを検証対象として認識しつつ、テストハーネス実行には `.pni/cache/dockerfiles/<root>/Dockerfile` を用いて依存解決（`composer install`）の再現性を検証。

2. **Stage 2 (Offline Lint Gate & Unit Test + Coverage — `--network=none`)**:
   - **Step 2A — 全 PHP ファイル構文ゲート (`php -l`)**:
     - テストの有無に関わらず、対象ソース内の全 `.php` / `.phtml` に対して `php -l` を並列実行。PHP 8 系で削除された古い構文（例: `each()`, 波括弧オフセット `$str{0}`, 未定義定数構文エラー等）があれば即座に検出し `RuntimeFacts` のログ・失敗詳細へ記録！
   - **Step 2B — PHPUnit / Pest オフライン実行 + Clover カバレッジ抽出**:
     - `vendor/bin/pest` または `vendor/bin/phpunit`（無ければグローバル `phpunit`）が存在し、`tests/` または `*Test.php` が存在する場合に `-d pcov.enabled=1 --log-junit /tmp/pni-junit.xml --coverage-clover /tmp/pni-clover.xml` を `--network=none` で実行。
     - `parsers.py` に **`parse_clover_xml(xml_path)`** を新設:
       - Clover XML の `<project><metrics statements="..." coveredstatements="..." conditionals="..." coveredconditionals="..."/>` および各 `<file name="...">` 要素を既存の `_safe_parse_xml` で安全にパースし、`line_coverage_pct`・`branch_coverage_pct`・`lowest_covered_modules`（ワースト 10 ファイル）を Python / Java と全く同じ `CoverageResult` 型へ正規化する。

3. **Stage 3 (Archetype-Aware Smoke Verification)**:
   - **`library`** (`composer.json` の `"type": "library"` 等): `php -r "require 'vendor/autoload.php'; echo 'autoload-ok';"` で PSR-4 オートロード整合性を検証。
   - **`cli`** (`artisan` または `composer.json` の `"bin"` 存在時): `php artisan --version` または `<bin> --help` の終了コード `0` を検証。
   - **`web_api` / `raw_php`** (`public/index.php` またはルート `index.php` 存在時): コンテナ内で PHP 組み込みサーバー `php -S 127.0.0.1:18080 -t <docroot>` をバックグラウンド起動し、`/up`（Laravel 11 標準ヘルスチェック）、`/health`、または `/` へ HTTP リクエストを投げて Fatal Error / 500 にならず応答することを検証。
   - **`wordpress_plugin`**（WordPress プラグインヘッダー検出時）: コンテナ内で最小限の WordPress 関数スタブ（`ABSPATH`, `add_action`, `add_filter`, `register_activation_hook`, `register_rest_route` 等を定義した 30 行の軽量ブートストラップ）を読み込んだ上でメインプラグイン `.php` を `require_once` し、PHP Fatal Error 無くフック登録が完了することをスモーク検証する。

### 4.3. `security_scan` (Trivy) の PHP 統合検証
- 既存の `src/pni/_actions/security_scan/` はすでに **変更ほぼゼロで PHP に対応可能な設計** になっています:
  - [`parsers.py`](../../src/pni/_actions/security_scan/parsers.py) の `_OS_PKG_TYPES` 判定により、Trivy が `composer.lock` から検出する `Type="composer"`（`Class="lang-pkgs"`）の脆弱性は自動的に **`app_vuln_counts`**（アプリケーション依存 CVE）へ分類され、修正バージョン（`fixed_version`）まで抽出される。
  - 対象プロジェクトが古い `Dockerfile`（例: `FROM php:7.4-apache`、root 実行、`EXPOSE 80`）を持つ場合、Trivy `fs`（misconfig）が IaC 設定ミスを検出し、さらに `trivy image` が Debian/Alpine 層の古い OpenSSL / libcurl / PHP OS パッケージ CVE（`os_vuln_counts`）を網羅的に検出する。
- 追加調整として、`trivy_runner.py` のファイルシステムスキャン除外設定で不要なキャッシュディレクトリのみをスキップし、`composer.lock` とベンダリングされた古いライブラリを確実にスキャン対象に含めることを単体テストで保証します。

---

## 5. 詳細設計 — 柱4: PHP ルール体系・複合アクション・標準ワークフロー・CLI

### 5.1. PHP ベストプラクティス＆レガシー監査ルール (`src/pni/_rules/php/`)

Python / Java と対称な構成で以下 8 ファイルを整備します：

1. `src/pni/_rules/php/code_quality.md`:
   - PSR-12 準拠、名前空間・PSR-4 構造化、スーパーグローバル直接参照の禁止（Request オブジェクト抽象化）、`@` エラー抑制演算子やドメイン内 `die()`/`exit()` の排除、HTML と SQL/ビジネスロジックの分離。
2. `src/pni/_rules/php/typing.md`:
   - 全ファイルでの `declare(strict_types=1);` 必須化、引数・戻り値・プロパティ型宣言、`readonly class`・Backed Enum・Value Object の活用、`mixed` 抑制、PHPStan / Psalm レベル基準。
3. `src/pni/_rules/php/dependencies.md`:
   - `composer.json` + `composer.lock` による決定的依存管理、EOL PHP バージョン制約の排除、`include`/`require` 手動読み込みから PSR-4 オートロードへの移行、レイヤー間循環依存の禁止。
4. `src/pni/_rules/php/testing.md`:
   - PHPUnit 10/11 または Pest による自動テスト、`pcov` によるライン・ブランチカバレッジ基準（80% 目標）、外部 DB/HTTP のモック・インメモリ SQLite 分離。
5. `src/pni/_rules/php/modern_stack.md`:
   - PHP 8.2+ モダン機能（Constructor Property Promotion, `match` 式, Nullsafe `?->`, Attributes `#[...]`）、レガシー関数（`mysql_*`, `utf8_encode/decode`, `create_function`, `extract`）からの脱却、パスワードハッシュ（`password_hash` / `password_verify`）と厳密比較 `===` / `hash_equals()` の徹底。
6. `src/pni/_rules/php/frameworks/laravel.md`:
   - Eloquent `$fillable` 明示（`$guarded = []` 禁止）、FormRequest バリデーション、`config()` 経由の設定参照（`env()` 直呼び禁止）、Sanctum/Policy 認可、Eloquent バインディングによる `DB::raw` 回避。
7. `src/pni/_rules/php/frameworks/wordpress.md`:
   - WordPress Coding Standards & Plugin Security 黄金律：`ABSPATH` ガード、入力時の `wp_unslash()` + `sanitize_*()`、SQL の `$wpdb->prepare()` 必須化、状態変更時の `wp_verify_nonce()` + `current_user_can()` 二重チェック、REST API `permission_callback` 明示（`'__return_true'` 原則禁止）、出力時の遅延エスケープ（`esc_html`, `esc_attr`, `esc_url`, `wp_kses_post`）。
8. `src/pni/_rules/php/workflow_guide.md`:
   - AI エージェント向けの PHP リポジトリ構造判定ガイド（Composer/Laravel リポジトリ vs `public/` + ルート散在の素PHP vs WordPress `wp-content/plugins/*` の `targets.source` / `targets.tests` 設定パターン）。

（※ あわせて共通ルール `src/pni/_rules/common/security_vulnerability.md` にも PHP の CWE シンク例：`CWE-79` XSS, `CWE-98` LFI, `CWE-697` 型ジャグリング、`composer.lock` CVE 基準を追記します。）

### 5.2. PHP 複合アクション (`src/pni/_actions/php/`) と標準ワークフロー (`src/pni/_workflows/php/`)

- **複合アクション**:
  - `src/pni/_actions/php/repo_structure_audit.yaml`: `project_inspect` + `common/repo_hygiene`, `php/dependencies`, `php/modern_stack`
  - `src/pni/_actions/php/php_ast_audit.yaml`: `ast_analyze (lang: "php")` + `common/architecture`, `common/maintainability`, `common/security`, `common/security_vulnerability`, `php/code_quality`, `php/typing`, `php/frameworks/laravel`, `php/frameworks/wordpress`
  - `src/pni/_actions/php/php_test_audit.yaml`: `php/testing` に基づくテスト AST・アサーション密度評価
- **標準ワークフロー**:
  - `src/pni/_workflows/php/full_audit.yaml`: 全 8 ステップ（`repo_structure_audit` -> `php_ast_audit` -> `architecture_analysis` -> `php_test_audit` -> `container_runtime_audit` -> `security_vulnerability_audit` -> `emit_score` -> `write_drawlib_report`）
  - `src/pni/_workflows/php/quick_check.yaml`: コンテナ不要の高速静的監査（`repo_structure_audit` -> `php_ast_audit` -> `architecture_analysis` -> `php_test_audit` -> `emit_score`）
- **CLI 更新 (`src/pni/cli.py`)**:
  - `HELP_EPILOG` および `pni init --lang php` のヘルプ文言・バリデーションに `"php"` を追加。

---

## 6. サンプルプロジェクト案 (`examples/php/`) と期待診断結果

ユーザー様のご指摘通り、PHP の実態をリアルに実証するため、**「① モダンで堅牢な Composer / Laravel スタイル API」「② 素人が書いた緩いレガシー素PHP EC サイト」「③ 脆弱性だらけの WordPress カスタムプラグイン」** の **3 プロジェクト** を作成することを提案します。

### サンプル一覧と比較マトリクス

| サンプルパス | ワークフロー ID | 想定アーキタイプ / 特徴 | 仕込む代表的な品質・セキュリティ要素 | 想定総合スコア |
| :--- | :--- | :--- | :--- | :---: |
| **`examples/php/api_laravel_clean`** | `php_api_laravel_clean` | **モダン Composer + Laravel スタイル注文 API**<br>(`composer.json` + `composer.lock`, PHP 8.3, `declare(strict_types=1)`, PSR-4 `app/`, `routes/api.php`, PHPUnit `tests/`) | - Readonly DTO / Enum / Service レイヤー分離<br>- `Route::middleware('auth:sanctum')` 付きエンドポイント<br>- PDO / クエリビルダの完全プレースホルダバインド<br>- `password_hash` / `hash_equals`、HTTP タイムアウト明示<br>- 非 root・ピン留め `Dockerfile` ＋ PHPUnit テスト高カバレッジ | **85〜92 (A / S)** |
| **`examples/php/legacy_shop_messy`** | `php_legacy_shop_messy` | **Composer 無し「素PHP」レガシー EC 管理画面**<br>(`composer.json` 無し、`index.php`, `login.php`, `product.php`, `admin_export.php`, `includes/db.php`) | - **CWE-89 SQLi**: `"SELECT * FROM users WHERE user='" . $_POST['u'] . "'"`<br>- **CWE-79 XSS**: `echo "検索結果: " . $_GET['q'];`<br>- **CWE-98 LFI**: `include $_GET['page'] . ".php";`<br>- **CWE-78 OS Command Injection**: `shell_exec("zip -r backup.zip " . $_POST['dir'])`<br>- **CWE-502**: `unserialize($_COOKIE['cart'])`<br>- **CWE-327 & CWE-697**: `md5($pass) == $row['pw_hash']`（MD5 + `==` 型ジャグリング）<br>- `@` エラー握り潰し、平文 DB パスワード、`FROM php:7.4-apache` root 実行 `Dockerfile`、テスト 0 件 | **15〜24 (D)** |
| **`examples/php/wp_plugin_messy`** | `php_wp_plugin_messy` | **脆弱な WordPress 会員フォーム・分析プラグイン**<br>(`Plugin Name:` ヘッダー付き素PHPプラグイン、`member-portal.php`, `includes/ajax-handlers.php`, `includes/rest-api.php`) | - **未認証 REST API**: `register_rest_route('portal/v1', '/export', ['permission_callback' => '__return_true'])`<br>- **未認証 Admin-AJAX SQLi**: `add_action('wp_ajax_nopriv_search_members', ...)` 内で `$wpdb->get_results("SELECT * FROM {$wpdb->users} WHERE display_name LIKE '%{$_POST['term']}%'")`（`$wpdb->prepare` 無し）<br>- **CSRF & 権限漏れ**: 設定更新で `wp_verify_nonce()` と `current_user_can('manage_options')` 欠如<br>- **Stored/Reflected XSS**: 管理画面での未エスケープ `echo $_GET['tab']`、`ABSPATH` ガード欠如 | **18〜28 (D)** |

> **ポイント**: この 3 つが揃うことで、`reports/php/` 配下に生成される 3 冊の PDF レポート（`api_laravel_clean.pdf`, `legacy_shop_messy.pdf`, `wp_plugin_messy.pdf`）を見比べるだけで、`pni501` がモダンフレームワークの設計品質から素PHP・WordPress 特有の泥臭い脆弱性までを一網打尽にできることが一目で伝わります。

---

## 7. 段階的実装フェーズとテスト計画

承認いただいた後、以下の 5 フェーズで段階的に実装・検証を進めます（すべてのコードチェック・テスト実行は `./pcli` 経由で実施します）。

### Phase 1: 言語基盤・`project_inspect`・ルール＆テンプレート新設
- `src/pni/_rules/manager.py`、`src/pni/cli.py` の `"php"` 対応（`composer.json`, `wp-config.php`, `Plugin Name:`, 素PHP `*.php` 自動検出）。
- `src/pni/_actions/project_inspect.py` に `composer.json` / `composer.lock` 解析、PHP バージョン制約監査、WordPress / Laravel / Symfony 検出、素PHP モダナイゼーション課題抽出、`vendor/` 除外を実装。
- `src/pni/_rules/php/*.md`（8 ファイル）、`src/pni/_actions/php/*.yaml`（3 ファイル）、`src/pni/_workflows/php/*.yaml`（2 ファイル）を作成。

### Phase 2: `ast_analyze/php/` フル解析スイート＆ CWE / Attack Surface 実装
- `src/pni/_actions/ast_analyze/models.py` の `SecuritySinkCategory` に `"xss"`, `"file_inclusion_or_traversal"`, `"loose_comparison_or_auth"` を追加し、`IGNORED_DIR_NAMES` に `"vendor"` を追加。
- `src/pni/_actions/ast_analyze/php/` 配下の全チェッカー（`imports`, `typing`, `docs`, `quality`, `dependencies`, `testing`, `operational`, `security`, `frameworks`）を実装し、`runner.py` に `"php"` スイートを登録。

### Phase 3: コンテナ実行ハーネス (`_dockerfiles/php/`) ＆ `runtime_check` Clover カバレッジ統合
- `src/pni/_dockerfiles/php/{composer,raw}.dockerfile` を作成し、`_dockerfiles/manager.py` を拡張。
- `src/pni/_actions/runtime_check/{selector.py,parsers.py,smoke.py,runner.py}` に PHP ステージコマンド（`php -l` 構文ゲート、PHPUnit + `pcov`、`parse_clover_xml`、`artisan` / `php -S` / WordPress スタブスモーク検証）を実装。

### Phase 4: 単体テスト網羅・静的解析パス確認 (`./pcli`)
- `tests/pni/test_php_support.py`（および `test_ast_analyze_php.py`, `test_runtime_check_php.py`）を追加し、以下を網羅的に単体テスト：
  - Composer / 素PHP / WordPress それぞれの `detect_active_language` と `project_inspect`
  - 全 10 種の PHP CWE 危険シンク検出と、Laravel / Symfony / WordPress (`register_rest_route`, `wp_ajax_nopriv_*`) / 素PHP のエンドポイント＆認証ヒント抽出
  - Laravel (`$guarded = []`, `env()`) と WordPress (Nonce / Capability / `$wpdb->prepare` / `ABSPATH`) のフレームワーク検査
  - `parse_clover_xml` パーサーと PHP `runtime_check` コマンド組み立て
- `./pcli code-check all`（Ruff lint/format + Ty 型検査エラー 0 件）および `./pcli test all --parallel`（高カバレッジ維持）を確認。

### Phase 5: 3 種の PHP サンプルプロジェクト作成＆ E2E ワークフロー・PDF レポート生成
- `examples/php/{api_laravel_clean,legacy_shop_messy,wp_plugin_messy}` と `.pni/workflows/php_*.yaml` を作成。
- 実コンテナ（`runtime_check` + `security_scan` Trivy）を含む全 3 ワークフローを実行し、`reports/php/*.pdf`（A4 7 章構成レポート）を生成して検証する。

---

## 8. 実装着手前の確認事項

本プランの内容で進めてよろしいでしょうか？特に以下の 2 点についてご希望があればお知らせください（特になければ推奨案のまま実装を開始します）：

1. **サンプルプロジェクトのラインナップ（3 構成）**:
   - 提案の **3 本立て**（① `api_laravel_clean`：モダン Composer/Laravel 系クリーン例、② `legacy_shop_messy`：Composer 無し素PHP EC サイト問題例、③ `wp_plugin_messy`：脆弱な WordPress プラグイン問題例）でよろしいでしょうか？（もし WordPress のクリーン例なども追加したい場合は調整可能です）
2. **メインターゲットとするフレームワーク専用チェッカーの範囲**:
   - 初回実装では利用シェアと問題発生率が圧倒的に高い **Laravel** と **WordPress** の 2 大フレームワーク専用チェッカー（＋ Symfony 属性ルートの Attack Surface 抽出）を実装する方針としていますが、CakePHP や CodeIgniter 固有ルールも初回から厚めに含めたいご希望はありますでしょうか？
