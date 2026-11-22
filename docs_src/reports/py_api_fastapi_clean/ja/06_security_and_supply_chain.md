# 6. 詳細分析：セキュリティ・サプライチェーン・API 攻撃面

セキュリティ評価は、Trivy によるファイルシステム＋コンテナイメージ SCA、静的 AST 危険シンク／シークレット検査、および稼働中 Docker コンテナに対するライブ HTTP DAST ペネトレーションテスト（19 プローブ）を組み合わせて実施しました。重要な結論として、`order-dispatch` が宣言する 5 つの実行時アプリ依存（`fastapi`、`pydantic`、`pydantic-settings`、`uvicorn`、`httpx`）の **CVE は 0 件** であり、ハードコード秘密情報および危険 AST シンクも **0 件** です。コンテナ側の脆弱性負債はすべて旧 `python:3.12.6-slim-bookworm` ベースイメージに起因（ビルド専用 `pip@24.2` CVE 6 件 + Debian 12.7 OS CVE 612 件）しており、ライブ DAST でも重大・高リスクの悪用可能欠陥はゼロで、防御多層化の 3 項目（`CWE-306`・`CWE-200`・`CWE-693`）のみが検出されました。

```drawlib align=center code=fold file=supply_chain_vuln_breakdown.png caption="サプライチェーン＆コンテナ脆弱性内訳：宣言アプリ依存 0 件 vs. ビルド専用 pip@24.2 vs. Debian 12.7 OS"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.styles import Styles
from drawlib.text import text

setup(width=146, height=68, dpi=150)

# Left Chart: Python App vs Build-Time Tool (pip@24.2) — Multi-series with mandatory horizontal legend
app_chart = BarChart(
    axis_line_style=Styles.DarkThin,
    width=58.0,
    height=38.0,
    categories=["Declared App\n(5 runtime deps)", "Build Tool\n(pip@24.2)"],
    orientation="vertical",
    bar_mode="group",
    bar_width_ratio=0.72,
    bar_r=0.6,
    axis_text_style=Styles.Dark.patch(text_size=9.5),
    grid_style=Styles.MutedDashedThin,
    value_text_style=Styles.DarkBold.patch(text_size=9.5),
    value_format="{:.0f}",
    title="Python Packages: App vs. Build-Time pip",
    title_style=Styles.DarkBold.patch(text_size=10.8),
)
app_chart.configure_y_axis(
    min_value=0.0,
    max_value=7.0,
    ticks=[0, 1, 2, 3, 4, 5, 6],
    show_grid=True,
    label="CVE Count",
)
app_chart.add_series("CRITICAL", [0, 0], style=Styles.DangerFlat)
app_chart.add_series("HIGH", [0, 0], style=Styles.WarningFlat)
app_chart.add_series("MEDIUM", [0, 5], style=Styles.WarningNeutral)
app_chart.add_series("LOW", [0, 1], style=Styles.SecondaryNeutral)
app_chart.draw((10.0, 17.0))
app_chart.draw_legend(
    (6.0, 4.0),
    text_style=Styles.Dark.patch(text_size=9.2),
    orientation="horizontal",
    item_gap=4.5,
)

# Right Chart: Debian 12.7 Base-Image OS CVEs (612 Total)
os_chart = BarChart(
    axis_line_style=Styles.DarkThin,
    width=56.0,
    height=38.0,
    categories=["CRIT", "HIGH", "MED", "LOW"],
    orientation="vertical",
    bar_width_ratio=0.58,
    bar_r=0.7,
    axis_text_style=Styles.Dark.patch(text_size=9.6),
    grid_style=Styles.MutedDashedThin,
    value_text_style=Styles.DarkBold.patch(text_size=9.8),
    value_format="{:.0f}",
    title="Debian 12.7 Base Image OS CVEs (612 Total)",
    title_style=Styles.DarkBold.patch(text_size=10.8),
)
os_chart.configure_y_axis(
    min_value=0.0,
    max_value=290.0,
    ticks=[0, 50, 100, 150, 200, 250],
    show_grid=True,
    label="OS CVE Count",
)
os_chart.add_series("Debian 12.7 OS", [9, 158, 253, 173], style=Styles.PrimaryNeutral)
os_chart.draw((84.0, 17.0))

text(
    (112.0, 5.2),
    "Trivy IaC: 1 LOW (DS-0026 No HEALTHCHECK) | Secrets: 0",
    style=Styles.Muted.patch(text_size=9.2),
)

save()
```

