# PNI501 × Drawlib 品質監査・相互改善計画書 v2 (Audit & Cross-Repo Integration Plan)

- **更新日**: 2026-11-04
- **対象リポジトリ**:
  1. **`pni501` 側** (`pni` パッケージ / CLI): 監査エンジン・AST アナライザ・Drawlib レポートコンパイラ側
  2. **`drawlib` 側** (`drawlib` `v0.3.5+`): 監査対象ライブラリ兼レポート描画エンジン側
- **確定した設計方針（v2 合意事項）**:
  1. **`drawlib >= 0.3.5` 完全前提**: レガシーなフラット構成（`<target>_src/*.md`）の後方互換シムは設けず、`pni501` 内の全 Drawlib プロジェクト（`docs/*_src` 3件・`reports_src/**/*_src` 11件）を先に `drawlib 0.3.5` ネイティブ形式（`drawlib.toml` + `<lang>/`）へ移行する。`pyproject.toml` の `drawlib>=0.3.5` 更新および `uv sync` は実施済み。
  2. **リスト形式のランタイムアーキタイプ (`runtime_types`)**: 単一文字列および曖昧な `"hybrid"` を廃止し、`RuntimeArchetype = Literal["web_api", "worker", "cli", "library"]` のリスト `runtime_types: list[RuntimeArchetype]`（例: `drawlib` = `["cli", "library"]`、`pni501` = `["cli"]`、FastAPI+CLI = `["web_api", "cli"]`）で該当ロールを正確に列挙する。
  3. **`conftest.py` フック型アサーション検出時の抑制**: `conftest.py` の `pytest_runtest_call` 等フック内アサーションや `autouse=True` フィクスチャの `yield` 後アサーションが検出された場合、配下テストの `assertion_free_tests` 警告を抑制し、`AstFacts.test_harness_notes` に記録する。

---

## 1. 全体ロードマップ（推奨実行順序）

| ステップ | 作業対象 | フェーズ名 | 主な内容 | 状態 / 依存関係 |
| :---: | :---: | :--- | :--- | :--- |
| **Step 0** | **`pni501`** | **Phase P0: 依存更新 & 既存 Drawlib プロジェクトの `0.3.5` 移行** | ・`pyproject.toml` を `drawlib>=0.3.5` に更新 & `uv sync`（**完了**）<br>・`docs/*_src`（3件）および `reports_src/**/*_src`（11件）を `drawlib.toml` + `<lang>/` 構造へ移行 | `pyproject.toml` / `uv.lock` 完了、プロジェクト移行から着手 |
| **Step 1** | **`pni501`** | **Phase P1: ブロッカー解消（Tarjan SCC & `drawlib 0.3.5` レポータ対応）** | ・非再帰 Tarjan SCC + 正規化閉路抽出 + `if TYPE_CHECKING:` 分離（内部循環 & `DEP004` 両対応）<br>・`compiler.py` の `drawlib.toml` + `<lang>/` ネイティブ化・`<target>_<lang>.pdf` 正規化・`rules show` 改称6トピック同期 | 最優先 |
| **Step 2** | **`pni501`** | **Phase P2: AST 解析精度・生成コード除外・リスト型アーキタイプ対応** | ・関数パラメータ CST コメント混入バグ修正（`docs.py` / `typing.py` / `quality.py`）<br>・`targets.exclude` の全パイプライン伝播 & `_generated` 再エクスポート除外<br>・対象 `.venv` の `top_level.txt` + `RECORD` 解決<br>・`conftest.py` フック型アサーション抑制 & シークレット誤検知抑制<br>・`runtime_types: list[RuntimeArchetype]` 導入 & `RuntimeCheckOptions` 拡充 | Step 1 と連続実施 |
| **Step 3** | **`drawlib`** | **Phase D1: 事前検出されたコード品質・依存・CI 課題の修正** | ・直接 import している `pillow` / `numpy` / `markupsafe` の `pyproject.toml` 明示宣言<br>・外部 HTTP タイムアウト・`hashlib.md5(..., usedforsecurity=False)`・`# type: ignore[...]` 修正<br>・レイヤー境界・内部循環参照・複雑度ホットスポット・GitHub Actions `permissions:` の整備 | 単独で並行可 |
| **Step 4** | **`drawlib`** | **Phase D2: `.pni/` ワークフロー・オフライン検証ハーネス導入と監査実行** | ・`.gitignore` 整理と `.pni/` 初期化<br>・`library_hygiene_audit` + `cli_guidelines_audit` を統合したカスタム `full_audit.yaml` 作成<br>・Playwright / 事前アセット取得を組み込んだ `.pni/dockerfiles/` ハーネス構築と監査レポート出力 | Step 0〜2 完了後 |

