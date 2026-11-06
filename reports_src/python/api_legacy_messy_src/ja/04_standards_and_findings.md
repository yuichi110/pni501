# 4. 検査指標・ルール適合マトリクスと指摘一覧

本ワークフロー（`py_api_legacy_messy` / `wf-fe76f694`）では、8つの AI 解釈ステップと5つの決定論的検査（`project_inspect`・`ast_analyze`・`run_check`・`security_scan`・`web_pentest`）を通じて全15エンジニアリングルールを検証しました。結果は **`FAIL` 14件・`WARN` 1件・`PASS` 0件（適合率 `0.0%`）**、検出指摘は計 **28件（`CRITICAL` 8件・`HIGH` 14件・`MEDIUM` 5件・`LOW` 1件）** です。全8監査ステップのスコアがいずれも Grade D 帯（`10〜22`点）に沈んでいます。

```drawlib file=04_audit_step_scores.png caption="図4-1: 8監査ステップ別スコア比較（低スコア順）とルール適合・指摘重大度KPI"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.smartarts import KpiCards
from drawlib.styles import Styles

setup(width=146, height=68, dpi=150)

chart = BarChart(
    axis_line_style=Styles.Gray5Thin,
    grid_style=Styles.Gray3DashedThin,
    axis_text_style=Styles.Dark.patch(text_size=9.0),
    value_text_style=Styles.DangerBold.patch(text_size=9.2),
    background_style=Styles.Neutral,
    title="8監査ステップ別スコア (低スコア順・100点満点)",
    title_style=Styles.DarkBold.patch(text_size=10.5),
    categories=[
        "動的DAST",
        "脆弱性・SAST",
        "Pythonテスト",
        "サプライチェーン",
        "運用準備度",
        "リポジトリ構造",
        "コンテナ実行",
        "Python AST",
    ],
    orientation="horizontal",
    bar_width_ratio=0.62,
    bar_r=0.8,
    value_format="{:.0f}",
)
chart.value_axis.min_value = 0
chart.value_axis.max_value = 100
chart.add_series("監査スコア", [10, 12, 12, 14, 16, 18, 18, 22], style=Styles.Danger)
chart.draw((2, 2), width=82, height=64)

kpis = KpiCards(
    style=Styles.WhiteBordered,
    metric_style=Styles.DangerBold.patch(text_size=16.5),
    text_style=Styles.DarkBold.patch(text_size=10.0),
    description_style=Styles.Dark.patch(text_size=9.0),
    accent_style=Styles.Danger,
)
kpis.add("14 件", "FAIL (重大違反)", "15ルール中14件が不適合判定")
kpis.add("1 件", "WARN (改善推奨)", "git_workflow (.gitignore欠落)")
kpis.add("0 件", "PASS (完全適合)", "合格ルールゼロ (適合率 0.0%)")
kpis.add("28 件", "指摘総数", "CRIT 8 / HIGH 14 / MED 5 / LOW 1")
kpis.draw((87, 2), width=57, height=64, columns=2)

save()
```

## ルール適合マトリクス（`FAIL -> WARN -> PASS`）と重大指摘サマリー

以下の図4-2では評価された主要エンジニアリングルールの不適合証跡を、図4-3では最優先で是正すべき `CRITICAL` 指摘8件を一覧化しています。

