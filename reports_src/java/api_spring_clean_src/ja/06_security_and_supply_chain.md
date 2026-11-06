# 6. 詳細分析：セキュリティ・脆弱性・API境界

本章では、Trivy (`0.69.3`) による `pom.xml` および解決済みマルチステージ Docker イメージ（`eclipse-temurin:21.0.4_7-jre-jammy`）に対する SCA 脆弱性スキャン・Dockerfile IaC 設定検査・秘密情報スキャン、AST による危険な CWE コードシンク・Spring Boot HTTP API 攻撃面の評価、ならびに `.pni/pentests/examples/java/api_spring_clean/` を用いた隔離ループバック動的 Web ペネトレーションテスト（`web_pentest` / `SEC-06`）の結果を統合して分析する。

```drawlib file=security_cve_and_governance.png caption="Maven アプリケーション依存 vs Ubuntu OS層 CVE内訳と Dockerfile / DAST 検査指標"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.icons import phosphor
from drawlib.smartarts import KpiCards, Panel
from drawlib.styles import Styles

setup(width=146, height=70, dpi=150)

panel = Panel(
    "深刻度別 CVE 比較 (Maven App 75件 vs Ubuntu 22.04 OS 453件) & DAST 境界検査",
    "Trivy 0.69.3 + httpx DAST",
    style=Styles.Neutral,
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=10.0),
    description_style=Styles.White.patch(text_size=9.0),
    header_height=10.0,
)
panel.draw(xy=(2, 3), width=142, height=64)

chart = BarChart(
    axis_line_style=Styles.Neutral,
    grid_style=Styles.NeutralThin,
    axis_text_style=Styles.DarkBold.patch(text_size=9.3),
    value_text_style=Styles.DarkBold.patch(text_size=9.0),
    background_style=Styles.White.patch(shape_r=1.8),
    categories=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
    orientation="vertical",
    bar_mode="group",
    bar_width_ratio=0.66,
    bar_r=0.8,
    width=78,
    height=48,
)
chart.add_series("Maven App依存 (75件)", [8, 29, 28, 10], style=Styles.Danger)
chart.add_series("Ubuntu 22.04 OS層 (453件)", [0, 5, 294, 154], style=Styles.Primary)
chart.draw(xy=(5, 6))

kpis = KpiCards(
    style=Styles.White,
    metric_style=Styles.DangerBold.patch(text_size=12.0),
    text_style=Styles.DarkBold.patch(text_size=9.4),
    description_style=Styles.Dark.patch(text_size=8.8),
    metric_width_ratio=0.36,
    spacing=2.4,
)
kpis.add(
    "8 / 29 件",
    "Maven CRIT / HIGH CVE",
    "Tomcat 10.1.30 / WebMVC / Jackson",
    icon=phosphor.warning,
    accent_style=Styles.Danger,
    icon_style=Styles.Danger,
)
kpis.add(
    "LOW 1 件",
    "Dockerfile IaC 検査",
    "非root UID 10001 / DS-0026のみ",
    icon=phosphor.package,
    accent_style=Styles.Warning,
    metric_style=Styles.WarningBold.patch(text_size=12.0),
    icon_style=Styles.Warning,
)
kpis.add(
    "12 / 16 PASS",
    "動的 DAST (CRIT/HIGH 0)",
    "CWE-306/755(MED 2)・CWE-693(LOW)",
    icon=phosphor.shield_check,
    accent_style=Styles.Primary,
    metric_style=Styles.PrimaryBold.patch(text_size=11.6),
    icon_style=Styles.Primary,
)
kpis.draw(xy=(86, 6), width=55, height=48, columns=1)

save()
```

## アプリケーション CVE vs OS 層 CVE・IaC・API 境界評価（SEC-01〜SEC-05）

