# 2. アーキテクチャとソースコード構成

`legacy-billing` はパッケージ構造上は **5層 Spring MVC アーキテクチャ（Entrypoint / Controller / Service / Client / Model・Util、計6本番ファイル・187 LOC）** を採るが、実際には `BillingManager`（Service 層）が上位の `BillingController`（Controller 層）を逆方向に `@Autowired` 注入する双方向循環依存を抱えている。

```drawlib file=arch_tree_and_inventory.png caption="ソースディレクトリ構造ツリーとASTモジュールインベントリ (本番6ファイル・187 LOC)"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import Panel, Table, TreeNode
from drawlib.styles import Styles

setup(width=146, height=78, dpi=150)

left_panel = Panel(
    "リポジトリ構成ツリー",
    "",
    style=Styles.Neutral,
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=10.2),
    icon=phosphor.git_branch,
    icon_style=Styles.White,
    header_height=9.5,
)
left_panel.draw(xy=(2, 3), width=48, height=72)

t_style = Styles.Dark.patch(text_size=8.8)
b_style = Styles.PrimaryBold.patch(text_size=9.0)
d_style = Styles.DangerBold.patch(text_size=8.8)
w_style = Styles.WarningBold.patch(text_size=8.8)

root = TreeNode(
    "api_spring_messy/",
    text_style=b_style,
    line_style=Styles.Neutral,
    line_horizontal_margin=0.9,
    line_horizontal_length=2.0,
    line_vertical_margin=3.5,
)
root.add("pom.xml / Dockerfile [CRIT]", text_style=d_style)
root.add(".github/workflows/build.yml", text_style=d_style)
root.add("README.md (2 lines)", text_style=t_style)
src_node = root.add("src/main/.../billing/", text_style=b_style)
src_node.add("BillingApp.java (9 LOC)", text_style=t_style)
src_node.add("controller/BillingController", text_style=w_style)
src_node.add("service/BillingManager [1.0]", text_style=d_style)
src_node.add("client/GatewayClient [0.88]", text_style=d_style)
src_node.add("model/InvoiceRecord (15 LOC)", text_style=Styles.SuccessBold.patch(text_size=8.8))
src_node.add("util/LegacyDateHelper", text_style=w_style)
tst_node = root.add("src/test/.../billing/", text_style=b_style)
tst_node.add("BillingManagerTest.java", text_style=w_style)
root.draw(xy=(4.2, 62.5))

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=9.0),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.2),
    border_style=Styles.NeutralThin,
)
rows = [
    ["モジュール", "LOC", "公開型・メソッドと主要責務・健全性メモ"],
    ["service/\nBillingManager.java", "78", "processBatchBilling | 請求集計・税加算・再試行\n[Risk 1.00] 循環依存・複雑度56・==比較・空catch"],
    ["controller/\nBillingController.java", "38", "chargeCustomer, lastChannel | /charge 公開\n[Risk 0.58] ANYメソッド・無認証・parseLong・Raw Map"],
    ["client/\nGatewayClient.java", "32", "sendCharge | 外部決済HTTP POST送信\n[Risk 0.88] 秘密鍵直書き・Timeout不在・* import"],
    ["model/\nInvoiceRecord.java", "15", "InvoiceRecord, getInvoiceId, getAmountCents\n[健全] final不変DTO・Javadoc完備の基準モデル"],
    ["util/\nLegacyDateHelper.java", "15", "formatTimestamp, collectAuditTags\nDate/SimpleDateFormat/Raw Vector・未定義呼出先"],
    ["BillingApp.java", "9", "main | @SpringBootApplication 起動エントリポイント"],
]
tbl.draw_flexible(
    xy=(52, 75),
    column_widths=[30, 9, 52],
    row_heights=[7.5, 10.5, 10.5, 10.5, 10.0, 10.0, 9.0],
    data=rows,
)

save()
```

## レイヤー境界違反（双方向循環依存）とリスクホットスポット

