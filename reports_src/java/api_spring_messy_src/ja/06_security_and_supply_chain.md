# 6. 詳細分析：セキュリティ・脆弱性・動的DAST検証

本章では、Trivy (`0.69.3`) によるファイルシステム SCA（ソフトウェア構成解析）・`Dockerfile` IaC 設定検査、AST によるハードコード秘密情報・CWE 危険シンク・HTTP API エンドポイント境界・GitHub Actions サプライチェーン検査、および隔離ループバック環境による動的 Web ペネトレーション監査（`SEC-06 / web_pentest`）の結果を統合して評価する。

```drawlib file=security_cve_and_misconfig.png caption="Trivy アプリケーションCVE・Dockerfile設定不備・API/DASTリスク内訳"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.icons import phosphor
from drawlib.smartarts import KpiCards
from drawlib.styles import Styles

setup(width=146, height=72, dpi=150)

chart = BarChart(
    axis_line_style=Styles.Neutral,
    grid_style=Styles.NeutralThin,
    axis_text_style=Styles.DarkBold.patch(text_size=9.0),
    value_text_style=Styles.DarkBold.patch(text_size=9.0),
    background_style=Styles.Neutral.patch(shape_r=2.0),
    categories=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
    orientation="vertical",
    bar_mode="group",
    bar_width_ratio=0.68,
    bar_r=0.8,
    width=78,
    height=52,
    title="深刻度別 セキュリティ検出内訳 (Trivy + AST + DAST)",
    title_style=Styles.DarkBold.patch(text_size=9.8),
)
chart.add_series("App CVE (LATEST範囲)", [1, 0, 0, 0], style=Styles.Danger)
chart.add_series("Dockerfile IaC", [0, 1, 1, 1], style=Styles.Warning)
chart.add_series("Secret / API / DAST", [2, 2, 1, 0], style=Styles.Primary)
chart.draw(xy=(4, 14))
chart.draw_legend(
    xy=(5, 5.5),
    text_style=Styles.DarkBold.patch(text_size=8.3),
    orientation="horizontal",
    swatch_width=2.2,
    swatch_height=1.2,
    item_gap=2.8,
)

kpis = KpiCards(
    style=Styles.Neutral,
    metric_style=Styles.DangerBold.patch(text_size=12.2),
    text_style=Styles.DarkBold.patch(text_size=9.6),
    description_style=Styles.Dark.patch(text_size=8.8),
    metric_width_ratio=0.35,
    spacing=2.8,
)
kpis.add(
    "CVSS 9.8*",
    "CVE-2022-22965",
    "*LATEST(0.0.0)静的範囲マッチ",
    icon=phosphor.bug,
    accent_style=Styles.Danger,
    icon_style=Styles.Danger,
)
kpis.add(
    "ERROR",
    "動的 Web Pentest",
    "ビルド失敗で起動停止 (15.74s)",
    icon=phosphor.warning,
    accent_style=Styles.Warning,
    metric_style=Styles.WarningBold.patch(text_size=12.0),
    icon_style=Styles.Warning,
)
kpis.add(
    "ANY /charge",
    "無認証 API & 秘密直書き",
    "CWE-306/650/20・秘密鍵露出",
    icon=phosphor.lock_key,
    accent_style=Styles.Danger,
    metric_style=Styles.DangerBold.patch(text_size=11.5),
    icon_style=Styles.Danger,
)
kpis.draw(xy=(85, 9), width=58, height=57, columns=1)

save()
```

## セキュリティゲート（SEC-01〜SEC-05）および CI サプライチェーンの詳細評価

