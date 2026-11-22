# 対応 55 言語マトリクス

`pni501`（`v0.2.0`）は、従来の `ast-grep-py` を完全に置き換えた統一 1 パス `TreeCursor` インデックス付き **ネイティブ `tree-sitter` CST 解析エンジン**（**57 個のネイティブ文法**）により、**55 言語（プログラミング言語・スクリプト・HDL・IaC/スキーマ/設定 DSL）**に対して決定論的な静的解析（`ProjectFacts` / `AstFacts`）、言語別エンジニアリングルール、隔離コンテナテスト/カバレッジハーネス（**40 個の組み込み `.dockerfile` テンプレート**）、および Trivy サプライチェーンセキュリティスキャンを提供します。

```drawlib align=center code=fold file=six_languages_matrix_hero.png caption="対応 55 言語マトリクス（57 ネイティブ Tree-sitter 文法）：3 ティア構成とオンデマンド ABI3 配布アーキテクチャ"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import CardList, KpiCards, Panel
from drawlib.styles import Styles

setup(width=184, height=96, dpi=150)

t1_panel = Panel(
    "Tier A: Full Engineering Audit (20)",
    header_variant="filled",
    header_height=8.0,
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=10.8),
)
t1_panel.draw(xy=(3.0, 21.0), width=57.0, height=72.0)

t1_cards = CardList(
    style=Styles.WhiteBordered.patch(shape_r=1.4),
    text_style=Styles.DarkBold.patch(text_size=10.2),
    description_style=Styles.Dark.patch(text_size=9.8),
    badge_shape="rounded_rect",
    badge_style=Styles.PrimaryNeutral,
    badge_text_style=Styles.PrimaryBold.patch(text_size=10.0),
    icon_style=Styles.PrimaryBold,
    direction="vertical",
    spacing=2.0,
)
t1_cards.add(
    "Core 6 Deep Suites",
    "Python, Java, PHP, Go,\nTypeScript, JavaScript",
    badge_text="06",
    icon=phosphor.star,
)
t1_cards.add(
    "Systems & Enterprise",
    "C#, Rust, Kotlin, Swift,\nC, C++, Scala, COBOL",
    badge_text="08",
    icon=phosphor.cpu,
)
t1_cards.add(
    "App, Web & Data",
    "Ruby, Dart, Elixir,\nVue, Perl, R",
    badge_text="06",
    icon=phosphor.code,
)
t1_cards.draw(xy=(5.0, 23.0), width=53.0, height=59.5)

t2_panel = Panel(
    "Tier B: Declarative Static (20)",
    header_variant="filled",
    header_height=8.0,
    style=Styles.PrimaryNeutral.patch(shape_r=2.0),
    header_style=Styles.SecondaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=10.8),
)
t2_panel.draw(xy=(63.5, 21.0), width=57.0, height=72.0)

t2_cards = CardList(
    style=Styles.WhiteBordered.patch(shape_r=1.4),
    text_style=Styles.DarkBold.patch(text_size=10.2),
    description_style=Styles.Dark.patch(text_size=9.8),
    badge_shape="rounded_rect",
    badge_style=Styles.SecondaryNeutral,
    badge_text_style=Styles.SecondaryBold.patch(text_size=10.0),
    icon_style=Styles.SecondaryBold,
    direction="vertical",
    spacing=2.0,
)
t2_cards.add(
    "Shell, Scripting & Web",
    "Bash, PowerShell, Groovy,\nLua, Objective-C, Svelte",
    badge_text="06",
    icon=phosphor.terminal_window,
)
t2_cards.add(
    "Functional & Scientific",
    "Haskell, F#, OCaml, Zig,\nJulia, Fortran, MATLAB",
    badge_text="07",
    icon=phosphor.sliders_horizontal,
)
t2_cards.add(
    "HDL, GPU & Web3",
    "CUDA, Verilog, VHDL, Ada,\nOdin, Solidity, Common Lisp",
    badge_text="07",
    icon=phosphor.shield_check,
)
t2_cards.draw(xy=(65.5, 23.0), width=53.0, height=59.5)

t3_panel = Panel(
    "Tier C: Companion DSLs (15)",
    header_variant="filled",
    header_height=8.0,
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=10.8),
)
t3_panel.draw(xy=(124.0, 21.0), width=57.0, height=72.0)

t3_cards = CardList(
    style=Styles.WhiteBordered.patch(shape_r=1.4),
    text_style=Styles.DarkBold.patch(text_size=10.2),
    description_style=Styles.Dark.patch(text_size=9.8),
    badge_shape="rounded_rect",
    badge_style=Styles.PrimaryNeutral,
    badge_text_style=Styles.PrimaryBold.patch(text_size=10.0),
    icon_style=Styles.PrimaryBold,
    direction="vertical",
    spacing=2.0,
)
t3_cards.add(
    "IaC & Containers",
    "Dockerfile, HCL/Terraform,\nBicep, Nix",
    badge_text="04",
    icon=phosphor.cloud,
)
t3_cards.add(
    "Build & Schemas",
    "Makefile, Starlark/Bazel,\nProtocol Buffers, SQL",
    badge_text="04",
    icon=phosphor.wrench,
)
t3_cards.add(
    "Web & Config Formats",
    "HTML, CSS, SCSS, YAML,\nJSON, TOML, XML",
    badge_text="07",
    icon=phosphor.file_code,
)
t3_cards.draw(xy=(126.0, 23.0), width=53.0, height=59.5)

footer = KpiCards(
    style=Styles.Neutral.patch(shape_r=1.5),
    metric_style=Styles.PrimaryBold.patch(text_size=12.0),
    text_style=Styles.DarkBold.patch(text_size=9.8),
    accent_style=Styles.PrimaryFlat,
    accent_position="top_bar",
    metric_layout="top_stack",
    spacing=3.0,
)
footer.add("55 Languages", "57 Native Tree-sitter CSTs")
footer.add("52 PyPI Wheels", "Bundled ABI3 Grammars")
footer.add("5 On-Demand", "COBOL, R, Vue, Proto, Docker")
footer.add("40 Harnesses", "Isolated Container Dockerfiles")
footer.draw(xy=(3.0, 3.0), width=178.0, height=15.0, columns=4)

save()
```

