# 1. マイグレーション戦略サマリーと多軸ギャップマトリクス

本段階的 PR 実行計画（`phased_pr`）は、ベースライン監査 `wf-8177454c`（**グレード C・66/100**）で多数の課題が確認された `legacy-billing` を、Java 1.8 / バージョン未固定 Spring Boot / 循環依存モノリスから、**Clean Architecture**（`domain` / `port` / `usecase` / `adapter`）を採用した決定論的な **Java 21 LTS + Spring Boot 3.4.x + PostgreSQL 16（JPA + Flyway） + Redis 7** サービスへモダナイズします。

```drawlib align=center code=fold file=multi_axis_gap_matrix.png caption="7 軸の As-Is ベースライン vs. To-Be 目標状態 変換ギャップマトリクス"
from drawlib.canvas import save, setup
from drawlib.preset_colors import CssColors
from drawlib.smartarts import Table
from drawlib.styles import Colors, Styles
from drawlib.text import text

setup(width=156, height=88, dpi=150)

text(
    (78.0, 83.2),
    "Multi-Axis As-Is -> To-Be Transformation Gap Matrix (7 Axes)",
    style=Styles.DarkBold.patch(text_size=12.5),
)

table = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=9.5),
    header_cell_style=Styles.PrimaryFlat,
    header_text_style=Styles.WhiteBold.patch(text_size=10.0),
    border_style=Styles.MutedThin,
)

table.set_style_cell_evenodd(
    even_color=Colors.Light,
    even_text_style=Styles.Dark.patch(text_size=9.5),
    odd_color=Colors.White,
    odd_text_style=Styles.Dark.patch(text_size=9.5),
)
table.set_style_cell_header(
    background_color=Colors.Dark,
    text_style=Styles.WhiteBold.patch(text_size=10.0),
)
table.set_style_cell(
    background_color=Styles.PrimaryNeutral.shape_fill_color,
    text_style=Styles.DarkBold.patch(text_size=9.5),
    rows=[1, 2, 3, 4, 5, 6, 7],
    columns=[0],
)
table.set_style_cell(
    background_color=Styles.DangerNeutral.shape_fill_color,
    text_style=Styles.DangerBold.patch(text_size=9.5),
    rows=[1, 2, 6, 7],
    columns=[3],
)
table.set_style_cell(
    background_color=Styles.WarningNeutral.shape_fill_color,
    text_style=Styles.WarningBold.patch(text_size=9.5),
    rows=[3, 4, 5],
    columns=[3],
)
table.set_style_border(
    top=Styles.DarkBold.patch(line_width=1.4),
    top2=Styles.DarkBold.patch(line_width=1.0),
    bottom=Styles.DarkBold.patch(line_width=1.4),
    between_rows=Styles.MutedThin.patch(line_color=CssColors.LightGray, line_width=0.6),
    between_columns=Styles.MutedThin.patch(line_color=CssColors.LightGray, line_width=0.5),
)

data = [
    ["Axis", "As-Is Baseline (66/100)", "To-Be Target State", "Risk", "Execution Approach"],
    [
        "1. Runtime\n(language)",
        "Java 1.8 vs java.net.http &\nBoot 4.2.0; Date/Vector",
        "Java 21 LTS + mvnw, records,\njava.time Clock & List",
        "CRITICAL",
        "P0 toolchain, W1 domain,\nP2 UpgradeToJava21",
    ],
    [
        "2. Framework\n(Spring/Test)",
        "Boot LATEST, javax.servlet,\nJUnit 4, @Autowired fields",
        "Spring Boot 3.4 BOM, Jakarta,\nJUnit 5 + Mockito + JaCoCo",
        "CRITICAL",
        "P0 BOM pin + Golden Master,\nP2 OpenRewrite Boot 3.4",
    ],
    [
        "3. Architecture\n(Clean Arch)",
        "Controller <-> Manager cycle,\ncognitive=56 god method",
        "Inward Clean Arch: domain,\nport, usecase, adapter",
        "HIGH",
        "Leaf-first Waves 1->4,\nP1 cycle cut (PR-04)",
    ],
    [
        "4. Database\n(Persistence)",
        "Private @Transactional stub\n(no spring-tx), System.out",
        "PostgreSQL 16 JPA + Flyway\nV1 DDL & public @Transactional",
        "HIGH",
        "P1 RepositoryPort shim,\nP2 JPA + Testcontainers",
    ],
    [
        "5. Cache/State\n(Concurrency)",
        "Static raw INVOICE_CACHE &\nmutable singleton channel",
        "Stateless beans + Redis 7\nStringRedisTemplate w/ TTL",
        "HIGH",
        "W3 delete channel field,\nP2 Redis adapter (PR-06)",
    ],
    [
        "6. Security\n(Auth/Boundary)",
        "Hardcoded <REDACTED_SECRET>,\nunbounded HTTP, ANY /charge",
        "@ConfigurationProperties,\nRestClient timeouts, @Valid",
        "CRITICAL",
        "P0 clear CVE range, P2\nRestClient, P3 DTO/secrets",
    ],
    [
        "7. Container\n& CI/CD",
        "Root openjdk:latest, no probe,\npull_request_target @main",
        "Multi-stage Temurin 21 Alpine\nnon-root + SHA-pinned CI",
        "CRITICAL",
        "P4 hardened Docker/CI +\nPNI audit, Trivy & DAST",
    ],
]

table.draw_flexible(
    xy=(4.0, 78.5),
    column_widths=[24.0, 40.0, 40.0, 14.0, 30.0],
    row_heights=[8.0, 9.2, 9.2, 9.2, 9.2, 9.2, 9.2, 9.2],
    data=data,
    align="top_left",
)
save()
```

