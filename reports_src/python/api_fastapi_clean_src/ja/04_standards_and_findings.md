# 4. 検査指標・ルール適合マトリクスと指摘一覧

本ワークフロー（`py_api_fastapi_clean` / `wf-ee9a9eb6`）では、8つの AI 監査ステップと5つの決定論的検査（`project_inspect`・`ast_analyze`・`run_check`・`security_scan`・`web_pentest`）を通じて全16ルールを評価しました。結果は **`FAIL` 0件・`WARN` 7件・`PASS` 9件（適合率 56.3%）**、改善指摘は計20件（`HIGH` 1件・`MEDIUM` 7件・`LOW` 12件）です。

```drawlib file=04_audit_step_scores.png caption="図4-1: 全8監査ステップ別スコア比較（低スコア順）とルール適合・指摘内訳KPI"
from drawlib.canvas import setup
from drawlib.charts.bar import BarChart
from drawlib.smartarts import KpiCards
from drawlib.styles import Styles

setup(width=146, height=68, dpi=150)

chart = BarChart(
    axis_line_style=Styles.Gray5Thin,
    grid_style=Styles.Gray3DashedThin,
    axis_text_style=Styles.Dark.patch(text_size=9.2),
    value_text_style=Styles.DarkBold.patch(text_size=9.2),
    background_style=Styles.Neutral,
    title="全8監査ステップ別スコア (低スコア順・100点満点)",
    title_style=Styles.DarkBold.patch(text_size=10.5),
    categories=[
        "脆弱性・SAST",
        "テスト監査",
        "Web侵入検証",
        "コンテナ実行",
        "構造・統制",
        "運用準備度",
        "供給網・CI",
        "AST静的解析",
    ],
    orientation="horizontal",
    bar_width_ratio=0.62,
    bar_r=0.8,
    value_format="{:.0f}",
)
chart.value_axis.min_value = 0
chart.value_axis.max_value = 105
chart.add_series("監査スコア", [78, 78, 78, 86, 91, 91, 92, 93], style=Styles.Primary)
chart.draw((2, 2), width=82, height=64)

kpis = KpiCards(
    style=Styles.WhiteBordered,
    metric_style=Styles.PrimaryBold.patch(text_size=15.5),
    text_style=Styles.DarkBold.patch(text_size=9.5),
    description_style=Styles.Dark.patch(text_size=9.5),
    accent_style=Styles.Primary,
)
kpis.add("0 件", "FAIL (重大違反)", "構文・重大侵害ゼロ")
kpis.add("7 件", "WARN (改善推奨)", "OS・認証・分岐網羅")
kpis.add("9 件", "PASS (完全適合)", "4層DAG・12Factor")
kpis.add("20 件", "指摘総数", "H:1 / M:7 / L:12")
kpis.draw((87, 2), width=57, height=64, columns=2)
```

## WARN ルール7件の要点と上位重大度指摘の可視化

`WARN` 判定となった7ルールはいずれも設計破綻ではなく、ベースイメージ更新・ロックファイル完全化・OAuth2/JWT 認証フック＆HTTPヘッダ実装・`TestClient` 統合テスト追加によって確実に `PASS` へ昇格可能です。

```drawlib file=04_warn_rules_and_top_findings.png caption="図4-2: 要注意 (WARN) ルール7件の証跡サマリーと解消アプローチ"
from drawlib.canvas import setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=72, dpi=150)

tbl = Table(
    cell_style=Styles.WarningNeutral,
    text_style=Styles.Dark.patch(text_size=9.5),
    header_cell_style=Styles.Dark,
    header_text_style=Styles.WhiteBold.patch(text_size=9.5),
    border_style=Styles.Gray4Thin,
)
tbl.draw_flexible(
    (2, 70),
    column_widths=[14.0, 36.0, 46.0, 46.0],
    row_heights=[9.0, 8.5, 8.5, 8.5, 8.5, 8.5, 8.5, 8.5],
    data=[
        ["判定", "ルールID", "主な検出証跡 (Evidence)", "PASS昇格への解消条件"],
        ["WARN", "common/security_vulnerability", "OS 508・pip 6・DAST CWE-306/200/693", "最新slim化・API認証・nosniffヘッダ追加"],
        ["WARN", "common/security", "routes.py:L60,L83 認証・認可未実装", "/v1/ordersへのOAuth2/JWT認可強制"],
        ["WARN", "python/dependencies", "uv.lock推移的依存未記録・pip install", "uv lock完全化とuv sync --frozen適用"],
        ["WARN", "common/supply_chain", "Dockerfile HEALTHCHECK欠落・pip残存", "HEALTHCHECK追加とマルチステージ化"],
        ["WARN", "python/testing", "test_routes.pyがHTTP呼び出し未実行", "TestClient + MockTransportテスト追加"],
        ["WARN", "common/runtime_verification", "全体分岐62.5% (routes 56%, webhook 55.6%)", "HTTP全分岐通電で分岐75%以上へ向上"],
        ["WARN", "common/documentation", "READMEにpytest/ruff/ty手順が未記載", "開発検証コマンドと全環境変数を追記"],
    ],
)
```