```drawlib file=04_rule_compliance_matrix.png caption="図4-2: 主要ルール適合マトリクス抜粋 (FAIL -> WARN -> PASS 順)"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=76, dpi=150)

tbl = Table(
    cell_style=Styles.DangerNeutral,
    text_style=Styles.Dark.patch(text_size=8.8),
    header_cell_style=Styles.Dark,
    header_text_style=Styles.WhiteBold.patch(text_size=9.2),
    border_style=Styles.Gray4Thin,
)
tbl.draw_flexible(
    (2, 74),
    column_widths=[12.0, 36.0, 48.0, 46.0],
    row_heights=[8.5, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0],
    data=[
        ["判定", "ルールID", "決定論的検出証跡 (Evidence)", "PASS化への必須要件"],
        ["FAIL", "common/security_vulnerability", "CVE 3,561件・CWE-502/78・DAST起動不能(error)", "slim化・safe_load・起動復旧&DAST合格"],
        ["FAIL", "common/runtime_verification", "行網羅率6.6%・分岐0.0%・起動PydanticUserError", "schemas修正・行85%以上のテスト網羅"],
        ["FAIL", "common/supply_chain", "ロック無・pull_request_target・@main・root実行", "uv.lock・pull_request最小権限・非root化"],
        ["FAIL", "common/architecture", "循環依存3経路・domain->handlers/infra._internal", "ACTIVE_PROMO_CODES移設・単方向DAG化"],
        ["FAIL", "common/maintainability", "認知的複雑度44・8引数・tags=[]・global辞書", "DTO引数化・状態注入・関数分割"],
        ["FAIL", "python/typing", "型網羅44.4%・未注釈9箇所・無制限type:ignore", "全公開関数型注釈・Pydantic v2厳格化"],
        ["FAIL", "python/testing", "12ソースに対しassert無し2行テスト1件のみ", "ミラー構成pytestスイートとHTTP検証"],
        ["WARN", "common/git_workflow", ".gitignore不在・PR上でdeployスクリプト実行", ".gitignore追加とPR自動検証ゲート分離"],
    ],
)

save()
```

```drawlib file=04_critical_findings_table.png caption="図4-3: 最重大 (CRITICAL) 指摘8件の箇所・証跡・推奨修正サマリー"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=80, dpi=150)

tbl = Table(
    cell_style=Styles.WhiteBordered,
    text_style=Styles.Dark.patch(text_size=8.6),
    header_cell_style=Styles.Danger,
    header_text_style=Styles.WhiteBold.patch(text_size=9.0),
    border_style=Styles.Gray4Thin,
)
tbl.draw_flexible(
    (2, 78),
    column_widths=[12.0, 32.0, 48.0, 50.0],
    row_heights=[8.2, 8.2, 8.2, 8.2, 8.2, 8.2, 8.2, 8.2, 8.2],
    data=[
        ["重大度", "対象箇所", "検出証跡 (Evidence)", "推奨される是正措置"],
        ["CRIT", "processor.py:8", "WEBHOOK_SIGNING_SECRET ハードコード", "コードから即時削除・環境変数/Secret管理へ移行"],
        ["CRIT", "Dockerfile:1", "python:latest (root)・OS CRIT 24 / HIGH 436", "python:3.12-slim固定・非root USER・多段ビルド化"],
        ["CRIT", "schemas.py:9 (DAST)", "web_pentest server_booted=false (3.52s)", "legacy_flag:bool付与・起動復旧しDASTゲート実行"],
        ["CRIT", "processor.py:30,63", "yaml.load (CWE-502) & shell=True (CWE-78)", "yaml.safe_load採用・shell=True呼び出し完全廃止"],
        ["CRIT", "deploy.yml:4,11", "pull_request_target + checkout@main 未固定", "pull_request化・contents:read・40文字SHA固定"],
        ["CRIT", "tests/test_orders.py:4", "実測行カバレッジ6.6% (7/106)・分岐0.0%", "主要6モジュールの単体/TestClient検証を追加"],
        ["CRIT", "tests/test_orders.py:4", "test_currency_smoke に assert 文がゼロ", "明示的 assert 追加と異常系・境界値テスト整備"],
        ["CRIT", "schemas.py:9 (Smoke)", "未注釈 legacy_flag=True でASGI起動失敗", "bool型注釈付与とPydantic v2モデルへ移行"],
    ],
)

save()
```

## 全15ルール適合マトリクス一覧（`FAIL -> WARN -> PASS` 順）

