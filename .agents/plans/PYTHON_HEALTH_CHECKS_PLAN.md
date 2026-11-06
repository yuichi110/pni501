# Python コード・プロジェクト健全性検査 詳細仕様 & 優先度計画書

本ドキュメントは、多言語・フレームワーク横断の全体設計書である [CHECK_LANGUAGE_MATRIX_PLAN.md](./CHECK_LANGUAGE_MATRIX_PLAN.md) と対になる **Python 専用の詳細設計書** です。

Python エコシステムの著名ツールの調査結果、有効性 × 実装難易度のランク付け、および共通抽象クラス群（[`src/pni/_actions/ast_analyze/base/`](../../src/pni/_actions/ast_analyze/base)）を具象化する **Python 固有の AST アルゴリズム・フレームワーク検査（FastAPI 等）・Modern Stack 移行判定（Flask → FastAPI 等）** の詳細を定義します。

---

## 1. 著名な Python 健全性検査ツールの調査サマリー（8領域）

| 領域 | 代表的な著名ツール | 主な検査基準・メトリクス |
| :--- | :--- | :--- |
| **1. コード品質・バグ構文・Import 整列** | **Ruff** (`F`/`E`/`I`/`B`/`UP`/`SIM`/`C90`/`PT`/`RUF`), **Pylint**, **Flake8**, **Vulture** | 未使用変数/import、**`isort` 準拠の import 分類・空行・辞書順整列 (`I001`)**、ミュータブルデフォルト引数等のバグ温床 (`flake8-bugbear`)、例外握りつぶし、旧式構文 (`pyupgrade`)、デッドコード (`Vulture`) |
| **2. 複雑度・保守性指標** | **Radon**, **Xenon**, **complexipy**, **Wily** | **循環的複雑度 (McCabe CC)**、**認知的複雑度 (Cognitive Complexity: ネスト深さ加重)**、Halstead 指標、保守性指数 (Maintainability Index: `0〜100`)、関数行数・引数数 |
| **3. 型安全性・API 型網羅性** | **Pyright** (`--verifytypes`), **mypy** (`--strict` + `--any-exprs-report`), **ty** | 引数・戻り値・属性の**型ヒント付与率**、公開シンボルの **Type Completeness Score**、`Any` 混入率、エラーコード無指定の `# type: ignore`、PEP 561 `py.typed` マーカー有無 |
| **4. アーキテクチャ・モジュール境界** | **import-linter**, **Tach**, **pydeps** | レイヤー違反（下位→上位の逆流 import）、循環依存 (SCC: 強連結成分)、モジュール間の不安定度 $I = C_e / (C_a + C_e)$、プライベートモジュール (`_internal`) の外部参照禁止 |
| **5. 依存関係・パッケージ構成衛生** | **deptry**, **sp-repo-review** (Scientific Python), **validate-pyproject** | **`pyproject.toml` 宣言と実コード `import` の照合**（未宣言依存 `DEP001`・未使用依存 `DEP002`・開発依存の本番混入 `DEP004`）、PEP 621 メタデータ完備、`src/` レイアウト、ロックファイル有無 |
| **6. セキュリティ・サプライチェーン** | **Bandit** (`flake8-bandit`), **Semgrep**, **pip-audit**, **OpenSSF Scorecard** | 危険 API 呼び出し (`eval`/`exec`, `shell=True`, `yaml.load`, `pickle`)、ハードコード秘密情報、依存パッケージの既知 CVE、CI 権限・ピン留め運用 |
| **7. テスト健全性・実効性** | **pytest**, **coverage.py** (`branch=True`), **mutmut**, **Hypothesis** | 分岐カバレッジ (Branch Coverage)、**アサーション無しテスト (Assertion-free test) の検出**、テスト対ソース比率、モック過多率、ミューテーションスコア |
| **8. Docstring 品質・Git Hotspot** | **interrogate**, **pydoclint**, **pydocstyle** (`Ruff D`), **CodeScene**, **SonarQube** | モジュール/公開クラス/公開関数の **Docstring カバレッジ**、**関数シグネチャ（引数・戻り値）と Docstring 記述の一致検証**、**Git 変更頻度 (Churn) × 複雑度** によるホットスポット特定 |

