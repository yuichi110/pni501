# 多言語・フレームワーク健全性検査マトリックス & 抽象クラス設計書

本ドキュメントは、`pni501` において Python 以外の主流言語・置き換え対象の旧主流言語・主要フレームワークまで見据えた **「検査項目 × 言語マトリックス」** および **「フレームワーク × モダナイゼーション設計」** を定義し、実装着手前に [`src/pni/_actions/ast_analyze/base/`](../../src/pni/_actions/ast_analyze/base) の抽象クラス群と [`AstFacts`](../../src/pni/_actions/ast_analyze/models.py) / [`ProjectFacts`](../../src/pni/_actions/project_inspect.py) のスキーマを確定させるための全体設計書です。

Python 個別の詳細な AST ルール・実装仕様については、対になる [PYTHON_HEALTH_CHECKS_PLAN.md](./PYTHON_HEALTH_CHECKS_PLAN.md) を参照してください。

---

## 1. 対象言語スコープの整理（`ast-grep-py` 実機検証に基づく4分類）

当リポジトリ環境の `ast-grep-py` に標準バンドルされているパーサーを実機検証した結果を踏まえ、対象言語を以下の **4カテゴリ** に分類します（COBOL・Fortran 等の導入コストが過大なレガシー言語は対象外とします）。

### `ast-grep-py` 組込サポート検証結果
- **組込済（追加バイナリ不要で即時 CST 解析可能）**:
  `python`, `java`, `typescript`, `tsx`, `javascript`, `go`, `rust`, `csharp`, `kotlin`, `cpp`, `c`, `swift`, `dart`, `ruby`, `php`, `scala`, `bash`, `lua`, `elixir`, `haskell`, `zig`, `hcl`, `yaml`, `json`, `html`, `css`
- **未組込（`LanguageNotSupported` — 動的 `.so` ビルドなしでは CST 解析不可）**:
  `perl`, `cobol`, `fortran`, `groovy`, `objc`, `r`, `sql`

### PNI における言語カテゴリ戦略

| カテゴリ | 対象言語 | `ast-grep` | PNI での位置づけ・検査アプローチ |
| :--- | :--- | :---: | :--- |
| **Cat A: モダン主流言語**<br>*(Full AST Suite)* | **Python**, **Java** *(実装済/強化)*<br>**TypeScript (`tsx`)**, **Go** *(次期優先)*<br>**Rust**, **Kotlin**, **C#**, **Modern C++** *(将来)* | **◎ 組込済** | [`LanguageAnalyzerSuite`](../../src/pni/_actions/ast_analyze/runner.py#L77-L89) の全抽象チェッカーを実装し、型安全性・Import整列・Doc・複雑度・依存をフル計測する。 |
| **Cat B: 近代化・移行判断を伴う旧主流／スクリプト言語**<br>*(AST Suite + 移行判定)* | **JavaScript (`.js`)** → *TypeScript 推奨*<br>**Bash (`.sh`)** → *肥大化時は Python/Go 推奨*<br>**PHP** → *PHP 8.2+ 厳格型 or 他言語移行*<br>**Ruby** → *Sorbet/RBS 導入 or 他言語移行*<br>**C (生C)** → *新規は Rust / Modern C++ 推奨* | **◎ 組込済** | `ast-grep-py` でそのまま構文解析が可能。品質・危険構文の検査に加え、**「規模・用途に応じたモダン言語への移行勧告ファクト」** を出力する。 |
| **Cat C: `ast-grep` 非組込の置換推奨レガシー言語**<br>*(軽量検出 + 移行勧告専用)* | **Perl (`.pl`, `.pm`, `.cgi`)**<br>**Batch / VBScript (`.bat`, `.vbs`)** | **× 未組込** | C拡張 `.so` を同梱せず、[`project_inspect.py`](../../src/pni/_actions/project_inspect.py) の軽量スキャナ（ファイル数・行数・`use strict` 有無等）で検出し、**Python / Go 等へのリプレース推奨** を確定ファクト化する。 |
| **スコープ外** | COBOL, Fortran, アセンブリ等 | × 未組込 | パーサー維持コスト対効果が低いため PNI の自動解析対象外とする。 |

---

## 2. 検査項目 × 言語 マトリックス表

記号の意味：
- **`◎`**: 必須・高有効（その言語における最重要品質シグナル）
- **`○`**: 同型対応（言語ごとの構文差を吸収して同じ抽象メトリクスに正規化可能）
- **`△`**: 部分対応（簡易検査または一部指標のみ該当）
- **`N/A`**: 言語仕様またはコンパイラ強制により非該当（抽象クラスでは `None` を返し、不当な減点も水増し加点も行わない）