## モダナイゼーションのエグゼクティブ要約

ベースライン監査 `wf-8177454c`（`java_api_spring_messy`）では、`pom.xml` が Java 1.8 を指定している一方で `GatewayClient.java` が Java 11 の `java.net.http` を import し、かつ `spring-boot-starter-web:LATEST` が Spring Boot 4.2.0（バイトコード `61.0`）を解決してしまうため、クリーンな Maven / Docker 環境でのビルドが失敗することが確認されています。さらに、`BillingController` と `BillingManager` 間の実行時循環依存（`circularController`）、同期化されていない可変シングルトン・静的キャッシュ（`channel`、`INVOICE_CACHE`）、空の `catch` による例外握り潰し、および全 HTTP メソッドを受け入れる未検証の `@RequestMapping("/charge")` が運用リスクを高めています。

ハイラムの法則（Hyrum's Law）による暗黙的破壊を防ぐため、一括書き換えではなく **5 段階ゲート方式の段階的 PR（`phased_pr`）** で安全に移行を進めます。

- **Phase 0（`PR-01`, `PR-02`）**: Java 21 LTS + Spring Boot 3.4.x BOM でビルドを復旧し、JUnit 5 + MockMvc のゴールデンマスター特性テストにより `POST /charge` 契約（`customerId`, `amountCents`, `billedCents`）を厳格に固定します。
- **Phase 1（`PR-03`, `PR-04`）**: 依存ゼロの末端モジュール（Wave 1）から純粋なドメイン層を抽出し、Wave 3 で `BillingManager -> BillingController` 循環エッジを切断して入出力 Port と一時的なインメモリ・シムを整備します。
- **Phase 2（`PR-05`, `PR-06`）**: 機械的な OpenRewrite コードモッド差分を `PR-05` に隔離した上で、`PR-06` にて Testcontainers / WireMock で検証済みの PostgreSQL 16（JPA + Flyway）、Redis 7（TTL 付き）、タイムアウト付き Spring `RestClient` アダプタへ差し替えます。
- **Phase 3（`PR-07`）**: `@PostMapping("/charge")` と `@Valid` Java 21 レコード DTO を導入し、ハードコードされた `GATEWAY_SECRET`（`<REDACTED_SECRET>`）を排除して SLF4J 構造化ロギングとステークホルダー承認済みの意思決定項目（`DEC-JAVA-01`..`DEC-JAVA-04`）を適用します。
- **Phase 4（`PR-08`）**: 破綻した root 実行の `openjdk:latest` Dockerfile と特権 `pull_request_target` CI を、マルチステージ非 root `eclipse-temurin:21-jre-alpine`、Actuator `/actuator/health` プローブ、およびコミット SHA 固定 CI へ刷新し、最終 PNI v2 監査・Trivy・ライブ DAST を通過させます。

