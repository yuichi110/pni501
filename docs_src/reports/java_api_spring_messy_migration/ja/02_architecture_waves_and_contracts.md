# 2. 目標アーキテクチャ、リファクタリング Wave およびデータ契約

`BillingController <-> BillingManager` 間の循環依存を断ち切り、ビジネスロジックをインフラ詳細から分離するため、`legacy-billing` を Java 21 LTS + Spring Boot 3.4 上の **Clean Architecture（ヘキサゴナル / Ports & Adapters）** へ移行します。移行作業は末端依存から順に 4 つのトポロジカル Wave に沿って実行します。

```drawlib align=center code=fold file=target_clean_architecture.png caption="To-Be Clean Architecture（Ports & Adapters）UML クラス構成と依存性逆転図"
from drawlib.canvas import save, setup
from drawlib.diagrams.class_diagram import ClassDiagram, ClassNode
from drawlib.fonts import FontRoboto, FontSourceCode
from drawlib.shapes import rectangle
from drawlib.styles import Colors, Styles
from drawlib.text import text

setup(width=208, height=116, dpi=150)

# Top canvas title well above the 4 Clean Architecture layer bands
text(
    (104.0, 111.0),
    "Target Clean Architecture: Strict Inward Dependencies & Port/Adapter Inversion",
    style=Styles.DarkBold.patch(text_size=12.5),
)

# Subtle layer backdrop bands (y=4..105, band titles at y=101.2, class boxes below y=94)
bands = [
    (27.0, 54.5, 46.0, 100.0, "1. adapter.in.web", Styles.Neutral),
    (79.0, 54.5, 50.0, 100.0, "2. port.in / usecase / domain", Styles.PrimaryNeutral.patch(shape_fill_color=Colors.Light)),
    (131.0, 54.5, 46.0, 100.0, "3. port.out (SPI)", Styles.SecondaryNeutral.patch(shape_fill_color=Colors.Light)),
    (181.0, 54.5, 46.0, 100.0, "4. adapter.out.*", Styles.Neutral),
]
for cx, cy, bw, bh, title, st in bands:
    rectangle(
        (cx, cy),
        width=bw,
        height=bh,
        style=st.patch(shape_r=2.0, shape_line_style="dashed", shape_line_width=1.0),
    )
    text((cx, cy + bh / 2.0 - 3.2), title, style=Styles.DarkBold.patch(text_size=10.0))

hdr_primary = Styles.PrimaryNeutral.patch(text_font=FontRoboto.ROBOTO_BOLD, text_color=Colors.Dark, text_size=9.5)
hdr_secondary = Styles.SecondaryNeutral.patch(text_font=FontRoboto.ROBOTO_BOLD, text_color=Colors.Dark, text_size=9.5)
hdr_success = Styles.SuccessNeutral.patch(text_font=FontRoboto.ROBOTO_BOLD, text_color=Colors.Dark, text_size=9.5)
hdr_neutral = Styles.Neutral.patch(text_font=FontRoboto.ROBOTO_BOLD, text_color=Colors.Dark, text_size=9.5)

cd = ClassDiagram(
    node_style=Styles.Neutral.patch(text_font=FontSourceCode.ROBOTO_MONO, text_color=Colors.Dark, text_size=9.5),
    header_style=hdr_primary,
    edge_style=Styles.DarkBold,
    edge_text_style=Styles.Dark.patch(text_size=9.5),
)

# Column 1: Inbound Web Adapter (com.example.billing.adapter.in.web)
ctrl = cd.add(
    ClassNode("BillingController", stereotype="adapter.in.web", width=40.0, header_style=hdr_primary)
    .add_attribute("useCase", "ChargeUseCase", visibility="-")
    .add_method("charge", "req", "ChargeResp"),
    xy=(23.0, 74.0),
)
dtos = cd.add(
    ClassNode("ChargeRequest / Resp", stereotype="record DTO", width=40.0, header_style=hdr_neutral)
    .add_attribute("customerId", "String", visibility="+")
    .add_attribute("amountCents", "long", visibility="+")
    .add_attribute("billedCents", "long", visibility="+"),
    xy=(23.0, 28.0),
)

# Column 2: Inbound Port, UseCase & Pure Domain Core
in_port = cd.add(
    ClassNode("ChargeCustomerUseCase", stereotype="interface", width=44.0, header_style=hdr_secondary)
    .add_method("charge", "BillingCmd", "Summary"),
    xy=(75.0, 80.0),
)
usecase = cd.add(
    ClassNode("ProcessBatchBillingSvc", stereotype="usecase", width=44.0, header_style=hdr_primary)
    .add_attribute("gateway", "PaymentGatewayPort", visibility="-")
    .add_attribute("cache", "InvoiceCachePort", visibility="-")
    .add_attribute("audit", "BillingAuditRepoPort", visibility="-")
    .add_method("charge", "BillingCmd", "Summary"),
    xy=(75.0, 50.0),
)
domain = cd.add(
    ClassNode("Invoice / Money / Tax", stereotype="domain record", width=44.0, header_style=hdr_success)
    .add_attribute("invoiceId", "String", visibility="+")
    .add_attribute("currency", "Currency", visibility="+")
    .add_method("computeTax", "Money, Cur", "Money")
    .add_method("formatPeriod", "Clock", "String"),
    xy=(75.0, 18.0),
)

# Column 3: Outbound SPI Ports (com.example.billing.port)
gw_port = cd.add(
    ClassNode("PaymentGatewayPort", stereotype="interface", width=40.0, header_style=hdr_secondary)
    .add_method("sendCharge", "id, Money", "bool"),
    xy=(127.0, 80.0),
)
cache_port = cd.add(
    ClassNode("InvoiceCachePort", stereotype="interface", width=40.0, header_style=hdr_secondary)
    .add_method("putSummary", "id, val, ttl", "void"),
    xy=(127.0, 50.0),
)
audit_port = cd.add(
    ClassNode("BillingAuditRepoPort", stereotype="interface", width=40.0, header_style=hdr_secondary)
    .add_method("saveAudit", "id, Money", "void"),
    xy=(127.0, 20.0),
)

# Column 4: Outbound Infrastructure Adapters (com.example.billing.adapter.out.*)
gw_adapter = cd.add(
    ClassNode("RestGatewayAdapter", stereotype="adapter.out.gw", width=40.0, header_style=hdr_neutral)
    .add_attribute("props", "GatewayProps", visibility="-")
    .add_method("sendCharge", "id, Money", "bool"),
    xy=(177.0, 80.0),
)
cache_adapter = cd.add(
    ClassNode("RedisCacheAdapter", stereotype="adapter.out.cache", width=40.0, header_style=hdr_neutral)
    .add_attribute("redis", "StringRedisTpl", visibility="-")
    .add_method("putSummary", "id, val, ttl", "void"),
    xy=(177.0, 50.0),
)
audit_adapter = cd.add(
    ClassNode("JpaBillingAuditAdapter", stereotype="adapter.out.db", width=40.0, header_style=hdr_neutral)
    .add_attribute("repo", "AuditJpaRepo", visibility="-")
    .add_method("saveAudit", "id, Money", "void"),
    xy=(177.0, 20.0),
)

# Inward dependencies & Dependency Inversion realizations (zero crossings)
cd.connect(ctrl, in_port, "dependency", start_side="right", end_side="left")
cd.connect(ctrl, dtos, "dependency", start_side="bottom", end_side="top")
cd.connect(usecase, in_port, "realization", start_side="top", end_side="bottom")
cd.connect(usecase, domain, "dependency", start_side="bottom", end_side="top")
cd.connect(usecase, gw_port, "dependency", start_side="right", end_side="left")
cd.connect(usecase, cache_port, "dependency", start_side="right", end_side="left")
cd.connect(usecase, audit_port, "dependency", start_side="right", end_side="left")
cd.connect(gw_adapter, gw_port, "realization", start_side="left", end_side="right")
cd.connect(cache_adapter, cache_port, "realization", start_side="left", end_side="right")
cd.connect(audit_adapter, audit_port, "realization", start_side="left", end_side="right")

cd.draw(xy=(4.0, 4.0))
save()
```

