# 3. To-Be ターゲットアーキテクチャ設計（Clean Architecture & Port/Adapter）

確定した設計方針に基づき、すべての技術的詳細（Spring Web、PostgreSQL JPA、Redis 7、決済 HTTP 通信）を外側の `adapter` 層へ押し出し、ビジネスルールを純粋 Java 21 `record` で構成された `domain` 層と `usecase` 層へ集約する **Clean Architecture（4層構造）** を導入する。すべての依存矢印は内側（`adapter -> usecase -> port -> domain`）を向き、ArchUnit テストで逆方向 import を CI ブロックする。

```drawlib file=to_be_clean_architecture_diagram.png caption="To-Be Clean Architecture クラス・Port/Adapter 境界設計図"
from drawlib.canvas import save, setup
from drawlib.diagrams.class_diagram import ClassDiagram, ClassNode
from drawlib.styles import Styles

setup(width=146, height=92, dpi=150)

diag = ClassDiagram(
    node_style=Styles.Neutral,
    header_style=Styles.PrimaryFlat,
    edge_style=Styles.PrimaryBold,
    edge_text_style=Styles.Dark.patch(text_size=8.4),
    style=Styles.Neutral.patch(shape_r=2.0),
    width=140,
    height=84,
    title="To-Be Clean Architecture: Adapter -> Port -> UseCase -> Domain (DIP 単方向依存)",
    title_style=Styles.DarkBold.patch(text_size=9.8),
)

in_web = ClassNode(
    "BillingController",
    stereotype="adapter.in.web (Stateless)",
    width=40,
    header_height=8.0,
    row_height=3.5,
    header_style=Styles.PrimaryNeutral,
)
in_web.add_method("charge", "@Valid ChargeHttpReq", "ChargeHttpResp")

in_port = ClassNode(
    "ChargeCustomerUseCase",
    stereotype="<<interface>> port.in",
    width=40,
    header_height=8.0,
    row_height=3.5,
    header_style=Styles.SuccessNeutral,
)
in_port.add_method("execute", "ChargeCommand", "ChargeResult")

uc_impl = ClassNode(
    "ChargeCustomerInteractor",
    stereotype="usecase (Orchestrator)",
    width=42,
    header_height=8.0,
    row_height=3.5,
    header_style=Styles.PrimaryNeutral,
)
uc_impl.add_attribute("gateway / cache / audit", "port.out.*")

dom_mdl = ClassNode(
    "Invoice / BillingTaxPolicy",
    stereotype="domain (Java 21 record)",
    width=42,
    header_height=8.0,
    row_height=3.5,
    header_style=Styles.SuccessNeutral,
)
dom_mdl.add_method("calculateTotal", "Money, Currency", "Money")

out_ports = ClassNode(
    "Gateway / Cache / AuditPort",
    stereotype="<<interface>> port.out (x3)",
    width=42,
    header_height=8.0,
    row_height=3.5,
    header_style=Styles.SuccessNeutral,
)
out_ports.add_method("charge / cache / saveAudit", "Domain VO", "Result")

ad_http = ClassNode(
    "HttpPaymentGatewayAdapter",
    stereotype="adapter.out.gateway (Timeout)",
    width=42,
    header_height=8.0,
    row_height=3.5,
    header_style=Styles.WarningNeutral,
)
ad_http.add_attribute("connect=3s, read=5s", "RestClient")

ad_pg = ClassNode(
    "JpaBillingAuditAdapter",
    stereotype="adapter.out.persistence (PG16)",
    width=42,
    header_height=8.0,
    row_height=3.5,
    header_style=Styles.WarningNeutral,
)
ad_pg.add_attribute("Flyway V1 + Spring JPA", "PostgreSQL 16")

ad_redis = ClassNode(
    "RedisInvoiceCacheAdapter",
    stereotype="adapter.out.cache (Redis 7)",
    width=40,
    header_height=8.0,
    row_height=3.5,
    header_style=Styles.WarningNeutral,
)
ad_redis.add_attribute("TTL=15m JSON", "StringRedisTemplate")

diag.add(in_web, xy=(24, 68))
diag.add(in_port, xy=(71, 68))
diag.add(uc_impl, xy=(117, 68))
diag.add(dom_mdl, xy=(117, 41))
diag.add(out_ports, xy=(68, 41))
diag.add(ad_http, xy=(24, 13))
diag.add(ad_pg, xy=(72, 13))
diag.add(ad_redis, xy=(118, 13))

diag.connect(in_web, in_port, directed=True)
diag.connect(uc_impl, in_port, directed=True)
diag.connect(uc_impl, dom_mdl, directed=True)
diag.connect(uc_impl, out_ports, directed=True)
diag.connect(ad_http, out_ports, directed=True)
diag.connect(ad_pg, out_ports, directed=True)
diag.connect(ad_redis, out_ports, directed=True)
diag.draw(xy=(3, 4))

save()
```