## 全16ルール適合マトリクス（`WARN` → `PASS` 順）

| 判定 | ルールID | Step | 主な検証証跡と判定根拠 |
| :---: | :--- | :---: | :--- |
| **WARN** | `common/documentation` | `act-02` | `README.md:L1-L34` に概要・起動・設定・API例を備えるが、`pytest`/`ruff`/`ty` 実行手順と `ORDER_DISPATCH_VIP_DISCOUNT_RATE` 記載が不足。 |
| **WARN** | `common/runtime_verification` | `act-12` | ビルド(`28.40s`)・単体テスト(`4/4`)・`/healthz` スモーク(`200`)は全て成功、行網羅率 `85.2%` だが分岐網羅率が `62.5%`（目標70%未満）。 |
| **WARN** | `common/security` | `act-03` | DTO `extra="forbid"`・非root実行・秘密漏洩0件を満たすが、`routes.py:L60,L73,L83` の OAuth2/JWT 認証・テナント認可が未実装。 |
| **WARN** | `common/security_vulnerability` | `act-05`/`16` | 実行時依存CVE `0件`・危険シンク `0件`・DAST重大指摘 `0件`(`15/19`合格)だが、OS CVE `508件`・`pip@24.2` `6件`・ライブ `CWE-306`/`200`/`693` を検出。 |
| **WARN** | `common/supply_chain` | `act-14` | GitHub Actions 40文字SHA固定・`contents: read`・Dependabot週次監視を完備するが、`Dockerfile` の `pip install .` と `uv.lock` 不完全が残存。 |
| **WARN** | `python/dependencies` | `act-02` | `pyproject.toml` で実行時5依存と `dev` 群を分離済だが、`uv.lock` にサードパーティ解決ピンとハッシュが含まれていない。 |
| **WARN** | `python/testing` | `act-10` | テスト4件すべてアサーション有・オフライン決定論的だが、`tests/test_routes.py` が `TestClient` 経由の HTTP 実行を行っていない。 |
| **PASS** | `common/architecture` | `act-05` | 循環依存 `0件`・境界違反 `0件`。`api -> services -> domain/infra` の単方向 DAG と `domain/` のフレームワーク非依存を維持。 |
| **PASS** | `common/git_workflow` | `act-02` | `.gitignore` でキャッシュ・仮想環境を除外し、`.github/workflows/ci.yml` で `push` / `pull_request` 自動検証ゲートを運用。 |
| **PASS** | `common/maintainability` | `act-05` | 複雑関数 `0件`・過剰引数 `0件`・グローバル状態 `0件`。最大ファイル長 `74 LOC`（計435 LOC）で高い凝集度と保守性を維持。 |
| **PASS** | `common/production_readiness` | `act-09` | 外部通信タイムアウト漏れ `0件`（`5.0s` 明示）・障害時 `WEBHOOK_DEFERRED` 縮退・`/healthz` 起動スモーク `2.49s` で HTTP `200` 応答。 |
| **PASS** | `common/twelve_factor` | `act-09` | 環境変数参照を `ServiceSettings` に一元化（散在参照 `0件`）、標準 `logging` モジュール採用（`print` 出力 `0件`）。 |
| **PASS** | `python/code_quality` | `act-05` | Google スタイル Docstring カバレッジ `100.0%`、空 Docstring・シグネチャ不一致ともに `0件`。 |
| **PASS** | `python/frameworks/fastapi` | `act-05` | 非推奨 `@app.on_event` 不使用、`@asynccontextmanager lifespan`・`Depends` DI・全ルートの `response_model` 明示を徹底。 |
| **PASS** | `python/modern_stack` | `act-05` | Import衛生 `100.0%`、ワイルドカード Import `0件`、未使用・未宣言依存 `0件`、`StrEnum` / PEP 604 型記法を採用。 |
| **PASS** | `python/typing` | `act-05` | 型安全性カバレッジ `100.0%`、`Any` 乱用・無制限 `type: ignore` `0件`、`src/order_dispatch/py.typed` マーカー配置済。 |

## 全20件の指摘一覧（重大度 `HIGH` → `MEDIUM` → `LOW` 順）