| 抽象チェッカー (`base/`) | 抽象検査項目 | Python | Java | TypeScript | Go | Rust | JS *(→TS候補)* | PHP / Ruby | Bash *(肥大化監視)* | Perl *(軽量検出)* |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`imports.py`**<br>*(Import 衛生)* | **グループ順序・空行・辞書順整列** | **◎** (`isort`) | **◎** (`static`分離+辞書順) | **◎** (外部/内部順) | **◎** (`goimports`順) | **○** (`std`/外部/`crate`) | **○** (ESM整列) | **△** (`use`/`require`順) | `N/A` | `N/A` |
| | **ワイルドカード Import 禁止** | **◎** (`import *`) | **◎** (`import pkg.*;`) | **△** (`* as ns`は可) | **◎** (`import . "pkg"`) | **◎** (`use foo::*;`) | **△** (CommonJS混在検出) | **△** | `N/A` | `N/A` |
| | **非トップレベル（関数内/途中）Import** | **◎** (`PLC0415`) | `N/A` *(構文不可)* | **○** (動的`require`) | `N/A` *(構文不可)* | **△** (関数内`use`) | **◎** (途中`require`) | **◎** (途中`require`) | **○** (`source`乱用) | `N/A` |
| **`typing.py`**<br>*(型安全性)* | **関数/メソッド/属性の型注釈率** | **◎** (引数/戻り値/属性) | **◎** (Raw型排除率) | **◎** (暗黙`any`排除率) | `N/A` *(構文必須)* | `N/A` *(構文必須)* | **×→移行勧告** (JSDoc有無のみ) | **◎** (PHP8型宣言 / RBS) | `N/A` | `N/A` |
| | **弱い型・型抜け道 (`weak_types`)** | **◎** (`Any`, 生`list`) | **◎** (`Object`乱用) | **◎** (`any`, `as any`) | **◎** (`any`/`interface{}`, `unsafe`) | **◎** (`unsafe`ブロック) | **◎** (全動的型) | **○** (`mixed`乱用) | `N/A` | `N/A` |
| | **無指定の型チェッカー抑制コメント** | **◎** (裸`# type: ignore`) | **◎** (`@SuppressWarnings`) | **◎** (`@ts-ignore`) | **△** (`//nolint`無指定) | **○** (`#[allow(...)]`乱用) | **○** (`// @ts-nocheck`) | **△** (`@phpstan-ignore`) | **△** (`shellcheck disable`) | `N/A` |
| | **パッケージ型配布設定** | **◎** (`py.typed`) | `N/A` | **◎** (`strict: true`, `d.ts`) | `N/A` | `N/A` | **○** (`checkJs`) | **◎** (`strict_types=1`) | `N/A` | **○** (`use strict;`) |
| **`docs.py`**<br>*(API 文書)* | **公開モジュール/型/関数の文書付与率** | **◎** (Docstring) | **◎** (Javadoc `/**`) | **◎** (TSDoc `/**`) | **◎** (`// Symbol ...`) | **◎** (`///` rustdoc) | **○** (JSDoc) | **○** (PHPDoc / YARD) | **△** (ヘッダ説明) | **△** (POD有無) |
| | **空・`TODO` のみの形骸化文書検出** | **◎** | **◎** | **◎** | **◎** | **◎** | **○** | **○** | `N/A` | `N/A` |
| | **引数・戻り値タグと実シグネチャの一致** | **◎** (`Args:`/`Returns:`) | **◎** (`@param`/`@return`) | **◎** (`@param`/`@returns`) | `N/A` *(タグ文化なし)* | `N/A` *(引数タグなし)* | **○** (JSDoc `@param`) | **◎** (`@param`型・名前) | `N/A` | `N/A` |
| **`quality.py`**<br>*(複雑度・構文)* | **LOC・関数長・McCabe / 認知的複雑度** | **◎** | **◎** | **◎** | **◎** | **◎** | **◎** | **◎** | **◎** *(>100行で置換勧告)* | **◎** *(行数・ファイル数)* |
| | **ミュータブルなグローバル/静的状態** | **◎** (`global`/可変定数) | **◎** (` non-final static`) | **○** (`let`/`var` export) | **◎** (パッケージ`var`) | **◎** (`static mut`) | **◎** (`var` / `window`) | **◎** (`global`/`$_SESSION`直参照) | **○** (未`local`変数) | **○** (`our`/package変数) |
| | **言語固有の地雷・危険構文 (`bug_risk_idioms`)** | **◎** (可変デフォルト引数, 裸`except:`, `eval`) | **◎** (空`catch`, 文字列`==`, `System.out`) | **◎** (未await Promise, `==`, `eval`) | **◎** (`_ = err`握り潰し, `panic`乱用) | **◎** (本番`.unwrap()`乱用) | **◎** (`==`, `var`, `eval`) | **◎** (`eval`, `extract`, `==`緩い比較) | **◎** (`set -euo pipefail`欠落, 未クォート`$var`) | **◎** (`use warnings`欠落, `eval ""`, CGI直書き) |
| **`dependencies.py`**<br>*(依存・境界)* | **内部モジュール/パッケージ循環依存 (SCC)** | **◎** | **◎** | **◎** | `N/A` *(コンパイラ禁止)* | `N/A` *(mod循環不可)* | **◎** | **○** | `N/A` | `N/A` |
| | **マニフェスト宣言 vs 実 Import 過不足** | **◎** (`pyproject.toml`) | **○** (`pom.xml`/`gradle`) | **◎** (`package.json`) | `N/A` (`go mod tidy`強制) | **○** (`Cargo.toml`) | **◎** (`package.json`) | **○** (`composer`/`Gemfile`) | `N/A` | **△** (`cpanfile`) |
| | **非公開モジュール (`_internal` 等) 越境参照** | **◎** (`_pkg`外部参照) | **○** (`internal`パッケージ) | **◎** (内部パス直import) | `N/A` (`internal/`強制) | `N/A` (`pub(crate)`強制) | **○** | **△** | `N/A` | `N/A` |
| **`testing.py`**<br>*(テスト実効性)* | **アサーション無し（形骸化）テスト検出** | **◎** (`pytest`) | **◎** (`JUnit`) | **◎** (`Vitest`/`Jest`) | **◎** (`t.Error`/`require`無) | **◎** (`assert!`無) | **◎** | **◎** (`PHPUnit`/`RSpec`) | **△** (`bats`有無) | **△** (`Test::More`有無) |
| | **公開モジュール対テスト対応率** | **◎** | **◎** | **◎** | **◎** (`*_test.go` 1:1) | **◎** (`#[cfg(test)]`) | **○** | **○** | **△** | **△** (`t/*.t`) |

