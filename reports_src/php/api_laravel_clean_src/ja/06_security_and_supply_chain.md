# 6. 詳細分析：セキュリティ・脆弱性・動的ペネトレーション検証

本章では、Trivy (`0.69.3`) によるリポジトリファイルシステムおよび解決済み Docker イメージ（`php:8.3.12-cli-bookworm` ベース）に対する SCA 脆弱性スキャン・Dockerfile IaC 設定検査・秘密情報スキャン、PHP AST による危険な CWE コードシンクおよび Laravel HTTP API 認可境界の評価に加え、隔離ループバックコンテナに対して `pytest + httpx` で実パケット検証を行う **動的Webペネトレーションテスト（`web_pentest` / `.pni/pentests/examples/php/api_laravel_clean/`、全18プローブ）** の結果を統合して分析する。

```drawlib file=security_cve_and_governance.png caption="図6-1: Composer アプリケーション依存 (0件) vs Debian 12.7 OS層 CVE内訳と動的DAST境界指標"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.icons import phosphor
from drawlib.smartarts import KpiCards, Panel
from drawlib.styles import Styles

setup(width=146, height=70, dpi=150)

panel = Panel(
    "深刻度別 CVE 分離比較 (Composer App 0件 vs Debian 12.7 OS 8,892件) & DAST防御指標",
    "Trivy 0.69.3 (passed) + web_pentest 18 Probes (passed)",
    style=Styles.Neutral,
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=10.0),
    description_style=Styles.White.patch(text_size=9.3),
    header_height=10.0,
)
panel.draw(xy=(2, 3), width=142, height=64)

chart = BarChart(
    axis_line_style=Styles.Neutral,
    grid_style=Styles.NeutralThin,
    axis_text_style=Styles.DarkBold.patch(text_size=9.5),
    value_text_style=Styles.DarkBold.patch(text_size=9.2),
    background_style=Styles.White.patch(shape_r=1.8),
    categories=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
    orientation="vertical",
    bar_mode="group",
    bar_width_ratio=0.66,
    bar_r=0.8,
    width=78,
    height=48,
)
chart.add_series("Composer App依存 (0件)", [0, 0, 0, 0], style=Styles.Success)
chart.add_series("Debian 12.7 OS層 (8,892件)", [28, 1330, 5683, 1692], style=Styles.Warning)
chart.draw(xy=(5, 6))

kpis = KpiCards(
    style=Styles.White,
    metric_style=Styles.SuccessBold.patch(text_size=12.2),
    text_style=Styles.DarkBold.patch(text_size=9.6),
    description_style=Styles.Dark.patch(text_size=9.0),
    metric_width_ratio=0.35,
    spacing=2.4,
)
kpis.add(
    "0 / 0 件",
    "Composer App CVE",
    "外部ランタイム依存ゼロでCVE皆無",
    icon=phosphor.shield_check,
    accent_style=Styles.Success,
    icon_style=Styles.Success,
)
kpis.add(
    "0 / 0 件",
    "IaC 不備 / Secret 漏洩",
    "UID 10001・HEALTHCHECK・.dockerignore",
    icon=phosphor.lock_key,
    accent_style=Styles.Success,
    icon_style=Styles.Success,
)
kpis.add(
    "0 CRIT/HIGH",
    "DAST 18 Probes & Sanctum",
    "13 PASS / 4 ヘッダ・URI改善 (SEC-06)",
    icon=phosphor.check_circle,
    accent_style=Styles.Primary,
    metric_style=Styles.PrimaryBold.patch(text_size=11.8),
    icon_style=Styles.Primary,
)
kpis.draw(xy=(86, 6), width=55, height=48, columns=1)

save()
```

## アプリケーション SCA・OS ベースイメージ CVE・IaC・API 境界評価