- **Maven アプリケーション依存関係 (`SEC-01` — `FAIL`)**: `pom.xml` の `spring-boot-starter-parent:3.3.4` から解決される推移依存に計 **`75` 件**（`CRITICAL: 8`, `HIGH: 29`, `MEDIUM: 28`, `LOW: 10`）の CVE が検出された。特に組み込み Tomcat (`tomcat-embed-core@10.1.30`) の Partial PUT RCE（`CVE-2025-24813`, CVSS 10.0）や認証バイパス群（`10.1.58` で修正）、`spring-webmvc@6.1.13` の `XsltView` RCE（`CVE-2026-47884`, CVSS 9.8）、および `jackson-databind`/`jackson-core@2.17.2` の任意コード実行・DoS 群（`2.18.11` で修正）は最優先で BOM アップグレードが必要である。
- **コンテナ OS 層と Dockerfile ハードニング (`SEC-01` / `SEC-02`)**: `eclipse-temurin:21.0.4_7-jre-jammy`（Ubuntu 22.04）OS 層では `CRITICAL` は `0` 件だが、`libssl3`/`openssl`（`CVE-2026-45447`, CVSS 8.8）と `gpgv`（`CVE-2025-68973`, CVSS 7.8）の `HIGH` 計 `5` 件が検出された。Dockerfile 自体は非 root ユーザ `spring`（`UID 10001`）と `-Dserver.address=127.0.0.1` を徹底しており、IaC 指摘は `HEALTHCHECK` 未定義（`DS-0026`, `LOW`）1件のみである。
- **秘密情報・CWE コードシンク・Spring API 攻撃面 (`SEC-03`〜`SEC-05`)**: 秘密情報漏洩（`0` 件）および危険な CWE コードシンク（SQLi / OS コマンド注入 / 安全でないデシリアライズ等 `0` 件）は完全にクリーンである。一方、公開された 2 つの REST エンドポイントはいずれも認証ヒントを持たず、特に状態変更と外部 HTTP 発信を伴う `POST /api/v1/items/{sku}/reserve` には `TODO(security)` コメントが残存しており、外部 Ingress 公開前に OAuth2 JWT 認可と `SupplierRestClient` の Jackson シリアライズ化が必須である。

```drawlib file=security_api_and_cve_table.png caption="Spring Boot API攻撃面マトリクスおよび主要CVE・Dockerfile検査詳細一覧"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=112, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=9.0),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.3),
    border_style=Styles.NeutralThin,
)
rows = [
    ["区分 / 深刻度", "ルート / CVE・検査ID", "ハンドラ・対象パッケージ", "現状 -> 推奨修正・更新先", "リスク・境界検査の詳細"],
    ["API [HIGH]", "POST /api/v1/\nitems/{sku}/reserve", "InventoryController.\nreserveItem (:52)", "auth=NONE (@Min(1)のみ)\n-> OAuth2 JWT + @Pattern", "無認証で在庫引当と外部補充POSTを\n誘発可能 (57行目 TODO security)"],
    ["API [INFO]", "GET /api/v1/\nitems/{sku}", "InventoryController.\ngetItem (:38)", "auth=NONE (読取専用)\n-> 公開範囲に応じJWT保護", "SKU指定の単一在庫参照。未知SKU時は\nOptional空から 404 を返却"],
    ["App [CRITICAL]", "CVE-2025-24813\n(他 CRIT 6件)", "tomcat-embed-core\n(pom.xml)", "10.1.30 -> 10.1.58\n(または 11.0.25)", "Partial PUT RCE (CVSS 10.0)・\nHTTP/2未検証・認証バイパス"],
    ["App [CRITICAL]", "CVE-2026-47884\n(+HIGH 5件)", "spring-webmvc / core /\nexpression (pom.xml)", "6.1.13 -> 6.2.19 /\nSpring Framework 7.0.9", "XsltView パス制限不備による RCE\n(CVSS 9.8)・SpEL/静的資源 DoS"],
    ["App [HIGH]", "CVE-2026-54512\nCVE-2026-54513 他6件", "jackson-databind /\njackson-core (pom.xml)", "2.17.2 -> 2.18.11\n(または 2.21.7)", "PolymorphicTypeValidator 回避に\nよる任意コード実行・JSON DoS"],
    ["App [HIGH]", "CVE-2025-22235\nCVE-2026-40973", "org.springframework.boot:\nspring-boot (pom.xml)", "3.3.4 -> 3.5.14\n(または 4.0.6)", "Actuator マッチャ不整合および\n予測可能一時ディレクトリ悪用"],
    ["OS [HIGH]", "CVE-2026-45447\n(計2パッケージ)", "libssl3 / openssl\n(ubuntu 22.04)", "3.0.2-0ubuntu1.18\n-> 3.0.2-0ubuntu1.25", "OpenSSL PKCS7_verify() における\nHeap Use-After-Free (CVSS 8.8)"],
    ["OS [HIGH]", "CVE-2025-68973", "gpgv\n(ubuntu 22.04)", "2.2.27-3ubuntu2.1\n-> 2.2.27-3ubuntu2.5", "GnuPG 境界外書込による情報漏洩・\n任意コード実行リスク (CVSS 7.8)"],
    ["IaC [LOW]", "DS-0026\n(SEC-02)", "Dockerfile\n(eclipse-temurin JRE)", "HEALTHCHECK 未定義\n-> /actuator/health 監視", "非root(UID 10001)・127.0.0.1固定済\nヘルスチェック命令のみ未設定"],
    ["SAST / Secret", "SEC-03 / SEC-04", "全Javaソース・設定群", "漏洩 0件 / CWEシンク 0件\n-> Jackson直列化で完全化", "秘密情報0・CWE-78/89/502 0件\nSupplierRestClient:45のみ文字列連結"],
]
tbl.draw_flexible(
    xy=(3, 109),
    column_widths=[19, 25, 27, 27, 42],
    row_heights=[7.5] + [9.8] * 10,
    data=rows,
)

save()
```