| 判定 | ルールID | 主検出ステップ | 決定論的証跡と判定サマリー |
| :---: | :--- | :---: | :--- |
| **FAIL** | `common/architecture` | `python_ast_audit` | 循環依存 `3件`（`handlers -> processor -> pricing -> handlers`）、境界違反 `2件`（`pricing -> handlers`, `pricing -> infra._internal`）、FastAPI/Flask 同居。 |
| **FAIL** | `common/documentation` | `repo_structure_audit` | `README.md` は2行（見出し1個）のみ。セットアップ・環境変数・API仕様・テスト手順が欠落し、106行 Bash の説明も皆無。 |
| **FAIL** | `common/maintainability` | `python_ast_audit` | `process_order_batch` が58行・16分岐・認知的複雑度 `44`・引数 `8個`（上限6超過）、`tags=[]`、`ORDER_STATE_CACHE`、裸の `except:` を保持。 |
| **FAIL** | `common/production_readiness` | `service_readiness_audit` | `requests.post` タイムアウト欠落・`async` 内同期阻害、FastAPI `/healthz` 不在（未マウント Flask に定義）、`uvicorn` 未宣言、起動クラッシュ。 |
| **FAIL** | `common/runtime_verification` | `container_runtime_audit` | 実測行カバレッジ `6.6%`（`7/106` 文）・分岐 `0.0%`、ASGI 起動スモークが `schemas.py:9` の `PydanticUserError`（`1.92s`, exit=1）で失敗。 |
| **FAIL** | `common/security` | `repo_structure_audit` | `processor.py:8` のハードコード署名鍵、`config/service_account_dummy.json` 同梱、`yaml.load`、`shell=True`、`Any` 境界入力。 |
| **FAIL** | `common/security_vulnerability` | `security_vulnerability_audit` / `web_penetration_audit` | Python CVE `7件`（HIGH 4件）、Debian OS CVE `3,554件`（CRIT 24 / HIGH 436）、IaC 不備 `3件`、CWE-502/78、無認証 API、動的 `web_pentest` 起動失敗（`server_booted=false`）。 |
| **FAIL** | `common/supply_chain` | `repo_structure_audit` | ロックファイル `0件`・未ピン依存 `8/8`、`pull_request_target` + `checkout@main` + `permissions` 欠落、root `:latest` コンテナ、`LICENSE`/`SECURITY.md` 不在。 |
| **FAIL** | `common/twelve_factor` | `service_readiness_audit` | 散在 `os.getenv`、インメモリ `ORDER_STATE_CACHE`、`/tmp/order_spool/fees.dat` 依存、`print()` 3箇所、非推奨 `@app.on_event("startup")`。 |
| **FAIL** | `python/code_quality` | `python_ast_audit` | Docstring 網羅率 `40.9%`（欠落12件、`TODO` 1件、`pricing.py:8` 引数名不一致1件）、裸の `except:` と `except Exception: pass`。 |
| **FAIL** | `python/dependencies` | `repo_structure_audit` | `pyproject.toml`/`uv.lock` 不在、実行時に `flake8`/`black`/`urllib3` 混入、`uvicorn`（Dockerfile）と `boto3`（`gateway.py`）が未宣言。 |
| **FAIL** | `python/modern_stack` | `python_ast_audit` | Import衛生 `75.0%`（`isort` 違反4件、`from math import *`、関数内 `import json`）、Pydantic v1 `@validator`/`Config`、`os.path` 利用。 |
| **FAIL** | `python/testing` | `python_test_audit` | 12ソースに対しテストファイル1件・関数1件のみ、かつ `assert` 文が `0個`（アサーションフリーテスト）。 |
| **FAIL** | `python/typing` | `python_ast_audit` | 型安全性カバレッジ `44.4%`（未注釈7箇所、未型付け `dict` 1箇所、`schemas.py:9` 無制限 `# type: ignore` 1箇所、`py.typed` 無し）。 |
| **WARN** | `common/git_workflow` | `repo_structure_audit` | `.gitignore` 不在によりビルド生成物や秘密鍵混入リスクがあり、PR トリガーでテストではなく同期スクリプトを実行。 |