---

## 2. Part 1: `pni501` リポジトリ側の詳細実装計画

### 2.0. Phase P0: 既存 Drawlib プロジェクト群の `0.3.5` ネイティブ移行

- **対象ディレクトリ（全14プロジェクト）**:
  1. `docs/doc_src`: `type = "doc"`, `default_lang = "en"`, `langs = ["en"]`, `style = "google"`（`00_cover.md`〜`06_*.md` を `en/` へ移動）
  2. `docs/rules_and_actions_src`: `type = "doc"`, `default_lang = "en"`, `langs = ["en"]`, `style = "google"`（`00_cover.md`〜`05_*.md` を `en/` へ移動）
  3. `docs/slide_src`: `type = "slide"`, `default_lang = "ja"`, `langs = ["ja"]`, `style = "google"`（`01_title.md`〜`11_thank_you.md` を `ja/` へ移動）
  4. `reports_src/{python,java,php}/*_src`（計11件）: `type = "doc"`, `default_lang = "ja"`, `langs = ["ja"]`, `style = "google"`（各 `00_cover.md`〜`06_*.md` を `ja/` へ移動）
- **移行内容**:
  - 各 `*_src/` 直下に `drawlib.toml`（`[project]` + `[i18n]`）を作成し、チャプター/スライド `.md`（`README.md` 除く）を `<default_lang>/` サブディレクトリへ `git mv` 相当で移動する（`_assets/` 相対パス参照は全プロジェクトでゼロ件であることを確認済み）。
  - `drawlib 0.3.5` の `build pdf <src>/ -o <target>.pdf` は `<target>_<lang>.pdf` を出力するため、各 `build_pdf.sh` で単一ロケール出力 `<target>_<lang>.pdf` を `<target>.pdf` へ正規化（`mv -f`）し、既存の `docs/doc.pdf`, `docs/rules_and_actions.pdf`, `docs/slide.pdf`, `reports/**/*.pdf` パス契約を維持する。

---

### 2.1. Phase P1: ブロッカー解消（Tarjan SCC & `drawlib 0.3.5` レポータ完全対応）

#### P1-1. 循環依存検出アルゴリズムの非再帰 Tarjan SCC 化と `if TYPE_CHECKING:` 分離
- **対象ファイル**:
  - `src/pni/_actions/ast_analyze/base/dependencies.py`
  - `src/pni/_actions/ast_analyze/python/dependencies.py`
  - `src/pni/_actions/ast_analyze/models.py`
  - `src/pni/_workflows/engine.py`
  - `tests/pni/test_health_checkers.py`