## 動的Webペネトレーションテスト (`web_pentest` / `.pni/pentests/` — SEC-06)

PNI の `web_penetration_audit` ステップ（スコア `72 / 100`, Grade `B`, ルール判定 `WARN`）では、`.pni/pentests/examples/java/api_spring_clean/` に実体化された4ファイル構成の Python + `pytest` + `httpx` ペネトレーションスイート（`conftest.py`, `test_app_probes.py`, `test_baseline_http.py`, `test_target_surface.py`）を用い、隔離ループバックコンテナ（`http://127.0.0.1:53369`, `server_booted=true`）に対して計 **`16` プローブ**をライブ実行した（所要 `7.19s`：`12` PASS / `3` FAIL / `1` SKIP / `0` ERROR、CRITICAL・HIGH 脆弱性 `0` 件）。

- **ライブ実証された防御境界 (`12` PASS)**: `POST /api/v1/items/SKU-100/reserve?quantity=not-an-int` が `HTTP 400` で安全に型拒否されること（`CWE-20` PASS）に加え、`GET /api/v1/items/1` に対する反射型 XSS カナリア（`CWE-79`）、SQL エラー・スタックトレース露出（`CWE-89` / `CWE-209`）、`../../../../etc/passwd` パストラバーサル（`CWE-22`）、ならびに `.env` / `.git/HEAD` / ワイルドカード CORS 検査（`CWE-538` / `CWE-942`）がすべて合格した。
- **ライブ検出された3件のエンドポイント・ヘッダ課題 (`2` MEDIUM / `1` LOW)**:
  1. **`[MEDIUM] CWE-306` (`test_app_probes.py` -> `InventoryController.java:57`)**: 無認証の `POST /api/v1/items/SKU-UNAUTH-PROBE/reserve?quantity=1` が認証フィルタに遮断されず `InventoryService.reserveStock()` まで到達し、`HTTP 500` を返却した（期待値：`401` / `403`）。
  2. **`[MEDIUM] CWE-755` (`test_app_probes.py` -> `InventoryService.java:64`)**: 未知 SKU に対する `POST /api/v1/items/SKU-MISSING-999/reserve?quantity=1` で `IllegalArgumentException("Unknown SKU: ...")` が未捕捉のまま送出され、制御された `404 ProblemDetail` ではなく未処理の `HTTP 500` となった。
  3. **`[LOW] CWE-693` (`test_baseline_http.py` -> `InventoryController.java:18`)**: `GET /api/health -> 404` 応答に `X-Content-Type-Options: nosniff` ヘッダが付与されていない。

