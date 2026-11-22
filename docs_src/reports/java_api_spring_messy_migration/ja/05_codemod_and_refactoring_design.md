# 5. 自動コードモッドと境界アダプタ設計

コードレビュー負荷を抑え決定論的な AST 変換を保証するため、本計画では **OpenRewrite による自動コードモッド（3 レシピ・`PR-05` に隔離）** と、3 件の事前ブロッカー（`BLK-01`..`BLK-03`）および 4 件の状態／I/O 境界タッチポイントに対する **手動 Port & Adapter 設計** を明確に分離します。

```drawlib align=center code=fold file=codemod_vs_manual_breakdown.png caption="OpenRewrite 自動コードモッドレシピ vs. 手動アーキテクチャリファクタリングの分担と事前ブロッカー"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.preset_colors import CssColors
from drawlib.smartarts import Table
from drawlib.styles import Colors, Styles
from drawlib.text import text

setup(width=156, height=78, dpi=150)

text(
    (78.0, 73.8),
    "Mechanical OpenRewrite Codemods vs. Manual Port/Adapter Refactoring Scope",
    style=Styles.DarkBold.patch(text_size=12.0),
)

# Left: Grouped BarChart of Automated vs Manual file touches across Phases 0..4
chart = BarChart(
    axis_line_style=Styles.Dark.patch(line_width=1.0),
    categories=["P0", "P1", "P2", "P3", "P4"],
    width=54.0,
    height=44.0,
    bar_mode="group",
    bar_width_ratio=0.70,
    bar_r=0.8,
    title="File Touches by Execution Mode",
    title_style=Styles.DarkBold.patch(text_size=10.5),
    axis_text_style=Styles.Dark.patch(text_size=9.5),
    grid_style=Styles.MutedThin,
    value_text_style=Styles.DarkBold.patch(text_size=9.5),
    value_format="{:.0f}",
)
chart.add_series("OpenRewrite / Auto", [1.0, 0.0, 7.0, 0.0, 0.0], style=Styles.PrimaryFlat)
chart.add_series("Manual Design", [2.0, 4.0, 3.0, 3.0, 3.0], style=Styles.SecondaryNeutral)
chart.configure_y_axis(min_value=0.0, max_value=8.0, tick_step=2.0, label="Files")
chart.draw(xy=(9.0, 11.0))
chart.draw_legend(xy=(6.0, 63.0), text_style=Styles.Dark.patch(text_size=9.5), orientation="horizontal")

# Right: OpenRewrite Recipe Catalog & Blocker Summary Table
text((111.0, 65.5), "OpenRewrite Recipes (PR-05) & Pre-Requisite Blockers", style=Styles.DarkBold.patch(text_size=10.5))

table = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=9.5),
    header_cell_style=Styles.PrimaryFlat,
    header_text_style=Styles.WhiteBold.patch(text_size=9.8),
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
    text_style=Styles.WhiteBold.patch(text_size=9.8),
)
table.set_style_cell(
    background_color=Styles.PrimaryNeutral.shape_fill_color,
    text_style=Styles.PrimaryBold.patch(text_size=9.5),
    rows=[1, 2, 3],
    columns=[0],
)
table.set_style_cell(
    background_color=Styles.DangerNeutral.shape_fill_color,
    text_style=Styles.DangerBold.patch(text_size=9.5),
    rows=[4],
    columns=[0],
)
table.set_style_cell(
    background_color=Styles.WarningNeutral.shape_fill_color,
    text_style=Styles.WarningBold.patch(text_size=9.5),
    rows=[5, 6],
    columns=[0],
)
table.set_style_border(
    top=Styles.DarkBold.patch(line_width=1.4),
    top2=Styles.DarkBold.patch(line_width=1.0),
    bottom=Styles.DarkBold.patch(line_width=1.4),
    between_rows=Styles.MutedThin.patch(line_color=CssColors.LightGray, line_width=0.6),
    between_columns=Styles.MutedThin.patch(line_color=CssColors.LightGray, line_width=0.5),
)

data = [
    ["Type / ID", "Recipe or Blocker", "Scope", "Resolution"],
    ["Codemod\n(OR-1)", "UpgradeToJava21", "6 files", "POM props, diamond,\ndeprecated JDK APIs"],
    ["Codemod\n(OR-2)", "UpgradeSpringBoot_3_4", "6 files", "javax.* -> jakarta.*,\nBoot 3.4 starters"],
    ["Codemod\n(OR-3)", "JUnit4to5Migration", "1 file", "JUnit 4 @Test/Assert\n-> Jupiter api.*"],
    ["BLK-01\nCRIT", "Java 1.8 vs java.net.http\n(GatewayClient.java:4)", "Phase 0", "Pin Java 21 + Boot\n3.4 BOM (PR-01)"],
    ["BLK-02\nHIGH", "Controller <-> Manager\ncircular dependency", "Phase 1", "Sever back-edge via\nPorts/DTO (PR-04)"],
    ["BLK-03\nMED", "@Transactional without\nspring-tx (Manager:12)", "Phase 2", "Add spring-boot-data\nJPA + Flyway (PR-06)"],
]

table.draw_flexible(
    xy=(70.0, 62.5),
    column_widths=[17.0, 29.0, 12.0, 25.0],
    row_heights=[7.5, 8.2, 8.2, 8.2, 8.2, 8.2, 8.2],
    data=data,
    align="top_left",
)
save()
```

