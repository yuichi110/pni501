# 対応 6 言語マトリクス

`pni501` (`v0.1.4`) は、**Python・Java・PHP・Go・TypeScript・JavaScript の主要 6 言語**に対して、決定論的な静的解析（`ProjectFacts` および単一パス Tree-sitter `AstFacts`）、言語別エンジニアリングルール、隔離コンテナテスト・カバレッジハーネス（`.pni/dockerfiles/`）、および Trivy セキュリティスキャンを一貫したアーキテクチャで提供します。

```drawlib align=center code=fold file=six_languages_matrix_hero.png caption="対応 6 言語マトリクス：マニフェスト・Tree-sitter AST パーサー・テスト/カバレッジツールチェーン・コンテナハーネス"
from drawlib.canvas import save, setup
from drawlib.icons import code
from drawlib.smartarts import CardList, Panel
from drawlib.styles import Styles

setup(width=184, height=86, dpi=150)

left_panel = Panel(
    "1. Backend & Enterprise (Python / Java / PHP)",
    header_variant="filled",
    header_height=8.5,
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=11.2),
)
left_panel.draw(xy=(4.0, 4.0), width=85.5, height=78.0)

left_cards = CardList(
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
left_cards.add(
    "Python (python — 3.11 / 3.12 / 3.13)",
    "Manifest: pyproject.toml, uv.lock, poetry.lock\n"
    "AST/Rules: stdlib ast + ast-grep | 7 rules\n"
    "Harness: uv/poetry/pip -> pytest + coverage",
    badge_text="PY",
    icon=code.python,
)
left_cards.add(
    "Java (java — JDK 8 / 11 / 17 / 21 LTS)",
    "Manifest: pom.xml, build.gradle(.kts)\n"
    "AST/Rules: ast-grep (java) | 6 rules (Spring)\n"
    "Harness: maven/gradle -> JUnit 5 + JaCoCo",
    badge_text="JV",
    icon=code.java,
)
left_cards.add(
    "PHP (php — 8.1..8.4 & Raw PHP)",
    "Manifest: composer.json, artisan, wp-config\n"
    "AST/Rules: ast-grep (php) | 8 rules (Laravel/WP)\n"
    "Harness: composer/raw -> php -l + PHPUnit/PCOV",
    badge_text="PHP",
    icon=code.php,
)
left_cards.draw(xy=(6.5, 6.5), width=80.5, height=64.5)

right_panel = Panel(
    "2. Cloud-Native & Web (Go / TypeScript / JS)",
    header_variant="filled",
    header_height=8.5,
    style=Styles.PrimaryNeutral.patch(shape_r=2.0),
    header_style=Styles.SecondaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=11.2),
)
right_panel.draw(xy=(94.5, 4.0), width=85.5, height=78.0)

right_cards = CardList(
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
right_cards.add(
    "Go (go — 1.21 / 1.22 / 1.23 / 1.24)",
    "Manifest: go.mod, go.sum (*_test.go split)\n"
    "AST/Rules: ast-grep (go) | 5 rules (GoDoc/err)\n"
    "Harness: go.dockerfile -> go vet + coverprofile",
    badge_text="GO",
    icon=code.go,
)
right_cards.add(
    "TypeScript (typescript — Node 18 / 20 / 22)",
    "Manifest: package.json + tsconfig.json\n"
    "AST/Rules: ast-grep (ts/tsx) | 5 rules (strict)\n"
    "Harness: node.dockerfile -> Vitest/Jest + tsc",
    badge_text="TS",
    icon=code.typescript,
)
right_cards.add(
    "JavaScript (javascript — Node 18 / 20 / 22)",
    "Manifest: package.json + jsconfig.json\n"
    "AST/Rules: ast-grep (tsx) | 5 rules (JSDoc)\n"
    "Harness: node.dockerfile -> Vitest + node --check",
    badge_text="JS",
    icon=code.javascript,
)
right_cards.draw(xy=(97.0, 6.5), width=80.5, height=64.5)

save()
```

---

## 1. 6 言語のエンドツーエンド機能マトリクス