```drawlib file=security_web_pentest_dast.png caption="動的Webペネトレーションテスト (.pni/pentests/) 実行サマリーとプローブ別検証結果"
from drawlib.canvas import save, setup
from drawlib.smartarts import KpiCards, Table
from drawlib.styles import Styles

setup(width=146, height=96, dpi=150)

kpis = KpiCards(
    style=Styles.Neutral,
    metric_style=Styles.PrimaryBold.patch(text_size=12.0),
    text_style=Styles.DarkBold.patch(text_size=9.2),
    description_style=Styles.Neutral.patch(text_size=8.6),
    accent_position="top_bar",
    metric_layout="top_stack",
    spacing=2.5,
)
kpis.add(
    "PASSED (7.19s)",
    "隔離ループバック DAST",
    "http://127.0.0.1:53369 起動済",
    accent_style=Styles.Success,
    metric_style=Styles.SuccessBold.patch(text_size=11.8),
)
kpis.add(
    "12 / 16 PASS",
    "プローブ合格数 (SKIP 1)",
    "4ファイル pytest + httpx 実行",
    accent_style=Styles.Primary,
)
kpis.add(
    "0 件",
    "CRIT / HIGH ライブ脆弱性",
    "XSS / SQLi / Traversal すべて防御",
    accent_style=Styles.Success,
    metric_style=Styles.SuccessBold.patch(text_size=12.0),
)
kpis.add(
    "MED 2 / LOW 1",
    "検出 DAST 指摘 (計3件)",
    "CWE-306, CWE-755, CWE-693",
    accent_style=Styles.Warning,
    metric_style=Styles.WarningBold.patch(text_size=11.8),
)
kpis.draw(xy=(3, 74), width=140, height=19, columns=4)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=8.6),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.0),
    border_style=Styles.NeutralThin,
)
rows = [
    ["結果 / 深刻度", "CWE / プローブファイル", "対象エンドポイント・コード箇所", "ライブHTTP観測エビデンスと改善アクション"],
    [
        "FAIL [MEDIUM]",
        "CWE-306\ntest_app_probes.py",
        "POST /api/v1/items/{sku}/reserve\nInventoryController.java:57",
        "無認証 POST ?quantity=1 が認証フィルタ不在で reserveStock へ到達し HTTP 500\n-> Spring Security OAuth2 JWT 認可で 401/403 拒否を強制",
    ],
    [
        "FAIL [MEDIUM]",
        "CWE-755\ntest_app_probes.py",
        "POST /api/v1/items/{sku}/reserve\nInventoryService.java:64",
        "POST /SKU-MISSING-999/reserve?quantity=1 で未知SKU例外が未処理 HTTP 500\n-> @RestControllerAdvice で IllegalArgumentException を 404 ProblemDetail 化",
    ],
    [
        "FAIL [LOW]",
        "CWE-693\ntest_baseline_http.py",
        "GET /api/health (全応答共通)\nInventoryController.java:18",
        "GET /api/health -> 404 応答で X-Content-Type-Options ヘッダが欠落\n-> Spring Security 既定ヘッダで X-Content-Type-Options: nosniff を常時付与",
    ],
    [
        "PASS [検証済]",
        "CWE-20\ntest_app_probes.py",
        "POST /api/v1/items/SKU-100/reserve\n(@RequestParam int quantity)",
        "POST ?quantity=not-an-int -> HTTP 400 Bad Request を返却し 500 化を防止",
    ],
    [
        "PASS [検証済]",
        "CWE-79 / 89 / 209 / 22\ntest_target_surface.py",
        "GET /api/v1/items/1\n& ベースライン露出検査",
        "XSSカナリア反射なし・SQL/スタックトレース漏洩なし・../etc/passwd 漏洩なし\n(.env / .git / 危険CORS 露出も test_baseline_http.py 9プローブで PASS)",
    ],
]
tbl.draw_flexible(
    xy=(3, 71),
    column_widths=[21, 27, 36, 56],
    row_heights=[7.2, 13.0, 13.0, 13.0, 9.8, 12.0],
    data=rows,
)

save()
```
