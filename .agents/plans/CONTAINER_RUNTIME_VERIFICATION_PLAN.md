# コンテナベース動的検証（ビルド・単体テスト・実測カバレッジ・起動スモーク）実装計画書

本ドキュメントは、ホスト検査マシンに多様な言語ランタイム（Python 各バージョン、JDK 8〜21、Maven、Gradle 等）を直接インストールすることなく、**Docker または Podman コンテナを用いて「① ビルド/依存解決の成否」「② 単体テストの実動合否」「③ 実測の行・分岐カバレッジ」「④ アプリ/CLI/ライブラリの起動可能性（Smoke Check）」を決定論的に計測し、PNI の評価・レポート基盤へ統合する**ための確定実装計画書です。

対象 OS は **Linux / macOS** とし、Windows コンテナ / Windows ホスト固有パス処理は現時点ではスコープ外とします。

---

## 1. 背景・目的と基本設計方針

### 1.1. 現状の課題（静的解析のみの限界）
現在の PNI は [`project_inspect`](../../src/pni/_actions/project_inspect.py) と [`ast_analyze`](../../src/pni/_actions/ast_analyze/runner.py) による高速な静的解析を備えていますが、以下の項目は実際にコードを動かさなければ確定できません。

1. **ビルド・依存解決の実動性**: `pyproject.toml` / `requirements.txt` / `pom.xml` / `Dockerfile` に書かれた依存関係が本当に競合せず解決・コンパイルできるか。
2. **単体テストの真の合否**: テスト関数と `assert` 文が存在していても、実行時に `AssertionError` や `ImportError` で落ちていないか。
3. **実測コードカバレッジ**: AST 上の「モジュール対テストファイル対応率」だけでなく、実際にどの行・分岐が何 % 実行されたか（Line / Branch Coverage）。
4. **起動可能性（Bootability）**:
   - **Library**: `import <pkg>` 時に循環 import や初期化例外でクラッシュしないか。
   - **CLI**: エントリポイント（`<cmd> --help`）が正常終了（exit code `0`）するか。
   - **Web API**: FastAPI の `lifespan` や Spring Boot の DI コンテナ初期化（循環 `@Autowired` の `BeanCurrentlyInCreationException` 等）で即死せず、ポート待受・ヘルス応答に到達できるか。

### 1.2. 確定した6つの設計原則

1. **ビルドツール別の簡潔な `.dockerfile` 資産の同梱 (`src/pni/_dockerfiles/<lang>/<tool>.dockerfile`)**
   - Cloud Native Buildpacks (`pack`) のような暗黙的なブラックボックスを使わず、ビルドシステム名をファイル名に明示した純粋な `.dockerfile`（`uv.dockerfile`, `maven.dockerfile` 等）を `src/pni/_dockerfiles/` 配下に管理する。
   - Docker / Podman 標準の `ARG`（`ARG PYTHON_VERSION=3.12`, `ARG JAVA_VERSION=21` 等）＋ `--build-arg` のみで制御し、Python コード内に文字列結合テンプレートを持たない。
2. **解析対象ソース（`targets.root`）単位でのキャッシュ Dockerfile 管理（案A）**
   - 原本ソースには一切ファイルを追加しない。
   - ビルド定義は `workflow_id` ではなくソース（`targets.root`）に紐づくため、**`.pni/cache/dockerfiles/<targets.root>/Dockerfile`** に実体ファイルを配置して全ワークフロー間で共有する：
     - 通常利用（`targets.root == "."`）: **`.pni/cache/dockerfiles/Dockerfile`**
     - サブディレクトリ指定（例: `targets.root == "examples/python/lib_clean"`）: **`.pni/cache/dockerfiles/examples/python/lib_clean/Dockerfile`**
   - 同じディレクトリに BuildKit / Podman 標準認識の **`Dockerfile.dockerignore`** も自動生成し、対象ソースに `.dockerignore` が無い場合でも `.git` や `.venv`、`node_modules`、`reports` 等の不要データ転送を自動抑止する。
   - すでに `.pni/cache/dockerfiles/<targets.root>/Dockerfile` が存在する場合はそれを優先再利用し（AI やユーザーが対象ソース向けに調整した内容を保持）、`force_regenerate_dockerfile: true` 指定時のみテンプレートから上書き再生成する。