---

## 2. Python 検査項目の優先度ランク付け（有効性 × 実装難易度）

`pni501` 単体（`ast-grep-py` + Python 標準ライブラリ）で外部 CLI 依存なしに高速・確定実行できるかを踏まえた優先度ランキングです。

| Tier | 順位 | 検査項目 | 対応チェッカー | PNI 現状 | 有効性 | 実装難易度 | 理由・ROI |
| :---: | :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| **Tier S**<br>*(必須)* | **S-1** | **Import 整列・グルーピング検査 (`isort` 準拠)** | `PythonImportChecker` | **未実装** | `★★★★★` | **低 (易)** | `sys.stdlib_module_names` + AST 行番号のみで外部ツール無しに完全確定判定可能。 |
| **Tier S**<br>*(必須)* | **S-2** | **型アノテーション徹底 & 型抜け道検出** | `PythonTypingChecker` + `project_inspect` | 一部実装済 | `★★★★★` | **低 (易)** | 引数/戻り値/属性の未注釈箇所リスト、生ジェネリクス (`list` 等)、裸の `# type: ignore`、`py.typed` 検査を低コストで網羅可能。 |
| **Tier S**<br>*(必須)* | **S-3** | **Docstring 必須化 & シグネチャ整合性検査** | `PythonDocChecker` | 基本実装済 | `★★★★★` | **低〜中** | `@overload` 除外、空/`TODO` Docstring 検出、`Args:` と実 AST 引数の不一致検出でドキュメントの形骸化を確実に捕捉。 |
| **Tier A**<br>*(高ROI)* | **A-1** | **`pyproject.toml` 宣言依存 vs 実 `import` 突合** | `PythonDependencyChecker` | 未実装 | `★★★★★` | **低〜中** | `deptry` 相当（未使用依存・未宣言依存・Dev依存の本番混入）を確定検出可能。 |
| **Tier A**<br>*(高ROI)* | **A-2** | **認知的複雑度 (Cognitive Complexity) & 引数過多** | `PythonQualityChecker` | 基本CCのみ | `★★★★☆` | **低 (易)** | ネスト深さ加重により真に読みづらい複雑関数を特定。 |
| **Tier A**<br>*(高ROI)* | **A-3** | **Python 地雷・危険構文 (`bug_risk_idioms`)** | `PythonQualityChecker` | 未実装 | `★★★★☆` | **低 (易)** | 可変デフォルト引数、裸の `except:`、`eval`/`shell=True`/`yaml.load` 等を `ast-grep` で即座に検出。 |
| **Tier A**<br>*(高ROI)* | **A-4** | **テストコード AST 検査 (`tests/`)** | `PythonTestChecker` | 未実装 | `★★★★☆` | **低〜中** | `assert` / `pytest.raises` 無しの形骸化テスト検出、公開モジュール対テスト対応率を確定算出。 |
| **Tier A**<br>*(高ROI)* | **A-5** | **FastAPI 等のフレームワーク検査 & Modern Stack 診断** | `FastApiChecker` + `project_inspect` + Rules | 未実装 | `★★★★★` | **低〜中** | `async def` 内の同期ブロッキング検出や `Flask → FastAPI` 移行提案など、PNI ならではの付加価値が高い。 |
| **Tier B**<br>*(発展)* | **B-1** | **Git Churn × 複雑度 ホットスポット** | `git_inspect` (仮) | 未実装 | `★★★★☆` | **中** | `git log` 変更回数 × 複雑度で危険ファイルを特定し `drawlib` ヒートマップへ連携。 |
| **Tier B**<br>*(発展)* | **B-2** | **プライベートモジュール (`_internal`) 越境参照** | `PythonDependencyChecker` | 循環のみ済 | `★★★★☆` | **低〜中** | 他パッケージの `_` 始まり非公開モジュールを外部から import している箇所を検出。 |
| **Tier B**<br>*(発展)* | **B-3** | **重複コード (Clone) / Dead Code 横断検出** | `PythonQualityChecker` | 未実装 | `★★★☆☆` | **中〜高** | 動的呼び出し・フレームワーク Hook による偽陽性対策が必要。 |
| **Tier C**<br>*(外部向き)* | **C-1** | **既知 CVE 監査 (`pip-audit`) / ミューテーション (`mutmut`)** | 外部連携 | 未実装 | `★★★☆☆` | **高 (通信/時間)** | ネットワーク依存・長時間実行のためオフライン確定プリミティブからは分離。 |

