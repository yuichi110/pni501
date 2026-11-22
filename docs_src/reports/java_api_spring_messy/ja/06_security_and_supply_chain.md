# 6. 詳細分析: セキュリティ・サプライチェーン・API 攻撃面

`legacy-billing` はセキュリティおよびサプライチェーン関連の主要ゲートすべてに不合格です（`security=50/100`, `security_vulnerability_audit=18/100`, `supply_chain_audit=15/100`, `web_penetration_audit=20/100`）。未固定 Spring Boot 依存による CRITICAL CVE 範囲露出、特権 GitHub Actions ワークフロー、廃止 root Dockerfile、ハードコードされたゲートウェイ秘密鍵（`<REDACTED_SECRET>`）、および Maven ビルド失敗で DAST 検証が封じられた未認証エンドポイントが、開発から配信までの全層にまたがっています。

```drawlib align=center code=hide file=sec_supply_chain_breakdown.png caption="領域・重要度別のセキュリティ検出事項内訳（左）および静的 Trivy SCA と実 Maven 解決の整合整理（右）"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.smartarts import CardList, Panel
from drawlib.styles import Styles

setup(width=146, height=68, dpi=150)

# Left: Multi-series stacked BarChart with explicit legend
bar = BarChart(
    axis_line_style=Styles.Dark,
    width=70.0,
    height=46.0,
    categories=["SCA\nCVEs", "Docker\nIaC", "CI\nActions", "AST\nSecrets", "API\nSurface"],
    orientation="vertical",
    bar_mode="stack",
    bar_width_ratio=0.62,
    bar_r=0.8,
    axis_text_style=Styles.DarkBold.patch(text_size=9.5),
    grid_style=Styles.MutedThin,
    value_text_style=Styles.WhiteBold.patch(text_size=9.5),
    value_format="{:.0f}",
    title="Security & Supply-Chain Defects by Surface",
    title_style=Styles.DarkBold.patch(text_size=11.0),
)
bar.configure_y_axis(min_value=0, max_value=4, tick_step=1, show_grid=True)
bar.add_series("CRITICAL", [1, 0, 1, 1, 0], style=Styles.DangerFlat)
bar.add_series("HIGH", [0, 1, 1, 0, 1], style=Styles.WarningFlat)
bar.add_series("MED / LOW", [0, 2, 1, 0, 0], style=Styles.PrimaryFlat)
bar.draw(xy=(6.0, 13.0))
bar.draw_legend(
    xy=(11.0, 4.5),
    text_style=Styles.DarkBold.patch(text_size=9.5),
    orientation="horizontal",
    item_gap=6.0,
)

# Right: Reconciling Trivy Static Range vs Live Maven Resolution
p_rec = Panel(
    "Reconciling Trivy SCA vs. Live Maven (LATEST)",
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=10.2),
    header_variant="filled",
    header_height=7.5,
)
p_rec.draw((80.0, 5.0), width=62.0, height=58.0)

cards = CardList(
    style=Styles.Neutral.patch(shape_r=1.8),
    text_style=Styles.DarkBold.patch(text_size=9.8),
    description_style=Styles.Dark.patch(text_size=9.2),
    badge_shape="rounded_rect",
    badge_style=Styles.PrimaryFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.0),
    direction="vertical",
    spacing=2.4,
)
cards.add(
    "Static Trivy FS Scan",
    "is_unpinned_specifier=True:\nfull CVE range -> CVE-2022-22965.",
    badge_text="SCA",
    style=Styles.DangerNeutral.patch(shape_r=1.8),
    badge_style=Styles.DangerFlat,
)
cards.add(
    "Live Maven Harness",
    "Pulls Spring Boot 4.2.0 -> 61.0\ncrash on Java 1.8 (52.0).",
    badge_text="BUILD",
    style=Styles.WarningNeutral.patch(shape_r=1.8),
    badge_style=Styles.WarningFlat,
)
cards.add(
    "Unified P0 Resolution",
    "Pin Java 21 + Boot 3.4.x BOM +\nmvnw: fixes CVE & build crash.",
    badge_text="FIX",
    style=Styles.SuccessNeutral.patch(shape_r=1.8),
    badge_style=Styles.SuccessFlat,
)
cards.draw((83.0, 8.0), width=56.0, height=44.5)

save()
```

---

## サプライチェーン・SCA・コンテナ堅牢化監査

### ガバナンスおよびサプライチェーン基準値

- **ロックファイルと依存衛生**: `has_lockfile=False`（`mvnw` および依存検証なし）、`dependencies_count=2`、`unpinned_dependencies_count=1`（`org.springframework.boot:spring-boot-starter-web:LATEST`）。
- **ガバナンスと自動化**: `has_license=False`、`has_security_policy=False`、`has_dependency_automation=False`（Dependabot/Renovate 未設定）、`has_gitignore=False`。
- **Trivy スキャナー構成**: `ghcr.io/aquasecurity/trivy:0.69.3`（`docker`）、`scanned_filesystem=True`、`scanned_resolved_image=False`（`openjdk:latest not found` によりプロジェクトイメージ構築が失敗したため、OS ベースイメージ CVE は `0`／未検証状態）。