3. **`docker build`（ネット許可）と `docker run --network=none`（ネット遮断）の2段階分離**
   - 依存パッケージ取得とコンパイルは `build` フェーズで完結させ、Docker / Podman 標準のレイヤーキャッシュを最大限活用する。
   - 単体テスト・カバレッジ計測・起動スモークはビルド済みイメージに対して原則 **`--network=none`** で実行し、レガシーコード内の外部 URL への誤通信を防止すると同時に「外部ネットワークに依存した壊れやすい単体テスト」を炙り出す。
4. **解析対象ディレクトリを一切汚さない（Zero Host Pollution）**
   - ホスト側の対象コードへコンテナから書き込みマウントを行わない。実行ログ・JUnit XML・カバレッジ JSON/XML などのワークフロー実行結果ファイルは **`.pni/cache/<workflow_id>/runtime/`** 配下に集約する。
5. **「既存 `Dockerfile` のビルド検証」と「検査ハーネス `Dockerfile` による動的計測」の二刀流**
   - 対象リポジトリに本番用 `Dockerfile` がある場合、**① 対象自身の `Dockerfile` がビルドできるかの検証** と、**② `.pni/cache/dockerfiles/<targets.root>/Dockerfile` によるテスト・カバレッジ・起動検証** を両方実施する。
6. **1回のハーネスビルドで「ビルド検証 → テスト＆カバレッジ → 起動スモーク」を使い回す**
   - 1つのハーネスイメージに対して短命コンテナ（`--rm`）の実行コマンドを切り替えるだけで全動的チェックを完結させ、再ビルド時間をゼロにする。

---

## 2. `src/pni/_dockerfiles/` と `.pni/cache/dockerfiles/` の詳細仕様

### 2.1. PNI 同梱テンプレート構成 (`src/pni/_dockerfiles/`)

```text
src/pni/_dockerfiles/
├── __init__.py          # ensure_target_dockerfile, resolve_builtin_dockerfile, list_builtin_dockerfiles
├── manager.py           # targets.root 単位の .pni/cache/dockerfiles/ 生成・再利用・.dockerignore 管理
├── python/
│   ├── uv.dockerfile        # uv (pyproject.toml + uv.lock / PEP 621) 用ハーネス
│   ├── poetry.dockerfile    # Poetry (pyproject.toml + poetry.lock) 用ハーネス
│   └── pip.dockerfile       # requirements.txt / setup.py / 標準 pip 用ハーネス
└── java/
    ├── maven.dockerfile     # Maven (pom.xml / mvnw) + Surefire + JaCoCo 外付け注入ハーネス
    └── gradle.dockerfile    # Gradle (build.gradle / gradlew) + JUnit XML + JaCoCo ハーネス
```

> **`.pni/` 初期化ポリシー**:
> `pni init` 実行時はユーザーの `.pni/` ディレクトリを肥大化させないよう `.pni/dockerfiles/` の自動展開は行わず、`run_check` 実行時に組み込み `src/pni/_dockerfiles/<lang>/<tool>.dockerfile` から `.pni/cache/dockerfiles/<targets.root>/Dockerfile` を自動生成します（明示的にローカル `.pni/dockerfiles/<lang>/<tool>.dockerfile` や `with: { dockerfile: "..." }` が置かれている場合はそちらを優先解決します）。

### 2.2. キャッシュディレクトリ構造の全体像 (`.pni/cache/`)