## アーキテクチャ依存ルールと同心円レイヤー境界

目標パッケージ構造では、ArchUnit や静的 import 検査で検証可能な「内向き依存のみ」の原則を強制します。

| 目標レイヤー | パッケージ | 責務 | 許可される依存先 | 禁止される import |
| :--- | :--- | :--- | :--- | :--- |
| **Domain Layer** | `com.example.billing.domain` | 純粋な Java 21 不変レコード（`Invoice`, `Money`, `BillingSummary`）、`Currency`/`InvoiceStatus` 列挙型、決定論的 `TaxPolicy`、および `BillingPeriodFormatter`。 | *（なし — 外部依存ゼロ）* | `org.springframework.*`, `jakarta.persistence.*`, `jakarta.servlet.*`, `java.net.http.*` |
| **Port Layer** | `com.example.billing.port` | インバウンド UseCase 契約（`ChargeCustomerUseCase`, `ProcessBatchBillingUseCase`）およびアウトバウンド SPI 契約（`PaymentGatewayPort`, `InvoiceCachePort`, `BillingAuditRepositoryPort`）。 | `Domain Layer` | `org.springframework.web.*`, `jakarta.persistence.*` |
| **UseCase Layer** | `com.example.billing.usecase` | 上位 Controller 参照を持たず、税計算・有界リトライ・キャッシュ更新・監査永続化を統括する純粋オーケストレーション層（`ProcessBatchBillingService`）。 | `Domain Layer`, `Port Layer` | `com.example.billing.adapter.*`, `org.springframework.web.*` |
| **Inbound Web Adapter** | `com.example.billing.adapter.in.web` | ステートレスな `BillingController`（`@PostMapping("/charge")`）、厳格な外部 JSON キーを保持する `@Valid ChargeRequest`/`ChargeResponse` DTO、例外マッピング。 | `Port Layer`, `Domain Layer` | `com.example.billing.adapter.out.*` |
| **Outbound Infrastructure Adapters** | `com.example.billing.adapter.out` | `RestClientPaymentGatewayAdapter`（タイムアウト + `@ConfigurationProperties`）、`JpaBillingAuditAdapter`（PostgreSQL 16 + Flyway + public `@Transactional`）、`RedisInvoiceCacheAdapter`（Redis 7 TTL）。 | `Port Layer`, `Domain Layer` | `com.example.billing.adapter.in.*` |