すべての対応言語は共通の `LanguageAnalyzerSuite` プロトコル（`src/pni/_actions/ast_analyze/runner.py`）および 4 ステージのコンテナ実行検証エンジン（`src/pni/_actions/runtime_check/runner.py`）に統合されており、言語ランタイムの違いを問わず正規化された `ProjectFacts`・`AstFacts`・`RuntimeFacts`・`SecurityScanFacts` スキーマを出力します。

| 評価軸・機能 | Python (`python`) | Java (`java`) | PHP (`php`) | Go (`go`) | TypeScript (`typescript`) | JavaScript (`javascript`) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **マニフェスト / ロックファイル** | `pyproject.toml`, `setup.py`, `requirements.txt`, `uv.lock`, `poetry.lock` | `pom.xml`, `build.gradle(.kts)`, `settings.gradle(.kts)`, `gradle.lockfile` | `composer.json`, `composer.lock`, `artisan`, `wp-config.php`, 素の `*.php` | `go.mod`, `go.sum`, `go.work` | `package.json`, `tsconfig.json`, `pnpm-lock.yaml`, `package-lock.json`, `yarn.lock` | `package.json`, `jsconfig.json`, `pnpm-lock.yaml`, `package-lock.json`, `yarn.lock` |
| **対象ソース拡張子** | `.py` | `.java` | `.php`, `.phtml` | `.go` (`*_test.go` を自動分離) | `.ts`, `.tsx` (`.d.ts` 除外・`*.test.ts` 自動分離) | `.js`, `.jsx`, `.mjs`, `.cjs` (同梱 `.d.ts` 型宣言を認識) |
| **AST パーサーエンジン** | Python 標準 `ast` + `ast-grep-py` (`python`) | `ast-grep-py` (`java`) | `ast-grep-py` (`php` + 混在 HTML プリプロセッサ) | `ast-grep-py` (`go`) | `ast-grep-py` (`typescript` / `tsx`) | `ast-grep-py` (`tsx`) |
| **言語別複合アクション** | `python_ast_audit`, `python_test_audit` | `java_ast_audit`, `java_test_audit` | `php_ast_audit`, `php_test_audit` | `go_ast_audit`, `go_test_audit` | `typescript_ast_audit`, `typescript_test_audit` | `javascript_ast_audit`, `javascript_test_audit` |
| **組み込みルール数** | `7` ファイル (`code_quality`, `typing`, `dependencies`, `modern_stack`, `testing`, `frameworks/fastapi`, `workflow_guide`) | `6` ファイル (`code_quality`, `typing`, `dependencies`, `testing`, `frameworks/spring_boot`, `workflow_guide`) | `8` ファイル (`code_quality`, `typing`, `dependencies`, `modern_stack`, `testing`, `frameworks/laravel`, `frameworks/wordpress`, `workflow_guide`) | `5` ファイル (`code_quality`, `typing`, `dependencies`, `testing`, `workflow_guide`) | `5` ファイル (`code_quality`, `typing`, `dependencies`, `testing`, `workflow_guide`) | `5` ファイル (`code_quality`, `typing`, `dependencies`, `testing`, `workflow_guide`) |
| **コンテナテンプレート** | `python/uv.dockerfile`, `poetry.dockerfile`, `pip.dockerfile` (`3.11`–`3.13`) | `java/maven.dockerfile`, `gradle.dockerfile` (Temurin `8`/`11`/`17`/`21`) | `php/composer.dockerfile`, `raw.dockerfile` (PHP CLI `8.1`–`8.4`) | `go/go.dockerfile` (Golang Bookworm `1.22`–`1.24`, 非 root `USER pni`) | `typescript/node.dockerfile` (Node Bookworm `18`/`20`/`22` + Playwright Chromium) | `javascript/node.dockerfile` (Node Bookworm `18`/`20`/`22` + Playwright Chromium) |
| **オフラインテスト & カバレッジ** | `pytest --junitxml=/out/junit.xml --cov --cov-report=json:/out/coverage.json` | `mvn test` / `gradle test` + JaCoCo XML (`/out/jacoco.xml`) | `php -l` 構文ゲート + `phpunit` + PCOV Clover (`/out/clover.xml`) | `go vet ./...` + `go test -v -coverprofile=/out/coverage.out ./...` | `vitest run` / `jest --coverage` (`coverage-summary.json` / `lcov.info`)、WTR、Mocha、または `tsc --noEmit` | `vitest run` / `jest --coverage` / `@web/test-runner` / Mocha / `node --test` |
| **Stage 3 スモークプローブ** | ASGI/WSGI `TestClient` 疎通・CLI `--help`・`importlib.import_module` | Spring Boot TCP `:18080` 起動確認・`main --help`・`target/classes` 検証 | `php -S` HTTP ルート疎通・`php artisan --version`・PSR-4 オートロード・WP プラグインフック検証 | `go build ./...` モジュール全体のコンパイル・リンク検証 | `tsc --noEmit` 型チェック（モノレポサブパッケージ対応）または Node ランタイム検証 | `node --check` による `.js`/`.mjs`/`.cjs` 構文チェック |