```text
.pni/cache/
├── .gitignore                                         # 自動生成・自己修復 ("*\n")
├── CACHEDIR.TAG                                       # バックアップ除外タグ
├── workflow_state.db                                  # SQLite ワークフロー実行状態 DB
├── dockerfiles/                                       # 【ソース (targets.root) 単位で共有】
│   ├── Dockerfile                                     # targets.root == "." の場合
│   ├── Dockerfile.dockerignore                        # コンテキスト肥大化防止用
│   └── examples/
│       ├── python/
│       │   └── lib_clean/
│       │       ├── Dockerfile                         # targets.root == "examples/python/lib_clean"
│       │       └── Dockerfile.dockerignore
│       └── java/
│           └── api_spring_clean/
│               ├── Dockerfile
│               └── Dockerfile.dockerignore
└── <workflow_id>/                                     # 【ワークフロー単位の出力・スナップショット】
    ├── facts.json                                     # ProjectFacts + AstFacts + RuntimeFacts + ArchitectureRecord
    ├── architecture.json
    ├── blueprint.json
    └── runtime/                                       # コンテナ実行生ログ & 解析元レポート
        ├── runtime_facts.json
        ├── build.log
        ├── test.log
        ├── smoke.log
        └── out/
            ├── junit.xml / surefire/*.xml
            ├── coverage.json / jacoco.xml
            └── smoke.json
```

### 2.3. 各 `.dockerfile` の役割と `ARG` パラメータ仕様

#### (1) `python/uv.dockerfile`
- **対象判定**: `build_system == "uv"` または `uv.lock` 存在時
- **主な `ARG`**:
  - `ARG PYTHON_VERSION=3.12`（`requires-python` から `3.11` / `3.12` / `3.13` 等を自動選定）
  - `ARG EXTRA_APT_PACKAGES=""`（C 拡張等で `gcc libpq-dev` 等が必要な場合のみ Workflow `with:` から注入）
- **レイヤー構成**:
  1. `FROM ghcr.io/astral-sh/uv:python${PYTHON_VERSION}-bookworm-slim`
  2. 非 root 実行ユーザー `pni`（UID `10001`）と結果出力ディレクトリ `/out`（`chown pni:pni`）を作成
  3. `/opt/pni-venv` を作成し、`COPY --chown=pni:pni . /workspace` 後にプロジェクト本体・開発依存をインストールしたうえで、対象側に未定義でも必ず **`pytest` と `pytest-cov` を保証インストール**（`uv pip install pytest pytest-cov`）
  4. `USER pni`・`WORKDIR /workspace`・`ENV PATH="/opt/pni-venv/bin:$PATH"` を設定（Stage 2 / Stage 3 が `--network=none` かつ非 root で即実行可能）

#### (2) `python/poetry.dockerfile`
- **対象判定**: `build_system == "poetry"` または `poetry.lock` 存在時
- **レイヤー構成**:
  - `FROM python:${PYTHON_VERSION}-slim-bookworm` に `poetry` と `/opt/pni-venv` を構成し、`poetry install` 後に `pytest pytest-cov` を保証追加し、`USER pni` で固定。

#### (3) `python/pip.dockerfile`
- **対象判定**: `requirements.txt` / `setup.py` / ロックファイル無し `pyproject.toml`（レガシー構成含む）
- **レイヤー構成**:
  - `FROM python:${PYTHON_VERSION}-slim-bookworm`
  - `/opt/pni-venv` を作成し、`requirements*.txt` があればインストール、`pyproject.toml` または `setup.py` があれば `pip install --no-build-isolation -e .`（フォールバック `pip install -e .`）を実行、最後に `pip install pytest pytest-cov` を導入。

#### (4) `java/maven.dockerfile`
- **対象判定**: `build_system == "maven"`（`pom.xml` 存在時）
- **主な `ARG`**:
  - `ARG JAVA_VERSION=21`（`pom.xml` の `java.version` / `maven.compiler.source` から `8`, `11`, `17`, `21` を自動選定。`1.8` は `8` に正規化）
  - `ARG JACOCO_VERSION=0.8.12`
- **レイヤー構成（オフラインテスト対応）**:
  1. `FROM maven:3.9-eclipse-temurin-${JAVA_VERSION}`
  2. `/workspace` にソースをコピーし、**ビルドフェーズ（ネット有効）のうちに以下を実行**:
     - `mvn -B test-compile`（コンパイル成否の確定）
     - `mvn -B dependency:go-offline` および `org.jacoco:jacoco-maven-plugin:${JACOCO_VERSION}:help` の事前プラグイン解決（対象の `pom.xml` に JaCoCo 設定が無くても、Stage 2 の `--network=none` オフライン環境下で `mvn -B -o org.jacoco:jacoco-maven-plugin:${JACOCO_VERSION}:prepare-agent test org.jacoco:jacoco-maven-plugin:${JACOCO_VERSION}:report` を動作させるため）
  3. `/out` ディレクトリを作成し権限を調整。