## トポロジカル・リファクタリング Wave（1..4）と循環切断

決定論的 import DAG 解析により、本番 Java ソース 6 ファイルを末端から 4 つの Wave に分割しています。内部依存ゼロの Wave 1 を最初に型安全化し、Wave 3 で強連結成分（`BillingController <-> BillingManager`）の上向きバックエッジ `BillingManager.circularController -> BillingController` を切断した上で、Wave 4 のコンポジションルート結線を完了します。

```drawlib align=center code=fold file=refactoring_waves_and_cycle_cut.png caption="末端優先トポロジカル・リファクタリング Wave（1..4）と Wave 3 循環依存の切断設計"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.lines import line
from drawlib.shapes import rectangle
from drawlib.smartarts import Panel, Roadmap
from drawlib.styles import Colors, Styles
from drawlib.text import text

setup(width=156, height=82, dpi=150)

text(
    (78.0, 77.5),
    "Topological Refactoring Waves (1..4) & BillingManager -> BillingController Cycle Cut",
    style=Styles.DarkBold.patch(text_size=12.0),
)

# Left: Vertical Roadmap of Waves 1..4
rm = Roadmap(
    style=Styles.Neutral.patch(shape_r=2.0),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Muted.patch(text_size=9.5),
    spine_style=Styles.DarkBold,
    badge_style=Styles.PrimaryNeutral,
    badge_text_style=Styles.PrimaryBold.patch(text_size=9.8),
    icon_style=Styles.PrimaryBold,
    direction="vertical",
    curve_bend=0.0,
    card_shape="rounded_rect",
    spacing=2.6,
)
rm.add(
    "Wave 1: Leaf Models & Time Utilities",
    "InvoiceRecord.java, LegacyDateHelper.java -> domain records & Clock",
    badge_text="W1",
    icon=phosphor.code,
)
rm.add(
    "Wave 2: Outbound Gateway Client",
    "GatewayClient.java -> PaymentGatewayPort + RestClient adapter",
    badge_text="W2",
    icon=phosphor.arrows_clockwise,
)
rm.add(
    "Wave 3: Strongly Connected Component (Cycle Cut)",
    "BillingController <-> BillingManager -> sever circularController",
    badge_text="W3",
    icon=phosphor.warning,
    style=Styles.DangerNeutral.patch(shape_r=2.0),
    badge_style=Styles.DangerFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.8),
    icon_style=Styles.DangerBold,
)
rm.add(
    "Wave 4: Composition Root & Entrypoint",
    "BillingApp.java -> @ConfigurationPropertiesScan + Actuator probes",
    badge_text="W4",
    icon=phosphor.rocket_launch,
    badge_style=Styles.PrimaryFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.8),
)
rm.draw(xy=(4.0, 5.0), width=92.0, height=68.0)

# Right: Cycle-Cut Before/After Panel
cut_panel = Panel(
    "Wave 3 Cycle Cut (PR-04)",
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.DarkBold.patch(shape_fill_color=Colors.Dark),
    text_style=Styles.WhiteBold.patch(text_size=10.5),
    header_variant="filled",
    header_height=8.5,
    header_align="center",
)
cut_panel.draw((100.0, 5.0), width=52.0, height=68.0)

# As-Is Cyclic Box (Top half inside panel)
text((126.0, 61.2), "As-Is: Bidirectional Runtime Cycle", style=Styles.DangerBold.patch(text_size=9.8))
rectangle(
    (112.5, 51.0),
    width=21.0,
    height=11.0,
    style=Styles.DangerNeutral.patch(shape_r=1.8),
    text="Billing\nController",
    text_style=Styles.DarkBold.patch(text_size=9.5),
)
rectangle(
    (139.5, 51.0),
    width=21.0,
    height=11.0,
    style=Styles.DangerNeutral.patch(shape_r=1.8),
    text="Billing\nManager",
    text_style=Styles.DarkBold.patch(text_size=9.5),
)
line((123.2, 53.5), (128.8, 53.5), arrow_head="->", style=Styles.DarkBold)
line((128.8, 48.2), (123.2, 48.2), arrow_head="->", style=Styles.DangerDashedBold)
text((126.0, 42.2), "X Cut: @Autowired circularController", style=Styles.DangerBold.patch(text_size=9.5))

# Transition arrow down
line((126.0, 38.8), (126.0, 32.8), arrow_head="->", style=Styles.PrimaryBold)

# To-Be Acyclic Box (Bottom half inside panel)
text((126.0, 29.5), "To-Be: Acyclic Port Inversion", style=Styles.SuccessBold.patch(text_size=9.8))
rectangle(
    (112.5, 19.0),
    width=21.0,
    height=11.0,
    style=Styles.PrimaryNeutral.patch(shape_r=1.8),
    text="Billing\nController",
    text_style=Styles.DarkBold.patch(text_size=9.5),
)
rectangle(
    (139.5, 19.0),
    width=21.0,
    height=11.0,
    style=Styles.SuccessNeutral.patch(shape_r=1.8),
    text="UseCase\nService",
    text_style=Styles.DarkBold.patch(text_size=9.5),
)
line((123.2, 19.0), (128.8, 19.0), arrow_head="->", style=Styles.SuccessBold)
text((126.0, 9.8), "Pass scalar requestMethod via DTO\n(0 shared state, 0 cycles)", style=Styles.Dark.patch(text_size=9.5))

save()
```

