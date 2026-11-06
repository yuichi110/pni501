# 6. 詳細分析：セキュリティ・脆弱性・API境界

Trivy によるファイルシステムおよびビルド済コンテナイメージ検査（`security_scan`）、Python AST SAST 解析、および隔離ループバックコンテナに対する **動的 Web ペネトレーションテスト（`web_pentest` / `.pni/pentests/examples/python/api_fastapi_clean`）** の結果、**アプリケーションの直接・推移的 Python 実行時ライブラリ（`fastapi`, `httpx`, `pydantic`, `pydantic-settings`, `uvicorn`）の CVE は `0件`**、コード内の **CWE 危険シンクは `0件`**、秘密情報漏洩 **`0件`**、ライブ DAST における **CRITICAL / HIGH 脆弱性も `0件`（`15/19` プローブ合格）** でした。一方、コンテナ同梱 `pip@24.2` に6件（MEDIUM 5 / LOW 1）、古い `python:3.12.6-slim-bookworm`（Debian 12.7）OS 層に508件（CRITICAL 9 / HIGH 116）、およびライブ HTTP 検証で実証された3件の境界ハードニング課題（`CWE-306` 未認証 `POST /v1/orders` HTTP `201`、`CWE-200` `/openapi.json` 公開、`CWE-693` `nosniff` ヘッダ欠落）が確認されました。

```drawlib file=06_vulnerability_breakdown.png caption="図6-1: レイヤ別CVE重大度内訳（左）と修正バージョンが判明している優先パッチ対象一覧（右）"
from drawlib.canvas import setup
from drawlib.charts.bar import BarChart
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=68, dpi=150)

chart = BarChart(
    axis_line_style=Styles.Gray5Thin,
    grid_style=Styles.Gray3DashedThin,
    axis_text_style=Styles.Dark.patch(text_size=9.5),
    value_text_style=Styles.DarkBold.patch(text_size=9.5),
    background_style=Styles.Neutral,
    title="コンテナ内レイヤ別 CVE 検出数 (重大度別)",
    title_style=Styles.DarkBold.patch(text_size=10.5),
    categories=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
    orientation="vertical",
    bar_mode="group",
    bar_width_ratio=0.72,
    bar_r=0.6,
    value_format="{:.0f}",
)
chart.value_axis.min_value = 0
chart.value_axis.max_value = 240
chart.add_series("Python実行時依存", [0, 0, 0, 0], style=Styles.Success)
chart.add_series("同梱 pip@24.2", [0, 0, 5, 1], style=Styles.Warning)
chart.add_series("Debian 12.7 OS層", [9, 116, 213, 162], style=Styles.Danger)
chart.draw((2, 2), width=66, height=64)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=9.5),
    header_cell_style=Styles.Dark,
    header_text_style=Styles.WhiteBold.patch(text_size=9.5),
    border_style=Styles.Gray4Thin,
)
tbl.draw_flexible(
    (71, 65),
    column_widths=[14.0, 22.0, 39.0],
    row_heights=[9.5, 10.5, 10.5, 10.5, 10.5, 10.5],
    data=[
        ["重大度", "対象パッケージ", "代表CVE / 修正済バージョン"],
        ["CRIT", "libgnutls30", "CVE-2026-42010 -> 3.7.9-2+deb12u7"],
        ["CRIT", "libssl3 / openssl", "CVE-2026-31789 -> 3.0.19-1~deb12u2"],
        ["CRIT", "perl-base", "CVE-2026-8376 -> 5.36.0-7+deb12u4"],
        ["MED", "pip (24.2)", "CVE-2026-13346他5件 -> 26.2.0 / 除外"],
        ["LOW", "Dockerfile", "DS-0026 -> HEALTHCHECK 命令を追加"],
    ],
)
```

## AST 危険シンク検査（CWE）と HTTP API 攻撃対象領域マップ

AST セキュリティシンク走査ではコマンド実行・任意コード評価・SQLインジェクション・安全でないデシリアライズ等の CWE 危険パターンは一切検出されませんでした。外部公開前に強化すべき境界は、認証ヒントを持たない `/v1/orders` 系2エンドポイントの認証・テナント認可と、`main.py` における OpenAPI 公開制御・HTTP セキュリティヘッダ付与です。