---

## 3. 各具象チェッカー（`src/pni/_actions/ast_analyze/python/`）の詳細仕様

[CHECK_LANGUAGE_MATRIX_PLAN.md](./CHECK_LANGUAGE_MATRIX_PLAN.md) で定義した6つの言語共通抽象クラス + フレームワークプラグインに対する Python 具象クラスの仕様です。

### 3.1. `PythonImportChecker` (`python/imports.py` — `BaseImportChecker` 継承)【Tier S-1】

- **対象 AST ノード (`tree-sitter-python`)**:
  - `import_statement`（例: `import os`, `import numpy as np`）
  - `import_from_statement`（例: `from pathlib import Path`, `from .models import AstFacts`）
  - `wildcard_import`（例: `from module import *` → 即座に `wildcard_imports` に記録）
- **スコープ判定**:
  - `module` 直下の連続する import 文（および `if TYPE_CHECKING:` ブロック直下の import 文）をトップレベル import セクションとして扱う。
  - `function_definition` / `class_definition` 内部、または実行ステートメントの後に出現する import 文（`__future__` やモジュール Docstring 直後以外）を `late_imports`（Ruff `PLC0415` 相当）として記録する。
- **`isort` / Ruff `I001` 互換の4グループ分類ロジック**:
  0. **`FUTURE` (Group 0)**: `from __future__ import ...`
  1. **`STDLIB` (Group 1)**: ルートモジュール名が `sys.stdlib_module_names`（Python 3.11+ 標準セット）に含まれるもの
  2. **`THIRD_PARTY` (Group 2)**: 相対 import でなく、`STDLIB` でもプロジェクト内 `root_packages` でもない外部パッケージ
  3. **`FIRST_PARTY` (Group 3)**: プロジェクトの `src/` またはルート配下で検出されたパッケージ名（`root_packages`）に一致するもの、または先頭 `.` を持つ `relative_import`
- **検証する3条件（`unsorted_imports` 判定）**:
  1. **グループ順序**: トップレベル import 列において Group 番号が単調非減少（`0 ≤ 1 ≤ 2 ≤ 3`）であること。
  2. **グループ間空行**: Group 番号が切り替わる箇所で、`prev_node.range().end.line` と `curr_node.range().start.line` の間に少なくとも1行の空行（行番号差 `>= 2`、直前コメント行を考慮）があること。
  3. **グループ内ソート**: 同一グループ内で「ストレート `import` → `from ... import`」の順であり、モジュールパスが辞書順（小文字正規化キー）に並んでいること。さらに同一 `from x import a, b` 内のインポート名リストも整列されていること。

---

### 3.2. `PythonTypingChecker` (`python/typing.py` — `BaseTypingChecker` 継承)【Tier S-2】

既存の [`PythonTypingChecker`](../../src/pni/_actions/ast_analyze/python/typing.py) を以下の通り拡張します。

1. **関数・メソッド型注釈 (`type_safety_issues`)**:
   - 全ての `function_definition` について、全パラメータ（第1引数 `self` / `cls` を除く通常引数、デフォルト付き引数、`*args`、`**kwargs`、keyword-only 引数）および戻り値 `-> ...` の有無を検査。
   - 現在はカバレッジ `%` のみ集計して未注釈関数の箇所を捨てていたため、未注釈の引数または戻り値がある関数を `type_safety_issues` に `CodeLocation` として明示出力する。
2. **クラス属性の型注釈チェック**:
   - `class_definition` 直下の `expression_statement > assignment` において、`type` フィールドを持たないクラス変数・フィールド定義（`__slots__` 等の特殊属性を除く）を `type_safety_issues` に含める。
3. **弱い型・未パラメータ化ジェネリクス (`weak_type_usages`)**:
   - `Any` の使用に加え、型注釈ノード内で型引数（`generic_type` の `[...]`）を伴わない生の組み込みコンテナ型（`list`, `dict`, `tuple`, `set`, `Callable` 単体）を検出する。