## As-Is -> To-Be コンポーネントおよび Port/Adapter マッピング

| 既存ソース・シンボル | Wave | 移行先レイヤー | To-Be コンポーネントと役割 | 主なリファクタリング内容 |
| :--- | :--- | :--- | :--- | :--- |
| `model/InvoiceRecord.java` (`InvoiceRecord`) | Wave 1 | Domain Layer | `com.example.billing.domain.Invoice` / `Money` *（純粋 Java 21 レコード）* | クラスを不変 Java 21 `record` へ変換し、非負金額などの不変条件チェックを追加。 |
| `util/LegacyDateHelper.java` (`LegacyDateHelper`) | Wave 1 | Domain Layer | `com.example.billing.domain.BillingPeriodFormatter` *（ドメイン時刻ポリシー）* | `SimpleDateFormat`・`Date`・`Vector` をスレッドセーフな `DateTimeFormatter`・`Clock`・`List<String>` へ置換。 |
| `client/GatewayClient.java` (`sendCharge`) | Wave 2 | Outbound Adapters | `adapter.out.gateway.RestClientPaymentGatewayAdapter` *（`PaymentGatewayPort` 実装）* | `LEGACY_PAYMENT_URL` と `GATEWAY_SECRET`（`<REDACTED_SECRET>`）を `@ConfigurationProperties` へ外部化し、接続・読取タイムアウト付き `RestClient` と SLF4J へ置換。 |
| `service/BillingManager.java` (`processBatchBilling`) | Wave 3 | UseCase Layer | `usecase.ProcessBatchBillingService` *（`ProcessBatchBillingUseCase` 実装）* | `@Autowired circularController` を切断し、`cognitive=56`・引数 8 個のメソッドを `BillingCommand` + `TaxPolicy` へ分解して 3 つのアウトバウンド Port に委譲。 |
| `service/BillingManager.java` (`INVOICE_CACHE`) | Wave 3 | Outbound Adapters | `adapter.out.cache.RedisInvoiceCacheAdapter` *（`InvoiceCachePort` 実装）* | 非同期の静的 raw `HashMap` を、明示的 TTL 付きの Redis 7 `StringRedisTemplate` 実装へ移行。 |
| `service/BillingManager.java` (`saveAuditTrail`) | Wave 3 | Outbound Adapters | `adapter.out.persistence.JpaBillingAuditAdapter` *（`BillingAuditRepositoryPort` 実装）* | 無効な `private @Transactional` + `System.out` スタブを、PostgreSQL 16 JPA リポジトリ + Flyway DDL + public `@Transactional` へ置換。 |
| `controller/BillingController.java` (`chargeCustomer`) | Wave 3/4 | Inbound Web Adapter | `adapter.in.web.BillingController` *（インバウンド HTTP アダプタ）* | 可変フィールド `channel` を削除し、`@PostMapping("/charge")` + `@Valid ChargeRequest` へ厳格化。JSON 出力キーを維持しつつ `ChargeCustomerUseCase` をコンストラクタ DI。 |
| `BillingApp.java` (`BillingApp`) | Wave 4 | Composition Root | `com.example.billing.BillingApp` + `BillingConfiguration` | `@ConfigurationPropertiesScan` の有効化、アダプタ Bean の結線、Spring Boot Actuator ヘルスプローブの公開。 |