---

## 1. 3 ティア構成の 55 言語アーキテクチャ（57 ネイティブ Tree-sitter 文法）

全 55 言語のメタデータは単一の宣言的レジストリ（`src/pni/_languages/registry.py`）で一元管理され、統一 1 パス `tree-sitter` CST レイヤ（`src/pni/_actions/ast_analyze/_cst.py`）を通じて解析されます。PHP（`php` + `php_only`）および TypeScript（`typescript` + `tsx`、JavaScript と共有）が複数方言文法を持つため、合計 **57 個のネイティブ `tree-sitter` 文法**をカバーします。

| ティア | 対象範囲・言語数 | 解析器・実行検証ケイパビリティ | 対象言語一覧 |
| :--- | :--- | :--- | :--- |
| **Tier A — フルエンジニアリング監査** | **20 言語** (`full_audit`) | マニフェスト/ロックファイル完全解析、深いネイティブ CST 検査（コア 6 言語の専用マルチチェッカ + 拡張 14 言語の統合スイート）、隔離コンテナハーネス（`20/20`）、Trivy スキャン、言語別 `6`〜`8` ルールファイル。 | **Python**, **Java**, **PHP**, **Go**, **TypeScript**, **JavaScript**, **C#**, **Rust**, **Ruby**, **Kotlin**, **Swift**, **C**, **C++**, **Scala**, **Dart**, **Elixir**, **Vue**, **Perl**, **COBOL**, **R** |
| **Tier B — 宣言的静的監査** | **20 言語** (`static_audit`) | 統一宣言的 Tree-sitter CST 静的解析（複雑度・ドキュメント衛生・型/契約検査・CWE 危険シンク）、各 `6` ルールファイル、さらに 15 エコシステム向けコンテナハーネス（Bash, PowerShell, Groovy, Lua, Haskell, F#, OCaml, Zig, Julia, Fortran, Svelte, Verilog, VHDL, Ada, Common Lisp）。 | **Bash/Shell**, **PowerShell**, **Groovy**, **Objective-C**, **Lua**, **Haskell**, **F#**, **OCaml**, **Zig**, **Julia**, **Fortran**, **MATLAB**, **Svelte**, **Solidity**, **CUDA**, **Verilog/SystemVerilog**, **VHDL**, **Ada**, **Odin**, **Common Lisp** |
| **Tier C — コンパニオン IaC / スキーマ / ビルド / 設定** | **15 言語** (`companion_dsl`) | 主言語（Tier A/B）リポジトリに同居する **コンパニオン DSL の自動並列スキャン**（`companion_ast_facts`）および単体監査、各 `6` ルールファイル。IaC ハードニング・コンテナ安全性・スキーマ品質・ビルド決定論性を評価。 | **Dockerfile**, **HCL/Terraform**, **Bicep**, **Nix**, **Makefile**, **Starlark/Bazel**, **Protocol Buffers**, **SQL**, **HTML**, **CSS**, **SCSS**, **YAML**, **JSON**, **TOML**, **XML** |