- **アプリケーション依存関係 SCA (`app_vuln_counts.total = 0` — 完全クリーン)**: 本番ランタイムは PHP 8.3 コアと `ext-pdo` のみで構成されサードパーティ Composer パッケージへの実行時依存を持たないため、アプリケーション層の既知脆弱性は `CRITICAL: 0`, `HIGH: 0`, `MEDIUM: 0`, `LOW: 0` の **計 `0` 件**（Trivy `status = "passed"`）である。
- **コンテナ OS ベースイメージ層 (`php:8.3.12-cli-bookworm` / Debian 12.7)**: 検出された OS パッケージ脆弱性（`CRITICAL: 28`, `HIGH: 1330`, `MEDIUM: 5683`, `LOW: 1692`）はすべて `Dockerfile:1` の固定スナップショット `php:8.3.12-cli-bookworm` に同梱された Debian 12 システムライブラリ（`libgnutls30`, `libssl3`/`openssl`, `libxml2`, `perl`/`libperl5.36`, `linux-libc-dev`, `libsqlite3-dev`）に起因する。最新の `php:8.3.x-bookworm`（`@sha256` 固定）への更新とマルチステージビルドによる `libsqlite3-dev` / コンパイラ除去で一括解消できる。
- **Dockerfile IaC・CI 供給網・秘密情報衛生 (`misconfigurations = 0`, `secrets = 0`)**: `Dockerfile` は非特権ユーザ `appuser`（`UID 10001`, `/usr/sbin/nologin`）実行、3秒タイムアウト `/healthz` `HEALTHCHECK`、`.dockerignore` による `.git`/`vendor`/`.env`/`*.sqlite` 除外を完備し、Trivy IaC 指摘 `0` 件を達成した。`.github/workflows/ci.yml` も `permissions: contents: read` と `actions/checkout@11bd7190...` のフル SHA 固定を徹底している。
- **CWE コードシンク (`0` 件) と HTTP API 攻撃面 (`without_auth_hint = 0`)**: AST セキュリティ解析で SQLi / コマンド注入 / `eval` / `unserialize` 等の危険なシンクは **`0` 件** であった。公開 API 2ルート（`GET /api/orders`, `POST /api/orders`）は `Route::middleware('auth:sanctum')` で保護され、`OrderPayload` の厳格入力検証、`OrderRepository` の PDO プリペアドステートメント、`OrderFulfillmentService` の `random_bytes(8)` 採番および `hash_equals()` 定数時間 HMAC-SHA256 検証により多層防御が確立されている。

## 動的Webペネトレーションテスト (`web_pentest` / `.pni/pentests/`, SEC-06)

隔離ループバックコンテナ（`127.0.0.1`）に対して `.pni/pentests/examples/php/api_laravel_clean/`（`test_baseline_http.py`, `test_target_surface.py`, `test_app_probes.py`）の計 `18` プローブを実行した結果、**`status = "passed"`（`13` PASS / `4` FAIL / `1` SKIP、`CRITICAL: 0`・`HIGH: 0`）** を達成した。無認証 `POST /api/orders` における注文状態変更の不成立（`CWE-306` PASS）、境界引用符入力時の SQL エラー・スタックトレース非露出（`CWE-89`/`CWE-209` PASS）、反射型 XSS カナリア非反射（`CWE-79` PASS）、`../../../../etc/passwd` トラバーサル遮断（`CWE-22` PASS）、および `.env`/`.git`/`composer.json` 機密非露出が実 HTTP 応答で確認された。残る4件の FAIL はすべて開発用 `php -S` サーバおよびヘッダ設定に起因する中〜低リスクのハードニング項目（`TRACE / -> 200` `CWE-693` Medium、`X-Powered-By: PHP/8.3.36` `CWE-200` Low、`X-Content-Type-Options: nosniff` 未付与 `CWE-693` Low、`public/index.php:31` の `filter_input(INPUT_SERVER, 'REQUEST_URI')` が `cli-server` 下で `'/'` へフォールバックする `CWE-755` Low）である。

```drawlib file=security_web_pentest_probes.png caption="図6-2: 動的Webペネトレーションテスト (.pni/pentests/ 全18プローブ: 13 PASS / 4 FAIL / 1 SKIP) 結果一覧"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=90, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=8.7),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.1),
    border_style=Styles.NeutralThin,
)
rows = [
    ["判定 / 深刻度", "プローブスイート / CWE", "対象エンドポイント", "ライブHTTP応答エビデンス", "評価・ハードニング方針"],
    ["PASS\n[防御実証]", "test_app_probes.py\nCWE-306 / CWE-209", "POST /api/orders\nGET /, /up, /healthz", "BearerなしPOSTで201/order_id不成立\n全ヘルス応答が厳格UTF-8 JSON (200)", "Sanctum認可保護とJSON専用応答\nによるHTML/トレース非露出を実証"],
    ["PASS\n[防御実証]", "test_target_surface.py\nCWE-89 / 79 / 22", "GET /api/orders\n(SQLi/XSS/LFI境界)", "引用符1'\"`・<pni-xss-canary>・\n../../../../etc/passwd いずれも不成立", "SQLSTATE漏洩・XSS反射・ファイル\n開披シグネチャすべて 0 件"],
    ["FAIL\n[MEDIUM]", "test_baseline_http.py\nCWE-693 (TRACE)", "TRACE /\n(Dockerfile:20)", "TRACE / -> HTTP 200 OK\n(php -S 組込み開発サーバ応答)", "本番SAPI (Nginx/Caddy+PHP-FPM)\nで TRACE メソッドを 405 遮断"],
    ["FAIL\n[LOW]", "test_baseline_http.py\nCWE-200 / CWE-693", "GET /\n(Dockerfile / index.php)", "X-Powered-By: PHP/8.3.36 露出\nX-Content-Type-Options=<absent>", "expose_php=Off または header_remove\nと nosniff ヘッダ明示付与"],
    ["FAIL\n[LOW]", "test_app_probes.py\nCWE-755 (URI解決)", "GET /api/nonexistent\n-probe-route (index:31)", "filter_input(INPUT_SERVER,'REQUEST_URI')\nがcli-server下で'/'(200)へフォールバック", "$_SERVER['REQUEST_URI'] ?? '/' を\n参照し未知URIへ確実に 404 返却"],
]
tbl.draw_flexible(
    xy=(3, 87),
    column_widths=[20, 29, 28, 36, 27],
    row_heights=[7.4] + [14.8] * 5,
    data=rows,
)