---

## 3. フレームワーク単体検査 & Modern Stack（移行推奨）マトリックス

### 3.1. 設計原則：「言語＝継承 (`1:1`)」「フレームワーク＝コンポジション (`1:N`)」

1つのプロジェクトは複数のライブラリ・フレームワーク（例: `FastAPI` + `Pydantic` + `SQLAlchemy` + `pytest`）を同時に利用するため、言語クラスを継承分岐させるのではなく、**[`project_inspect.py`](../../src/pni/_actions/project_inspect.py) が検出した `detected_frameworks` に基づいて「Rules（Markdown）」と「Framework AST Checker（プラグイン）」を動的にアタッチする構成**とします。

### 3.2. フレームワーク × モダナイゼーション対応表

| 言語 | 主要フレームワーク単体検査 (`BaseFrameworkChecker` + Rules) | ① 無条件減点する「世代遅れ負債」<br>*(Objective Legacy Debt)* | ② 用途・規模に応じて提案する「モダン移行推奨」<br>*(Contextual Modernization Advisory)* |
| :--- | :--- | :--- | :--- |
| **Python** | ・**FastAPI**: `async def` 内の同期ブロッキング呼び出し (`requests`, `time.sleep`)、`response_model`/戻り値型欠落、`Depends` 活用<br>・**Pydantic v2**: `ConfigDict` 準拠、ミュータブル初期値回避<br>・**SQLAlchemy 2.0**: `select()` + `Mapped[]` 型安全クエリ<br>・**pytest**: fixture 設計、`unittest.TestCase` 混在回避 | ・`setup.py` のみ（`pyproject.toml` 未移行）<br>・ロックファイル（`uv.lock` 等）欠如<br>・Pydantic v1 記法（`.dict()`, `class Config`）<br>・SQLAlchemy 1.x `session.query()`<br>・旧式型ヒント（`typing.List`/`Optional` → PEP 585/604） | ・**`Flask` / `Bottle` (JSON REST API用途)** → **`FastAPI`** (+ Pydantic v2) への移行推奨（※SSR/Jinja2用途や Django Admin 用途は除外）<br>・**`argparse` / `optparse` (中規模以上CLI)** → **`Typer` / `Click`** 推奨<br>・**`flake8`+`black`+`isort` 分散** → **`Ruff`** 統合推奨<br>・`async` 関数内の **`requests`** → **`httpx`** 推奨 |
| **Java** | ・**Spring Boot**: `@Autowired` フィールド注入禁止（コンストラクタ DI 必須）、`private` メソッドへの `@Transactional` 誤用、Controller からの JPA `@Entity` 直返却禁止<br>・**JUnit 5**: `@Test` 可視性、`Assertions` 統一 | ・Java 8 / 11 固定（Java 21 LTS 未到達）<br>・`javax.*` 名前空間（Spring Boot 3 / `jakarta.*` 未移行）<br>・JUnit 4 (`org.junit.Test`) 残存<br>・`Date`/`Calendar` 使用（`java.time` 未移行） | ・ボイラープレート DTO クラス / Lombok `@Value` 乱用 → **Java `record` / `sealed interface`** 活用推奨<br>・高並行ブロッキング構成 → **Java 21 Virtual Threads** 検討推奨 |
| **TS / JS** | ・**React / Next.js**: Hooks ルール違反、Server/Client 境界の秘密情報漏洩<br>・**NestJS / Hono**: DTO バリデーション (`Zod` / `class-validator`) 必須 | ・**純粋 JavaScript (`.js`) でのバックエンド/中規模以上フロント開発**（TypeScript 未導入）<br>・`tsconfig.json` で `"strict": true` 未有効<br>・CommonJS (`require`/`module.exports`) 残存 | ・未型付け **`Express`** → **`Hono` / `Fastify` / `NestJS` (TypeScript + Zod/OpenAPI)** への移行推奨<br>・レガシー Webpack / Babel 複雑構成 → **Vite / Biome or ESLint v9** 推奨 |
| **Go** | ・**net/http / Gin / Echo**: `context.Context` 第一引数伝搬、HTTP クライアントの `Timeout` 未設定防止 (`http.DefaultClient` 直叩き検出) | ・`GOPATH` 前提構成（`go.mod` 欠如）<br>・Go 1.18 未満（Generics 以前）<br>・非推奨 `io/ioutil` パッケージ使用 | ・小規模ルーティングのみでの過剰な独自ラッパー → **Go 1.22+ 標準 `net/http` 強化ルーター** または **`oapi-codegen` / `Connect-RPC`** 推奨 |
| **旧主流 / スクリプト** | ・**Bash**: `set -euo pipefail` 検査<br>・**PHP (Laravel/Symfony)**: `declare(strict_types=1)`、生 SQL 禁止 | ・**Perl (`.pl`/`.pm`)** の新規・現役バッチ運用<br>・PHP 7 以前 / フレームワーク無しの生 `.php` 混在テンプレート | ・**Perl スクリプト資産** → **Python / Go** への段階的リプレース推奨<br>・**100行超・複雑分岐を持つ Bash スクリプト** → **Python (`Typer`) / Go CLI** への置き換え推奨 |