4. **無指定の `# type: ignore` 検出 (`unscoped_type_ignores`)**:
   - `comment` ノードを走査し、`[error-code]` を伴わない裸の `# type: ignore` および `# pyright: ignore`（Ruff `PGH003` 相当）を行番号付きで記録する。
5. **旧式型構文の近代化ヒント (`modernization_hints`)**:
   - `typing.List`, `typing.Dict`, `typing.Tuple`, `typing.Optional`, `typing.Union` のインポート・使用を検出し、PEP 585 (`list[T]`) / PEP 604 (`T | None`) への移行ヒントを記録する。
6. **`py.typed` マーカー検査（[`project_inspect.py`](../../src/pni/_actions/project_inspect.py)）**:
   - 公開パッケージディレクトリ直下に `py.typed` が存在するかを `ProjectFacts.has_type_marker` として記録する。

---

### 3.3. `PythonDocChecker` (`python/docs.py` — `BaseDocChecker` 継承)【Tier S-3】

既存の [`PythonDocChecker`](../../src/pni/_actions/ast_analyze/python/docs.py) を以下の通り強化します。

1. **必須対象の整理と `@overload` 除外**:
   - 対象：モジュール先頭、公開クラス（`not name.startswith("_")`）、公開関数・公開メソッド（`not name.startswith("_")` かつ非ネスト）。
   - `decorated_definition` に `@overload`（または `@typing.overload`）が付与されている型スタブ関数は、直後の実装本体にのみ Docstring を書くのが Python 標準規約であるため、必須母数から除外する。
2. **空・プレースホルダー Docstring の検出 (`empty_docstrings`)**:
   - クォートと空白・改行を取り除いた実質テキストが空文字、または `TODO`, `TBD`, `FIXME`, `...` のみの Docstring を `empty_docstrings` に記録し、未記述（非カバー）として扱う。
3. **Docstring 引数セクションと実 AST 引数の整合性検査 (`doc_signature_mismatches`)**:
   - Google スタイル（`Args:` / `Keyword Args:`）、NumPy スタイル（`Parameters\n----------`）、Sphinx スタイル（`:param <name>:`）のいずれかで引数が記述されている Docstring をパース。
   - Docstring 記載の引数名集合と、AST から抽出した実パラメータ名集合（`self`/`cls` 除外、`*args`/`**kwargs` 正規化）を比較し、**「実コードに存在するが `Args:` から漏れている引数」** または **「削除・リネーム済みなのに `Args:` に残存している幽霊引数」** を確定検出する。

---

### 3.4. `PythonQualityChecker` (`python/quality.py` — `BaseQualityChecker` 継承)【Tier A-2 / A-3】

1. **Cognitive Complexity（認知的複雑度）の導入**:
   - 単純な分岐ノード数（McCabe 風）だけでなく、`if_statement`, `for_statement`, `while_statement`, `try_statement`, `match_statement` がネストするたびに `+ (1 + current_nesting_depth)` を加算する認知的複雑度を算出し、閾値（例: `> 15`）超過を `complex_functions` に詳細値付きで出力する。
   - 引数過多（例: `self`/`cls` を除き `> 6` 個のパラメータを持つ関数）も設計上の不吉な臭い（Long Parameter List）として検出可能にする。
2. **Python 固有の地雷・セキュリティ構文 (`bug_risk_idioms`)**:
   - **可変デフォルト引数 (`Ruff B006`)**: `default_parameter` / `typed_default_parameter` のデフォルト値に `list` (`[...]`), `dict` (`{...}`), `set` リテラルや `list()`/`dict()`/`set()` 呼び出しが使われている箇所。
   - **例外の握りつぶし (`Ruff E722 / S110`)**: 型指定のない裸の `except:`、または `except Exception: pass`（ログも再送出もコメントもない完全無視）。
   - **危険 API 使用 (`Bandit S`)**: `eval(...)`, `exec(...)`, `subprocess.*(..., shell=True)`, `pickle.loads(...)`, `SafeLoader` 指定のない `yaml.load(...)`。

---