- **改修仕様**:
  1. **非再帰（明示スタック）Tarjan SCC + 上限付き正規化単純閉路抽出 (`BaseDependencyChecker.detect_cycles`)**:
     - Python の再帰上限（`RecursionError`）を回避するため、明示スタックによる非再帰 Tarjan 法で $O(V + E)$ の強連結成分分解を実装する。
     - ノード数 1（自己ループなし）の自明 SCC を即座に除外し、非自明 SCC の誘導部分グラフ内でのみ単純閉路を探索する。
     - `max_cycles_per_scc: int = 5`、`max_total_cycles: int = 50`、`max_steps_per_scc: int = 2000` の安全上限を設け、抽出した閉路は辞書順最小ノードを先頭に回転（例: `["a", "b", "c", "a"]`）して重複排除する（既存の `tests/pni/test_java_support.py` とも完全互換）。
  2. **`if TYPE_CHECKING:` ガード内 import の分離 (`PythonDependencyChecker`)**:
     - 親 `if_statement` チェーンを検査する `_is_in_type_checking_guard(node)` を実装する（`if TYPE_CHECKING:` / `if typing.TYPE_CHECKING:` / `if t.TYPE_CHECKING:` の consequence ブロックのみを `True` とし、`if not TYPE_CHECKING:` や `else:` ブランチ内の実行時 import は誤って除外しない）。
     - **内部依存グラフ**: `internal_import_graph` / `circular_dependencies` は実行時 import のみで構築する。型チェック時のみの import を含めた場合のみ発生する閉路は `DependencyResult.type_checking_cycles` および `AstFacts.type_checking_cycles: list[list[str]]`（`metrics_snapshot["type_checking_cycles_count"]`）へ分離記録する。
     - **サードパーティ依存検査**: `TYPE_CHECKING` 内のみのサードパーティ import は `used_runtime_dists` には加算（`unused_dependencies` 誤検知防止）しつつ、`dev_dependencies` や型スタブのみの宣言でも `undeclared_dependencies`（`DEP004`）を発火させない。

#### P1-2. `compiler.py` および AI プロンプト・ドキュメント群の `drawlib >= 0.3.5` ネイティブ化
- **対象ファイル**:
  - `src/pni/_reporter/compiler.py`
  - `src/pni/_reporter/drawlib_guide.py`
  - `src/pni/_actions/common/write_drawlib_report.yaml`, `write_migration_report.yaml`, `write_progress_report.yaml`
  - `src/pni/_rules/common/agent_instruction.md`, `src/pni/_instructions/agent.md`
  - `.agents/rules/drawlib.md`, `.agents/rules/pni.md`, `README.md`, `docs/README.md`, `docs/doc_src/en/*.md`
  - `tests/pni/test_reporter.py`, `tests/pni/test_architecture_and_cli_guides.py`
- **改修仕様**:
  1. **`compiler.py` の `drawlib 0.3.5` 純粋対応（レガシーシムなし）**:
     - 標準ライブラリ `tomllib` で `src_dir / "drawlib.toml"` の `[i18n]`（`default_lang`, `langs`）を読み取る `_read_drawlib_i18n_config(src_dir)` を実装する。
     - `_find_chapter_markdown_files(src_dir)` は `src_dir / lang` 配下の `[0-9]*.md` / チャプター `.md`（`README.md`・`_*` 除外）を走査する。
     - `scaffold_report_project()` は `src_dir / lang` 配下の既存チャプター退避・復元およびスターターサンプル（`00_cover.md`, `01_overview.md`, `02_design.md`）削除を行う（旧 `navbar.md` 削除処理は撤去）。
     - `compile_report_project()` は `drawlib_tools.build_pdf(str(src_dir), output_file=str(pdf_candidate), ...)` が返す生成パス（`<target>_<default_lang>.pdf`）を受け取り、単一ロケール時は `pdf_candidate`（`<output_dir>/<target>.pdf`）へ `replace()`（複数ロケール時はデフォルトロケールを `shutil.copy2`）して `reports/<target>.pdf` 出力契約を保証する。
     - `_collect_deliverables()` の Markdown 収集を `markdown_dir.rglob("*.md")`（`<markdown_dir>/<lang>/*.md` 対応）に更新する。
     - `_DrawlibToolsProtocol` の引数名・戻り値型を `drawlib 0.3.5` の `drawlib.tools` 実装に完全一致させる。
  2. **`drawlib rules show` トピック名・チャプターパスの全面同期**:
     - `drawlib 0.3.5` で改称・分割された全6トピックを一括更新する：
       - `lib-smartarts` → `lib-smartarts-overview`
       - `lib-charts` → `lib-charts-overview`
       - `lib-diagrams` → `lib-diagrams-overview`
       - `lib-icons` → `lib-icons-overview`
       - `lib-shapes` → `lib-shapes-overview`
       - `lib-graph` → `lib-graph-overview`
     - `drawlib_guide.py` および `write_*_report.yaml` のチャプター作成パス案内を `<src_dir>/<target>_src/<lang>/00_cover.md`（デフォルト `en/`、日本語指定時 `ja/`）に統一する。