---

## 4. 抽象クラス設計（`src/pni/_actions/ast_analyze/` 改訂アーキテクチャ）

マトリックスから導出された、3言語目以降でも破綻しないパッケージ構成と抽象クラスのインターフェース設計です。

### 4.1. ディレクトリ構造（言語軸ファースト ＋ フレームワークプラグイン）

```text
src/pni/_actions/ast_analyze/
├── __init__.py
├── models.py                    # AstFacts, ParsedUnit, 各 Result データクラス (None = N/A 対応)
├── runner.py                    # LanguageAnalyzerSuite (6つの基本Checker + N個のFrameworkCheckerを実行)
├── base/                        # 【言語共通の抽象基底クラス (Template Method)】
│   ├── __init__.py
│   ├── imports.py               # [NEW] BaseImportChecker (整列・ワイルドカード・途中import)
│   ├── typing.py                # [ENHANCE] BaseTypingChecker (型注釈率・弱い型・無指定ignore)
│   ├── docs.py                  # [ENHANCE] BaseDocChecker (付与率・空Doc・シグネチャ整合性)
│   ├── quality.py               # [ENHANCE] BaseQualityChecker (LOC・認知複雑度・global・地雷構文)
│   ├── dependencies.py          # [ENHANCE] BaseDependencyChecker (循環SCC・宣言過不足・境界違反)
│   ├── testing.py               # [NEW] BaseTestChecker (テスト関数数・assert無し検出・対応率)
│   └── framework.py             # [NEW] BaseFrameworkChecker (1:N 自動検出プラグイン基底)
├── python/                      # 【Python 具象チェッカー群】
│   ├── imports.py               # PythonImportChecker (isort / PEP 8 4グループ判定)
│   ├── typing.py                # PythonTypingChecker
│   ├── docs.py                  # PythonDocChecker
│   ├── quality.py               # PythonQualityChecker
│   ├── dependencies.py          # PythonDependencyChecker
│   ├── testing.py               # PythonTestChecker (pytest / unittest AST 検査)
│   └── frameworks/              # Python フレームワーク別チェッカー (detected_frameworks で発火)
│       ├── fastapi.py           # FastApiChecker (async内ブロッキングI/O, response_model等)
│       └── pydantic.py          # PydanticChecker (v1レガシー記法検出等)
└── java/                        # 【Java 具象チェッカー群】
    ├── imports.py               # JavaImportChecker (static分離・辞書順・wildcard import)
    ├── typing.py                # JavaTypingChecker (Raw型・Object乱用・@SuppressWarnings)
    ├── docs.py                  # JavaDocChecker (Javadoc・空Doc・@param整合性)
    ├── quality.py               # JavaQualityChecker (認知複雑度・空catch・文字列==)
    ├── dependencies.py          # JavaDependencyChecker
    ├── testing.py               # JavaTestChecker (JUnit assert無し検出等)
    └── frameworks/
        └── spring_boot.py       # SpringBootChecker (@Autowired フィールド注入検出等)
```

