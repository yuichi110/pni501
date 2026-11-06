# 3. 推奨する変更対応

検出された20件の指摘と7件の `WARN` ルールを最小工数で解消するため、緊急度・効果順に **P0（即時対応：1件）→ P1（高優先度：4件）→ P2（本番運用・HTTPヘッダ強化：6件）** の計11アクションへ集約しました。対象コードの構造変更は小さく、`Dockerfile`・`uv.lock`・API認証依存関数・ASGI 統合テスト・セキュリティヘッダミドルウェアの整備で全リスクを解消できます。

```drawlib file=03_remediation_roadmap.png caption="図3-1: フェーズ別改善ロードマップ (P0 基盤脆弱性解消 -> P1 認証・ロック・検証強化 -> P2 本番運用・DASTヘッダ強化)"
from drawlib.canvas import setup
from drawlib.smartarts import Panel, Roadmap
from drawlib.styles import Styles

setup(width=146, height=62, dpi=150)

Panel(
    "段階的改善ロードマップ (全11アクション: P0=1件 / P1=4件 / P2=6件)",
    style=Styles.Neutral,
    header_style=Styles.Primary,
    text_style=Styles.WhiteBold.patch(text_size=11.0),
).draw((2, 2), width=142, height=58)

rm = Roadmap(
    style=Styles.WhiteBordered,
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Dark.patch(text_size=9.5),
    spine_style=Styles.PrimaryBold,
    badge_style=Styles.Danger,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.5),
    direction="horizontal",
)
rm.add(
    "Phase 1: P0 基盤刷新",
    "最新python:3.12-slim更新と\n多段uvビルドでpip・OS CVE除去",
    badge_text="P0 即時",
)
rm.add(
    "Phase 2: P1 認証・検証",
    "完全uv.lock・/v1/orders認証・\nTestClient統合テストで分岐90%超",
    badge_text="P1 優先",
)
rm.add(
    "Phase 3: P2 運用・DAST強化",
    "nosniff/OpenAPI制御・共有プール・\n冪等キー・HEALTHCHECK・README",
    badge_text="P2 強化",
)
rm.draw((5, 5), width=136, height=42)
```

## 優先アクションと期待効果のマトリクス

上位5件（P0〜P1）および DAST 指摘（`CWE-306`/`CWE-200`/`CWE-693`）の完了により、セキュリティ軸（`78` → `94+`）・テスト軸（`81` → `95+`）・依存関係軸（`88` → `96+`）が大幅に改善し、総合 Grade S 水準（93点以上）へ到達します。

```drawlib file=03_priority_action_matrix.png caption="図3-2: P0〜P1 最優先改善アクションの対象ファイル・関連ルール・期待効果サマリー"
from drawlib.canvas import setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=66, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=9.5),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.5),
    border_style=Styles.Gray4Thin,
)
tbl.draw_flexible(
    (2, 64),
    column_widths=[12.0, 44.0, 38.0, 48.0],
    row_heights=[9.5, 10.5, 10.5, 10.5, 10.5, 10.5],
    data=[
        ["優先度", "推奨アクション要点", "変更対象ファイル", "解消されるリスク / 期待効果"],
        ["P0", "ベースイメージ更新 & pipレス多段ビルド", "Dockerfile", "pip CVE 6件全廃・OpenSSL/GnuTLS CRITICAL解消"],
        ["P1", "完全な uv.lock 生成 & --frozen 導入", "uv.lock, Dockerfile, ci.yml", "SHA-256ハッシュ検証済の100%決定論的ビルド"],
        ["P1", "/v1/orders OAuth2/JWT 認証・認可強制", "api/routes.py, settings.py", "DAST CWE-306未認証201注文注入・IDOR参照を防止"],
        ["P1", "TestClient + Lifespan HTTP 統合テスト", "tests/test_routes.py", "routes.py(56%)・main.py(67.9%)の未実行経路解消"],
        ["P1", "AsyncWebhookClient MockTransport 検証", "tests/test_dispatcher.py", "分岐カバレッジを62.5%から90%超へ引き上げ"],
    ],
)
```

## 全11件の改善アクション一覧（トレーサビリティ表）