```drawlib file=06_sast_and_api_surface.png caption="図6-2: サプライチェーン・SAST・DAST防御統制（左）とHTTP APIエンドポイント認可境界マップ（右）"
from drawlib.canvas import setup
from drawlib.smartarts import CardList, Panel, Table
from drawlib.styles import Styles

setup(width=146, height=68, dpi=150)

Panel(
    "SAST・DAST & サプライチェーン統制状況",
    style=Styles.Neutral,
    header_style=Styles.Success,
    text_style=Styles.WhiteBold.patch(text_size=10.5),
).draw((2, 2), width=58, height=64)

controls = CardList(
    style=Styles.WhiteBordered,
    text_style=Styles.DarkBold.patch(text_size=9.5),
    description_style=Styles.Dark.patch(text_size=9.5),
    badge_style=Styles.SuccessNeutral,
    badge_text_style=Styles.SuccessBold.patch(text_size=9.5),
)
controls.add("AST CWE危険シンク検査", "eval/exec/shell/SQLi/SSRF危険呼び出し 0件", badge_text="0 件")
controls.add("シークレット・鍵漏洩検査", "Trivy Secret・ASTハードコード秘密情報 0件", badge_text="0 件")
controls.add("DAST 注入・MassAssign防御", "extra='forbid' HTTP 422・XSS/SQLi/LFI全遮断", badge_text="15/19")
controls.add("CI権限 & コンテナ非特権", "contents:read + SHA固定 + UID 10001実行", badge_text="PASS")
controls.draw((4, 4), width=54, height=51)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=9.5),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.5),
    border_style=Styles.Gray4Thin,
)
tbl.draw_flexible(
    (63, 65),
    column_widths=[24.0, 15.0, 42.0],
    row_heights=[9.5, 16.5, 16.5, 16.5],
    data=[
        ["HTTP エンドポイント", "認証状態", "ライブDAST挙動と推奨アクセス制御"],
        ["GET /healthz\n(routes.py:L46)", "不要\n(公開可)", "HTTP 200応答確認済。nosniff等の\nセキュリティヘッダ追加を推奨(CWE-693)"],
        ["POST /v1/orders\n(routes.py:L59)", "未実装\n(CWE-306)", "extra='forbid'で422拒否済だが未認証で\nHTTP 201成功。OAuth2/JWT認証を強制"],
        ["GET /v1/orders/{id}\n(routes.py:L83)", "未実装\n(要対応)", "未存在IDはHTTP 404返却(スタック漏洩無)。\ncustomer_id所有権の認可を追加"],
    ],
)
```

## 動的Webペネトレーションテスト (`web_pentest` / `.pni/pentests/`)

隔離ループバック環境（`http://127.0.0.1:36095`、実行時間 `5.24s`）で稼働させた Uvicorn コンテナに対し、`.pni/pentests/examples/python/api_fastapi_clean/` の `pytest` + `httpx` プローブスイート（計4ファイル・全19プローブ）を実行しました。結果ステータスは **`passed`（合格 `15` / 失敗 `3` / スキップ `1` / エラー `0`、`CRITICAL`/`HIGH` 検出 `0件`）** です。Pydantic v2 `ConfigDict(extra="forbid")` による未宣言フィールド（`total_cents`, `is_admin`）の `HTTP 422` 拒否や、反射型 XSS・SQL エラー／スタックトレース露出・パストラバーサル・CORS Origin 反射・`.env`/`.git` 露出・HTTP `TRACE` への防御が実証された一方、以下の3件の改善項目がライブ HTTP 応答として裏付けられました。