#### (5) `java/gradle.dockerfile`
- **対象判定**: `build_system == "gradle"`（`build.gradle` / `build.gradle.kts` 存在時）
- **主な `ARG`**: `ARG JAVA_VERSION=21`
- **レイヤー構成**:
  - `FROM gradle:8.10-jdk${JAVA_VERSION}`
  - JaCoCo 自動注入用の初期化スクリプト `/opt/pni/jacoco.init.gradle` を配置し、ビルド時に `gradle --no-daemon -I /opt/pni/jacoco.init.gradle testClasses` を実行してキャッシュとコンパイルを確定させ、Stage 2 で `--offline test jacocoTestReport` を実行可能にする。

---

## 3. 実行エンジンと4段階パイプライン詳細設計

### 3.1. モジュール分割 (`src/pni/_actions/runtime_check/`)

```text
src/pni/_actions/runtime_check/
├── __init__.py          # run_runtime_check, RuntimeFacts 等の公開エクスポート
├── models.py            # RuntimeFacts およびサブ結果の Pydantic モデル定義
├── engine_detect.py     # docker / podman バイナリ・デーモン稼働検出と安全な subprocess 実行ラッパー
├── selector.py          # ProjectFacts から tool 名 / build_args / 既定テスト・スモークコマンドを推論
├── parsers.py           # JUnit XML (pytest / Surefire), coverage.json, jacoco.xml の決定論パーサ
├── smoke.py             # library / cli / web_api アーキタイプ別の起動スモークコマンド＆ログ失敗分類器
└── runner.py            # Stage 0〜4 オーケストレータと .pni/cache/ 出力管理
```

### 3.2. コンテナランタイム検出とセキュリティ・リソース制限 (`engine_detect.py`)

1. **自動検出順序**:
   - パラメータ `container_engine: "auto" | "docker" | "podman"`（デフォルト `"auto"`）。
   - `"auto"` の場合、`docker` → `podman` の順で `shutil.which(...)` を確認し、`<bin> info` を `timeout=5s` で実行して応答する方を採用する。
2. **ランタイム不在時の挙動 (`on_missing_runtime`)**:
   - `"skip"`（デフォルト）: ワークフロー全体を止めず、`RuntimeFacts(engine_available=False, status="skipped", skip_reason="...")` を記録して後続ステップへ進む。
   - `"fail"`: CI 等でコンテナ検証を必須化したい場合にエラーを返す。
3. **共通セキュリティ・リソース制限フラグ**:
   - すべての `run` 実行に `--rm`, `--network=none`（`allow_test_network: true` 指定時を除く）, `--memory=2g`, `--cpus=2`, `--pids-limit=256`, `--security-opt=no-new-privileges` を付与する。
   - Podman 検出時は rootless 環境での `/out` 書き込み権限問題を避けるためボリュームフラグ `:Z` および `--userns=keep-id` を適切に制御する。
   - すべてのサブプロセス呼び出しは `shell=False` の引数リスト（`subprocess.run([...], timeout=..., check=False)`）で実行する。

### 3.3. Stage 0〜Stage 4 のステップバイステップ動作

1. **Stage 0: Pre-flight (`timeout=5s`)**
   - `docker` / `podman` の稼働確認、`.pni/cache/dockerfiles/<targets.root>/Dockerfile`（＋ `Dockerfile.dockerignore`）の準備、`.pni/cache/<workflow_id>/runtime/out/` のクリーンアップ。
2. **Stage 1A: Project Dockerfile Build Check (`timeout=180s`, 対象に `Dockerfile` / `Containerfile` がある場合のみ)**
   - `<engine> build -t pni-proj-<slug> -f <target_root>/Dockerfile <target_root>` を実行し、対象自身の本番用 `Dockerfile` が正常にビルドできるかを検証。