---

## 2. 決定論的な言語自動検出とサンドボックス実行パイプライン

`pni init` や `pni rules list`、またはワークフローステップを実行すると、`src/pni/_rules/manager.py` の `detect_active_language()` が以下の優先順位でリポジトリの主要言語を決定論的に自動判定します。

1. **主要ビルドマニフェストの検査**: ルートディレクトリのマニフェストを厳密な優先順で検査します。
   - **Python**: `pyproject.toml`, `setup.py`, `requirements.txt`
   - **Java**: `pom.xml`, `build.gradle`, `build.gradle.kts`, `settings.gradle`, `settings.gradle.kts`
   - **PHP**: `composer.json`, `wp-config.php`, `wp-config-sample.php`, `artisan`, `phpunit.xml`, `phpunit.xml.dist`
   - **Go**: `go.mod`, `go.work`
2. **Node.js プロジェクトにおける TypeScript / JavaScript 判別 (`_detect_node_language`)**:
   - `tsconfig.json` または `tsconfig.base.json` が存在する場合、あるいは `package.json` の `dependencies` / `devDependencies` に `"typescript"` が含まれる場合は即座に `typescript` と判定します。
   - `jsconfig.json` が存在する場合は `javascript` を返し、それ以外は `src/`・`app/`・`lib/`・`packages/`・`pages/`・`components/` 配下の `.ts`/`.tsx`（`.d.ts` を除く）と `.js`/`.jsx`/`.mjs`/`.cjs` の有無を比較します。
3. **ソースツリー拡張子フォールバック**: 標準ディレクトリ（`src/main/java`・`cmd/`・`internal/`・`pkg/`・`app/`・`public/`・`includes/`）のソース拡張子を走査し、該当がない場合はデフォルトの `python` にフォールバックします。