## 全28件の指摘一覧（`CRITICAL -> HIGH -> MEDIUM -> LOW` 順）

| # | 重大度 | ルールID | 箇所 | 検出された証跡と推奨修正内容 |
| :---: | :---: | :--- | :--- | :--- |
| 1 | **CRITICAL** | `common/security` | `order_app/services/processor.py:8` | `WEBHOOK_SIGNING_SECRET = "sk_live_***REDACTED***"` が直書き。即時削除・ローテーションし環境変数設定へ移行。 |
| 2 | **CRITICAL** | `common/security_vulnerability` | `Dockerfile:1` | `FROM python:latest` (Debian 13.7) に OS CVE 3,554件（CRIT 24 / HIGH 436）および `DS-0002` root 実行。`python:3.12-slim` 非root 多段化。 |
| 3 | **CRITICAL** | `common/security_vulnerability` | `order_app/schemas.py:9` | `web_pentest`（`http://127.0.0.1:54305`, `3.52s`）が `status="error"`・`server_booted=false`（`model-field-missing-annotation`）で起動失敗し全 DAST プローブが遮断。型注釈付与と起動復旧。 |
| 4 | **CRITICAL** | `common/security_vulnerability` | `order_app/services/processor.py:30` | `yaml.load(override_yaml)` (`CWE-502`) と L63 `subprocess.run(..., shell=True)` (`CWE-78`)。`yaml.safe_load` 化と `shell=True` 廃止。 |
| 5 | **CRITICAL** | `common/supply_chain` | `.github/workflows/deploy.yml:4` | `pull_request_target` + `actions/checkout@main` + `permissions` 未設定で `legacy_sync.sh` を実行。`pull_request` 化・SHA固定。 |
| 6 | **CRITICAL** | `common/runtime_verification` | `tests/test_orders.py:4` | `pytest-cov` 実測行カバレッジ `6.6%` (`7/106`)・分岐 `0.0%`（主要6モジュール全て `0.0%`）。単体・HTTP テストで 80%以上を強制。 |
| 7 | **CRITICAL** | `python/testing` | `tests/test_orders.py:4` | `test_currency_smoke()` に `assert` が皆無。明示的アサーションとミラー構成の pytest スイートを整備。 |
| 8 | **CRITICAL** | `common/runtime_verification` | `order_app/schemas.py:9` | 未注釈 `legacy_flag = True` により Pydantic v2 下で `PydanticUserError` が発生し ASGI 起動スモーク失敗。型注釈付与と Pydantic v2 移行。 |
| 9 | **HIGH** | `common/architecture` | `order_app/domain/pricing.py:3` | `order_app.api.handlers` 逆参照による循環依存と `infra._internal` 直接結合。定数を `constants.py` へ移し Decimal 演算化。 |
| 10 | **HIGH** | `common/production_readiness` | `order_app/api/handlers.py:31` | `/legacy/health` が未マウントの `Flask` 側に定義され FastAPI にヘルスプローブが無い。FastAPI `GET /healthz` へ統一。 |
| 11 | **HIGH** | `common/twelve_factor` | `order_app/services/processor.py:21` | `global ORDER_STATE_CACHE`・`tags=[]`・散在 `os.getenv`・`/tmp` ファイル参照。`pydantic-settings` と外部 Repository 注入へ移行。 |
| 12 | **HIGH** | `common/maintainability` | `order_app/services/processor.py:11` | 8引数・認知的複雑度 `44`・`tags=[]`・裸の `except:`（L31）・例外握り潰し（L64）。DTO化と責務別関数分割を実施。 |
| 13 | **HIGH** | `common/production_readiness` | `order_app/infra/gateway.py:11` | `async def` 内で `time.sleep(1)` と `timeout=` 無しの `requests.post` を実行。`httpx.AsyncClient(timeout=5.0)` へ置換。 |
| 14 | **HIGH** | `common/modern_stack` (`python/modern_stack`) | `order_app/infra/gateway.py:7` | `from math import *` と未宣言 `boto3` インポート（クリーン環境で `ImportError`）。不要インポート削除と非同期 HTTP 化。 |
| 15 | **HIGH** | `common/production_readiness` | `Dockerfile:6` | `CMD ["uvicorn", ...]` に対し `requirements.txt` に `uvicorn` が未宣言。実行時依存に明記し `HEALTHCHECK` を追加。 |
| 16 | **HIGH** | `common/supply_chain` | `Dockerfile:1` | `:latest` タグ・root 実行・`.dockerignore` 欠落により `config/` 鍵ファイルがイメージに混入。非root slim 化と除外設定追加。 |
| 17 | **HIGH** | `common/supply_chain` | `requirements.txt:1` | 全8依存が未ピン・ロック不在、`LICENSE`/`SECURITY.md`/Dependabot 欠落。`uv.lock` と OpenSSF ガバナンス文書を整備。 |
| 18 | **HIGH** | `python/dependencies` | `requirements.txt:1` | `setup.py` + `requirements.txt` に `flake8`/`black` が混在し `uvicorn`/`boto3` が欠落。PEP 621 `pyproject.toml` へ移行。 |
| 19 | **HIGH** | `common/security_vulnerability` | `order_app/api/handlers.py:17` | ステージ済 `.pni/pentests/`（`test_app_probes.py`: `CWE-306` 無認証 `POST /orders`・`CWE-20` 未型付け `items` 500 検証）が起動障害で `0/0` 未実行。修正後 CI DAST ゲート化。 |
| 20 | **HIGH** | `common/security_vulnerability` | `order_app/api/handlers.py:18` | `POST /orders` が認証無し・`response_model` 無し・`Dict[str, Any]` 入力で `customer_id` を破棄。認証依存と厳格 `OrderItem` DTO を実装。 |
| 21 | **HIGH** | `common/security_vulnerability` | `requirements.txt:6` | Python 依存 CVE 7件（HIGH 4件: `setuptools@70.3.0`, `urllib3@2.7.0` ×2, `msgpack@1.1.2`）。不要依存削除と `2.8.0+` 固定。 |
| 22 | **HIGH** | `common/supply_chain` | `Dockerfile:1` | `COPY . .` と root 実行による攻撃面拡大。マルチステージ `uv sync --frozen --no-dev` と最小権限ユーザを採用。 |
| 23 | **MEDIUM** | `common/supply_chain` | `scripts/legacy_sync.sh:1` | 106行の Bash スクリプトが `set -u`/`pipefail` 無しで `/var/tmp` を操作。型付き Python CLI サブコマンドへ刷新。 |
| 24 | **MEDIUM** | `common/twelve_factor` | `order_app/services/processor.py:25` | `print()` 出力3箇所および例外の無記録握り潰し。標準 `logging` による構造化ログとエラー記録へ統一。 |
| 25 | **MEDIUM** | `common/documentation` | `README.md:1` | 2行のみのスタブ文書。アーキテクチャ・環境構築・設定変数・API例・テスト実行手順を網羅した README へ拡充。 |
| 26 | **MEDIUM** | `common/security` | `config/service_account_dummy.json:1` | サービスアカウント形式の JSON がリポジトリ管理下に存在。Git 追跡から除外し `.gitignore`/`.dockerignore` で遮断。 |
| 27 | **MEDIUM** | `python/typing` | `order_app/schemas.py:5` | Pydantic v1 `@validator`/`Config.orm_mode`・可変 `metadata: dict = {}`・`# type: ignore`。Pydantic v2 `ConfigDict` へ更新。 |
| 28 | **LOW** | `python/code_quality` | `order_app/domain/pricing.py:8` | Docstring が存在しない旧引数 `raw_items`/`discount_pct` を記載（他12箇所で Docstring 欠落）。実シグネチャへ同期。 |