AST の内部 import グラフ解析により、`BillingController -> BillingManager -> BillingController` の **双方向循環依存（2サイクル）** が検出された。`BillingManager` は `@Autowired private BillingController circularController;` を保持し `lastChannel()` を逆参照している。また指摘密度から算出された `module_hotspots` では、`BillingManager.java`（`risk_score=1.00`）、`pom.xml`（`1.00`）、`Dockerfile`（`1.00`）、`.github/workflows/build.yml`（`0.90`）、`GatewayClient.java`（`0.88`）、`BillingController.java`（`0.58`）にリスクが集中している。

```drawlib file=arch_layer_hotspot_diagram.png caption="クラス依存関係グラフ（循環依存を含む）とモジュールリスク密度 (HeatmapOverlay)"
from drawlib.canvas import save, setup
from drawlib.charts.heatmap import HeatmapOverlay
from drawlib.diagrams.class_diagram import ClassDiagram, ClassNode
from drawlib.styles import Styles

setup(width=146, height=88, dpi=150)

diag = ClassDiagram(
    node_style=Styles.Neutral,
    header_style=Styles.PrimaryFlat,
    edge_style=Styles.PrimaryBold,
    edge_text_style=Styles.Dark.patch(text_size=8.8),
    style=Styles.Neutral.patch(shape_r=2.0),
    width=124,
    height=80,
    title="legacy-billing クラス依存グラフ × リスク密度オーバーレイ",
    title_style=Styles.DarkBold.patch(text_size=10.2),
)

n_app = ClassNode("BillingApp", stereotype="Bootstrap (9 LOC)", width=34, header_height=7.8, row_height=3.4)
n_app.add_method("main", "String[]", "void")

n_ctrl = ClassNode(
    "BillingController",
    stereotype="Controller (38 LOC)",
    width=38,
    header_height=7.8,
    row_height=3.4,
    header_style=Styles.Warning,
)
n_ctrl.add_attribute("channel", "String (mutable)")
n_ctrl.add_method("chargeCustomer", "Map, ...", "Map")

n_svc = ClassNode(
    "BillingManager",
    stereotype="Service (78 LOC)",
    width=40,
    header_height=7.8,
    row_height=3.4,
    header_style=Styles.Danger,
)
n_svc.add_attribute("INVOICE_CACHE", "static Map")
n_svc.add_method("processBatchBilling", "8 params", "Map")

n_cli = ClassNode(
    "GatewayClient",
    stereotype="Client (32 LOC)",
    width=36,
    header_height=7.8,
    row_height=3.4,
    header_style=Styles.Danger,
)
n_cli.add_attribute("GATEWAY_SECRET", "String")
n_cli.add_method("sendCharge", "id, cents", "boolean")

n_mdl = ClassNode(
    "InvoiceRecord",
    stereotype="Immutable DTO (15 LOC)",
    width=38,
    header_height=7.8,
    row_height=3.4,
    header_style=Styles.Success,
)
n_mdl.add_attribute("invoiceId / amountCents", "final")

n_utl = ClassNode("LegacyDateHelper", stereotype="Utility (15 LOC)", width=36, header_height=7.8, row_height=3.4)
n_utl.add_method("formatTimestamp", "Date", "String")

diag.add(n_app, xy=(22, 65))
diag.add(n_ctrl, xy=(66, 64))
diag.add(n_svc, xy=(66, 38))
diag.add(n_cli, xy=(22, 11))
diag.add(n_mdl, xy=(64, 11))
diag.add(n_utl, xy=(104, 11))

diag.connect(n_ctrl, n_svc, directed=True)
diag.connect(n_svc, n_ctrl, directed=True)
diag.connect(n_ctrl, n_mdl, directed=True)
diag.connect(n_svc, n_cli, directed=True)
diag.connect(n_svc, n_mdl, directed=True)
diag.connect(n_svc, n_utl, directed=True)
diag.draw(xy=(3, 4))

ov = HeatmapOverlay(
    min_style=Styles.Success,
    max_style=Styles.Danger,
    width=124,
    height=80,
    min_value=0.0,
    max_value=1.0,
    default_radius=13.5,
    max_alpha=0.26,
    show_contour_lines=False,
)
ov.add_spot(xy=(66, 38), value=1.00, radius=15.0)
ov.add_spot(xy=(22, 11), value=0.88, radius=13.5)
ov.add_spot(xy=(66, 64), value=0.58, radius=13.0)
ov.add_spot(xy=(22, 65), value=0.06, radius=9.0)
ov.add_spot(xy=(64, 11), value=0.06, radius=9.5)
ov.add_spot(xy=(104, 11), value=0.18, radius=10.0)
ov.draw(xy=(3, 4))
ov.draw_colorbar(
    xy=(131, 16),
    text_style=Styles.Dark.patch(text_size=9.0),
    length=52.0,
    thickness=2.6,
    orientation="vertical",
    label="Risk",
)

save()
```