```drawlib align=center code=fold file=language_detection_and_toolchains.png caption="決定論的な言語自動検出・単一パス AST チェッカー群・オフラインコンテナツールチェーンの連携"
from drawlib.canvas import save, setup
from drawlib.diagrams.architecture import ArchitectureDiagram, Node, NodeGroup, PhosphorIcon
from drawlib.styles import Styles

setup(width=168, height=84, dpi=150)

diag = ArchitectureDiagram(
    node_style=Styles.PrimaryBold,
    node_text_style=Styles.DarkBold.patch(text_size=10.0),
    edge_style=Styles.DarkBold,
    edge_text_style=Styles.DarkBold.patch(text_size=9.8),
    node_card_style=Styles.WhiteBordered.patch(shape_r=1.5),
)

g_detect = diag.add(
    NodeGroup(
        title="1. Auto-Detection & Inspect",
        width=48.0,
        height=74.0,
        style=Styles.Neutral.patch(shape_r=2.0),
        text_style=Styles.DarkBold.patch(text_size=10.5, halign="left", valign="top"),
    ),
    xy=(4.0, 5.0),
)
n_manifest = g_detect.add(
    Node(
        "detect_active_language()\nManifests & tsconfig/jsconfig",
        width=42.0,
        height=15.5,
        icon=PhosphorIcon.MAGNIFYING_GLASS,
        icon_size=5.2,
        card_style=Styles.PrimaryNeutral.patch(shape_r=1.5),
    ),
    xy=(24.0, 54.0),
)
n_inspect = g_detect.add(
    Node(
        "project_inspect (ProjectFacts)\nBuild Tool, Lockfiles & Runtime",
        width=42.0,
        height=15.5,
        icon=PhosphorIcon.PACKAGE,
        icon_size=5.2,
    ),
    xy=(24.0, 32.0),
)
n_pni_toml = g_detect.add(
    Node(
        ".pni/pni.toml Overrides\nTargets, Excludes & [[opt_out]]",
        width=42.0,
        height=15.5,
        icon=PhosphorIcon.SLIDERS_HORIZONTAL,
        icon_size=5.2,
        style=Styles.SecondaryBold,
        card_style=Styles.SecondaryNeutral.patch(shape_r=1.5),
    ),
    xy=(24.0, 10.0),
)

g_ast = diag.add(
    NodeGroup(
        title="2. Parse-Once AST Suite",
        width=52.0,
        height=74.0,
        style=Styles.Neutral.patch(shape_r=2.0),
        text_style=Styles.DarkBold.patch(text_size=10.5, halign="left", valign="top"),
    ),
    xy=(58.0, 5.0),
)
n_suite = g_ast.add(
    Node(
        "LanguageAnalyzerSuite\nSingle-Pass SgRoot Tree-sitter",
        width=46.0,
        height=15.5,
        icon=PhosphorIcon.TREE_STRUCTURE,
        icon_size=5.2,
        style=Styles.WhiteBold,
        text_style=Styles.WhiteBold.patch(text_size=10.0),
        card_style=Styles.PrimaryFlat.patch(shape_r=1.5),
    ),
    xy=(26.0, 54.0),
)
n_checkers = g_ast.add(
    Node(
        "9 Specialized Checkers\nImports, Typing, Docs, Quality, Test",
        width=46.0,
        height=15.5,
        icon=PhosphorIcon.LIST_CHECKS,
        icon_size=5.2,
        card_style=Styles.PrimaryNeutral.patch(shape_r=1.5),
    ),
    xy=(26.0, 32.0),
)
n_sec_ast = g_ast.add(
    Node(
        "Framework & CWE Sinks\ndangerous_sinks + api_endpoints",
        width=46.0,
        height=15.5,
        icon=PhosphorIcon.SHIELD_WARNING,
        icon_size=5.2,
    ),
    xy=(26.0, 10.0),
)

g_runtime = diag.add(
    NodeGroup(
        title="3. Container Harness & Scan",
        width=48.0,
        height=74.0,
        style=Styles.Neutral.patch(shape_r=2.0),
        text_style=Styles.DarkBold.patch(text_size=10.5, halign="left", valign="top"),
    ),
    xy=(116.0, 5.0),
)
n_select = g_runtime.add(
    Node(
        "select_harness_tool()\n10 Built-in .dockerfile Templates",
        width=42.0,
        height=15.5,
        icon=PhosphorIcon.CUBE,
        icon_size=5.2,
        style=Styles.SecondaryBold,
        card_style=Styles.SecondaryNeutral.patch(shape_r=1.5),
    ),
    xy=(24.0, 54.0),
)
n_offline = g_runtime.add(
    Node(
        "Offline Test, Coverage & Smoke\n--network=none -> /out/* XML/JSON",
        width=42.0,
        height=15.5,
        icon=PhosphorIcon.TERMINAL_WINDOW,
        icon_size=5.2,
        style=Styles.WhiteBold,
        text_style=Styles.WhiteBold.patch(text_size=10.0),
        card_style=Styles.PrimaryFlat.patch(shape_r=1.5),
    ),
    xy=(24.0, 32.0),
)
n_trivy = g_runtime.add(
    Node(
        "Trivy FS + Image Scan\nApp Lockfiles + OS Packages",
        width=42.0,
        height=15.5,
        icon=PhosphorIcon.SHIELD_CHECK,
        icon_size=5.2,
        card_style=Styles.PrimaryNeutral.patch(shape_r=1.5),
    ),
    xy=(24.0, 10.0),
)

diag.connect(n_manifest, n_inspect, routing="orthogonal")
diag.connect(n_pni_toml, n_inspect, routing="orthogonal")
diag.connect(n_suite, n_checkers, routing="orthogonal")
diag.connect(n_checkers, n_sec_ast, routing="orthogonal")
diag.connect(n_select, n_offline, routing="orthogonal")
diag.connect(n_offline, n_trivy, routing="orthogonal")

diag.connect(g_detect, g_ast, routing="orthogonal", style=Styles.PrimaryBold)
diag.connect(g_ast, g_runtime, routing="orthogonal", style=Styles.PrimaryBold)

diag.draw(xy=(0.0, 0.0))
save()
```