| # | 優先度 | 分野 | 推奨アクションと具体実装内容 | 対象ファイル | 関連ルール / CVE / CWE |
| :---: | :---: | :--- | :--- | :--- | :--- |
| 1 | **P0** | `security` | **`python:3.12-slim-bookworm` 最新化とマルチステージ `uv` ビルド採用**: 最新パッチ済イメージへ更新し、本番ステージから `pip@24.2` を除外する。 | `Dockerfile` | `common/security_vulnerability`, `common/supply_chain`, `CVE-2026-31789`, `CVE-2026-42010`, `CVE-2026-13346` |
| 2 | **P1** | `dependencies` | **完全な `uv.lock` 再生成と `--frozen` インストールの徹底**: `uv lock` で推移的依存とハッシュを記録し、`pip install .` を `uv sync --frozen --no-dev` に置換。 | `uv.lock`, `Dockerfile`, `.github/workflows/ci.yml` | `python/dependencies`, `common/supply_chain` |
| 3 | **P1** | `security` | **`/v1/orders` エンドポイントへの OAuth2/JWT 認証・テナント認可追加**: FastAPI `Depends` で Bearer トークンと `customer_id` 権限を検証し、未認証 HTTP `201`（`CWE-306`）を遮断。 | `src/order_dispatch/api/routes.py`, `src/order_dispatch/settings.py` | `common/security`, `common/security_vulnerability`, `CWE-306` |
| 4 | **P1** | `testing` | **FastAPI ルート・Lifespan の ASGI HTTP 統合テスト追加**: `with TestClient(create_app()) as client:` で `200`/`201`/`404`/`422` を検証する。 | `tests/test_routes.py`, `tests/test_dispatcher.py` | `python/testing` |
| 5 | **P1** | `testing` | **実測分岐・行カバレッジ未達箇所の解消**: `httpx.MockTransport` による `AsyncWebhookClient` 正常・5xx・Timeout 検証と `pricing.py:L49` 境界検証を追加。 | `tests/test_routes.py`, `tests/test_dispatcher.py`, `src/order_dispatch/api/routes.py`, `src/order_dispatch/infra/webhook_client.py` | `common/runtime_verification`, `python/testing` |
| 6 | **P2** | `architecture` | **Webhook `Idempotency-Key` 付与と永続 Repository 切替対応**: `record.order_id` を冪等キーヘッダに設定し、外部 DB アダプタ注入を可能にする。 | `src/order_dispatch/infra/webhook_client.py`, `src/order_dispatch/main.py` | `common/twelve_factor`, `common/production_readiness` |
| 7 | **P2** | `architecture` | **Lifespan スコープの `httpx.AsyncClient` コネクションプール共有**: リクエスト毎のクライアント生成を廃止し、TLS ハンドシェイク負荷を削減する。 | `src/order_dispatch/main.py`, `src/order_dispatch/infra/webhook_client.py` | `python/frameworks/fastapi`, `common/maintainability` |
| 8 | **P2** | `dependencies` | **コンテナ `HEALTHCHECK` 命令追加とベースイメージ `@sha256` 固定**: `/healthz` プローブ定義（Trivy `DS-0026` 解消）とダイジェスト固定を行う。 | `Dockerfile` | `common/supply_chain` |
| 9 | **P2** | `documentation` | **開発者検証コマンドと全環境変数リファレンスの `README.md` 追記**: `pytest`/`ruff`/`ty` 実行手順および `ORDER_DISPATCH_VIP_DISCOUNT_RATE` を明記する。 | `README.md` | `common/documentation` |
| 10 | **P2** | `security` | **ASGI セキュリティヘッダミドルウェア追加と本番 `/openapi.json` 非公開化**: `X-Content-Type-Options: nosniff` / `X-Frame-Options: DENY` 付与と `settings.env != 'dev'` での OpenAPI 無効化を行い、DAST 全19プローブ通過を達成する。 | `src/order_dispatch/main.py`, `src/order_dispatch/settings.py` | `common/security_vulnerability`, `CWE-693`, `CWE-200` |
| 11 | **P2** | `security` | **`ServiceSettings` の URL スキーム・数値境界バリデーション強化**: `HttpUrl`（HTTPS必須）と `Field(gt=0.0, le=30.0)` 等の起動時制約を追加する。 | `src/order_dispatch/settings.py` | `common/security`, `python/typing` |