## コードモッド実行前の手動ブロッカー（`BLK-01`..`BLK-03`）

OpenRewrite の LST（Lossless Semantic Tree）解析を正常動作させるため、`PR-05` 実行前に以下の 3 件の決定論的ブロッカーを順番に解消します。

| ブロッカー ID | 深刻度 | 対象箇所 | 決定論的検出内容 | 解消ゲート |
| :--- | :--- | :--- | :--- | :--- |
| **`BLK-01`** | **CRITICAL** | `examples/java/api_spring_messy/src/main/java/com/example/billing/client/GatewayClient.java:4` | `pom.xml` の宣言ターゲットが Java `1.8` であるにもかかわらず Java 11+ の `java.net.http` を import（Spring Boot 4.2.0 バイトコード `61.0` とも衝突）。 | **Phase 0（`PR-01`）** で `pom.xml` を Java 21 LTS + Spring Boot 3.4.x BOM へ固定し `mvnw` を追加。 |
| **`BLK-02`** | **HIGH** | `com.example.billing.controller.BillingController` <-> `com.example.billing.service.BillingManager` | `@Autowired private BillingController circularController` によるモジュール間の双方向循環依存。 | **Phase 1（`PR-04`）** で明示的スカラー／DTO 引数と `ChargeCustomerUseCase` Port により上向きバックエッジを切断。 |
| **`BLK-03`** | **MEDIUM** | `examples/java/api_spring_messy/src/main/java/com/example/billing/service/BillingManager.java:12` | `pom.xml` に `spring-tx` や Data/JDBC スターターが未宣言のまま `org.springframework.transaction.annotation.Transactional` を import し、かつ Spring AOP が無効化する `private` メソッドへ付与。 | `PR-04` で不正な private 注釈を除去し、**Phase 2（`PR-06`）** で `spring-boot-starter-data-jpa` + Flyway + public `@Transactional` な `JpaBillingAuditAdapter` を導入。 |

## OpenRewrite 自動変換レシピ一覧（`PR-05`）

3 つのレシピは手動ロジック変更を一切混ぜず、単一の機械変換 PR（`./mvnw rewrite:run && ./mvnw test`）として実行します。

| ツール | OpenRewrite レシピ ID | 対象ファイル数 | 自動変換スコープ |
| :--- | :--- | :--- | :--- |
| `openrewrite` | `org.openrewrite.java.migrate.UpgradeToJava21` | `6` | Maven コンパイラプロパティの Java 21 化、ダイヤモンド演算子の最新化、非推奨 JDK 8 API の自動置換。 |
| `openrewrite` | `org.openrewrite.java.spring.boot3.UpgradeSpringBoot_3_4` | `6` | 残存する `javax.servlet` / `javax.persistence` / `javax.validation` 名前空間の `jakarta.*` 書き換え、Spring Boot 3.4 スターター更新、コンストラクタ DI 化。 |
| `openrewrite` | `org.openrewrite.java.testing.junit5.JUnit4to5Migration` | `1` | 残存する JUnit 4 `@Test` および `Assert.*` 呼び出しを `org.junit.jupiter.api.*` へ決定論的に変換。 |

## 境界タッチポイント -> アウトバウンド Port & Adapter 設計

AST 境界解析で検出された 4 件の状態／DB／外部 HTTP タッチポイント（および `GatewayClient.java:13` のハードコード認証情報）に基づき、`PR-04`, `PR-06`, `PR-07` で Clean Architecture の Port & Adapter を構築します。