### 2.1 Python & Java エコシステム

**Python**（`pyproject.toml`, `uv`, `Poetry`, `pip`）および **Java**（`Maven`, `Gradle`）では、自動生成コード（`target/`, `build/`, Alembic の `migrations/versions/` 等）がプロダクション AST 指標に混入しないよう、`.pni/workflows/full_audit.yaml` の `targets` を明示的に指定します。

```yaml
# Python PEP 621 src/ layout (or source: ["app"] for FastAPI services)
targets:
  root: "."
  source: ["src"]
  tests: ["tests"]
  docs: ["README.md"]

# Java Maven / Gradle standard layout
targets:
  root: "."
  source: ["src/main/java"]
  tests: ["src/test/java"]
  docs: ["README.md"]
```

### 2.2 PHP & Go エコシステム

**PHP** はモダンな Composer / PSR-4 アプリケーション（Laravel, Symfony）だけでなく、Composer を使わないレガシーな素の PHP（`raw.dockerfile`）や WordPress プラグインにも対応しています。**Go**（`go.mod`）では、`source` と `tests` に同じディレクトリを指定しても、プロダクションコード（`*.go`）と同居するテストファイル（`*_test.go`）が自動的に分離されます。

```yaml
# PHP Laravel layout (use source: ["."] for legacy raw PHP or WordPress plugins)
targets:
  root: "."
  source: ["app", "src", "routes"]
  tests: ["tests"]
  docs: ["README.md"]

# Go module layout (co-located *_test.go files are separated automatically)
targets:
  root: "."
  source: ["cmd", "internal", "pkg"]
  tests: ["cmd", "internal", "pkg"]
  docs: ["README.md"]
```

### 2.3 TypeScript & JavaScript エコシステム

**TypeScript** および **JavaScript** リポジトリでは、`LanguageAnalyzerSuite` が型宣言ファイル（`*.d.ts`）を本番 AST のコード行数肥大化から除外しつつ、JavaScript ライブラリのコンパニオン `.d.ts` 定義（`package.json` の `"types"`/`"typings"` または同梱 `*.d.ts`）を `has_type_marker = True` および公開型シグネチャとして評価します。さらに IIFE/UMD クロージャや ES2022 `#private` メソッドを展開し、`index.ts` バレル再エクスポート循環（`type_checking_cycles`）を実装循環（`circular_dependencies`）から分離し、`*.test.ts(x)`・`*.spec.ts(x)`・`*.test.js(x)`・`*.spec.js(x)` および `__tests__/` 配下のファイルをテスト解析器へ自動振り分けします。

```yaml
# TypeScript / JavaScript layout (supports dedicated tests/ or co-located src/**/*.test.ts)
targets:
  root: "."
  source: ["src"]
  tests: ["tests", "src"]
  docs: ["README.md"]
```

---

## 3. 言語別 AST チェッカーと CWE セキュリティシンク抽出

各言語の `LanguageAnalyzerSuite` はソースファイルを **1 回だけ** Tree-sitter CST（`SgRoot`）にパースし、9 つの専門チェッカー（`imports`, `typing`, `docs`, `quality`, `dependencies`, `testing`, `framework`, `operational`, `security`）を一括実行します。