## 実行データフローと状態・並行制御モデル

リクエスト実行時は `/charge` から `BillingManager` へ8引数で処理が委譲されるが、シングルトン Bean 上の可変フィールド `BillingController.channel` と `public static Map INVOICE_CACHE = new HashMap()` が並行リクエスト間で共有され直接のデータ競合（Race Condition）を引き起こす（なお `LegacyDateHelper.formatTimestamp` 内の `SimpleDateFormat` および未使用 `collectAuditTags` の `Vector` はメソッドローカル生成のため直接のスレッド間競合ではなく、都度インスタンス生成および旧式 `java.util.Date` API のモダナイゼーション負債に分類される）。さらに `saveAuditTrail` の `@Transactional` は `spring-tx` 未宣言かつ `private` メソッド付与のため機能せず、`dateHelper.currentPeriodLabel()` の未定義呼び出しや実行時例外が空の `catch (Exception e) {}` で無言のまま握り潰される構造となっている。

```drawlib file=arch_execution_flow_roadmap.png caption="HTTP /charge リクエスト実行フローと潜在障害ポイント"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import Roadmap
from drawlib.styles import Styles

setup(width=146, height=58, dpi=150)

flow = Roadmap(
    style=Styles.Neutral,
    text_style=Styles.DarkBold.patch(text_size=9.5),
    description_style=Styles.Dark.patch(text_size=9.0),
    spine_style=Styles.PrimaryBold,
    badge_style=Styles.Primary,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.2),
    direction="horizontal",
    spacing=2.5,
)
flow.add(
    "1. ANY /charge 受信",
    "無型Mapとchannel更新\nLong.parseLong無検証",
    badge_text="S1",
    style=Styles.WarningNeutral,
    badge_style=Styles.Warning,
    icon=phosphor.globe,
    icon_style=Styles.Warning,
)
flow.add(
    "2. バッチ税計算",
    "8引数でService呼出\ncurrency == 参照比較バグ",
    badge_text="S2",
    style=Styles.DangerNeutral,
    badge_style=Styles.Danger,
    icon=phosphor.calculator if hasattr(phosphor, "calculator") else phosphor.chart_bar,
    icon_style=Styles.Danger,
)
flow.add(
    "3. 外部決済リトライ",
    "0円以下時にPOST送信\nTimeout/Backoff未設定",
    badge_text="S3",
    style=Styles.WarningNeutral,
    badge_style=Styles.Warning,
    icon=phosphor.arrows_clockwise if hasattr(phosphor, "arrows_clockwise") else phosphor.git_branch,
    icon_style=Styles.Warning,
)
flow.add(
    "4. キャッシュ・応答",
    "static生HashMap更新\n未定義呼出を空catch隠蔽",
    badge_text="S4",
    style=Styles.DangerNeutral,
    badge_style=Styles.Danger,
    icon=phosphor.database if hasattr(phosphor, "database") else phosphor.warning,
    icon_style=Styles.Danger,
)
flow.draw(xy=(3, 5), width=140, height=48)

save()
```