## 暗黙的 HTTP / 環境変数契約から型付き DTO へのマッピング

`api_compatibility=strict` に基づき、静的 AST 解析で検出されたすべての暗黙的 JSON キーおよび環境変数契約を、Java 21 レコード DTO と `@ConfigurationProperties` へ明示的に対応付けます。

```drawlib align=center code=fold file=implicit_contract_mapping.png caption="暗黙的 ANY /charge および環境変数契約から型付き Java 21 DTO / 設定レコードへのマッピング"
from drawlib.canvas import save, setup
from drawlib.preset_colors import CssColors
from drawlib.smartarts import Table
from drawlib.styles import Colors, Styles
from drawlib.text import text

setup(width=156, height=74, dpi=150)

text(
    (78.0, 69.5),
    "Strict External Contract Preservation: Implicit Keys -> Typed Java 21 DTOs & Config",
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
    background_color=Styles.PrimaryNeutral.shape_fill_color,
    text_style=Styles.PrimaryBold.patch(text_size=9.5),
    rows=[1, 2, 3, 4],
    columns=[0],
)
table.set_style_cell(
    background_color=Styles.WarningNeutral.shape_fill_color,
    text_style=Styles.WarningBold.patch(text_size=9.5),
    rows=[5],
    columns=[0],
)
table.set_style_cell(
    background_color=Styles.SecondaryNeutral.shape_fill_color,
    text_style=Styles.DarkBold.patch(text_size=9.5),
    rows=[6],
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
    ["Direction", "Contract Key", "Legacy Source & Default", "To-Be Typed Target", "Compatibility Guard"],
    [
        "HTTP Input",
        "customerId",
        "BillingController.java:26\nstring (default=\"anon\")",
        "ChargeRequest.customerId\n@Size / default fallback",
        "Preserved verbatim on\nPOST /charge JSON body",
    ],
    [
        "HTTP Input",
        "amountCents",
        "BillingController.java:27\ninteger (default=500)",
        "ChargeRequest.amountCents\nLong (default 500L)",
        "Validated in P3; zero-\namount gated by DEC-02",
    ],
    [
        "HTTP Output",
        "customerId",
        "BillingManager.java:86\nraw Map.put(\"customerId\")",
        "ChargeResponse.customerId\n(non-null String)",
        "Locked by P0 MockMvc\nGolden Master assertion",
    ],
    [
        "HTTP Output",
        "billedCents",
        "BillingManager.java:87\nraw Map.put(\"billedCents\")",
        "ChargeResponse.billedCents\n(long integer cents)",
        "Locked by P0 Golden Master;\ntax gated by DEC-JAVA-01",
    ],
    [
        "HTTP Output\n(Conditional)",
        "controllerPing",
        "BillingManager.java:81\nmutable lastChannel() leak",
        "Optional @JsonInclude\nstateless requestMethod",
        "Gated by DEC-JAVA-03;\nzero shared mutable state",
    ],
    [
        "Env Config",
        "LEGACY_PAYMENT_URL\n+ secret binding",
        "GatewayClient.java:13,16\nhardcoded <REDACTED_SECRET>",
        "GatewayProperties record\n@ConfigurationProperties",
        "Retains env var binding;\ndeletes literal secret",
    ],
]

table.draw_flexible(
    xy=(4.0, 65.5),
    column_widths=[20.0, 26.0, 35.0, 34.0, 33.0],
    row_heights=[8.0, 8.8, 8.8, 8.8, 8.8, 8.8, 8.8],
    data=data,
    align="top_left",
)
save()
```