### 1.1 Tier A 詳細マトリクス（コア 6 言語 + 拡張 14 言語）

コア 6 言語は専用の 9 チェッカ構成 `LanguageAnalyzerSuite` を備え、拡張 14 言語は統一宣言的 CST チェッカと言語別マニフェスト・ロックファイル・ルール・コンテナハーネスを統合しています。

| 言語 (`id`) | 主なマニフェスト / ロックファイル | 対象拡張子 | コンテナハーネステンプレート (`.pni/dockerfiles/`) |
| :--- | :--- | :--- | :--- |
| **Python (`python`)** | `pyproject.toml`, `setup.py`, `uv.lock`, `poetry.lock` | `.py` | `python/uv.dockerfile`, `poetry.dockerfile`, `pip.dockerfile` |
| **Java (`java`)** | `pom.xml`, `build.gradle(.kts)`, `gradle.lockfile` | `.java` | `java/maven.dockerfile`, `gradle.dockerfile` |
| **PHP (`php`)** | `composer.json`, `composer.lock`, `artisan`, `wp-config.php` | `.php`, `.phtml` | `php/composer.dockerfile`, `raw.dockerfile` |
| **Go (`go`)** | `go.mod`, `go.work`, `go.sum` | `.go` | `go/go.dockerfile` |
| **TypeScript (`typescript`)** | `tsconfig.json`, `package.json`, `pnpm-lock.yaml`, `package-lock.json` | `.ts`, `.tsx` | `typescript/node.dockerfile` |
| **JavaScript (`javascript`)** | `jsconfig.json`, `package.json`, `pnpm-lock.yaml`, `yarn.lock` | `.js`, `.jsx`, `.mjs`, `.cjs` | `javascript/node.dockerfile` |
| **C# (`csharp`)** | `*.csproj`, `*.sln`, `Directory.Build.props`, `packages.lock.json` | `.cs` | `csharp/dotnet.dockerfile` |
| **Rust (`rust`)** | `Cargo.toml`, `Cargo.lock` | `.rs` | `rust/cargo.dockerfile` |
| **Ruby (`ruby`)** | `Gemfile`, `Gemfile.lock`, `Rakefile`, `*.gemspec` | `.rb`, `.rake` | `ruby/bundler.dockerfile` |
| **Kotlin (`kotlin`)** | `build.gradle.kts`, `pom.xml`, `gradle.lockfile` | `.kt`, `.kts` | `kotlin/gradle.dockerfile`, `maven.dockerfile` |
| **Swift (`swift`)** | `Package.swift`, `Package.resolved` | `.swift` | `swift/swiftpm.dockerfile` |
| **C (`c`)** | `CMakeLists.txt`, `Makefile`, `meson.build` | `.c`, `.h` | `c/cmake.dockerfile` |
| **C++ (`cpp`)** | `CMakeLists.txt`, `conanfile.*`, `vcpkg.json` | `.cpp`, `.cc`, `.cxx`, `.hpp`, `.hh`, `.hxx` | `cpp/cmake.dockerfile` |
| **Scala (`scala`)** | `build.sbt` | `.scala`, `.sc` | `scala/sbt.dockerfile` |
| **Dart (`dart`)** | `pubspec.yaml`, `pubspec.lock` | `.dart` | `dart/pub.dockerfile` |
| **Elixir (`elixir`)** | `mix.exs`, `mix.lock` | `.ex`, `.exs` | `elixir/mix.dockerfile` |
| **Vue (`vue`)** | `nuxt.config.*`, `vue.config.js`, `package.json` | `.vue` | `vue/node.dockerfile` *(オンデマンド文法)* |
| **Perl (`perl`)** | `cpanfile`, `cpanfile.snapshot`, `Makefile.PL`, `Build.PL` | `.pl`, `.pm`, `.t` | `perl/cpan.dockerfile` |
| **COBOL (`cobol`)** | ソース拡張子自動検出 (`*.cob`, `*.cbl`, `*.cpy`) | `.cob`, `.cbl`, `.cpy` | `cobol/gnucobol.dockerfile` *(オンデマンド文法)* |
| **R (`r`)** | `DESCRIPTION`, `NAMESPACE`, `renv.lock` | `.r` | `r/r.dockerfile` *(オンデマンド文法)* |