- **SEC-01（非固定 `LATEST` 指定の静的範囲マッチ vs Maven 動的解決の整合性）**: `pom.xml` の `org.springframework.boot:spring-boot-starter-web@LATEST`（`is_unpinned_specifier=true`）に対し、Trivy の静的 `pom.xml` アナライザはシンボル指定 `LATEST` を下限値 `0.0.0` と解釈するため、影響範囲 `< 2.6.6` の **`CVE-2022-22965`（Spring4Shell, CVSS 9.8）に範囲マッチ** した。一方、第5章の Maven 動的ビルド時には中央リポジトリ上の最新 `4.2.0-RC1`（`CVE-2022-22965` 自体は修正済みだが Java 17+ 必須）が解決されて Java 1.8 と衝突している。すなわち両事象は矛盾ではなく、**「ロック・BOM 固定を欠く `LATEST` 指定が、静的監査上の脆弱範囲判定と実行時の破壊的バージョン流入を同時に招いている供給網欠陥」** という単一の根本原因に帰着する。なおコンテナ OS 層スキャン（`os_vuln_counts`）はイメージビルド失敗により未走査である。
- **SEC-02（Dockerfile ハードニング）**: Trivy IaC スキャンにより `Dockerfile` から `DS-0002`（`HIGH`：非 root `USER` 未指定による root 実行）、`DS-0001`（`MEDIUM`：`openjdk:latest` タグ使用）、`DS-0026`（`LOW`：`HEALTHCHECK` 未定義）の計3件が検出された（加えて `.dockerignore` も欠落）。
- **SEC-03〜SEC-05（秘密情報・CWE シンク・無認証 `/charge` 境界）**: SQLi/CMDi 等の危険コードシンク（`SEC-04`）は `0` 件だが、`GatewayClient.java:13` に決済 API のライブ秘密鍵定数（`GATEWAY_SECRET = "rk_live_***[REDACTED]***"`）が直書きされている（`SEC-03`）。さらに `BillingController.java:22-27` の `@RequestMapping("/charge")` は全 HTTP メソッド（`ANY`）を受け付け、認証・認可機構を一切持たず、未検証の生 `Map` ペイロードに対して `Long.parseLong` を直接実行している（`SEC-05`）。
- **CI サプライチェーン（OpenSSF Scorecard 観点）**: `.github/workflows/build.yml` は `pull_request_target` トリガー下で `actions/checkout@main`（SHA 非固定）と `mvn package` を実行し、`permissions:` 制限も欠く極めて危険な構成となっている。

```drawlib file=security_boundary_details_table.png caption="無認証 ANY /charge エンドポイント・ハードコード秘密情報・LATEST範囲CVE・IaC 詳細一覧"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=108, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=8.7),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.0),
    border_style=Styles.NeutralThin,
)
rows = [
    ["ゲート / 深刻度", "識別子・ルール", "対象箇所", "検出内容・攻撃面", "必須緩和・修正策"],
    ["SEC-01\n[CRITICAL*]", "CVE-2022-22965\n(LATEST範囲一致)", "pom.xml:20\nspring-boot-web", "LATESTを0.0.0基準で範囲照合\n(Maven実行時は4.2-RC1が流入)", "LATEST廃止・Spring 3.4固定BOM\n化後にOS層含め再スキャン"],
    ["SEC-03\n[CRITICAL]", "Hardcoded Secret\n(OWASP ASVS)", "GatewayClient\n.java:13", "GATEWAY_SECRET に本番形式鍵\n(rk_live_[REDACTED]) 直書き", "定数削除・鍵失効ローテーション\n・Secret Manager 注入化"],
    ["CI 供給網\n[CRITICAL]", "OpenSSF Token /\nPinned-Deps", ".github/workflows/\nbuild.yml:4", "pull_request_target + 権限無制限\n+ actions/checkout@main", "pull_request 化・contents:read\n明記・フルコミットSHA固定"],
    ["SEC-05\n[HIGH]", "Unauthenticated\nAPI Boundary", "BillingController\n.java:22-27", "ANY /charge が無認証・HTTP動詞\n無制限・parseLong無検証で公開", "@PostMapping 限定・Spring\nSecurity認証・@Valid DTO化"],
    ["SEC-02\n[HIGH]", "Trivy DS-0002", "Dockerfile", "USER 命令が存在せず最終コンテナ\nプロセスが root 権限で動作", "専用グループ・非 root USER を\n作成し実行権限を最小化"],
    ["SEC-02\n[MEDIUM]", "Trivy DS-0001", "Dockerfile:1", "FROM openjdk:latest の可変・\n廃止タグ指定 (.dockerignore不在)", "eclipse-temurin:21-jre 等の\n固定タグ/ダイジェストを採用"],
    ["SEC-02\n[LOW]", "Trivy DS-0026", "Dockerfile", "コンテナ HEALTHCHECK 命令が\n定義されていない", "Actuator /actuator/health を\n用いた HEALTHCHECK を定義"],
    ["SEC-04\n[PASS]", "CWE-78 / 89 /\n94 / 502 SAST", "src/main/java\n全6ファイル", "SQLi・コマンド実行・危険な\n逆直列化シンクは 0 件", "今後のDB導入時もパラメータ化\nクエリ方針を維持"],
]
tbl.draw_flexible(
    xy=(3, 105),
    column_widths=[20, 24, 24, 37, 35],
    row_heights=[7.2] + [11.8] * 8,
    data=rows,
)

save()
```

## 動的 Web ペネトレーション監査（SEC-06：`web_pentest` 起動ブロック診断と `.pni/pentests/` スイート構成）