### アプリケーション CVE および Dockerfile IaC 設定不備

| 区分 | ID | 重要度 | 対象 | 観測状況・詳細 | 推奨対策 |
| :--- | :--- | :---: | :--- | :--- | :--- |
| **アプリ CVE (`runtime_core`)** | **`CVE-2022-22965`** | **`CRITICAL`** *（CVSS 9.8）* | `pom.xml` (`spring-boot-starter-web@LATEST`) | `spring-framework: RCE via Data Binding on JDK 9+`（`is_unpinned_specifier=True` — 未固定のため静的 SCA が過去全範囲を評価。一方、実 Maven ビルドは `4.2.0` を取得し Java 1.8 でクラッシュ） | 修正済み BOM 版を明示固定（最小 `>= 2.5.12 / 2.6.6`、推奨 Spring Boot `3.4.x` BOM + Java 21 LTS） |
| **コンテナ OS CVE** | `—` | `INFO` | プロジェクト Docker イメージ | `0` 件（`openjdk:latest` 取得失敗のため `scanned_resolved_image=False`） | `eclipse-temurin:21-jre-alpine` へ移行しビルド済みイメージを再スキャン |
| **Dockerfile IaC** | **`DS-0002`** | **`HIGH`** | `Dockerfile` | コンテナ実行ユーザーが `root` のまま（非 root `USER` 命令が欠落） | 非 root ユーザーを作成し `USER appuser` を指定 |
| **Dockerfile IaC** | **`DS-0001`** | **`MEDIUM`** | `Dockerfile:1` | `FROM openjdk:latest` で可変 `:latest` タグを使用（さらにイメージ自体が廃止済み） | 明示タグまたはダイジェスト固定（`eclipse-temurin:21-jre-alpine`） |
| **Dockerfile IaC** | **`DS-0026`** | **`LOW`** | `Dockerfile` | `HEALTHCHECK` 命令が未定義、かつ `.dockerignore` も欠如 | Spring Actuator `/actuator/health` を検査する `HEALTHCHECK` と `.dockerignore` を追加 |

### CI/CD サプライチェーン露出（`.github/workflows/build.yml`）

1. **特権 `pull_request_target` トリガー**: 外部フォーク PR に対してベースリポジトリの特権トークン権限下で `mvn package` を実行する危険な構成です。`pull_request` トリガーへ置き換えてください。
2. **明示的 `permissions:` ブロックの欠如**: OpenSSF Token-Permissions の最小権限原則に違反しています。`permissions: { contents: read }` を明示してください。
3. **可変ブランチ参照（`actions/checkout@main`）**: 変動するブランチ先端を参照しておりサプライチェーン改ざん耐性がありません。検証済みの 40 桁フルコミット SHA で固定してください。

---

## シークレット衛生・API 攻撃面・DAST ブロック状況