## 境界タッチポイント（状態・DB・外部通信）から To-Be コンポーネントへのマッピング

`migration_analyze` が特定した4箇所の境界タッチポイント（`BillingController.channel`、`BillingManager.INVOICE_CACHE`、`@Transactional saveAuditTrail`、`GatewayClient` の `HttpClient`）を含む全既存シンボルの移行先責務を下表に定義する。

```drawlib file=component_mapping_table.png caption="As-Is クラス/タッチポイントから To-Be Clean Architecture への完全マッピング表"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=112, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=8.5),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.0),
    border_style=Styles.NeutralThin,
)
rows = [
    ["As-Is ソース / シンボル", "To-Be レイヤー", "To-Be コンポーネント / Port 役割", "境界分離・モダナイゼーション詳細"],
    [
        "InvoiceRecord.java\n(InvoiceRecord)",
        "domain",
        "domain.model.Invoice\n[Java 21 record VO]",
        "不変 record 化 + CurrencyCode / InvoiceStatus\nEnum 導入。フレームワーク依存ゼロ。",
    ],
    [
        "LegacyDateHelper.java\n(formatTimestamp)",
        "domain",
        "domain.support.AuditClock\n[Pure Time Policy]",
        "非スレッドセーフな SimpleDateFormat と Raw\nVector を廃止し java.time.Instant へ統一。",
    ],
    [
        "BillingManager.java\n(processBatchBilling)",
        "usecase /\nport.in",
        "ChargeCustomerInteractor\n-> ChargeCustomerUseCase",
        "Controller 逆参照を削除。3つの Outbound Port\nをコンストラクタ注入する純粋調停層へ再編。",
    ],
    [
        "BillingController.java\n(channel / chargeCustomer)",
        "adapter.in.web",
        "BillingController\n[Stateless Web Adapter]",
        "可変フィールド channel を完全撤去。@PostMapping\n+ @Valid Record DTO で外部 JSON 契約を維持。",
    ],
    [
        "BillingManager.java\n(INVOICE_CACHE: static Map)",
        "adapter.out.cache\n-> port.out",
        "RedisInvoiceCacheAdapter\n-> InvoiceCachePort",
        "プロセス内 static HashMap を撤去し Redis 7\n(TTL 15分・JSON 直列化) へマルチノード共有化。",
    ],
    [
        "BillingManager.java\n(@Transactional saveAuditTrail)",
        "adapter.out.persistence\n-> port.out",
        "JpaBillingAuditAdapter\n-> BillingAuditRepositoryPort",
        "PostgreSQL 16 + Spring Data JPA + Flyway V1\nマイグレーションで請求・監査証跡を永続化。",
    ],
    [
        "GatewayClient.java\n(HttpClient / SECRET)",
        "adapter.out.gateway\n-> port.out",
        "HttpPaymentGatewayAdapter\n-> PaymentGatewayPort",
        "秘密鍵を @ConfigurationProperties 注入へ外部化し\nconnect 3s / read 5s タイムアウトを強制。",
    ],
]
tbl.draw_flexible(
    xy=(3, 109),
    column_widths=[34, 24, 38, 44],
    row_heights=[8.0, 13.5, 13.5, 14.0, 14.0, 14.0, 14.0, 14.0],
    data=rows,
)

save()
```