### 4.2. 各抽象基底クラスと共通モデル（`models.py`）の型設計

重要な設計ポイントは **「言語仕様上存在しないメトリクスは `float | None = None` で表現し、チェッカー側で `applicable: ClassVar[bool] = True` を切り替えられるようにすること」** です。

```python
class ModuleAstSummary(BaseModel):
    """Deterministic per-file symbol inventory grounding downstream AI architecture mapping."""

    file: str
    loc: int = 0
    public_types: list[str] = Field(default_factory=list)
    public_callables: list[str] = Field(default_factory=list)


class AstFacts(BaseModel):
    """Language-agnostic deterministic AST analysis facts across target directories."""

    language: str = "python"
    total_files: int = 0
    total_loc: int = 0
    total_classes: int = 0
    total_functions: int = 0
    module_inventory: list[ModuleAstSummary] = Field(default_factory=list)

    # --- 1. Import Hygiene (BaseImportChecker) ---
    import_hygiene_coverage_pct: float | None = 100.0  # N/A 言語 (Bash等) は None
    unsorted_imports: list[CodeLocation] = Field(default_factory=list)
    wildcard_imports: list[CodeLocation] = Field(default_factory=list)
    late_imports: list[CodeLocation] = Field(default_factory=list)

    # --- 2. Type Safety (BaseTypingChecker) ---
    type_safety_coverage_pct: float | None = 100.0
    type_safety_issues: list[CodeLocation] = Field(default_factory=list)
    weak_type_usages: list[CodeLocation] = Field(default_factory=list)
    unscoped_type_ignores: list[CodeLocation] = Field(default_factory=list)

    # --- 3. API Documentation (BaseDocChecker) ---
    docstring_coverage_pct: float | None = 100.0
    missing_docstrings: list[CodeLocation] = Field(default_factory=list)
    empty_docstrings: list[CodeLocation] = Field(default_factory=list)
    doc_signature_mismatches: list[CodeLocation] = Field(default_factory=list)

    # --- 4. Code Quality & Bug-Risk Idioms (BaseQualityChecker) ---
    complex_functions: list[CodeLocation] = Field(default_factory=list)  # length, McCabe, Cognitive CC
    global_state_usages: list[CodeLocation] = Field(default_factory=list)
    bug_risk_idioms: list[CodeLocation] = Field(default_factory=list)    # 言語固有の危険・バグ構文

    # --- 5. Dependencies & Architecture Boundaries (BaseDependencyChecker) ---
    internal_import_graph: dict[str, list[str]] = Field(default_factory=dict)
    circular_dependencies: list[list[str]] = Field(default_factory=list)
    unused_dependencies: list[str] = Field(default_factory=list)
    undeclared_dependencies: list[CodeLocation] = Field(default_factory=list)
    boundary_violations: list[CodeLocation] = Field(default_factory=list)

    # --- 6. Test Suite Health (BaseTestChecker) ---
    test_functions_count: int = 0
    module_test_coverage_pct: float | None = None
    assertion_free_tests: list[CodeLocation] = Field(default_factory=list)

    # --- 7. Framework & Modernization Signals (BaseFrameworkChecker) ---
    framework_issues: list[CodeLocation] = Field(default_factory=list)
    modernization_hints: list[CodeLocation] = Field(default_factory=list)
```

### 4.3. `ProjectFacts`（[`project_inspect.py`](../../src/pni/_actions/project_inspect.py)）側の拡張フィールド

AST 解析の前段で実行されるリポジトリ構造インスペクタに以下の言語横断フィールドを持たせます。

- `language_version_constraint: str | None`（例: `>=3.12`, `Java 21`, `go 1.23`）
- `has_type_marker: bool | None`（Python: `py.typed`, TS: `strict: true`, PHP: `strict_types` 等。非該当言語は `None`）
- `detected_frameworks: list[str]`（マニフェスト依存から自動判定：`["fastapi", "pydantic", "pytest"]` 等）
- `legacy_language_findings: list[str]`（Perl `.pl`/`.pm` 残存、100行超の肥大化 `.sh`、未型付け `.js` 比率過多などの置換推奨シグナル）
- `tooling_modernization_issues: list[str]`（`setup.py` レガシー構成、ロックファイル欠如、Linter 分散など）