```drawlib align=center code=fold file=pr_effort_risk_distribution.png caption="フェーズ別 PR 件数・相対工数および多軸リスク分布（Phase 0..Phase 4）"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.smartarts import KpiCards
from drawlib.styles import Styles

setup(width=150, height=70, dpi=150)

# Left: Grouped BarChart comparing PR Count vs Relative Effort Units per Phase
chart = BarChart(
    axis_line_style=Styles.Dark.patch(line_width=1.0),
    categories=["Phase 0\nBuild/Test", "Phase 1\nCycle/Ports", "Phase 2\nCodemod/IO", "Phase 3\nDTO/Sec", "Phase 4\nDocker/CI"],
    width=80.0,
    height=44.0,
    bar_mode="group",
    bar_width_ratio=0.68,
    bar_r=0.8,
    title="Phased PR Volume & Relative Effort (S=1, M=2, L=3)",
    title_style=Styles.DarkBold.patch(text_size=11.5),
    axis_text_style=Styles.Dark.patch(text_size=9.5),
    grid_style=Styles.MutedThin,
    value_text_style=Styles.DarkBold.patch(text_size=9.5),
    value_format="{:.0f}",
)
chart.add_series("PR Count", [2.0, 2.0, 2.0, 1.0, 1.0], style=Styles.SecondaryNeutral)
chart.add_series("Effort Units (S=1,M=2,L=3)", [3.0, 3.0, 4.0, 2.0, 2.0], style=Styles.PrimaryFlat)
chart.configure_y_axis(min_value=0.0, max_value=5.0, tick_step=1.0, label="Count / Units")
chart.draw(xy=(10.0, 11.0))
chart.draw_legend(xy=(14.0, 63.0), text_style=Styles.Dark.patch(text_size=9.5), orientation="horizontal")

# Right: Risk & Scope Summary KPI Stack
kpis = KpiCards(
    style=Styles.Neutral.patch(shape_r=2.0),
    metric_style=Styles.DarkBold.patch(text_size=13.0),
    text_style=Styles.DarkBold.patch(text_size=10.0),
    description_style=Styles.Muted.patch(text_size=9.5),
    accent_style=Styles.PrimaryFlat,
    accent_position="left_pill",
    metric_layout="left_column",
    metric_width_ratio=0.34,
    spacing=2.6,
)
kpis.add(
    "4 CRIT",
    "Critical Risk Axes",
    "Runtime, Framework, Sec, CI",
    style=Styles.DangerNeutral.patch(shape_r=2.0),
    metric_style=Styles.DangerBold.patch(text_size=12.5),
    accent_style=Styles.DangerFlat,
)
kpis.add(
    "3 HIGH",
    "High Risk Axes",
    "Clean Arch, PostgreSQL, Redis",
    style=Styles.WarningNeutral.patch(shape_r=2.0),
    metric_style=Styles.WarningBold.patch(text_size=12.5),
    accent_style=Styles.WarningFlat,
)
kpis.add(
    "8 PRs",
    "Total Effort: 14 Units",
    "3 Small | 4 Medium | 1 Large",
    style=Styles.PrimaryNeutral.patch(shape_r=2.0),
    metric_style=Styles.PrimaryBold.patch(text_size=12.5),
    accent_style=Styles.PrimaryFlat,
)
kpis.add(
    ">= 85",
    "Exit Quality Gate",
    "From 66 (C) to Grade A/S",
    style=Styles.Neutral.patch(shape_r=2.0),
    metric_style=Styles.SuccessBold.patch(text_size=12.5),
    accent_style=Styles.SuccessFlat,
)
kpis.draw(xy=(96.0, 8.0), width=50.0, height=56.0, columns=1)

save()
```

## 合意済み前提条件（Assumptions）と明示的非対象（Non-Goals）

PR 分割に先立ち、スコープ境界と非対象項目を明確に固定しています。

| 区分 | 合意済み決定事項・ガードレール |
| :--- | :--- |
| **合意済み前提** | ランタイムおよびフレームワークは **Java 21 LTS + Spring Boot 3.4.x BOM**（Jakarta EE 10、JUnit 5 Jupiter、Mockito、JaCoCo）に固定する。 |
| **合意済み前提** | 永続化は **PostgreSQL 16**（Spring Data JPA + Flyway バージョン管理 DDL `V1__create_billing_audit.sql`）へ外部化する。 |
| **合意済み前提** | プロセス内の `BillingManager.INVOICE_CACHE` は、明示的 TTL を備えた **Redis 7**（`StringRedisTemplate` / Spring Data Redis）へ外部化する。 |
| **合意済み前提** | `POST /charge` の外部 HTTP JSON 契約（`customerId`, `amountCents`, `billedCents`）に対する **厳格な互換性（`strict`）** を維持する。 |
| **合意済み前提** | 曖昧な既存挙動（`controllerPing` キー、`String ==` 参照比較、固定 `100L` リトライ課金、空の `catch`）は `ask_human` 方針に従い Phase 3 前のステークホルダー意思決定ログへ隔離する。 |
| **明示的非対象（Out of Scope）** | **マイクロサービス分割**や複数アーティファクトへのリポジトリ分割は行わず、単一デプロイ可能な Maven アーティファクト（`com.example:legacy-billing`）を維持する。 |
| **明示的非対象（Out of Scope）** | 本移行ウェーブでは **Kafka や RabbitMQ 等のイベントバス**は導入しない。 |
| **明示的非対象（Out of Scope）** | `/charge` における破壊的な URL パス変更や `/v2/charge` バージョニングは導入しない。 |