---

## 2. GitHub Releases オンデマンド ABI3 文法配布アーキテクチャ

`pni501` 本体パッケージを軽量な **純 Python（`py3-none-any`）ホイール** に保ったまま、Linux・macOS・Windows 全環境で C コンパイラ不要のネイティブ `tree-sitter` 解析を実現するため、文法配布は 2 系統のハイブリッド構成（`src/pni/_languages/_grammar_assets.py`）を採用しています。

1. **PyPI 同梱 `abi3` ホイール（52 文法）**: 52 個の Tree-sitter 文法は標準の PyPI `tree-sitter-*` `abi3` ホイール（`source="package"`）として自動導入されます。
2. **GitHub Releases オンデマンド配布（5 文法・SHA-256 ピン留め検証）**: 3 OS 揃った PyPI ホイールが存在しない MIT ライセンスの 5 文法 — **COBOL (`cobol`)**・**R (`r`)**・**Vue (`vue`)**・**Protocol Buffers (`protobuf` / アセット `proto`)**・**Dockerfile (`dockerfile`)** — は、GitHub Actions により **5 プラットフォーム**（`linux_x86_64`、`linux_aarch64`、`macos_arm64`、`macos_x86_64`、`windows_amd64`）向け ABI3 バイナリとしてビルドされ、GitHub Releases（`grammars-v0.2.0`）で配布されます。
   - **初回利用時の遅延取得と完全性検証**: `.cob`・`.r`・`.vue`・`.proto`・`Dockerfile` の初回パース時に HTTPS で該当プラットフォームのアーカイブを取得し、**ピン留め済み SHA-256 ダイジェストを検証**したうえでスレッド＆ファイルロック保護下に展開キャッシュします（探索順：`PNI_GRAMMAR_CACHE_DIR` -> `pni/_cached_grammars` -> OS ユーザーキャッシュ `~/.cache/pni501/grammars` または `%LOCALAPPDATA%\pni501\grammars`）。
   - **オフライン・エアギャップ CI 対応**: `pni grammars` CLI により事前取得・状態確認・キャッシュ消去が可能です。

```bash
# プラットフォーム・リリースタグ・キャッシュ状況・ピン留め SHA-256 を確認
pni grammars status

# オフライン CI/コンテナ向けに 5 文法すべて（または個別指定）を事前ダウンロード
pni grammars prefetch --all
pni grammars prefetch dockerfile vue protobuf --force

# ローカルにキャッシュされた追加文法バイナリを削除
pni grammars clear
```