---

### 2.2. Phase P2: AST 解析精度・生成コード除外・リスト型ランタイムアーキタイプ対応

#### P2-1. Python 関数パラメータ CST コメントノード混入バグ修正
- **対象ファイル**:
  - `src/pni/_actions/ast_analyze/python/_helpers.py`
  - `src/pni/_actions/ast_analyze/python/typing.py`
  - `tests/pni/test_health_checkers.py`
- **改修仕様**:
  - `_helpers.py` に `_VALID_PARAM_KINDS: Final[frozenset[str]] = frozenset({"identifier", "typed_parameter", "default_parameter", "typed_default_parameter", "list_splat_pattern", "dictionary_splat_pattern"})` を定義し、`extract_callable_param_names()` および `typing.py` の `_collect_untyped_param_names()` で `child.kind() in _VALID_PARAM_KINDS` のみを対象とする。
  - これにより複数行シグネチャ内の `# noqa` / セクションコメントによる `doc_signature_mismatches` 偽陽性と `excessive_parameters` 水増しを同時に解消する。

#### P2-2. `targets.exclude` の全パイプライン伝播 & `_generated` 再エクスポート除外
- **対象ファイル**:
  - `src/pni/_workflows/base_model.py`（`WorkflowTargets.exclude: list[str] = Field(default_factory=list)` 追加）
  - `src/pni/_actions/ast_analyze/runner.py`（`discover_source_files` / `analyze` に `exclude_globs` 追加）
  - `src/pni/_actions/project_inspect.py`（`run_project_inspect` に `exclude_globs` 追加）
  - `src/pni/_workflows/engine.py`, `adhoc.py`, `manager.py`
  - `src/pni/_actions/migration_analyze/runner.py`
  - `src/pni/_actions/ast_analyze/python/imports.py`
  - `tests/pni/test_actions_and_workflows.py`, `tests/pni/test_health_checkers.py`
- **改修仕様**:
  - POSIX 相対パスに対する glob マッチヘルパー（`**/*_generated.py` や `*_generated.py` の両表記を直感的にマッチさせる `_matches_exclude_globs`）を共通化し、ワークフロー実行・アドホック実行・マイグレーション解析のすべてで `run.targets.exclude` を伝播させる。
  - `PythonImportChecker`（`python/imports.py`）において、`__init__.py`（または `__all__` を持つファサードモジュール）が `._generated` / `*_generated` モジュールを `from ... import *` で再エクスポートしている場合は自動生成バインディングの公開イディオムとして `wildcard_imports` から除外する。

#### P2-3. PyPI 配布名 ⇄ import 名解決の強化（対象 `.venv` の `top_level.txt` + `RECORD` 参照）
- **対象ファイル**:
  - `src/pni/_actions/ast_analyze/python/dependencies.py`
  - `tests/pni/test_health_checkers.py`
- **改修仕様**:
  - `_DIST_TO_IMPORT_ALIASES` に `"python_docx": ("docx",)`, `"python_pptx": ("pptx",)`, `"markdown_it_py": ("markdown_it",)`, `"xlsxwriter": ("xlsxwriter",)`, `"lxml": ("lxml",)` 等を追加する。
  - `project_root / ".venv"`（POSIX `lib/python*/site-packages` および Windows `Lib/site-packages`）が存在する場合、`importlib.metadata.distributions(path=...)` を走査し、`top_level.txt` に加えて `top_level.txt` を持たないモダン wheel（`hatchling`, `uv_build`, `flit_core` 製）向けに `dist.files`（`RECORD`）の最上位パッケージ/モジュール名も抽出してマッピングへ統合する。