### 3.5. `PythonDependencyChecker` (`python/dependencies.py` — `BaseDependencyChecker` 継承)【Tier A-1 / B-2】

1. **`deptry` 風のマニフェスト宣言 vs 実 Import 過不足突合**:
   - [`project_inspect.py`](../../src/pni/_actions/project_inspect.py) が抽出した本番 `dependencies` と `dev_dependencies` のパッケージ名を PEP 503 正規化（`-` / `_` 統一 + 代表的な配布名↔import名マッピング辞書 `pillow -> PIL`, `pyyaml -> yaml`, `beautifulsoup4 -> bs4`, `scikit-learn -> sklearn`, `ast-grep-py -> ast_grep_py` 等 + 環境内の `importlib.metadata.packages_distributions()` 補助利用）で解決。
   - **未使用依存 (`unused_dependencies`)**: `pyproject.toml` の `[project.dependencies]` にあるが `src/` 内で一度も import されていないパッケージ（CLI ツール専用パッケージ等の除外リスト考慮）。
   - **未宣言・Dev混入依存 (`undeclared_dependencies`)**: `src/` 内でサードパーティとして import されているのに `[project.dependencies]` に宣言されていない（誤って `dev` グループにのみ入っているケースを含む）箇所。
2. **プライベートモジュール越境参照 (`boundary_violations`)**:
   - 異なるトップレベル/サブパッケージ外から、アンダースコア始まりの非公開モジュール（例: `pni._workflows` が他ドメインの非公開内部ヘルパー `pni._reporter._internal` を直接 import する等、同一ドメイン外からの `_` モジュール直参照）を検出する。

---

### 3.6. `PythonTestChecker` (`python/testing.py` — `BaseTestChecker` 継承)【Tier A-4】

- **`tests/` ディレクトリの AST 解析**:
  1. `test_*` 関数および `Test*` クラス内の `test_*` メソッド総数を `test_functions_count` として集計。
  2. **アサーション無しテスト検出 (`assertion_free_tests`)**:
     - テスト関数本体内に `assert_statement`、`pytest.raises`、`pytest.warns`、`pytest.fail`、`self.assert*`、モックの `.assert_called*` のいずれも存在しない「実行するだけで検証していないテスト」をピンポイント抽出。
  3. **公開モジュール対テスト対応率 (`module_test_coverage_pct`)**:
     - `src/<pkg>/foo.py` に対して `tests/**/test_foo.py`（または `foo` を import しているテストファイル）が存在する割合を算出。

---

## 4. Python フレームワーク検査 & Modern Stack 移行推奨の詳細

### 4.1. Python フレームワーク別 AST チェッカー (`python/frameworks/`) & Rules (`_rules/python/frameworks/`)

`project_inspect.py` の `detected_frameworks` によって自動有効化されるモジュール群です。

| フレームワーク | 自動検出キー (`pyproject.toml`) | AST 確定検査 (`framework_issues`) | AI Rules (`_rules/python/frameworks/*.md`) での審査観点 |
| :--- | :--- | :--- | :--- |
| **FastAPI** | `fastapi` | 1. **`async def` ルート関数内の同期ブロッキング呼び出し**: `time.sleep()`, `requests.get/post/...`, 同期ファイルI/O、同期 `Session` 操作を確定検出（イベントループ停止事故の防止）<br>2. エンドポイントデコレータ (`@router.get` 等) での `response_model` も戻り値型アノテーションも両方欠落している箇所の検出<br>3. `HTTPException` で `status_code` にマジックナンバーを使っている箇所の軽微指摘 | ・`APIRouter` によるドメイン分割<br>・`Depends()` による DI とテスト容易性<br>・Pydantic スキーマの Request / Response / DB モデル分離<br>・Lifespan コンテキストマネージャの使用（非推奨 `@app.on_event("startup")` 回避） |
| **Pydantic** | `pydantic` | 1. **Pydantic v1 非推奨記法**: `class Config:`（→ `model_config = ConfigDict(...)`）、`@validator`（→ `@field_validator`）、`.dict()` / `.json()` / `.parse_obj()`（→ `.model_dump()` / `.model_validate()`）の検出<br>2. `Field(default=[])` のようなミュータブルデフォルトの検出 | ・境界（CLI入力・API入出力・設定ファイル・LLM構造化出力）での積極活用<br>・`Annotated` + `Field` による制約表現 |
| **SQLAlchemy** | `sqlalchemy` | 1. レガシー 1.x スタイル `session.query(...)` や `Column(...)` 宣言（→ 2.0 `select()` + `Mapped[...]` / `mapped_column()`）の検出 | ・Unit of Work / セッションライフサイクル管理<br>・N+1 クエリ防止 (`selectinload` / `joinedload`) |
| **Typer / Click** | `typer`, `click` | 1. CLI コマンド関数における引数型ヒント・ヘルプ Docstring の欠落検出 | ・サブコマンド階層整理、終了コード規約、Rich 出力連携 |