| 言語 | 型安全性・契約シグナル (`typing`) | コード品質・運用シグナル (`quality` / `operational`) | フレームワーク規約・CWE 危険シンク (`dangerous_sinks`) |
| :--- | :--- | :--- | :--- |
| **Python** | 公開関数・メソッドの引数/戻り値型ヒント率、`Any` / 無制限 `type: ignore`、`py.typed` マーカー | `isort` 順、Google/NumPy/Sphinx docstring と `Args:` 整合性、McCabe (`>7`)・認知的複雑度 (`>15`)、ミュータブルデフォルト引数、裸の `except:`、`timeout=` 欠落 | FastAPI `on_event`・`response_model` 欠落・`async def` 内の同期 I/O、`eval`/`exec` (`CWE-94`)、`subprocess(..., shell=True)` (`CWE-78`)、`pickle`/`yaml.load` (`CWE-502`)、SQL 文字列補間 (`CWE-89`) |
| **Java** | ジェネリクス型安全率、生型（`List` 等の `<T>` 欠落）、スコープなしの `@SuppressWarnings` | ワイルドカード `import .*`、Javadoc 率と `@param` 整合性、可変 `public static` フィールド、空の `catch`、サービス内の `System.out.println` | Spring Boot `@Autowired` フィールド注入、非 public `@Transactional`、`javax.*` 残存、`Runtime.exec` (`CWE-78`)、`ObjectInputStream.readObject` (`CWE-502`)、文字列連結 JDBC/JPQL (`CWE-89`) |
| **PHP** | `declare(strict_types=1)` 宣言率、引数・戻り値・プロパティ型ヒント率、無制限 `@phpstan-ignore` | PSR-4 名前空間 vs `include`/`require_once`、HTML/PHP 混在スパゲッティ、`$_GET`/`$_POST`/`$GLOBALS` 直参照、`@` エラー抑制、`die()`/`exit()`、マジックハッシュ `==` | Laravel `config/` 外の `env()`・`$guarded = []`・生 `DB::raw()`、WordPress 未エスケープ SQLi/XSS・CSRF nonce 欠落、`eval`/`shell_exec`/`unserialize` (`CWE-94`/`78`/`502`) |
| **Go** | 具体型・ジェネリクス vs 非型付け `any` / `interface{}`（`format string, ...any` は除外）、`unsafe.Pointer` 使用、裸の `//nolint` | `gofmt`/import グループ順、ドット import (`import .`)、エクスポートシンボルの GoDoc 率、エラー握り潰し（`_ = err` および `val, _ := ...`）、複数行 raw バッククォート LOC 除外、非 `main` での `panic()`、ループ内 `defer` | Gin/Echo/Fiber/Chi/net-http ルート抽出 (`api_endpoints`)、`exec.Command("sh", "-c", ...)` (`CWE-78`)、`db.Query(fmt.Sprintf(...))` (`CWE-89`)、`Timeout` 未設定 HTTP クライアント |
| **TypeScript** | `tsconfig.json` `"strict": true`、明示的な公開関数型、`: any` / `as any`、`@ts-ignore` vs `@ts-expect-error`、`expectTypeOf<T>()` / `assertType<T>()` | ES Module import 衛生、バレル `type_checking_cycles` 分離、TSDoc (`/** ... */`) 率、ES2022 `#private` メソッド、未処理 Promise、空の `catch {}`、`var` 宣言、`==` 緩い等価比較 | Express/Fastify/NestJS/Hono/Next.js ルート抽出、`dangerouslySetInnerHTML` / `innerHTML` (`CWE-79`)、`eval` / `new Function` (`CWE-94`)、`child_process.exec` (`CWE-78`)、SQL テンプレート文字列 (`CWE-89`) |
| **JavaScript** | JSDoc `@param {Type}`・`@returns {Type}` 契約カバー率、コンパニオン `.d.ts` 型宣言（`has_type_marker`）、`checkJs` / `// @ts-check`、非型付け `@param {*}` | ES Module `import`/`export` vs CommonJS `require()`、IIFE/UMD クロージャ展開、`const`/`let` vs `var`、厳密等価 `===`、Promise `.catch()` 処理、認知的複雑度 | Express/Fastify/Hono ルート抽出、DOM XSS (`innerHTML`, `document.write`, `CWE-79`)、`eval()` (`CWE-94`)、`child_process.exec` (`CWE-78`)、プレースホルダなしの生 SQL (`CWE-89`) |

全 52 個の組み込みルールファイル一覧や `.pni/` ローカルオーバーライドカスケード、`pni` CLI コマンドの詳細については [ルール拡張と CLI リファレンス](rules_and_cli.md) を、コンテナ実行およびライブ HTTP ペネトレーションテストの詳細は [決定論的解析器とペネトレーションテスト](../03_workflows_and_actions/analyzers_and_pentest.md) を参照してください。