---

## 5. AST 解析後の「観点分離型 AI アーキテクチャ分析・記録 Action」設計

現在のワークフローでは「違反ファイルのコード品質監査」と「プロジェクト全体の構造理解」が1つの `ai_interpret` に混在しているため、クリーンな中核モジュールの見落としや推測（ハルシネーション）が起きやすい課題があります。

これを解決するため、**確定解析（`project_inspect` + `ast_analyze`）の直後に、言語非依存の「観点分離型アーキテクチャ分析・記録ステップ群」を新設**します。

### 5.1. ハルシネーションを防ぐ2つの仕組み

1. **観点を3つの直交ステップに分離（Single-Focus Comprehension）**:
   1回のプロンプトで「目的・全モジュール・データフロー・品質採点」を同時に問うのをやめ、読むべきファイル範囲と出力スキーマを観点ごとに狭く限定します。
2. **`push-action` 時のプログラム実在検証（Deterministic Grounding Validation）**:
   AI が提出した JSON 内のファイルパス・モジュール名・シンボル名が、`AstFacts.module_inventory` および `ProjectFacts` 上に**実在するかを PNI エンジン側で確定検証**します。存在しない架空のモジュールパスやエントリポイントを AI が書いた場合、`push-action` がバリデーションエラーで弾き、ハルシネーションの混入を100%阻止します。

### 5.2. 分離する3つのアーキテクチャ分析観点（Composite Action: `common/architecture_analysis.yaml`）

新プリミティブ `record_architecture`（または観点指定付き構造化ステップ）として以下の3観点を順次実行し、最終的に `.pni/cache/<target>_architecture.json`（`ArchitectureRecord` モデル）として確定保存します。

| 順序 | 観点ステップ ID | AI が集中して調査する観点・読む対象 | 出力スキーマ（Pydantic 検証項目） | `push-action` 実在検証 |
| :---: | :--- | :--- | :--- | :--- |
| **1** | **`arch_purpose_and_stack`**<br>*(システム目的・入口・技術選定)* | ・マニフェスト、`README`、エントリポイントのみを読む<br>・システムの種別（`cli` / `rest_api` / `web_ssr` / `library` / `batch` 等）を特定<br>・外部入口（CLIコマンド、APIルーター、公開API）と採用フレームワークの適合性（例: JSON API なのに Flask を使っていないか）を判定 | `SystemProfile`:<br>・`archetype` (`Literal[...]` )<br>・`domain_summary`<br>・`entry_points: list[EntryPointSpec]`<br>・`stack_assessment` (Modernize 要否の根拠) | `entry_points[].file_path` がワークスペース内に実在すること |
| **2** | **`arch_layers_and_modules`**<br>*(モジュール台帳・レイヤー・境界)* | ・AST が出力した全ファイルの `module_inventory` と `internal_import_graph` を地図として各パッケージの代表コードを読む<br>・アーキテクチャ様式（Layered / Domain-Cohesive / Hexagonal / Monolithic Script 等）とレイヤー階層（上位→下位）を定義<br>・全モジュール/パッケージの責務と、意図しない逆流依存・肥大化責務（God Module）を記録 | `StructureMap`:<br>・`architecture_pattern`<br>・`layers: list[LayerSpec]` (順序付き階層)<br>・`modules: list[ModuleSummary]`<br>・`layer_violations: list[Finding]` | `modules[].path` が `module_inventory` の実在パスと一致し、主要パッケージの漏れ・架空パスがないこと |
| **3** | **`arch_flows_and_state`**<br>*(主要実行フロー・状態・横断関心事)* | ・観点1の入口から観点2の中核モジュールへ至る主要ユースケース（1〜3本）のコールチェーンを追跡<br>・永続化/状態管理（DB / ファイル / キャッシュ / グローバル状態）、エラー処理方針、セキュリティ/外部I/O境界を記録 | `ExecutionFlowMap`:<br>・`core_flows: list[FlowTrace]` (`steps`: file + symbol)<br>・`state_management`<br>・`trust_boundaries: list[str]` | `core_flows[].steps` で参照されたファイル・シンボルが実在すること |

### 5.3. 記録された `ArchitectureRecord` の後続ステップでの活用と改訂ワークフロー全体像