新しく追加された動的 Web ペネトレーション監査ステップ（`act-15: web_pentest`）は、`.pni/pentests/examples/java/api_spring_messy/` 配下の 4 ファイル（`conftest.py`, `test_app_probes.py`, `test_baseline_http.py`, `test_target_surface.py`）を検証スイートとしてロードし、Docker コンテナによる隔離ループバック起動を試行した。しかし Maven ビルド不整合によりコンテナ構築段階で失敗し、ライブ HTTP プローブ実行は **`status="error"`（`server_booted=false`, `duration_sec=15.74`）** で停止した。

- **起動失敗ログ原文 (`PentestFacts.boot_failure_reason`)**:
  - `Container build failed: ERROR: failed to build: failed to solve: process "/bin/sh -c mvn -B -Dmaven.repo.local=/m2repo       org.jacoco:jacoco-maven-plugin:${JACOCO_VERSION}:prepare-agent       test       -DfailIfNoTests=false       -Dmaven.test.failure.ignore=tru`
- **整備済み DAST プローブとコード欠陥の対応関係**: ライブ通信自体はビルド障害でブロックされたものの、`test_app_probes.py` およびベースラインスイートが検査対象とする 4 種類の脆弱性プローブは、`BillingController.chargeCustomer`（`BillingController.java:22-27`）の静的欠陥と 1 対 1 で一致している。ビルド復旧直後にこれらのプローブが検出し、移行フェーズの完了ゲートとして機能する検証項目を以下に整理する。

```drawlib file=security_web_pentest_dast.png caption="SEC-06 動的Webペネトレーション監査 (web_pentest) 実行ステータスと .pni/pentests プローブ構成"
from drawlib.canvas import save, setup
from drawlib.smartarts import KpiCards, Table
from drawlib.styles import Styles

setup(width=146, height=88, dpi=150)

kpis = KpiCards(
    style=Styles.Neutral,
    metric_style=Styles.DangerBold.patch(text_size=12.0),
    text_style=Styles.DarkBold.patch(text_size=9.2),
    description_style=Styles.Neutral.patch(text_size=8.8),
    accent_position="top_bar",
    metric_layout="top_stack",
    spacing=2.5,
)
kpis.add(
    "ERROR (15.74s)",
    "DAST 実行ステータス",
    "Container build failed",
    accent_style=Styles.Danger,
)
kpis.add(
    "false",
    "server_booted",
    "Maven v61 vs v52 衝突停止",
    accent_style=Styles.Danger,
)
kpis.add(
    "4 Files",
    "整備済プローブスイート",
    ".pni/pentests/.../messy/",
    accent_style=Styles.Primary,
    metric_style=Styles.PrimaryBold.patch(text_size=12.0),
)
kpis.add(
    "0 Executed",
    "ライブプローブ実行数",
    "ビルド復旧後に自動ゲート化",
    accent_style=Styles.Warning,
    metric_style=Styles.WarningBold.patch(text_size=12.0),
)
kpis.draw(xy=(3, 65.5), width=140, height=19.5, columns=4)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=8.6),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=8.9),
    border_style=Styles.NeutralThin,
)
rows = [
    ["プローブファイル / テスト名", "対象CWE / 重要度", "対象コード箇所", "検証内容と現状の内在脆弱性 (ビルド復旧後の期待防御)"],
    ["test_app_probes.py\nrequires_authentication", "CWE-306\n[HIGH]", "BillingController\n.java:22", "無認証 POST /charge 送信に対し 401/403 を要求。現状は認証機構が\n一切なく 200 OK で課金処理が実行されるため Spring Security 必須"],
    ["test_app_probes.py\nrejects_get_verb...", "CWE-650\n[MEDIUM]", "BillingController\n.java:22", "PUT /charge 送信に対し 405 Method Not Allowed を要求。現状は\n@RequestMapping(\"/charge\") が全HTTP動詞を受理するため @PostMapping 化"],
    ["test_app_probes.py\nhandles_malformed_amount", "CWE-20\n[MEDIUM]", "BillingController\n.java:27", "amountCents=\"not-a-number\" に対し 400/422 を要求。現状は未検証の\nLong.parseLong が NumberFormatException (HTTP 500) を誘発"],
    ["test_baseline_http.py &\ntest_target_surface.py", "CWE-693 / 538 /\n942 / 22 [LOW-MED]", "Spring Security /\nHTTP 境界全体", "X-Content-Type-Options: nosniff、CORS ワイルドカード抑止、.env/.git\n非露出、SQLi/XSS/パストラバーサル耐性のベースライン自動検証"],
]
tbl.draw_flexible(
    xy=(3, 62.5),
    column_widths=[34, 24, 24, 58],
    row_heights=[7.0, 13.0, 13.0, 13.0, 12.5],
    data=rows,
)

save()
```