| 結果 / 重大度 | CWE / カテゴリ | プローブテスト (`test_file`) | 対象エンドポイント / 実装箇所 | ライブ HTTP 実測証跡と推奨対策 |
| :---: | :---: | :--- | :--- | :--- |
| **FAIL (`MEDIUM`)** | `CWE-306` (`missing_authentication`) | `test_create_order_enforces_authentication_guard` (`test_app_probes.py`) | `POST /v1/orders` (`src/order_dispatch/api/routes.py:59`) | 未認証リクエストに対し `HTTP 201 Created`（`{"customer_id":"unauth-caller","tier":"vip","total_cents":1800,"status":"webhook_deferred"}`）を返却。OAuth2/JWT 認証 `Depends` で `401`/`403` を強制。 |
| **FAIL (`LOW`)** | `CWE-200` (`api_schema_exposure`) | `test_openapi_schema_not_publicly_exposed_without_auth` (`test_app_probes.py`) | `GET /openapi.json` (`src/order_dispatch/main.py:58`) | 未認証の `GET /openapi.json` が `HTTP 200`（`4,753` bytes）で全 API スキーマを公開。`settings.env != "dev"` 時は `openapi_url=None` 等で非公開化。 |
| **FAIL (`LOW`)** | `CWE-693` (`missing_security_headers`) | `test_x_content_type_options_nosniff` (`test_baseline_http.py`) | `GET /healthz` (`src/order_dispatch/main.py:60`) | `GET /healthz -> 200` 応答で `X-Content-Type-Options` が未設定（`<absent>`）。ASGI ミドルウェアで `nosniff` および `X-Frame-Options: DENY` を付与。 |
| **PASS (15件)** | `CWE-915`, `79`, `89`, `22`, `209`, `538`, `942` | `test_app_probes.py`, `test_target_surface.py`, `test_baseline_http.py` | `/v1/orders`, `/v1/orders/1`, `/healthz`, `/.env`, `/.git/config` | 不正フィールド注入は `HTTP 422` で遮断、XSS/SQLi/Traversal カナリア・不正 `Origin` CORS・`TRACE`・機密パス露出・`X-Powered-By` 漏洩はいずれもゼロ（HTML 非返却のため Clickjacking 1件のみスキップ）。 |

## 主要 CVE・IaC 指摘一覧と修正バージョン対照表

| 区分 | 重大度 | 脆弱性 / ルールID | パッケージ（現在値） | 修正バージョン (`fixed_version`) | 概要と推奨緩和策 |
| :--- | :---: | :--- | :--- | :--- | :--- |
| **OS (Debian 12.7)** | **CRITICAL** | `CVE-2026-42010`, `CVE-2026-33845` | `libgnutls30@3.7.9-2+deb12u3` | `3.7.9-2+deb12u7` | GnuTLS 認証バイパス / DTLS DoS。最新 `slim-bookworm` 取得・`apt-get upgrade` で解消。 |
| **OS (Debian 12.7)** | **CRITICAL** | `CVE-2026-31789` (+ HIGH 2件) | `libssl3`, `openssl@3.0.14-1~deb12u2` | `3.0.19-1~deb12u2` (`3.0.20` 推奨) | X.509 証明書処理バッファオーバーフロー / PKCS7 UAF。OpenSSL セキュリティ更新で解消。 |
| **OS (Debian 12.7)** | **CRITICAL** | `CVE-2026-8376`, `CVE-2026-42496` | `perl-base@5.36.0-7+deb12u1` | `5.36.0-7+deb12u4` | 正規表現ヒープ破壊・`Archive::Tar` シンボリックリンク横断。Debian セキュリティ更新で解消。 |
| **OS (Debian 12.7)** | **HIGH** | `CVE-2025-6965` | `libsqlite3-0@3.40.1-2` | `3.40.1-2+deb12u2` | SQLite 整数切り詰め脆弱性。最新ベースイメージ更新で解消（ランタイム未使用パッケージ）。 |
| **Python ツール** | **MEDIUM** | `CVE-2026-13346`, `CVE-2026-8643` 他 | `pip@24.2`（計6件: MED 5, LOW 1） | `26.2.0`（または本番除外） | マルチステージ `uv` ビルドにより本番イメージから `pip` 自体を除去することで根絶可能。 |
| **Python 実行時** | **なし** | — (`0 CVEs`) | `fastapi`, `httpx`, `pydantic`, `uvicorn` | 対応不要（脆弱性ゼロ） | アプリケーションが直接利用する Python ランタイム依存パッケージに既知 CVE は存在しない。 |
| **IaC (`Dockerfile`)** | **LOW** | `DS-0026` | `Dockerfile:L1-L14` | `HEALTHCHECK` 命令追加 | `/healthz` を定期確認する `HEALTHCHECK` 命令を追加し、オーケストレータ自動復旧を有効化。 |