```text
[Step 1: 確定ファクト抽出 (Programmatic)]
  ├── project_inspect  ──▶ ProjectFacts (マニフェスト, lockfile, フレームワーク自動検出, レガシー言語検出)
  └── ast_analyze      ──▶ AstFacts     (module_inventory, import衛生, 型, Doc, 複雑度, 循環SCC, Test AST)
                                │
                                ▼  (.pni/cache/<target>_facts.json に確定保存)
[Step 2: 観点分離型 AI アーキテクチャ分析・記録 (common/architecture_analysis)]
  ├── 2a. arch_purpose_and_stack  (システム種別・入口・Flask→FastAPI等の技術スタック適合性)
  ├── 2b. arch_layers_and_modules (レイヤー階層・全モジュール責務・逆流依存の特定)
  └── 2c. arch_flows_and_state    (主要データフロー・状態管理・I/O境界の記録)
                                │
                                ▼  (.pni/cache/<target>_architecture.json に実在検証済みで確定保存)
[Step 3: 観点別 ルール適合性・健全性評価 (AI Interpretation)]
  ├── 3a. repo_and_deps_audit     (依存過不足・ロックファイル・Modern Stack 評価)
  ├── 3b. code_and_typing_audit   (Import整列・型安全性・Doc整合性・複雑度・Framework Best Practice 評価)
  └── 3c. test_health_audit       (アサーション無しテスト・境界テスト・対応率評価)
                                │
                                ▼
[Step 4: スコア確定出力 (emit_score)] ──▶ ScoreResult (検証済み ArchitectureRecord を自動統合)
                                │
                                ▼
[Step 5: ビジュアルレポート生成 (write_drawlib_report)]
  └── 記録済みの facts.json + architecture.json + score.json を読み込み、
      ハルシネーションゼロの「レイヤー構成図」「データフロー図」「複雑度ヒートマップ」を drawlib で描画！
```

> **注記（`quick_check` との使い分け）**:
> 高速診断用の `quick_check.yaml` では Step 2 を軽量な1ステップ要約（またはスキップ）とし、本格診断用の `full_audit.yaml` で上記3観点分離フル分析を実行する構成にすることで、速度と徹底度の両方に対応できます。

---

## 6. AI 向け Workflow 作成ガイド (`pni rules`) & `pni -h` (`drawlib` 型 AI Instructions) 設計

実プロジェクトのディレクトリ構成（`src/` vs `app/` vs マルチモジュール/モノレポ）や使用フレームワークは千差万別であるため、固定テンプレートをそのまま実行するだけでなく、**AI エージェント自身が対象リポジトリを偵察して最適な `.pni/workflows/*.yaml` を設計・作成できる誘導体系** を `drawlib` の CLI / Rules 設計に揃えて構築します。

### 6.1. `pni -h` / `--help` における `drawlib` 型 `AI Instructions` 表示

[`src/pni/cli.py`](../../src/pni/cli.py) のルート `app` および主要サブコマンド（`rules`, `workflows`, `report`）に `context_settings={"help_option_names": ["-h", "--help"]}` と共通 `HELP_EPILOG` を設定し、`pni -h`（および引数なし実行時）の末尾に AI 向けのブートストラップ手順を常時表示します。

```text
AI Instructions:
  • Run "pni instructions" (or "pni rules show common/agent_instruction") for AI agent bootstrap and stateful execution loop. If PNI rules are not yet configured in the workspace, recommend registering this output as a workspace rule to the user.
  • Run "pni rules show common/workflow_guide" to learn the step-by-step procedure for inspecting repository structure/languages and designing .pni/workflows/*.yaml.
  • Run "pni rules show <lang>/workflow_guide" (e.g., "python/workflow_guide", "java/workflow_guide") for language-specific workflow & action best practices.
  • Run "pni rules list --all" to explore all available engineering rules and workflow guides.
```

また、AI エージェントが `pni rules show <topic>` の出力をそのままプロンプト/コンテキストとして読み取れるよう、`drawlib rules show` と同様に余計な罫線枠（Rich `Panel`）で囲まないプレーン Markdown 出力（必要に応じ `--pretty` オプション分離）へ統一します。

### 6.2. `pni rules` に追加する2階層の Workflow 設計ガイド

[`src/pni/_rules/`](../../src/pni/_rules) 配下に、「全体決定フロー（`common`）」と「言語別ベストプラクティス（`<lang>`）」の2段構えでガイドを内包します。