---

## 3. 決定論的な 55 言語自動検出とサンドボックス実行パイプライン

`pni init` や `pni rules list`、またはワークフローステップを実行すると、`src/pni/_rules/manager.py` の `detect_active_language()` がリポジトリの主言語（およびコンパニオン Tier C DSL）を手動フラグなしで決定論的に判定します。

1. **コア＆拡張マニフェストの検査**: Python・Java・PHP・Go・Node.js（`tsconfig.json` / `"typescript"` 依存で `typescript`、`jsconfig.json` で `javascript`）に加え、拡張 Tier A/B エコシステム（`Cargo.toml`、`*.csproj`、`Gemfile`、`Package.swift`、`build.sbt`、`pubspec.yaml`、`mix.exs`、`nuxt.config.*`、`cpanfile`、`DESCRIPTION`、`stack.yaml`、`dune-project`、`build.zig`、`Project.toml`、`fpm.toml`、`foundry.toml`、`alire.toml` 等）を厳密な優先順で検査します。
2. **ソースツリー拡張子フォールバック**: `.git`・`node_modules`・`vendor`・`target`・`.venv`・`.pni`・`.drawlib` を除外しつつ拡張子を走査し、マニフェストを持たない言語（C、COBOL、Bash、Verilog、VHDL、CUDA、Odin 等）も自動判定します。
3. **コンパニオン DSL・モノレポ自動検出**: `pni workflows plan` がモノレポコンポーネントおよび Tier C ファイル（`Dockerfile`、Terraform `.tf`、`.proto`、`.sql`、`.yaml`、`Makefile`、`BUILD.bazel`）を自動発見し、主言語監査と並列に IaC・スキーマ検証を実行します。

