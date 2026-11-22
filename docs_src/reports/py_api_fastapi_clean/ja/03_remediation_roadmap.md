# 3. 推奨改善ロードマップ

`order-dispatch` はすでに **グレード S（94/100）** に達しており、緊急対応を要する重大・高リスクのアプリ脆弱性（`P0` ブロッカー）は `0` 件です。したがって改善計画は、ライブ DAST で確認された `CWE-306` 認証欠如およびベースイメージ OS/`pip` CVE を解消する 2 件の **P1** セキュリティ強化施策と、マルチレプリカ水平スケールおよび分岐カバレッジ 80% 超を実現する 3 件の **P2** 本番仕上げ施策の 2 段階で構成されます。

```drawlib align=center code=fold file=remediation_roadmap.png caption="段階的改善ロードマップ（P1 セキュリティ強化 -> P2 本番運用仕上げ）"
from drawlib.canvas import save, setup
from drawlib.smartarts import Roadmap
from drawlib.styles import Styles
from drawlib.text import text

setup(width=146, height=74, dpi=150)

text(
    (73.0, 69.5),
    "order-dispatch — Phased Production Hardening Roadmap (0 P0 | 2 P1 | 3 P2)",
    style=Styles.DarkBold.patch(text_size=12.0),
)

rm = Roadmap(
    style=Styles.Neutral.patch(shape_r=1.8),
    text_style=Styles.DarkBold.patch(text_size=10.2),
    description_style=Styles.Muted.patch(text_size=9.5),
    spine_style=Styles.PrimaryBold,
    badge_style=Styles.PrimaryFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.8),
    direction="vertical",
    card_shape="rounded_rect",
    spacing=2.4,
)
rm.add(
    "Enforce OAuth2/JWT or mTLS Auth & Tenant AuthZ on /v1/orders",
    "routes.py | Add FastAPI Security/Depends() guard to resolve live DAST CWE-306 & line 73 TODO",
    badge_text="P1-1",
    style=Styles.WarningNeutral.patch(shape_r=1.8),
    badge_style=Styles.WarningFlat,
)
rm.add(
    "Refresh Base Image, Multi-Stage Build (No pip) & Add HEALTHCHECK",
    "Dockerfile | Patch python:3.12.x-slim, strip pip@24.2 from runtime venv, clear DS-0026",
    badge_text="P1-2",
    style=Styles.WarningNeutral.patch(shape_r=1.8),
    badge_style=Styles.WarningFlat,
)
rm.add(
    "Add Durable OrderRepository Adapter for Multi-Replica Prod",
    "main.py, repository.py | Wire PostgreSQL/Redis adapter via ServiceSettings (12-Factor VI)",
    badge_text="P2-3",
    style=Styles.PrimaryNeutral.patch(shape_r=1.8),
    badge_style=Styles.PrimaryFlat,
)
rm.add(
    "Add HTTP Security Headers & Gate /openapi.json in Production",
    "main.py | Set X-Content-Type-Options: nosniff, X-Frame-Options: DENY; openapi_url=None in prod",
    badge_text="P2-4",
    style=Styles.Neutral.patch(shape_r=1.8),
    badge_style=Styles.SecondaryFlat,
)
rm.add(
    "Expand FastAPI TestClient & httpx MockTransport Branch Tests",
    "test_routes.py, routes.py, webhook_client.py | Cover 200/404, lifespan, HTTPError (branch >=80%)",
    badge_text="P2-5",
    style=Styles.Neutral.patch(shape_r=1.8),
    badge_style=Styles.SecondaryFlat,
)
rm.draw((4.0, 3.0), width=138.0, height=62.5)

save()
```

## アクションプラン・トレーサビリティマトリクス

各改善アクションは、対象ファイル、関連 PNI ルール・CWE/CVE ID、および期待される改善効果と 1 対 1 で紐づけられています。