save()
```

```drawlib file=security_api_and_cve_table.png caption="図6-3: API攻撃面・CWE防御マトリクスおよび主要Debian 12 OS層CVE修正バージョン一覧"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=114, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=9.0),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.4),
    border_style=Styles.NeutralThin,
)
rows = [
    ["区分 / 判定", "ルート / CVE・検査対象", "対象モジュール・パッケージ", "現状構成 -> 推奨更新・防御策", "セキュリティ境界・リスク評価詳細"],
    ["API [PASS]", "POST /api/orders\n(routes/api.php:10)", "OrderController::store\n+ OrderPayload", "auth:sanctum 保護済\nSKU正規表現・qty 1..1000", "無認証アクセス遮断＋SQLi風SKU\nをドメイン到達前に即時拒絶"],
    ["API [PASS]", "GET /api/orders\n(routes/api.php:9)", "OrderController::\nlistRecent", "auth:sanctum 保護済\nPDO::PARAM_INT (1..100)", "Sanctum認可必須＋max(1,min(limit,100))\nで大量取得DoSを防止"],
    ["Probe [WARN]", "GET /up, /healthz\n(public/index.php:13)", "App\\Http\\\nbuildHealthResponse", "FILTER_SANITIZE_URL ->\n$_SERVER['REQUEST_URI']+nosniff", "副作用なしJSON応答・cli-server下\nでの未知URI 404応答統一を推奨"],
    ["SAST [PASS]", "CWE-89 / CWE-208 /\nCWE-330 検査", "OrderRepository /\nOrderFulfillmentSvc", "PDO::prepare + hash_equals\n+ random_bytes(8)", "危険なCWEシンク 0件・空シークレット\n即時拒絶でタイミング攻撃防止"],
    ["IaC / CI [PASS]", "Trivy IaC & Secret\n+ GitHub Actions", "Dockerfile / .dockerignore\n.github/workflows/ci.yml", "UID 10001 + HEALTHCHECK\ncheckout 40文字SHA固定", "IaC不備 0件・秘密漏洩 0件・最小権限\ncontents: read トークン徹底"],
    ["OS [CRITICAL]", "CVE-2026-42010\nCVE-2026-33845", "libgnutls30\n(debian 12.7)", "3.7.9-2+deb12u3\n-> 3.7.9-2+deb12u7", "GnuTLS NUL文字認証回避 (CVSS 9.8)\n・DTLS DoS (PHP層から直接未呼出)"],
    ["OS [CRITICAL]", "CVE-2026-31789\nCVE-2026-45447", "libssl3 / openssl\n(debian 12.7)", "3.0.14-1~deb12u2\n-> 3.0.19-1~deb12u2", "OpenSSL X.509証明書処理バッファ\n超過 (CVSS 9.8)・PKCS7 UAF"],
    ["OS [CRITICAL]", "CVE-2024-56171\nCVE-2025-49794", "libxml2\n(debian 12.7)", "2.9.14+dfsg-1.3~deb12u1\n-> 2.9.14+dfsg-1.3~deb12u2", "libxml2 Use-After-Free (CVSS 9.8)\n(本APIはJSON専用でXML未解析)"],
    ["OS [CRITICAL]", "CVE-2026-8376\nCVE-2026-13221", "perl / libperl5.36\n(debian 12.7)", "5.36.0-7+deb12u1\n-> 5.36.0-7+deb12u4", "Perl 正規表現コンパイル境界外書込\n・マルチステージ/slim化で縮小可"],
    ["OS [HIGH]", "CVE-2025-7458\n(ビルドヘッダ残存)", "libsqlite3-0 /\nlibsqlite3-dev", "3.40.1-2+deb12u2\n-> 多段ビルドで -dev 除外", "Dockerfile:6 の pdo_sqlite ビルド用\nlibsqlite3-dev を最終段から分離"],
]
tbl.draw_flexible(
    xy=(3, 111),
    column_widths=[19, 25, 26, 29, 41],
    row_heights=[7.5] + [9.9] * 10,
    data=rows,
)

save()
```