```drawlib align=center code=fold file=language_detection_and_toolchains.png caption="55 言語自動検出・1パス ネイティブ Tree-sitter CST エンジン・40 種オフラインコンテナハーネスの連携"
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
        "detect_active_language()\n55 Langs + Companion DSLs",
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
        "project_inspect (ProjectFacts)\nManifests, Lockfiles & Runtime",
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
        title="2. Native Tree-sitter CST",
        width=52.0,
        height=74.0,
        style=Styles.Neutral.patch(shape_r=2.0),
        text_style=Styles.DarkBold.patch(text_size=10.5, halign="left", valign="top"),
    ),
    xy=(58.0, 5.0),
)
n_suite = g_ast.add(
    Node(
        "1-Pass Tree-sitter CST (57)\n52 PyPI ABI3 + 5 Release Assets",
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
        "Core + Declarative Checkers\nImports, Typing, Docs, Quality",
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
        "select_harness_tool()\n40 Built-in .dockerfile Templates",
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
        "Offline Test, Coverage & Smoke\n--network=none -> /out/ XML/JSON",
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

### 3.1 言語別 CST チェッカと CWE セキュリティシンク抽出

すべてのソースファイルは **1 回だけ** `TreeCursor` インデックス付きネイティブ Tree-sitter CST（`src/pni/_actions/ast_analyze/_cst.py`）へパースされ、9 つの専門チェッカ領域（`imports`, `typing`, `docs`, `quality`, `dependencies`, `testing`, `framework`, `operational`, `security`）が一括実行されます。

| エコシステム | 型安全性・契約シグナル (`typing`) | コード品質・運用シグナル (`quality` / `operational`) | フレームワーク規約・CWE 危険シンク (`dangerous_sinks`) |
| :--- | :--- | :--- | :--- |
| **Python** | 公開関数・メソッドの引数/戻り値型ヒント率、`Any` / 無制限 `type: ignore`、`py.typed` マーカー | `isort` 順、Google/NumPy/Sphinx docstring と `Args:` 整合性、McCabe (`>7`)・認知的複雑度 (`>15`)、ミュータブルデフォルト引数、裸の `except:`、`timeout=` 欠落 | FastAPI `on_event`・`response_model` 欠落・`async def` 内の同期 I/O、`eval`/`exec` (`CWE-94`)、`subprocess(..., shell=True)` (`CWE-78`)、`pickle`/`yaml.load` (`CWE-502`)、SQL 文字列補間 (`CWE-89`) |
| **Java** | ジェネリクス型安全率、生型（`List` 等の `<T>` 欠落）、スコープなしの `@SuppressWarnings` | ワイルドカード `import .*`、Javadoc 率と `@param` 整合性、可変 `public static` フィールド、空の `catch`、サービス内の `System.out.println` | Spring Boot `@Autowired` フィールド注入、非 public `@Transactional`、`javax.*` 残存、`Runtime.exec` (`CWE-78`)、`ObjectInputStream.readObject` (`CWE-502`)、文字列連結 JDBC/JPQL (`CWE-89`) |
| **PHP** | `declare(strict_types=1)` 宣言率、引数・戻り値・プロパティ型ヒント率、無制限 `@phpstan-ignore` | PSR-4 名前空間 vs `include`/`require_once`、HTML/PHP 混在スパゲッティ、`$_GET`/`$_POST`/`$GLOBALS` 直参照、`@` エラー抑制、`die()`/`exit()`、マジックハッシュ `==` | Laravel `config/` 外の `env()`・`$guarded = []`・生 `DB::raw()`、WordPress 未エスケープ SQLi/XSS・CSRF nonce 欠落、`eval`/`shell_exec`/`unserialize` (`CWE-94`/`78`/`502`) |
| **Go** | 具体型・ジェネリクス vs 非型付け `any` / `interface{}`（`format string, ...any` は除外）、`unsafe.Pointer`、裸の `//nolint` | `gofmt`/import グループ順、ドット import (`import .`)、エクスポートシンボルの GoDoc 率、エラー握り潰し（`_ = err`・`val, _ := ...`）、非 `main` での `panic()`、ループ内 `defer` | Gin/Echo/Fiber/Chi/net-http ルート抽出 (`api_endpoints`)、`exec.Command("sh", "-c", ...)` (`CWE-78`)、`db.Query(fmt.Sprintf(...))` (`CWE-89`)、`Timeout` 未設定 HTTP クライアント |
| **TypeScript / JavaScript** | `tsconfig.json` `"strict": true`、公開型シグネチャ・JSDoc `@param`、同梱 `.d.ts` 型宣言、`any` / `@ts-ignore` | ES Module 衛生、バレル `type_checking_cycles` 分離、TSDoc/JSDoc 率、ES2022 `#private`、IIFE/UMD 展開、未処理 Promise、`var`・`==` | Express/Fastify/NestJS/Hono/Next.js ルート抽出、`dangerouslySetInnerHTML` / `innerHTML` (`CWE-79`)、`eval` / `new Function` (`CWE-94`)、`child_process.exec` (`CWE-78`)、生 SQL テンプレート (`CWE-89`) |
| **拡張 Tier A/B・Tier C DSL** | 宣言的 CST による関数シグネチャ型注釈率、`unsafe`/`void*` 等の危険キャスト、スキーマ・フィールド契約 | 統一宣言的 CST 複雑度・関数行数/引数数、インポートグラフ・循環抽出、ドキュメントコメント率、エラーハンドリング規律 | 言語別コマンド/コード/SQL インジェクションシンク、C/C++/CUDA のメモリ安全性、Solidity リエントランシ/`tx.origin`、Dockerfile `USER root`/未固定タグ、Terraform/Bicep の過剰公開・ハードコード秘匿情報 |

全 **356 個の組み込みルールファイル**・**182 個のアクションテンプレート**・**112 個のワークフローテンプレート**、`.pni/` ローカルオーバーライドカスケード、および全 `pni` CLI コマンドの詳細は [ルール拡張と CLI リファレンス](rules_and_cli.md) を、コンテナ実行およびライブ HTTP ペネトレーションテストの詳細は [決定論的解析器とペネトレーションテスト](../03_workflows_and_actions/analyzers_and_pentest.md) を参照してください。