3. **Stage 1B: Harness Image Build & Compile Check (`timeout=240s`, ネットワーク有効)**
   - `<engine> build -t pni-harness-<slug> --build-arg ... -f .pni/cache/dockerfiles/<targets.root>/Dockerfile <target_root>` を実行。
   - 依存解決・コンパイル成否を `RuntimeFacts.harness_build` に記録。失敗時は Stage 2 / Stage 3 を `"blocked"` として記録し Stage 4 へ進む。
4. **Stage 2: Offline Unit Test & Coverage Execution (`timeout=120s`, `--network=none`)**
   - `-v .pni/cache/<workflow_id>/runtime/out:/out:rw` をマウントしてテスト＆カバレッジを実行。
   - Python: `pytest` の JUnit XML (`/out/junit.xml`) と `pytest-cov` JSON (`/out/coverage.json`) を回収・解析。
   - Java: Surefire XML (`/out/surefire/TEST-*.xml`) と JaCoCo XML (`/out/jacoco.xml`) を回収・解析。
5. **Stage 3: Offline Bootability / Smoke Check (`timeout=30s`, `--network=none`)**
   - `library`: `python -c "import <top_pkg>"`（Java はコンパイル済み主要クラスのクラスロード検証）
   - `cli`: エントリポイント `<cmd> --help`（Java は `main` クラス実行確認）の exit code `0` 検証
   - `web_api`: コンテナ内でバックグラウンド起動し、最大 15 秒間 `127.0.0.1:<port>` のポート待受および代表ヘルスパス（`/healthz`, `/health`, `/actuator/health`, `/openapi.json`, `/`）への HTTP 応答をポーリング後、`SIGTERM` で停止。起動直後にクラッシュした場合はエラーログから `import_or_di_error`（循環 import や Spring `BeanCurrentlyInCreationException` 等）・`config_missing`・`external_service_unreachable` を分類記録する。
6. **Stage 4: Cleanup**
   - `cleanup_images=True`（デフォルト）に従い、作成した一時タグイメージ（`pni-harness-<slug>`, `pni-proj-<slug>`）を `rmi -f` で削除しディスク肥大化を防止する（BuildKit レイヤーキャッシュは維持されるため次回ビルドは高速）。

---

## 4. データモデル・ワークフロー・レポート統合仕様

### 4.1. `RuntimeFacts` スキーマ (`src/pni/_actions/runtime_check/models.py`)

- `RuntimeFacts`:
  - `status`: `"passed" | "failed" | "skipped" | "blocked" | "timeout" | "error"`
  - `container_engine`: `"docker" | "podman" | None`
  - `engine_available`: `bool`
  - `skip_reason`: `str`
  - `language`: `str`
  - `selected_dockerfile_template`: `str`（例: `"python/uv.dockerfile"`）
  - `cached_dockerfile_path`: `str`（例: `".pni/cache/dockerfiles/Dockerfile"` または `".pni/cache/dockerfiles/examples/python/lib_clean/Dockerfile"`）
  - `build_args`: `dict[str, str]`
  - `artifacts_dir`: `str`（`".pni/cache/<workflow_id>/runtime"`）
  - `project_dockerfile_build`: `Optional[ContainerBuildResult]`
  - `harness_build`: `ContainerBuildResult`
  - `test_execution`: `TestExecutionResult`（総数 / Passed / Failed / Error / Skipped / `failures: list[FailedTestCase]`）
  - `coverage`: `CoverageResult`（`line_coverage_pct`, `branch_coverage_pct`, `covered_lines`, `total_statements`, `lowest_covered_modules`）
  - `smoke_check`: `SmokeCheckResult`（`archetype`, `status`, `probed_endpoint`, `http_status`, `failure_kind`, `detail`）

### 4.2. 既存パイプラインへの接続

1. **[`_cache.py`](../../src/pni/_cache.py)**:
   - `default_target_dockerfile_rel_path(target_root: str)` -> `.pni/cache/dockerfiles/<normalized_target_root>/Dockerfile`（`target_root` が `"."` や `""` の場合は `.pni/cache/dockerfiles/Dockerfile`）
   - `default_runtime_rel_dir(workflow_id: str)` -> `.pni/cache/<workflow_id>/runtime`
   - `default_runtime_facts_rel_path(workflow_id: str)` -> `.pni/cache/<workflow_id>/runtime/runtime_facts.json`