```drawlib align=center code=hide file=sec_attack_surface_map.png caption="エンドツーエンドのセキュリティ境界と攻撃面マップ（CI/ビルド供給網、未認証 ANY /charge 入口、マスク済みハードコード秘密鍵）"
from drawlib.canvas import save, setup
from drawlib.lines import line
from drawlib.shapes import rectangle
from drawlib.smartarts import Panel
from drawlib.styles import Styles
from drawlib.text import text

setup(width=146, height=66, dpi=150)

text(
    (73.0, 62.0),
    "Security Boundary & Attack Surface Map (0 AST CWE Sinks | 1 Unauth Endpoint | 1 Hardcoded Secret)",
    style=Styles.DarkBold.patch(text_size=11.0),
)

# Zone 1: Delivery & Supply Chain
p1 = Panel(
    "1. Build & CI Supply Chain",
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.DangerNeutral,
    text_style=Styles.DarkBold.patch(text_size=10.0),
    header_variant="filled",
    header_height=7.0,
)
p1.draw((4.0, 6.0), width=42.0, height=51.0)
rectangle(
    (25.0, 41.0),
    width=36.0,
    height=11.0,
    style=Styles.DangerNeutral.patch(shape_r=1.5),
    text="GitHub Actions CI\npull_request_target + @main",
    text_style=Styles.DarkBold.patch(text_size=9.2),
)
rectangle(
    (25.0, 27.0),
    width=36.0,
    height=11.0,
    style=Styles.DangerNeutral.patch(shape_r=1.5),
    text="pom.xml (LATEST)\nCVE-2022-22965 range",
    text_style=Styles.DarkBold.patch(text_size=9.2),
)
rectangle(
    (25.0, 13.0),
    width=36.0,
    height=11.0,
    style=Styles.WarningNeutral.patch(shape_r=1.5),
    text="Dockerfile (root)\nDS-0002 / DS-0001 / DS-0026",
    text_style=Styles.DarkBold.patch(text_size=9.2),
)

# Zone 2: HTTP Ingress & Blocked DAST
p2 = Panel(
    "2. HTTP Ingress & DAST",
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=10.0),
    header_variant="filled",
    header_height=7.0,
)
p2.draw((52.0, 6.0), width=42.0, height=51.0)
rectangle(
    (73.0, 41.0),
    width=36.0,
    height=12.0,
    style=Styles.DangerFlat.patch(shape_r=1.5),
    text="ANY /charge (Line 22)\nNo Auth | Raw Map | No @Valid",
    text_style=Styles.WhiteBold.patch(text_size=9.2),
)
rectangle(
    (73.0, 26.5),
    width=36.0,
    height=11.0,
    style=Styles.WarningNeutral.patch(shape_r=1.5),
    text="web_pentest (SEC-06)\nBLOCKED: 0/0 probes executed",
    text_style=Styles.DarkBold.patch(text_size=9.2),
)
rectangle(
    (73.0, 13.0),
    width=36.0,
    height=10.5,
    style=Styles.SuccessNeutral.patch(shape_r=1.5),
    text="AST CWE Sinks (SAST)\n0 dangerous sinks detected",
    text_style=Styles.DarkBold.patch(text_size=9.2),
)

# Zone 3: Secret Hygiene & External Egress
p3 = Panel(
    "3. Secret & Outbound Egress",
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.DangerNeutral,
    text_style=Styles.DarkBold.patch(text_size=10.0),
    header_variant="filled",
    header_height=7.0,
)
p3.draw((100.0, 6.0), width=42.0, height=51.0)
rectangle(
    (121.0, 40.5),
    width=36.0,
    height=13.0,
    style=Styles.DangerNeutral.patch(shape_r=1.5),
    text="GatewayClient.java:13\nGATEWAY_SECRET =\n<REDACTED_SECRET>",
    text_style=Styles.DangerBold.patch(text_size=9.2),
)
rectangle(
    (121.0, 25.0),
    width=36.0,
    height=11.0,
    style=Styles.WarningNeutral.patch(shape_r=1.5),
    text="HttpClient (No Timeout)\nSystem.getenv + printStackTrace",
    text_style=Styles.DarkBold.patch(text_size=9.2),
)
rectangle(
    (121.0, 12.0),
    width=36.0,
    height=9.5,
    style=Styles.PrimaryNeutral.patch(shape_r=1.5),
    text="External Gateway POST\nbilling.example.invalid/charge",
    text_style=Styles.DarkBold.patch(text_size=9.0),
)

# Connectors between zones
line((46.5, 31.5), (51.5, 31.5), arrow_head="->", style=Styles.DarkBold)
line((94.5, 31.5), (99.5, 31.5), arrow_head="->", style=Styles.DarkBold)

save()
```

### シークレット検出・AST CWE シンク・HTTP 攻撃面マトリクス

| セキュリティ領域 | 対象 / シンボル | 状態 | 監査証跡の詳細 |
| :--- | :--- | :---: | :--- |
| **ハードコード秘密鍵 (`SEC-03`)** | `GatewayClient.GATEWAY_SECRET`（`GatewayClient.java:13`） | **`CRITICAL`** | AST の OWASP ASVS ヒューリスティックにより、本番形式のハードコード秘密鍵リテラル（`<REDACTED_SECRET>`）を検出。Trivy の汎用正規表現スキャンは `0` 件（ベンダー固有プレフィックス外のため）であり、AST と SCA の多層防御の有効性を示す結果となりました。直ちに削除・ローテーションし `@ConfigurationProperties` 注入へ移行してください。 |
| **AST 危険シンク (CWE SAST)** | 本番 Java ソース（`187 LOC`） | **`PASS (0)`** | SQL インジェクション、コマンド実行、安全でないデシリアライズ、XXE 等の CWE 危険シンクは `0` 件。 |
| **抽出 HTTP API 攻撃面 (`SEC-05`)** | `ANY /charge` -> `BillingController.chargeCustomer`（`BillingController.java:22`） | **`HIGH`** | 無制限 `@RequestMapping("/charge")` が `GET`/`POST`/`PUT`/`DELETE` 等すべての HTTP メソッドを `auth_hint=NONE`（認証なし）・生 `@RequestBody Map`・Bean Validation（`@Valid`）なしで受け付けます。 |
| **動的 Web ペネトレーション (`SEC-06`)** | `.pni/pentests/examples/java/api_spring_messy` | **`ERROR`（ブロック）** | 4 つの pytest/httpx プローブ（`conftest.py`, `test_app_probes.py`, `test_baseline_http.py`, `test_target_surface.py`）を生成済みですが、Java 8 下での `spring-boot-4.2.0.jar` ビルド失敗によりコンテナ起動不可（`server_booted=False`, `0/0` プローブ実行）となりました。`P0` ビルド復旧後、直ちに再実行してください。 |