---

### 4.2. Python Modern Stack（エコシステム近代化・移行推奨）基準

[`project_inspect.py`](../../src/pni/_actions/project_inspect.py) の確定ファクトと `_rules/python/modern_stack.md`（新設予定）を組み合わせ、以下の基準で近代化診断を行います。

#### ① 客観的レガシー負債（無条件で減点・改善要求）
- **パッケージング**: `setup.py` / `setup.cfg` / `requirements.txt` 単体運用 → **PEP 621 `pyproject.toml` + ロックファイル（`uv.lock` 推奨）** への移行
- **品質ツール分散**: `flake8` + `isort` + `black` + `pyupgrade` の個別導入 → **`Ruff` への一本化** 推奨
- **Python バージョン**: `requires-python` 未指定、または EOL バージョン（Python 3.9 以下）指定 → **Python 3.12+** 推奨
- **標準ライブラリ旧習**: `os.path.*` 多用 → **`pathlib.Path`**、`%` フォーマット / `.format()` 多用 → **f-string**、`logging` 生設定ボイラープレート等

#### ② 用途・文脈に応じた Modern Framework 移行推奨（AI × 確定ファクト連携）
- **Web / API フレームワーク (`Flask` / `Bottle` / `Falcon` → `FastAPI` 推奨)**:
  - **確定ファクト抽出**: `detected_frameworks` に `flask` が含まれる場合、併せて「Jinja2 `.html` テンプレートファイルの有無」「`jsonify` / JSON レスポンス比率」「OpenAPI / Pydantic / Marshmallow 等のスキーマ検証ライブラリの有無」を集計する。
  - **判定ルール**:
    - テンプレートを持たない（または極小の）**REST / JSON API サーバーやマイクロサービス**で `Flask` を使用している場合 → **型安全性・Pydantic v2 統合・OpenAPI 自動生成・非同期対応の観点から `FastAPI`（または `Litestar`）への移行を明確に推奨** する。
    - 伝統的なサーバーサイド HTML レンダリング（Jinja2 中心）の小規模管理ツールや、Django Admin / ORM フルスタック要件が明確なプロジェクトでは、無理な置換推奨は行わず現行フレームワークのベストプラクティス遵守を評価する。
- **CLI フレームワーク (`argparse` / `optparse` / `sys.argv` 直パース → `Typer` 推奨)**:
  - サブコマンドや多数のオプション（例: `add_argument` が5個以上）を持つ CLI で標準 `argparse` を手書きしている場合 → 型ヒントと Docstring から自動で CLI と補完を生成できる **`Typer`**（ゼロ外部依存が必須のライブラリを除く）への移行を推奨する。
- **HTTP クライアント (`urllib.request` / 非同期内 `requests` → `httpx` 推奨)**:
  - `async def` を使うコードベースで `requests` が混在している場合 → 同期・非同期両対応で型定義も完備された **`httpx`** への統一を推奨する。
- **肥大化シェルスクリプト / Perl スクリプトの Python 化**:
  - リポジトリ内に 100 行を超える `.sh` や `.pl` スクリプトが存在する場合 → テスタビリティ・型安全性・エラーハンドリングの観点から **Python (`Typer` + `pytest`)** への置き換えを推奨する。

---

## 5. Python ワークフロー (`python/full_audit.yaml`) と観点分離型アーキテクチャ分析の統合