## ライブ HTTP DAST（`15/19` プローブ）と抽出済み API 攻撃面

隔離 Docker コンテナ（`http://127.0.0.1:55857`, `28.04s`）に対して全 19 件のライブ HTTP プローブを実行した結果、XSS・SQL インジェクション・パストラバーサル・秘密情報漏えいに対して堅牢な耐性を確認しました（合格 `15`・失敗 `3`・スキップ `1`）。Pydantic v2 の `ConfigDict(extra="forbid")` による厳格な境界検証が不正ペイロードを確実に拒否する一方、失敗した 3 プローブではルート認証欠如（`CWE-306`）、既定の OpenAPI スキーマ公開（`CWE-200`）、および `X-Content-Type-Options: nosniff` ヘッダー欠如（`CWE-693`）が実測確認されました。

```drawlib align=center code=fold file=dast_api_attack_surface.png caption="ライブ HTTP DAST 結果、抽出 API エンドポイント、および実測確認済み CWE 検出事項"
from drawlib.canvas import save, setup
from drawlib.smartarts import CardList, KpiCards, Panel
from drawlib.styles import Styles

setup(width=146, height=74, dpi=150)

kpis = KpiCards(
    style=Styles.Neutral.patch(shape_r=1.5),
    metric_style=Styles.DarkBold.patch(text_size=12.0),
    text_style=Styles.DarkBold.patch(text_size=9.6),
    description_style=Styles.Muted.patch(text_size=9.0),
    accent_style=Styles.PrimaryFlat,
    accent_position="top_bar",
    metric_layout="top_stack",
    spacing=2.5,
)
kpis.add("0 / 0", "Secrets & Sinks", "0 Hardcoded, 0 AST CWEs", accent_style=Styles.SuccessFlat)
kpis.add("1 LOW", "IaC Misconfig", "DS-0026 No HEALTHCHECK", accent_style=Styles.WarningFlat)
kpis.add("15 / 19", "Live DAST Probes", "3 Failed, 1 Skipped (28s)", accent_style=Styles.PrimaryFlat)
kpis.add("0 / 3", "Auth-Guarded APIs", "/v1/orders Needs Depends()", accent_style=Styles.WarningFlat)
kpis.draw((3.0, 56.5), width=140.0, height=15.0, columns=4)

left_panel = Panel(
    "Extracted API Attack Surface (routes.py)",
    style=Styles.Neutral.patch(shape_r=1.8),
    header_style=Styles.PrimaryNeutral.patch(shape_r=1.8),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    header_height=8.0,
)
left_panel.draw((3.0, 3.0), width=68.0, height=50.5)

ep_cards = CardList(
    style=Styles.Neutral.patch(shape_r=1.5),
    text_style=Styles.DarkBold.patch(text_size=9.8),
    description_style=Styles.Muted.patch(text_size=9.2),
    badge_shape="rounded_rect",
    badge_style=Styles.SuccessFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.2),
    spacing=2.4,
)
ep_cards.add(
    "GET /healthz -> health_check",
    "routes.py:47 | Public readiness probe (auth_hint=NONE)",
    badge_text="GET",
    badge_style=Styles.SuccessFlat,
)
ep_cards.add(
    "POST /v1/orders -> create_order",
    "routes.py:60 | Mutating, NO auth guard (TODO line 73)",
    badge_text="POST",
    style=Styles.WarningNeutral.patch(shape_r=1.5),
    badge_style=Styles.WarningFlat,
)
ep_cards.add(
    "GET /v1/orders/{order_id} -> get_order",
    "routes.py:83 | Order lookup, NO auth/tenant guard",
    badge_text="GET",
    style=Styles.WarningNeutral.patch(shape_r=1.5),
    badge_style=Styles.WarningFlat,
)
ep_cards.draw((6.0, 5.5), width=62.0, height=38.0)

right_panel = Panel(
    "Verified Live HTTP DAST Findings (3)",
    style=Styles.Neutral.patch(shape_r=1.8),
    header_style=Styles.WarningNeutral.patch(shape_r=1.8),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    header_height=8.0,
)
right_panel.draw((75.0, 3.0), width=68.0, height=50.5)

dast_cards = CardList(
    style=Styles.Neutral.patch(shape_r=1.5),
    text_style=Styles.DarkBold.patch(text_size=9.8),
    description_style=Styles.Muted.patch(text_size=9.2),
    badge_shape="rounded_rect",
    badge_style=Styles.WarningFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.2),
    spacing=2.4,
)
dast_cards.add(
    "CWE-306: Unauth POST /v1/orders",
    "HTTP 201 returned with order_id (ord-94b1ebabb3)",
    badge_text="MED",
    style=Styles.WarningNeutral.patch(shape_r=1.5),
    badge_style=Styles.WarningFlat,
)
dast_cards.add(
    "CWE-200: Public /openapi.json",
    "GET /openapi.json returned HTTP 200 (4,753 bytes)",
    badge_text="LOW",
    badge_style=Styles.SecondaryFlat,
)
dast_cards.add(
    "CWE-693: Missing Security Header",
    "GET /healthz omitted X-Content-Type-Options: nosniff",
    badge_text="LOW",
    badge_style=Styles.SecondaryFlat,
)
dast_cards.draw((78.0, 5.5), width=62.0, height=38.0)

save()
```