```drawlib align=center code=fold file=boundary_touchpoints_adapter_design.png caption="状態・永続化・外部 HTTP 境界タッチポイントから Clean Architecture Port & Adapter への対応設計"
from drawlib.canvas import save, setup
from drawlib.preset_colors import CssColors
from drawlib.smartarts import Table
from drawlib.styles import Colors, Styles
from drawlib.text import text

setup(width=156, height=76, dpi=150)

text(
    (78.0, 71.8),
    "Boundary Touchpoints (State / DB / HTTP / Secret) -> Target Port & Adapter Design",
    style=Styles.DarkBold.patch(text_size=12.0),
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
    background_color=Styles.WarningNeutral.shape_fill_color,
    text_style=Styles.WarningBold.patch(text_size=9.5),
    rows=[1, 2],
    columns=[0],
)
table.set_style_cell(
    background_color=Styles.PrimaryNeutral.shape_fill_color,
    text_style=Styles.PrimaryBold.patch(text_size=9.5),
    rows=[3, 4],
    columns=[0],
)
table.set_style_cell(
    background_color=Styles.DangerNeutral.shape_fill_color,
    text_style=Styles.DangerBold.patch(text_size=9.5),
    rows=[5],
    columns=[0],
)
table.set_style_border(
    top=Styles.DarkBold.patch(line_width=1.4),
    top2=Styles.DarkBold.patch(line_width=1.0),
    bottom=Styles.DarkBold.patch(line_width=1.4),
    between_rows=Styles.MutedThin.patch(line_color=CssColors.LightGray, line_width=0.6),
    between_columns=Styles.MutedThin.patch(line_color=CssColors.LightGray, line_width=0.5),
)

data = [
    ["Boundary Kind", "Legacy Source & Symbol", "Current Coupling / Hazard", "Target Port Interface", "Target Adapter"],
    [
        "in_memory_state",
        "BillingController.java:20\nchannel (instance field)",
        "Mutable field on singleton\nSpring bean -> request race.",
        "ChargeCustomerUseCase\n(stateless BillingCommand)",
        "Stateless BillingController\npassing request.getMethod().",
    ],
    [
        "in_memory_state",
        "BillingManager.java:17\nstatic Map INVOICE_CACHE",
        "Unsynchronized static raw\nHashMap -> OOM & data race.",
        "InvoiceCachePort\nputSummary(id, val, ttl)",
        "RedisInvoiceCacheAdapter\n(Redis 7 + explicit TTL).",
    ],
    [
        "persistence_db",
        "BillingManager.java:91\nprivate @Transactional",
        "Self-invoked private AOP\nbypass + System.out stub.",
        "BillingAuditRepositoryPort\nsaveAudit(id, Money)",
        "JpaBillingAuditAdapter\n(PG 16 + Flyway V1 DDL).",
    ],
    [
        "external_http_rpc",
        "GatewayClient.java:22\nHttpClient.newHttpClient",
        "No connect/read timeouts;\nper-call client allocation.",
        "PaymentGatewayPort\nsendCharge(id, Money)",
        "RestClientPaymentGateway\nAdapter (bounded timeouts).",
    ],
    [
        "secret_config",
        "GatewayClient.java:13,16\nGATEWAY_SECRET / env",
        "Literal <REDACTED_SECRET>\n& untyped System.getenv().",
        "GatewayProperties\n(@ConfigurationProperties)",
        "External env/secret mount\n+ SLF4J (never log secrets).",
    ],
]

table.draw_flexible(
    xy=(4.0, 67.8),
    column_widths=[22.0, 30.0, 34.0, 30.0, 32.0],
    row_heights=[8.0, 10.6, 10.6, 10.6, 10.6, 10.6],
    data=data,
    align="top_left",
)
save()
```

### アダプタ実装ガードレール

1. **`JpaBillingAuditAdapter`（PostgreSQL 16 + Flyway）**:
   - `src/main/resources/db/migration/V1__create_billing_audit.sql` により `billing_audit` テーブル（`id`, `customer_id`, `billed_cents`, `currency`, `created_at`）をバージョン管理する。
   - `private` ではなくアダプタクラスの public メソッドに `@Transactional` を付与し、`PR-06` で Testcontainers 上の実 PostgreSQL 16 コンテナに対して結合検証する。
2. **`RedisInvoiceCacheAdapter`（Redis 7）**:
   - `StringRedisTemplate` を用いて名前空間付きキー（`billing:invoice:{customerId}`）と明示的な設定可能 TTL（例：`Duration.ofMinutes(15)`）を付与し、無制限なヒープ肥大化とスレッド間データ破壊を解消する。
3. **`RestClientPaymentGatewayAdapter`（Spring Boot 3.4 `RestClient`）**:
   - 共有 `ClientHttpRequestFactory` に明示的な `connectTimeout` / `readTimeout` を設定し、`LEGACY_PAYMENT_URL` とゲートウェイ認証情報（ソースから `<REDACTED_SECRET>` を削除・ローテーション）をバリデーション付き `@ConfigurationProperties` でバインドして WireMock でタイムアウト・5xx 耐性を検証する。