```drawlib align=center code=fold file=remediation_traceability_table.png caption="アクションプラン・トレーサビリティマトリクス（優先度・対象ファイル・関連ルール/CVE・期待効果）"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Colors, Styles
from drawlib.text import text

setup(width=146, height=64, dpi=150)

text(
    (73.0, 60.0),
    "Remediation Action Plan — File & Rule/CVE Traceability",
    style=Styles.DarkBold.patch(text_size=11.5),
)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=9.5),
    header_cell_style=Styles.PrimaryFlat,
    header_text_style=Styles.WhiteBold.patch(text_size=9.8),
    border_style=Styles.MutedThin,
    has_header=True,
)
tbl.set_style_cell_evenodd(
    Colors.White,
    Styles.Dark.patch(text_size=9.5),
    Colors.Neutral,
    Styles.Dark.patch(text_size=9.5),
)
tbl.set_style_cell_header(Colors.Primary, Styles.WhiteBold.patch(text_size=9.8))
tbl.set_style_cell(
    Styles.WarningNeutral.shape_fill_color,
    Styles.DarkBold.patch(text_size=9.5),
    rows=[1, 2],
    columns=[0],
)
tbl.set_style_cell(
    Styles.PrimaryNeutral.shape_fill_color,
    Styles.DarkBold.patch(text_size=9.5),
    rows=[3, 4, 5],
    columns=[0],
)

data = [
    ["Prio", "Action", "Target Files", "Related Rules / IDs", "Expected Impact"],
    [
        "P1",
        "Auth & tenant authZ\non /v1/orders",
        "api/routes.py",
        "common/\nsecurity_vulnerability,\nCWE-306",
        "Blocks unauth order\nwrites & enumeration",
    ],
    [
        "P1",
        "Refresh base image,\nno pip, HEALTHCHECK",
        "Dockerfile",
        "SEC-01/02, CVE-2026-\n42010 / 31789 / 8643",
        "Drops 6 pip CVEs, OS\nCRITs & DS-0026",
    ],
    [
        "P2",
        "Durable prod\nOrderRepository",
        "main.py,\ninfra/repository.py",
        "common/\ntwelve_factor",
        "Stateless multi-replica\nscale-out (12F VI)",
    ],
    [
        "P2",
        "Security headers &\nprod OpenAPI gate",
        "main.py",
        "SEC-06, CWE-693,\nCWE-200",
        "Closes live DAST\nheader/schema gaps",
    ],
    [
        "P2",
        "TestClient & httpx\nMockTransport tests",
        "test_routes.py,\nroutes.py, webhook",
        "common/\nruntime_verification",
        "Lifts branch cov from\n62.5% to >=80%",
    ],
]

tbl.draw_flexible(
    (2.0, 56.5),
    column_widths=[10.0, 32.0, 28.0, 40.0, 32.0],
    row_heights=[7.0, 9.2, 9.2, 9.2, 9.2, 9.2],
    data=data,
    align="top_left",
)

save()
```

### エンジニアリング詳細仕様（`P1 -> P2`）

| 優先度 | カテゴリ | 改善施策および実装仕様 | 対象ファイル | 関連ルール・ID | 期待される効果 |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **P1** | `security` | **`/v1/orders` エンドポイントへの認証・テナント認可の強制**: `POST /v1/orders` および `GET /v1/orders/{order_id}` に OAuth2/JWT または mTLS の呼び出し元プリンシパル `Depends()` 依存を導入し、`CWE-306` と 73 行目の `TODO(security)` を解消する。 | `src/order_dispatch/api/routes.py` | `common/security_vulnerability`, `CWE-306` | 未認証による不正注文作成および他テナント注文 ID 列挙を防止。 |
| **P1** | `security` | **`Dockerfile` ベースイメージ更新・`pip` 除外マルチステージ化・`HEALTHCHECK` 追加**: `python:3.12.6-slim-bookworm` を最新のパッチ適用済み 3.12 slim ダイジェストへ更新し、ビルド済み仮想環境のみを実行ステージへコピー（`pip@24.2` を除去）したうえで `/healthz` 向け `HEALTHCHECK` を追加する。 | `Dockerfile` | `common/security_vulnerability`, `SEC-01`, `SEC-02`, `CVE-2026-42010`, `CVE-2026-31789`, `CVE-2026-8643` | 全 6 件の `pip` CVE を根絶し、パッチ可能な Debian OS CRITICAL CVE と Trivy `DS-0026` を解消。 |
| **P2** | `architecture` | **マルチレプリカ本番配備向けの永続 `OrderRepository` アダプタ追加**: `env == "prod"` 時に `ServiceSettings` 経由で PostgreSQL/Redis 永続アダプタを注入できるようにし、プロセスを完全にステートレス化する。 | `src/order_dispatch/main.py`, `src/order_dispatch/infra/repository.py` | `common/twelve_factor` | 再起動時のデータ欠損ゼロと 12-Factor VI に準拠した水平レプリカ拡張を実現。 |
| **P2** | `security` | **HTTP セキュリティヘッダーミドルウェア追加と本番 `/openapi.json` 非公開化**: `X-Content-Type-Options: nosniff` および `X-Frame-Options: DENY` を付与する軽量 Starlette ミドルウェアを登録し、`settings.env == "prod"` では `openapi_url=None` とする。 | `src/order_dispatch/main.py` | `common/security_vulnerability`, `SEC-06`, `CWE-693`, `CWE-200` | ライブ DAST で検出された `CWE-693`・`CWE-200` のベースライン強化項目を解消。 |
| **P2** | `testing` | **FastAPI `TestClient` と `httpx` `MockTransport` による HTTP／ライフスパン分岐テスト追加**: `/healthz`、`POST /v1/orders`、`GET /v1/orders/{id}`（200・404）、ライフスパン起動／終了、および `MockTransport` による `httpx.HTTPError` フォールバック経路を網羅する。 | `tests/test_routes.py`, `src/order_dispatch/api/routes.py`, `src/order_dispatch/infra/webhook_client.py` | `common/runtime_verification` | 実測分岐カバレッジを `62.5%` から `>=80%` へ引き上げ、HTTP 境界テストの空白を解消。 |