## サプライチェーン統制とビルド専用 `pip@24.2` CVE

`order-dispatch` はリポジトリ統制ゲートをすべて満たしています（`uv.lock` コミット済み、実行時依存 `5` 件すべてバージョン固定、未固定依存 `0` 件、`SECURITY.md`、`.github/dependabot.yml`、`Apache-2.0 LICENSE`、`permissions: contents: read` かつコミット SHA 固定の GitHub Actions、非 root `appuser` `uid 10001`、`.dockerignore`、シークレット `0` 件、AST 危険シンク `0` 件）。Python レイヤーで Trivy が検出した CVE はすべて `python:3.12.6-slim-bookworm` 同梱のビルド専用ツール `pip@24.2` に由来します。

| CVE ID | スキャナ深刻度 | トリアージ後 | パッケージ（`python-pkg`） | 現行 -> 修正版 | CVSS | 概要 |
| :--- | :---: | :---: | :--- | :--- | :---: | :--- |
| `CVE-2026-8643` | MEDIUM | LOW（ビルド限定） | `pip` | `24.2` -> `26.1.2` | `8.0` | wheel 導入時の悪意あるエントリポイント名によるパストラバーサル |
| `CVE-2026-13346` | MEDIUM | LOW（ビルド限定） | `pip` | `24.2` -> `26.2.0` | `6.5` | 悪意あるパッケージインデックス経由の任意ファイル配置 |
| `CVE-2026-6357` | MEDIUM | LOW（ビルド限定） | `pip` | `24.2` -> `26.1` | `5.8` | 悪意ある wheel 導入時の任意コード実行・情報漏えい |
| `CVE-2025-8869` | MEDIUM | LOW（ビルド限定） | `pip` | `24.2` -> `25.3` | `5.3` | シンボリックリンク展開時の検証漏れ |
| `CVE-2026-3219` | MEDIUM | LOW（ビルド限定） | `pip` | `24.2` -> `26.1` | `5.0` | 不適切なアーカイブ処理による誤ファイル配置 |
| `CVE-2026-1703` | LOW | LOW | `pip` | `24.2` -> `26.0` | `3.9` | 細工された wheel 展開時のパストラバーサル情報漏えい |

## コンテナベースイメージ主要 OS CVE（`python:3.12.6-slim-bookworm` / Debian 12.7）

Trivy（`ghcr.io/aquasecurity/trivy:0.69.3`）はビルド済み `Dockerfile` イメージから `612` 件の Debian 12.7 OS パッケージ CVE（CRITICAL `9`・HIGH `158`・MEDIUM `253`・LOW `173`）および LOW IaC 設定不備 1 件（`DS-0026`: `HEALTHCHECK` 未定義）を報告しました。最新のパッチ済み `python:3.12.x-slim-bookworm` ダイジェストへ刷新することで、修正版が存在する以下の CRITICAL CVE を一括解消できます。