#### P2-4. `conftest.py` フック型アサーション抑制 & シークレット定数ヒューリスティック精緻化
- **対象ファイル**:
  - `src/pni/_actions/ast_analyze/python/testing.py`
  - `src/pni/_actions/ast_analyze/models.py`
  - `src/pni/_actions/ast_analyze/base/operational.py`
  - `src/pni/_workflows/engine.py`
  - `tests/pni/test_health_checkers.py`, `tests/pni/test_universal_standards.py`
- **改修仕様**:
  1. **`conftest.py` フック型アサーション検出と `assertion_free_tests` 抑制 (`testing.py`)**:
     - テストディレクトリ階層内の `conftest.py` を AST 検査し、(a) `pytest_runtest_call` / `pytest_runtest_makereport` / `pytest_pyfunc_call` フック関数内のアサーション、または (b) `@pytest.fixture(..., autouse=True)` の `yield` 後ティアダウンアサーションを検出する。
     - 該当 `conftest.py` のスコープ配下にあるテスト関数については `assertion_free_tests` への計上を**抑制**し、代わりに `AstFacts.test_harness_notes: list[str]`（例: `"tests/conftest.py: pytest_runtest_call hook performs automated post-test assertions"`）へ記録する。
  2. **シークレット検出ヒューリスティックの精緻化 (`is_likely_secret_literal`)**:
     - アセット/ドキュメント拡張子（`.png`, `.svg`, `.jpg`, `.jpeg`, `.webp`, `.gif`, `.ico`, `.json`, `.yaml`, `.yml`, `.toml`, `.ttf`, `.otf`, `.woff`, `.woff2`, `.css`, `.html`, `.md`）を持つ文字列を除外する。
     - 識別子名に非シークレット語（`icon`, `asset`, `image`, `img`, `color`, `style`, `font`, `glyph`, `badge`, `label`, `template`, `slug`）が含まれる場合を除外する。
     - 識別子名とリテラル値の英数字正規化文字列が一致・包含関係にある自己記述的定数/Enum スラッグ（例: `ONEPASSWORD = "onepassword"`, `K8S_SECRET = "k8s-secret"`, `GITHUB_TOKEN_URL_KEY = "github-token"`）を除外しつつ、`STRIPE_API_KEY = "sk_live_..."` 等の実シークレット検出は維持する。

#### P2-5. リスト形式ランタイムアーキタイプ `runtime_types` の導入（`"hybrid"` 廃止） & `RuntimeCheckOptions` 拡充
- **対象ファイル**:
  - `src/pni/_actions/_repo_governance.py`
  - `src/pni/_actions/project_inspect.py`
  - `src/pni/_actions/base_model.py`
  - `src/pni/_actions/pentest/server_plan.py`
  - `src/pni/_actions/runtime_check/models.py`, `selector.py`, `runner.py`, `smoke.py`
  - `src/pni/_workflows/engine.py`
  - `src/pni/_reporter/blueprint.py`
  - `src/pni/_rules/common/{workflow_guide,twelve_factor,production_readiness,cli_guidelines,library_guidelines}.md`
  - `src/pni/_actions/{python,java,php}/repo_structure_audit.yaml`, `src/pni/_actions/common/architecture_analysis.yaml`
  - `tests/pni/{test_universal_standards,test_runtime_check,test_web_pentest,test_health_checkers,test_php_support,test_architecture_and_cli_guides,test_aggregator_and_blueprint}.py`