| # | 重大度 | ルールID | 箇所 | 検出された証跡と推奨修正内容 |
| :---: | :---: | :--- | :--- | :--- |
| 1 | **HIGH** | `common/security_vulnerability` | `Dockerfile:1` | `python:3.12.6-slim-bookworm` (Debian 12.7) に OS CVE 508件（CRITICAL 9 / HIGH 116：`openssl`, `libgnutls30`, `perl-base` 等）。最新パッチ済イメージへ更新。 |
| 2 | **MEDIUM** | `python/dependencies` | `uv.lock:4` | ルート `order-dispatch` のみ記載され推移的依存ピンが欠落、`Dockerfile:9` が `pip install .` を使用。`uv lock` と `uv sync --frozen --no-dev` へ統一。 |
| 3 | **MEDIUM** | `common/security` | `api/routes.py:73` | `# TODO(security)` の通り OAuth2/JWT 認証・テナント別レート制限が未実装。FastAPI `Security`/`Depends` で認証・認可を強制。 |
| 4 | **MEDIUM** | `common/security_vulnerability` | `Dockerfile:9` | ランタイムイメージ内の `pip@24.2` に6件の CVE（MEDIUM 5 / LOW 1、`CVE-2026-13346` 等）。マルチステージビルドで本番から `pip` を除外。 |
| 5 | **MEDIUM** | `common/security_vulnerability` | `api/routes.py:59` | **SEC-06 ライブDAST (`CWE-306`)**: 未認証 `POST /v1/orders` が HTTP `201 Created`（`webhook_deferred`）で成功。OAuth2/JWT 認証ガードを実装。 |
| 6 | **MEDIUM** | `common/security_vulnerability` | `api/routes.py:60` | `POST /v1/orders` (L60) と `GET /v1/orders/{order_id}` (L83) が `has_auth_hint=false`。Bearer トークン検証と `customer_id` 所有権照合を追加。 |
| 7 | **MEDIUM** | `common/runtime_verification` | `api/routes.py:29` | 実測カバレッジで `routes.py` 行 `56.0%`（分岐 `0.0%`）、`main.py` 行 `67.9%`。`with TestClient(create_app())` で Lifespan と全 HTTP 応答分岐を実行。 |
| 8 | **MEDIUM** | `python/testing` | `tests/test_routes.py:23` | `router.routes` のパス文字列確認のみで ASGI リクエスト未実行。`TestClient` による `200`/`201`/`404`/`422` 統合テストを追加。 |
| 9 | **LOW** | `common/twelve_factor` | `main.py:33` | `InMemoryOrderRepository` がプロセス内メモリ保持。マルチレプリカ運用時は PostgreSQL/Redis 等の永続 `OrderRepository` 実装を選択可能にする。 |
| 10 | **LOW** | `python/frameworks/fastapi` | `infra/webhook_client.py:42` | 通知毎に `httpx.AsyncClient` を生成・破棄。Lifespan 管理の共有 `AsyncClient` 注入で Keep-Alive 接続プールを再利用。 |
| 11 | **LOW** | `common/production_readiness` | `infra/webhook_client.py:43` | Webhook POST に `Idempotency-Key` ヘッダや再送制御がない。`Idempotency-Key: record.order_id` 付与と Outbox 再送を検討。 |
| 12 | **LOW** | `common/supply_chain` | `workflows/ci.yml:18` | `ruff` と `pytest` のみ実行し、`pyproject.toml` 定義済の型チェッカ `ty` が未実行。`uv run ty check` ステップを CI に追加。 |
| 13 | **LOW** | `common/supply_chain` | `Dockerfile:14` | コンテナ `HEALTHCHECK` 未定義かつ `--host 127.0.0.1` 固定。オーケストレータ向けにホスト設定変数化と `/healthz` プローブを追加。 |
| 14 | **LOW** | `common/documentation` | `README.md:14` | 開発検証コマンド（`pytest`/`ruff`/`ty`）および `ORDER_DISPATCH_VIP_DISCOUNT_RATE` が未記載。開発手順と環境変数表を更新。 |
| 15 | **LOW** | `common/security` | `settings.py:17` | `webhook_url: str` にスキーム検証がない。`HttpUrl`（本番 HTTPS 強制）および `http_timeout_sec` の上限・下限 `Field` 制約を追加。 |
| 16 | **LOW** | `common/security_vulnerability` | `Dockerfile:12` | Trivy IaC 指摘 `DS-0026` (`LOW`): `Dockerfile` に `HEALTHCHECK` 命令が未定義。Python 標準ライブラリによる `/healthz` 確認を追加。 |
| 17 | **LOW** | `common/security_vulnerability` | `main.py:58` | **SEC-06 ライブDAST (`CWE-200`)**: `GET /openapi.json`（`4,753` bytes）が未認証で公開。本番環境では `openapi_url=None` 等で非公開化。 |
| 18 | **LOW** | `common/security_vulnerability` | `main.py:60` | **SEC-06 ライブDAST (`CWE-693`)**: `GET /healthz` 応答に `X-Content-Type-Options: nosniff` が未付与。ASGI セキュリティヘッダミドルウェアを追加。 |
| 19 | **LOW** | `common/runtime_verification` | `infra/webhook_client.py:36` | 実測カバレッジで `webhook_client.py` が `55.6%`（L36, L41-47 未通過）。`httpx.MockTransport` で 2xx・5xx・Timeout 経路を網羅。 |
| 20 | **LOW** | `python/testing` | `tests/test_dispatcher.py:13` | `_StubWebhookClient` 差し替えにより実クラス `AsyncWebhookClient` の単体テストが不在。`MockTransport` テストを追加。 |