2. **[`WorkflowFactsBundle`](../../src/pni/_workflows/base_model.py)** & **[`engine.py`](../../src/pni/_workflows/engine.py)**:
   - `WorkflowFactsBundle` に `runtime_facts: Optional[RuntimeFacts] = None` を追加。
   - `_execute_deterministic_step_if_needed` で `PrimitiveType.RUN_CHECK` を実行し、`facts.json` と `runtime_facts.json` を同時更新。
   - `get-action` のプロンプトに `_render_runtime_facts(rf)` を出力し、ビルド・単体テスト合否・実測 Line/Branch カバレッジ・起動スモーク結果を AI に提示。
3. **[`aggregator.py`](../../src/pni/_workflows/aggregator.py)** & **[`blueprint.py`](../../src/pni/_reporter/blueprint.py)**:
   - `ModuleHotspot` に実測低カバレッジによるリスク補正を反映。
   - `ReportBlueprint` の Chapter 00（Executive KPI）と Chapter 03（Quantitative Metrics）に、ビルド・テスト通過数・実測カバレッジ・起動スモーク結果・低カバレッジモジュール一覧を自動組み込み。

### 4.3. ルール・アクション・ワークフロー更新範囲

- **新規ルール**: `src/pni/_rules/common/runtime_verification.md`（クリーンビルド再現性、オフライン単体テスト通過、実測行/分岐カバレッジ基準、起動スモーク・DI 健全性）
- **新規コンポジットアクション**: `src/pni/_actions/common/container_runtime_audit.yaml`（`run_check` + `ai_interpret`）
- **ワークフロー組み込み方針（確定）**:
  - `quick_check.yaml`（組み込みテンプレートおよび `.pni/workflows/quick_check.yaml`）: **高速な静的解析のみのまま維持**
  - `full_audit.yaml`（Python / Java 組み込みテンプレートおよび `.pni/workflows/full_audit.yaml`）: **`container_runtime_audit` を標準ステップとして追加**
  - サンプル6ワークフロー（`py_lib_clean.yaml`, `py_api_fastapi_clean.yaml`, `py_cli_audit_tool.yaml`, `py_api_legacy_messy.yaml`, `java_api_spring_clean.yaml`, `java_api_spring_messy.yaml`）: **`container_runtime_audit` を組み込み**

---

## 5. 実装フェーズと検証計画

1. **Phase 1 (`_dockerfiles` & `_cache`)**:
   - `_cache.py` のパスヘルパー追加、`src/pni/_dockerfiles/`（`manager.py` + Python 3種 + Java 2種の `.dockerfile` + `.dockerignore` 自動生成）の実装。
2. **Phase 2 (`runtime_check` コアエンジン)**:
   - `models.py`, `engine_detect.py`, `selector.py`, `parsers.py`（JUnit XML / `coverage.json` / `jacoco.xml`）, `smoke.py`, `runner.py` の実装。
3. **Phase 3 (Workflow / Rules / Actions / Blueprint 統合)**:
   - `engine.py`, `aggregator.py`, `blueprint.py`, `runtime_verification.md`, `container_runtime_audit.yaml`, 各種ワークフロー YAML・ガイドの更新と `pni init --force` 同期。
4. **Phase 4 (単体テスト + 実 Docker E2E 検証 + `./pcli` 品質ゲート)**:
   - `tests/pni/test_runtime_check.py` でモック単体テスト（ランタイム未導入時の `skip`/`fail`、各パーサ、案Aキャッシュパス解決、`engine.py` 統合）を網羅。
   - ローカルの `/usr/bin/docker` を用いてサンプルプロジェクトで実コンテナビルド・オフラインテスト・カバレッジ抽出・起動スモーク（Clean の PASS と Messy の循環依存起動クラッシュ・低カバレッジ検出）を実機確認。
   - `./pcli code-check all` および `./pcli test all` で全 lint・型検査・テスト通過を確認。