- **改修仕様**:
  1. **`RuntimeArchetype` リスト化と `"hybrid"` 廃止**:
     - `RuntimeArchetype = Literal["web_api", "worker", "cli", "library"]` を定義し、`infer_runtime_types(...) -> list[RuntimeArchetype]` が該当するすべてのロールを定順（`["web_api", "worker", "cli", "library"]` の部分列、最低1要素）で返すようにする。
     - `web_api` / `worker` / `cli` のいずれかに該当するプロジェクトでも、`force_php_lib` または Python パッケージ直下に CLI/サーバエントリポイント（`cli`, `main`, `__main__`, `app`, `wsgi`, `asgi`, `server`, `worker`）以外の**公開（非 `_` 始まり）モジュール・サブパッケージが2つ以上**存在する場合は `"library"` もリストに含める（いずれにも該当しない場合はデフォルト `["library"]`）。
       - 判定例: `pni501` → `["cli"]`、`drawlib` → `["cli", "library"]`、FastAPI + Typer CLI → `["web_api", "cli"]`、純粋ライブラリ → `["library"]`。
     - **スキーマと既存 `reports/*_score.json` 互換性**:
       - `ProjectFacts.runtime_types: list[RuntimeArchetype] = Field(default_factory=lambda: ["library"])`（レガシー入力 `runtime_type_hint` が渡された場合の正規化 `model_validator` 付き）。
       - `SystemProfile.runtime_types: list[str] = Field(default_factory=lambda: ["library"])`（既存 `reports/*_score.json` 内の `"runtime_type": "..."` を `["..."]` に透過変換する `model_validator` 付き）。
       - `MetricScalar = str | int | float | bool | list[str]` に拡張し、`engine.py` は `metrics_snapshot["runtime_types"] = list(pf.runtime_types)` を出力する。
     - **下流コンポーネントの簡潔化**:
       - `project_inspect.py`（SemVer `==` 警告）: `"library" in runtime_types` で判定（`["cli", "library"]` の `drawlib` も漏れなく検査しつつ、純粋 `["cli"]` の `pni501` は対象外）。
       - `pentest/server_plan.py`: `"web_api" not in pf.runtime_types and not has_endpoints` でスキップ判定。
       - `runtime_check/smoke.py`: `pf.runtime_types` の要素に応じてスモークを構成。特に Python で `"cli"` と `"library"` の両方を持つ場合（`["cli", "library"]`）は `<cli_bin> --help` と `import <pkg>` の**両方**を連続検証する（ラベルは `"+".join(pf.runtime_types)` 例: `"cli+library"`）。
       - 各共通ルール（`twelve_factor.md`, `production_readiness.md`, `cli_guidelines.md`, `library_guidelines.md`, `workflow_guide.md`）から `"hybrid"` 表記を撤廃し、`runtime_types` に該当ロールが含まれるかどうかで明快に適用判定する。
  2. **`RuntimeCheckOptions` のテスト実行制御拡張**:
     - `RuntimeCheckOptions` に `pytest_extra_args: tuple[str, ...] = ()`（ワークフロー `with:` からは `list[str]` 指定可）および `pre_test_cmd: str = ""` を追加する。
     - `pre_test_cmd` 指定時は Stage 2 コンテナ内で同一ファイルシステム状態を保ったまま `sh -c "<pre_test_cmd> && <test_cmd>"` としてテスト実行前にチェーン実行する。

#### P2-6. `pni501` 側の検証ゲート
```bash
./pcli code-check all
./pcli test all
./docs/doc_src/build.sh
./docs/rules_and_actions_src/build.sh
./docs/slide_src/build.sh
```

---

## 3. Part 2: `drawlib` リポジトリ側の品質改善・導入計画

### 3.1. Phase D1: 事前試験で判明した `drawlib` 本体の品質・依存・ガバナンス改善

*(※ 本フェーズは `pni501` 側の改修完了を待たずに、`drawlib` 単体の品質向上として先行実施可能)*