## 7 軸モダナイゼーション詳細マトリクス

| 移行軸 (`category`) | リスク | 影響ファイル | 現状ベースライン (As-Is) | 目標状態 (To-Be) |
| :--- | :--- | :--- | :--- | :--- |
| `language_runtime` | **CRITICAL** | `pom.xml`, `GatewayClient.java`, `LegacyDateHelper.java` | `pom.xml` が Java 1.8 を指定し `java.net.http`（Java 11+）および Boot 4.2.0 バイトコード `61.0` と衝突。`LegacyDateHelper` は非スレッドセーフな `SimpleDateFormat`・`Date`・`Vector` を使用。 | Java 21 LTS ツールチェーン + Maven Wrapper（`mvnw`）、不変 Java 21 `record`、`java.time.Instant` / `DateTimeFormatter` / `Clock`、`List`/`ArrayList`。 |
| `framework` | **CRITICAL** | `pom.xml`, `BillingApp.java`, `BillingController.java`, `BillingManager.java`, `BillingManagerTest.java` | BOM なしの `spring-boot-starter-web:LATEST`、`javax.servlet:4.0.1`、アサーション不在の JUnit 4.13.2 テスト、`@Autowired` フィールド注入、全メソッド許可の `@RequestMapping`、`spring-tx` 欠落。 | 固定された Spring Boot 3.4.x BOM、`jakarta.servlet` / `jakarta.validation`、Spring `RestClient`、コンストラクタ DI、`@PostMapping("/charge")`、JUnit 5 Jupiter + Mockito + JaCoCo。 |
| `architecture_pattern` | **HIGH** | `InvoiceRecord.java`, `BillingController.java`, `BillingManager.java`, `GatewayClient.java` | 実行時循環依存 `BillingController <-> BillingManager`（`circularController`）、認知的複雑度 `cognitive=56`（引数 8 個）の肥大メソッド、raw `Map`/`List` ペイロード。 | 内向き依存のみの厳格な Clean Architecture：フレームワーク非依存の `domain` レコードと `TaxPolicy`、入出力 `port` インターフェース、純粋な `usecase`、隔離された `adapter` 群。 |
| `database_persistence` | **HIGH** | `pom.xml`, `BillingManager.java` | `BillingManager.saveAuditTrail()` が `private @Transactional`（Spring AOP 自己呼び出しで無効化、`spring-tx` も未宣言）を使用し `System.out` へ出力。 | PostgreSQL 16 と Flyway `V1__create_billing_audit.sql`、public `@Transactional` を備えた `JpaBillingAuditAdapter` が実装する `BillingAuditRepositoryPort`。 |
| `cache_state` | **HIGH** | `BillingController.java`, `BillingManager.java` | 同期化されていない静的 raw `Map`（`BillingManager.INVOICE_CACHE`）およびシングルトン可変フィールド（`BillingController.channel`）によるリクエスト間データ競合。 | ステートレスな Controller / UseCase、および明示的 TTL を持つ Redis 7 `StringRedisTemplate` 実装の `RedisInvoiceCacheAdapter`（`InvoiceCachePort`）。 |
| `auth_security` | **CRITICAL** | `GatewayClient.java`, `BillingController.java`, `pom.xml` | `GatewayClient.java:13` のハードコード秘密鍵 `GATEWAY_SECRET`（`<REDACTED_SECRET>`）、型なし `System.getenv`、タイムアウトなしの `HttpClient.newHttpClient()`、無認証 `ANY /charge`、未固定 CVE-2022-22965 範囲。 | `@ConfigurationProperties` による機密・エンドポイント設定、タイムアウト制限付き `RestClient`、`@PostMapping("/charge")` + `@Valid ChargeRequest`、認証フィルタ、SLF4J 構造化ロギング。 |
| `container_cicd` | **CRITICAL** | `Dockerfile`, `.github/workflows/build.yml` | 削除済みタグの `FROM openjdk:latest`（root 実行、`.dockerignore`・`HEALTHCHECK` なし）、および `permissions` 未設定の `pull_request_target` + `actions/checkout@main`。 | マルチステージ `eclipse-temurin:21-jdk` / `21-jre-alpine` 非 root イメージ + `.dockerignore` + Actuator `HEALTHCHECK`、`contents: read`・コミット SHA 固定の `pull_request` CI。 |