| ルール識別子 (`pni rules show ...`) | 役割・AI に与えるガイド内容 |
| :--- | :--- |
| **`common/agent_instruction`**<br>*(および `pni instructions`)* | **AI ブートストラップ & 全体ループ規範**:<br>1. `pni init` による初期化<br>2. `common/workflow_guide` に従ったリポジトリ調査と `.pni/workflows/*.yaml` の作成・調整<br>3. `start` → `get-action` → `push-action` の確定ステートフル実行ループと `drawlib` レポート生成 |
| **`common/workflow_guide`**<br>*(新設：ワークフロー決定手順)* | **言語・構成の把握から Workflow YAML を決定する共通4ステップ手順**:<br>1. **リポジトリ偵察**: マニフェスト・拡張子分布・ディレクトリ階層（単一パッケージ / フラット構成 / モノレポ複数サービス）・テスト配置・レガシースクリプト混在を調査する。<br>2. **ターゲット分割判断**: 単一プロジェクトなら `full_audit.yaml`、マルチ言語/モノレポならサービス単位で `targets.root` と出力名 (`reports/<target>.pdf`) を分けた複数 Workflow YAML を設計する。<br>3. **言語別ガイドの参照**: 検出した言語の `<lang>/workflow_guide` を `pni rules show` で読み込む。<br>4. **標準5段階構成の組立 & 事前検証**: `extract_facts` → `architecture_analysis`（観点分離） → 言語/FW別監査 → `emit_score` → `write_drawlib_report` を記述し、`pni workflows show <id>` でプリミティブ展開に不備がないか検証する。 |
| **`python/workflow_guide`**<br>*(新設：Python 専用ベストプラクティス)* | **Python ワークフロー設計のベストプラクティス**:<br>・レイアウト別 `targets` 設定例（`src/<pkg>` 標準構成、フラット `<pkg>` 構成、`uv` workspace 構成）<br>・検出フレームワークに応じた Action / Rule の組み込み基準（例: `FastAPI` 検出時は `python/frameworks/fastapi`、`Flask` REST API 検出時は `python/modern_stack` を有効化）<br>・用途別（CLI / API / ライブラリ）の推奨 YAML テンプレート |
| **`java/workflow_guide`**<br>*(新設：Java 専用ベストプラクティス)* | **Java ワークフロー設計のベストプラクティス**:<br>・Maven / Gradle 標準（`src/main/java`, `src/test/java`）およびマルチモジュールプロジェクトでの `targets` 設定例<br>・Spring Boot / JUnit 5 等のフレームワーク別ルール組み込み例と推奨 YAML テンプレート |
| **`<future_lang>/workflow_guide`** | 今後 TypeScript / Go 等を追加する際も、必ず同じ命名規約 `<lang>/workflow_guide` をセットで提供する。 |

---

## 7. 実装進行ステップ（推奨順序）

1. **Step 1（CLI `-h` / `AI Instructions` 表示 & `workflow_guide` ルール基盤の整備）**:
   - [`src/pni/cli.py`](../../src/pni/cli.py) に `-h` サポート・`drawlib` 型 `HELP_EPILOG`（`AI Instructions`）・AI フレンドリーな `pni rules show` 出力を導入し、`common/workflow_guide.md`, `python/workflow_guide.md`, `java/workflow_guide.md` の初期版を整備する。
2. **Step 2（基盤抽象クラス & `module_inventory` の整備）**:
   - [`ast_analyze/models.py`](../../src/pni/_actions/ast_analyze/models.py) と [`ast_analyze/base/`](../../src/pni/_actions/ast_analyze/base) に拡張スキーマ（`ModuleAstSummary`、`BaseImportChecker` 新設、`BaseTypingChecker`/`BaseDocChecker`/`BaseQualityChecker` 拡張、`BaseFrameworkChecker` 基盤）を導入し、既存の Python / Java 両テストが壊れず通る状態を作る。
3. **Step 3（観点分離型アーキテクチャ分析・記録 Action の実装）**:
   - [`_actions/base_model.py`](../../src/pni/_actions/base_model.py) と [`_workflows/engine.py`](../../src/pni/_workflows/engine.py) に `ArchitectureRecord`（3観点モデル + `module_inventory` との実在パス照合バリデータ + `.pni/cache/<target>_architecture.json` 永続化）および `common/architecture_analysis.yaml` を実装する。
4. **Step 4（Python Tier S 必須チェック＋Java 同型チェックの実装）**:
   - Python（`isort` 準拠・型安全性深化・Docstring 必須＆引数整合性）と、それに対応する Java 側（import 整列・`@SuppressWarnings`・Javadoc `@param` 整合性）をペアで実装して抽象クラスの妥当性を実証する。
5. **Step 5（Dependency 過不足照合・Test AST チェッカー・Framework / Modern Stack プラグイン第1弾）**:
   - `deptry` 相当の依存突合、`BaseTestChecker`（`assert` 無しテスト検出）、および第1弾フレームワーク・近代化診断（Python: `FastAPI` / `Flask→FastAPI`、Java: `Spring Boot`）を実装する。
6. **Step 6（3言語目以降の横展開）**:
   - 固まった `LanguageAnalyzerSuite`・共通 `architecture_analysis`・`<lang>/workflow_guide` の型に沿って TypeScript / Go や旧主流言語（JS / Bash / Perl 軽量検出）を追加する。