#### 1. 直接 import しているランタイム依存パッケージの明示宣言 (`DEP001` / `DEP004` 解消)
- **対象ファイル**: `pyproject.toml`
- **内容**:
  - 現在 `src/drawlib/` 内で直接 `import PIL` / `import numpy` / `import markupsafe` を行っているが、`matplotlib` および `jinja2` の間接依存に頼っている。
  - `[project.dependencies]` に互換性のある柔軟な SemVer 下限（例: `"pillow>=10.2"`, `"numpy>=1.26"`, `"markupsafe>=2.1"` — `./dcli pypi deps` で現行解決ツリーと Python 3.11〜3.13 互換性を確認のうえ決定）を明示追加する。

#### 2. 外部通信タイムアウト・FIPS 互換 MD5・型 ignore・例外ハンドリングの改善
- **外部 HTTP タイムアウトの明示**:
  - `src/drawlib/_core/l3_external/_package.py`: `urllib.request.urlopen(req, timeout=60)` のように明示的タイムアウト引数を追加し、ネットワーク不調時の無期限ハングを防止する。
- **非暗号用途 MD5 の FIPS 環境対応**:
  - `src/drawlib/_core/l3_external/_download.py` および `src/drawlib/_core/l4_canvas/_text_utils.py`: キャッシュキー生成用の `hashlib.md5(...)` に `usedforsecurity=False` を付与する。
- **スコープなし `# type: ignore` の解消（4箇所）**:
  - `src/drawlib/_core/l3_images/_dimage.py`
  - `src/drawlib/_core/l4_canvas/_image_code.py`
  - `src/drawlib/_diagrams/state/_render_transition.py`
  - 上記の素の `# type: ignore` を具体的なエラーコード指定または型安全な記述へ修正し、`./dcli code-check type`（`ty`）を通過させる。
- **サイレントな `try ... except ...: pass` の整理（6箇所）**:
  - `src/drawlib/_builder/_common/office.py`, `src/drawlib/_builder/doc_builder/processor/options.py`, `src/drawlib/_cli/commands/show.py`, `src/drawlib/_core/l3_styles/_base_styles.py`, `src/drawlib/_slide/_blocks.py`, `src/drawlib/_templates/_project.py` の意図的な例外無視を `contextlib.suppress(...)` または適切なデバッグログ出力に統一する。

#### 3. レイヤー境界・内部循環参照・複雑度ホットスポットの点検
- **内部コア ⇄ 公開ファサード間の参照整理**:
  - `src/drawlib/_core/l4_canvas/_image_code.py` が公開ファサード `drawlib.canvas` を参照して生じている循環（`l4_canvas -> _image_code -> drawlib.canvas -> l4_canvas`）を確認し、`l4_canvas` 内部シンボルで完結できる場合は下位レイヤー内参照へ整理する。
- **サブパッケージ間のプライベートモジュール直接参照の整理**:
  - `src/drawlib/_diagrams/_common.py` から `_icons.*._generated` への直接 import や、`_builder` から `_core.l4_canvas._base` / `_canvas`・`_slide._assets` / `_blocks` への参照について、各サブパッケージの `__init__.py` を境界窓口として経由する形へ段階的に整理する。
- **高認知的複雑度関数の分割検討**:
  - `src/drawlib/_builder/_common/cache.py` の `_hash_referenced_local_assets` 等、分岐・ネストが深い関数を小さな純粋ヘルパー関数へ分割し保守性を高める。

#### 4. GitHub Actions 権限の最小化・サプライチェーン衛生
- **対象ファイル**:
  - `.github/workflows/quality.yml`
  - `.github/workflows/ut_github.yml`
  - `.github/workflows/ut_pypi.yml`
  - `.github/workflows/ut_template.yml`
- **内容**:
  - 各ワークフローの最上位（またはジョブ単位）に `permissions: contents: read` を明記し、`GITHUB_TOKEN` のデフォルト権限を最小化する（OpenSSF Scorecard 準拠）。

---

### 3.2. Phase D2: `pni501` 改修後の `drawlib` への `.pni/` 導入と監査運用

