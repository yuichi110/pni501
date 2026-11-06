# 2. As-Is 依存グラフ解析・移行 Wave・暗黙の外部契約

`migration_analyze` による AST 内部 import グラフおよび強連結成分（Tarjan SCC）分解の結果、全6本番モジュールは **Wave 1（純粋 Leaf）→ Wave 2（外部 HTTP クライアント）→ Wave 3（SCC 循環依存ペア）→ Wave 4（起動エントリポイント）** の4段階に分類された。

```drawlib file=as_is_waves_and_cycle_cut.png caption="トポロジカル移行 Wave (Wave 1-4) と SCC 循環依存の推奨切断ポイント"
from drawlib.canvas import save, setup
from drawlib.diagrams.class_diagram import ClassDiagram, ClassNode
from drawlib.styles import Styles

setup(width=146, height=84, dpi=150)

diag = ClassDiagram(
    node_style=Styles.Neutral,
    header_style=Styles.PrimaryFlat,
    edge_style=Styles.PrimaryBold,
    edge_text_style=Styles.DarkBold.patch(text_size=8.6),
    style=Styles.Neutral.patch(shape_r=2.0),
    width=140,
    height=76,
    title="As-Is トポロジカル Wave 分解と循環依存切断エッジ (Cut: BillingManager -> BillingController)",
    title_style=Styles.DarkBold.patch(text_size=9.8),
)

w4_app = ClassNode(
    "BillingApp",
    stereotype="Wave 4: Entrypoint",
    width=36,
    header_height=8.0,
    row_height=3.5,
    header_style=Styles.PrimaryNeutral,
)
w4_app.add_method("main", "String[]", "void")

w3_ctrl = ClassNode(
    "BillingController",
    stereotype="Wave 3: SCC Cycle",
    width=42,
    header_height=8.0,
    row_height=3.5,
    header_style=Styles.WarningNeutral,
)
w3_ctrl.add_attribute("channel", "String (mutable)")
w3_ctrl.add_method("chargeCustomer", "Map", "Map")

w3_mgr = ClassNode(
    "BillingManager",
    stereotype="Wave 3: SCC Cut Source",
    width=44,
    header_height=8.0,
    row_height=3.5,
    header_style=Styles.DangerNeutral,
)
w3_mgr.add_attribute("circularController", "BillingController [CUT]")
w3_mgr.add_attribute("INVOICE_CACHE", "static raw Map")

w2_cli = ClassNode(
    "GatewayClient",
    stereotype="Wave 2: Outbound HTTP",
    width=38,
    header_height=8.0,
    row_height=3.5,
    header_style=Styles.WarningNeutral,
)
w2_cli.add_method("sendCharge", "String, long", "boolean")

w1_inv = ClassNode(
    "InvoiceRecord",
    stereotype="Wave 1: Pure Leaf DTO",
    width=38,
    header_height=8.0,
    row_height=3.5,
    header_style=Styles.SuccessNeutral,
)
w1_inv.add_attribute("invoiceId / amountCents", "final")

w1_dt = ClassNode(
    "LegacyDateHelper",
    stereotype="Wave 1: Leaf Util",
    width=38,
    header_height=8.0,
    row_height=3.5,
    header_style=Styles.SuccessNeutral,
)
w1_dt.add_method("formatTimestamp", "Date", "String")

diag.add(w4_app, xy=(22, 61))
diag.add(w3_ctrl, xy=(68, 60))
diag.add(w3_mgr, xy=(114, 59))
diag.add(w2_cli, xy=(25, 16))
diag.add(w1_inv, xy=(72, 16))
diag.add(w1_dt, xy=(116, 16))

diag.connect(w3_ctrl, w3_mgr, directed=True)
diag.connect(w3_mgr, w3_ctrl, directed=True, style=Styles.DangerBold)
diag.connect(w3_mgr, w2_cli, directed=True)
diag.connect(w3_mgr, w1_inv, directed=True)
diag.connect(w3_mgr, w1_dt, directed=True)
diag.connect(w3_ctrl, w1_inv, directed=True)
diag.draw(xy=(3, 4))

save()
```

- **循環依存の推奨切断ポイント（Cycle Cut）**: 下位レイヤーである `BillingManager` が上位 Web レイヤーの `BillingController.lastChannel()` を逆参照するバックエッジを切断対象とする。`channel` スカラー値をリクエストスコープの `ChargeCommand` 引数として上位から順方向に渡すことで、挙動を変えずに SCC サイクルを解消できる。

## 暗黙の API 入出力契約・環境変数インベントリ（後方互換ガードレール）

`BillingController.chargeCustomer` は型付き DTO ではなく `Map<String, Object>` で入出力を扱っているため、AST 解析により `getOrDefault` / `put` 呼び出しから実際の外部 JSON 契約を復元した。`api_compatibility: strict` に従い、Inbound Web Adapter の Record DTO で下表のキー互換を保証する。

```drawlib file=implicit_contracts_inventory.png caption="AST 抽出された暗黙の外部 REST 契約 (/charge) と環境変数契約"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=86, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=8.8),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.0),
    border_style=Styles.NeutralThin,
)
rows = [
    ["区分 / 方向", "キー・変数名", "推定型 / 既定値", "抽出箇所", "To-Be DTO・設定マッピング方針"],
    [
        "POST /charge\nInput JSON",
        "customerId",
        "String\n(既定: \"anon\")",
        "BillingController\n:L26",
        "ChargeHttpRequest.customerId\n(Phase 0-2 互換維持 → Phase 3 @NotBlank)",
    ],
    [
        "POST /charge\nInput JSON",
        "amountCents",
        "Integer / Long\n(既定: \"500\")",
        "BillingController\n:L27",
        "ChargeHttpRequest.amountCents\n(Phase 3 で @Positive 検証を PO 合意適用)",
    ],
    [
        "POST /charge\nOutput JSON",
        "customerId",
        "String",
        "BillingManager\n:L86",
        "ChargeHttpResponse.customerId\n(厳格互換維持: 必須出力フィールド)",
    ],
    [
        "POST /charge\nOutput JSON",
        "billedCents",
        "Long (integer)",
        "BillingManager\n:L87",
        "ChargeHttpResponse.billedCents\n(厳格互換維持: 税計算反映後の請求額)",
    ],
    [
        "POST /charge\nOutput JSON",
        "controllerPing",
        "String (診断キー)",
        "BillingManager\n:L81",
        "Decision Log DEC-03 対象: リクエスト\nX-Channel 由来で互換出力し v2 で廃止予告",
    ],
    [
        "Environment\nVariable",
        "LEGACY_PAYMENT_URL",
        "URI String\n(fallback URL あり)",
        "GatewayClient\n:L16",
        "PaymentGatewayProperties (billing.gateway.url)\n起動時 @NotNull @URL バリデーション強制",
    ],
]
tbl.draw_flexible(
    xy=(3, 83),
    column_widths=[24, 27, 25, 24, 40],
    row_heights=[8.0, 12.0, 12.0, 11.5, 11.5, 12.5, 12.5],
    data=rows,
)

save()
```