| CVE ID | 深刻度 | Debian パッケージ | 現行 -> 修正バージョン | CVSS | 概要 |
| :--- | :---: | :--- | :--- | :---: | :--- |
| `CVE-2026-42010` | **CRITICAL** | `libgnutls30` | `3.7.9-2+deb12u3` -> `3.7.9-2+deb12u7` | `9.8` | GnuTLS ユーザー名内 NUL 文字による認証バイパス |
| `CVE-2026-31789` | **CRITICAL** | `libssl3`, `openssl` | `3.0.14-1~deb12u2` -> `3.0.19-1~deb12u2` | `9.8` | OpenSSL 32bit 環境での X.509 証明書処理ヒープオーバーフロー |
| `CVE-2026-8376` | **CRITICAL** | `perl-base` | `5.36.0-7+deb12u1` -> `5.36.0-7+deb12u4` | `9.8` | Perl 32bit ビルドでの正規表現コンパイル時ヒープオーバーフロー |
| `CVE-2023-45853` | **CRITICAL** | `zlib1g` | `1:1.2.13.dfsg-1` -> *（上流修正なし）* | `9.8` | zlib `zipOpenNewFileInZip4_6` 整数オーバーフロー |
| `CVE-2026-33845` | **CRITICAL** | `libgnutls30` | `3.7.9-2+deb12u3` -> `3.7.9-2+deb12u7` | `9.1` | GnuTLS DTLS ゼロ長フラグメントによる DoS |
| `CVE-2025-7458` | **CRITICAL** | `libsqlite3-0` | `3.40.1-2` -> *（上流修正なし）* | `9.1` | SQLite 整数オーバーフロー |
| `CVE-2026-13221` | **CRITICAL** | `perl-base` | `5.36.0-7+deb12u1` -> `5.36.0-7+deb12u4` | `9.1` | Perl 大規模正規表現処理の不具合 |
| `CVE-2026-42496` | **CRITICAL** | `perl-base` | `5.36.0-7+deb12u1` -> `5.36.0-7+deb12u4` | `9.1` | `perl-archive-tar` 細工シンボリックリンク経由パストラバーサル |
| `CVE-2025-6965` | **HIGH** | `libsqlite3-0` | `3.40.1-2` -> `3.40.1-2+deb12u2` | `9.8` | SQLite 整数切り捨て |

## ライブ HTTP DAST 検出事項および API エンドポイント攻撃面

**AST 危険コードシンク**: `0` 件。  
**ペネトレーションテストスイート**: `.pni/pentests/examples/python/api_fastapi_clean`（合格 `15/19`・失敗 `3`・スキップ `1`）。

| エンドポイント / 攻撃面 | ハンドラ / プローブテスト ID | 認証 / CWE | 深刻度 | 実測証跡・境界評価 |
| :--- | :--- | :---: | :---: | :--- |
| `GET /healthz` | `health_check`（`routes.py:47`） / `test_baseline_http::test_x_content_type_options_nosniff` | `auth_hint=NONE` ・ `CWE-693` | **LOW** | 意図的な公開レディネスプローブ。`GET /healthz -> 200` 応答に `X-Content-Type-Options` ヘッダーが欠如。 |
| `POST /v1/orders` | `create_order`（`routes.py:60`） / `test_app_probes::test_create_order_enforces_authentication_guard` | `auth_hint=NONE` ・ `CWE-306` | **MEDIUM** | 状態変更エンドポイントが未認証リクエストを受理し HTTP `201` と生成 `order_id`（`ord-94b1ebabb3`）を返却（73 行目 `TODO(security)` に一致）。 |
| `GET /v1/orders/{order_id}` | `get_order`（`routes.py:83`） | `auth_hint=NONE` ・ `CWE-306` | **MEDIUM** | 注文参照に呼び出し元認証・テナント所有権検証が未設定。`POST /v1/orders` と同時に認証ガードを導入すべき対象。 |
| `GET /openapi.json` | `test_app_probes::test_openapi_schema_not_publicly_exposed_without_auth` | `CWE-200` | **LOW** | 既定設定で認証不要の OpenAPI スキーマが公開（`GET /openapi.json -> 200`, `4,753` bytes）。本番環境では `openapi_url=None` で無効化推奨。 |