#### 1. 実行方式とリポジトリ管理方針
- **実行方式**:
  - `pni501` 自身が `drawlib` に依存しているため、`drawlib` の `[dependency-groups].dev` に直接入れて循環ロックを作るよりも、開発中は `uv run --directory <pni501_repo> pni ...` または `uvx --from <pni501_repo_or_pypi> pni ...` で分離実行する方式を基本とする。
- **`.gitignore` の整備**:
  - `.pni/cache/`、`.pni/state.db*`、および一時生成物を `.gitignore` に追加する。
  - `.pni/workflows/` と `.pni/dockerfiles/` は `drawlib` 固有の監査設定としてバージョン管理可能にする。

#### 2. `drawlib` 向けカスタムワークフロー (`.pni/workflows/full_audit.yaml`)
- `drawlib` は `runtime_types = ["cli", "library"]` と自動判定される構成であり、以下の構成で定義する：
  - `targets`:
    - `source`: `["src/drawlib"]`
    - `tests`: `["tests/drawlib"]`
    - `docs`: `["README.md"]`
    - `exclude`: `["**/*_generated.py"]`（自動生成アイコンバインディングのノイズを分離）
  - `steps`:
    1. `repo_structure_audit`（リポジトリ構造・マニフェスト・CI 検査）
    2. `python_ast_audit`（Python AST 品質・型・Docstring・依存グラフ検査）
    3. `architecture_analysis`（3観点のアーキテクチャ記録：`l1_core..l4_canvas`, ドメインモジュール, `_builder`/`_cli`）
    4. `library_hygiene_audit`（公開 SDK 境界・`py.typed`・SemVer 依存境界・Import 純粋性）
    5. `cli_guidelines_audit`（`drawlib` CLI の `--help`/`--version`・終了コード・標準出力分離）
    6. `supply_chain_audit`（GitHub Actions 権限・シークレット衛生）
    7. `python_test_audit`（テストスイート構成・`conftest.py` 画像比較フック考慮）
    8. `container_runtime_audit`（クリーンルームビルド・`--network=none` 全単体テスト・実測カバレッジ・CLI+Import スモーク）
    9. `security_vulnerability_audit`（Trivy による CVE・シークレット・CWE シンク診断）
    10. `emit_score`（7軸スコア JSON 出力）
    11. `write_drawlib_report`（`drawlib v0.3.5+` による 7章構成 A4 PDF 診断レポート生成）

#### 3. `drawlib` 用コンテナ検証ハーネス (`.pni/dockerfiles/root/Dockerfile`)
- `tools/docker/Dockerfile.test_local` と同等のオフラインテスト成立条件を満たすハーネスを構成する：
  1. `apt-get` で `libgl1`, `libglx-mesa0`, `libglib2.0-0` を導入（`matplotlib` 用）。
  2. `.dockerignore` で除外される `docs_src/README_PYPI.md` に対し、パッケージインストール前に `mkdir -p docs_src && touch docs_src/README_PYPI.md` を実行して `uv pip install -e .` を通す。
  3. イメージビルド時（ネットワーク有効時）に `playwright install --with-deps --only-shell chromium` および `drawlib cache download --all` を実行し、`container_runtime_audit` の `--network=none` 環境でも PDF/PPTX テストおよびフォント・アイコンテストが100%オフライン通過するようにする。
  4. `pytest-xdist` を導入し、`pytest_extra_args: ["-n", "auto", "--dist", "loadfile"]` で高速にカバレッジ計測を実行する。

#### 4. `drawlib` 側の検証ゲート
```bash
./dcli code-check all
./dcli test all
./dcli docs build --all
./dcli docs serve site --check
```
- さらに `pni` が生成した `drawlib` 診断レポート（`<lang>/00_cover.md` 〜 `06_security_and_supply_chain.md`）に対し、`drawlib show ... -g` によるグリッド目視確認（Stage 2）とビルド済み PDF の確認（Stage 3）を実施する。