[CHECK_LANGUAGE_MATRIX_PLAN.md の Section 5](./CHECK_LANGUAGE_MATRIX_PLAN.md#L184) で設計した通り、従来の「AST 解析とコード品質評価と構造理解を1ステップで行う構成」を改め、**確定ファクト抽出の直後に3観点分離型のアーキテクチャ分析・記録 Action (`common/architecture_analysis`)** を挟みます。

```yaml
# 改訂版 python/full_audit.yaml のステップ構成イメージ
steps:
  # 1. 確定ファクト一括抽出 (.pni/cache/full_audit_facts.json)
  - id: extract_facts
    uses: python_extract_facts        # project_inspect + ast_analyze (module_inventory 含む)

  # 2. 観点分離型アーキテクチャ分析・記録 (.pni/cache/full_audit_architecture.json)
  #    ※ push-action 時に実在ファイルパス・モジュール台帳との照合検証を実行してハルシネーションを排除
  - id: analyze_architecture
    uses: architecture_analysis       # 2a: 目的/入口/Stack -> 2b: レイヤー/全モジュール -> 2c: 実行フロー/状態

  # 3. 観点別ルール適合性・健全性評価（記録された ArchitectureRecord を前提知識として参照）
  - id: deps_and_modern_stack
    uses: python_deps_and_stack_audit # 依存過不足 (deptry相当), pyproject衛生, Flask->FastAPI等の近代化評価

  - id: code_typing_and_docs
    uses: python_code_health_audit    # isort整列, 型安全性, Docstring整合性, 複雑度, FastAPI等のFW検査

  - id: test_health
    uses: python_test_audit           # assert無しテスト検出, モジュール対応率, 境界値テスト評価

  # 4. スコア出力 & 5. drawlib ビジュアルレポート生成
  - id: output_score
    uses: emit_score

  - id: create_report
    uses: write_drawlib_report
```

特に Python においては、`2a. arch_purpose_and_stack` でプロジェクトが **「CLI ツール」「JSON REST API」「Web SSR」「ライブラリ」** のどれであるかが最初に確定記録されるため、後続の `python_deps_and_stack_audit` における **`Flask → FastAPI` や `argparse → Typer` の移行推奨判定を誤診ゼロで実行できる**ようになります。

---

## 6. AI 向け Python ワークフロー作成ガイド (`python/workflow_guide.md`) の仕様

`pni -h` の `AI Instructions` から誘導される `pni rules show common/workflow_guide`（共通決定手順）に続き、Python プロジェクトと判明した際に AI が参照する **`pni rules show python/workflow_guide`**（`src/pni/_rules/python/workflow_guide.md`）には以下の実践ガイドを記載します。

1. **Python ディレクトリ構成別の `targets` マッピング指針**:
   - **`src/` レイアウト標準型**: `source: ["src"]`, `tests: ["tests"]`
   - **フラットパッケージ型 (`<pkg_name>/` 直置き)**: ルート直下の `__init__.py` を持つパッケージディレクトリを特定し、`source: ["<pkg_name>"]`（`tools/` 等の補助コードがあれば併記するか別 Workflow 化）を指定する。
   - **Web アプリ構成 (`app/` + `scripts/` + `migrations/`)**: Alembic 等の自動生成マイグレーション（`migrations/versions/`）が AST ノイズにならないよう、`source: ["app"]` に絞るベストプラクティスを明記する。
   - **`uv` / Poetry Workspace（モノレポ複数パッケージ）**: `packages/*` ごとに `targets.root` とレポート名（`reports/<pkg>_audit.pdf`）を分けた個別 Workflow YAML を生成する手順を示す。
2. **検出ライブラリに応じた Rules / Actions カスタマイズ表**:
   - `pyproject.toml` / `requirements.txt` に `fastapi` があれば `rules: ["python/frameworks/fastapi"]` を追加
   - `flask` / `bottle` / `argparse` 等があれば `rules: ["python/modern_stack"]` を追加
   - `.sh` / `.pl` スクリプトが同梱されていればレガシースクリプト移行評価を含める
3. **検証コマンドの徹底**:
   - YAML 作成後、必ず `pni workflows show <workflow_id>` を実行してターゲット解決とプリミティブ展開列を確認してから `pni workflows start <workflow_id>` を呼ぶ手順を明文化する。
