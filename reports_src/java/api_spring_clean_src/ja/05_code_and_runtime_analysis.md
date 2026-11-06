# 5. 詳細分析：コード品質・テスト・動的検証

本章では、Java AST 静的解析によって計測されたモジュール単位のコード品質・SIG 保守性・ジェネリクス型安全性指標と、隔離 Docker コンテナ（Java 21 / Maven 3.9.9）上で実行されたマルチステージ `Dockerfile` ビルド、オフライン JUnit 5 単体テスト、JaCoCo 実測カバレッジ、および Spring Boot 起動スモーク検証の結果を詳細に分析する。

```drawlib file=code_module_quality_heatmap.png caption="モジュール × 品質ディメンション適合度マトリクス (0 - 100%)"
from drawlib.canvas import save, setup
from drawlib.charts.heatmap import HeatmapChart
from drawlib.styles import Styles

setup(width=146, height=70, dpi=150)

hm = HeatmapChart(
    min_style=Styles.DangerNeutral,
    max_style=Styles.Primary,
    x_categories=["import衛生", "厳格型安全", "Javadoc率", "JaCoCo行網羅", "JaCoCo分岐網羅"],
    y_categories=[
        "SupplierRestClient (43)",
        "InventoryApplication (12)",
        "InventoryController (33)",
        "StockItem (22)",
        "InventoryService (43)",
        "ReorderPolicy (15)",
        "SupplierProperties (12)",
    ],
    axis_line_style=Styles.Neutral,
    axis_text_style=Styles.DarkBold.patch(text_size=9.0),
    value_text_style=Styles.DarkBold.patch(text_size=9.2),
    background_style=Styles.Neutral.patch(shape_r=2.0),
    width=114,
    height=56,
    min_value=0.0,
    max_value=100.0,
    cell_gap=0.8,
    cell_r=0.8,
    value_format=lambda v: f"{v:.1f}%",
    title="全7モジュール 静的品質・JaCoCo動的カバレッジ適合マトリクス",
    title_style=Styles.DarkBold.patch(text_size=10.5),
)
hm.add_row("SupplierRestClient (43)", [100.0, 100.0, 100.0, 30.4, 0.0])
hm.add_row("InventoryApplication (12)", [100.0, 100.0, 100.0, 33.3, 100.0])
hm.add_row("InventoryController (33)", [100.0, 100.0, 100.0, 62.5, 100.0])
hm.add_row("StockItem (22)", [100.0, 100.0, 100.0, 71.4, 50.0])
hm.add_row("InventoryService (43)", [100.0, 100.0, 100.0, 89.5, 50.0])
hm.add_row("ReorderPolicy (15)", [100.0, 100.0, 100.0, 100.0, 100.0])
hm.add_row("SupplierProperties (12)", [100.0, 100.0, 100.0, 100.0, 100.0])
hm.draw(xy=(6, 6))
hm.draw_colorbar(
    xy=(126, 12),
    text_style=Styles.Dark.patch(text_size=9.0),
    length=42.0,
    thickness=2.6,
    orientation="vertical",
    label="適合率(%)",
)

save()
```

## 静的コード品質・SIG 保守性・並行処理安全性の評価

- **SIG 保守性・型安全・Javadoc 衛生**: 全7ソースファイル合計 `180` LOC（最大は `InventoryService.java` と `SupplierRestClient.java` の各 `43` LOC）と極めて凝集度が高く、複雑関数（`0` 件）・過剰引数（`0` 件）・ワイルドカード import（`0` 件）・raw 型（`0` 件）・Javadoc 欠落（`0` 件）すべてで `100.0%` 適合を達成している。
- **並行リクエスト時の競合状態（Check-Then-Act）**: `InventoryService.reserveStock`（65〜70行目）では `inventoryStore.get(sku)` で取得した `StockItem` に対して `withAdditionalReservation` を計算した後に `inventoryStore.put(sku, updated)` を呼び出している。同一 SKU へ同時リクエストが到達した際、2スレッドが同じ `existing` を読み取って片方の引当を上書き消失させる競合窓が存在するため、`inventoryStore.compute(...)` によるアトミック遷移への改修が必要である。
- **Spring 設定検証・例外ハンドリング**: `SupplierProperties` は `@ConfigurationProperties(prefix = "inventory.supplier")` の不変 `record` だが `@Validated` が未付与であり、また `InventoryController` には未知 SKU（`IllegalArgumentException`）や在庫不足（`IllegalStateException`）を HTTP `404` / `409` へ写像する `@RestControllerAdvice` が未実装である。

## コンテナ動的検証（マルチステージビルド・オフライン JUnit 5・JaCoCo・起動検証 & DAST 連携）

PNI の `run_check` により、リポジトリ同梱マルチステージ `Dockerfile` のクリーンビルド（`44.38s`）および Java 21 ハーネスビルド（`1.03s`、キャッシュ済レイヤー活用）を実行し、ネットワーク完全遮断（`-o` かつ `--network=none`）環境下で JUnit 5 単体テスト（`2 / 2` 件合格、`11.04s`）と JaCoCo `0.8.12` カバレッジ計測を実施した。さらに `InventoryApplication` の起動スモークチェックでは `4.51s` でポート `18080`（`tcp://127.0.0.1:18080`）への正常バインドが確認された。加えて、後続の `web_pentest`（`.pni/pentests/examples/java/api_spring_clean/`、`7.19s`）によるライブ HTTP 検証でも不正型パラメータ `quantity=not-an-int` の `400 Bad Request` 拒否が動作確認された一方、単体テスト未網羅であった `InventoryService.java:67` の未知 SKU 例外パスがライブ HTTP 上で未処理 `500`（`CWE-755`）を返すことが実証された（詳細は第6章参照）。

```drawlib file=runtime_verification_breakdown.png caption="コンテナ動的検証KPIと全7モジュール JaCoCo 実測カバレッジ内訳"
from drawlib.canvas import save, setup
from drawlib.smartarts import KpiCards, Table
from drawlib.styles import Styles

setup(width=146, height=82, dpi=150)

kpis = KpiCards(
    style=Styles.Neutral,
    metric_style=Styles.SuccessBold.patch(text_size=12.0),
    text_style=Styles.DarkBold.patch(text_size=9.4),
    description_style=Styles.Neutral.patch(text_size=8.8),
    accent_position="top_bar",
    metric_layout="top_stack",
    spacing=2.5,
)
kpis.add(
    "PASSED (44.4s)",
    "マルチステージ Dockerfile",
    "ハーネスビルドも合格 (1.03s)",
    accent_style=Styles.Success,
)
kpis.add(
    "2 / 2 PASS",
    "オフライン JUnit 5",
    "--network=none / -o (11.0s)",
    accent_style=Styles.Success,
)
kpis.add(
    "62.7% / 50.0%",
    "JaCoCo 行 / 分岐網羅率",
    "42 / 67 命令列 (目標85%/75%)",
    accent_style=Styles.Warning,
    metric_style=Styles.WarningBold.patch(text_size=12.0),
)
kpis.add(
    "BOUND (4.51s)",
    "Spring 起動 & DAST (12/16)",
    "127.0.0.1起動合格・Actuator無",
    accent_style=Styles.Primary,
    metric_style=Styles.PrimaryBold.patch(text_size=12.0),
)
kpis.draw(xy=(3, 60), width=140, height=19, columns=4)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=9.2),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.3),
    border_style=Styles.NeutralThin,
)
rows = [
    ["対象モジュール (行網羅率昇順)", "行網羅率", "分岐網羅率", "実行 / 総行数", "未実行行 (missing_lines_preview)"],
    ["client/SupplierRestClient.java", "30.4%", "0.0%", "7 / 23", "45-55行 (requestRestock 通信・例外処理全体)"],
    ["InventoryApplication.java", "33.3%", "N/A", "1 / 3", "21, 22行 (SpringApplication.run エントリ)"],
    ["api/InventoryController.java", "62.5%", "N/A", "5 / 8", "40, 41, 42行 (getItem 200/404 応答パス)"],
    ["domain/StockItem.java", "71.4%", "50.0%", "5 / 7", "40, 43行 (数量<=0・在庫不足の例外送出分岐)"],
    ["service/InventoryService.java", "89.5%", "50.0%", "17 / 19", "54行 (findBySku), 67行 (未知SKU例外分岐)"],
    ["domain/ReorderPolicy.java", "100.0%", "100.0%", "5 / 5", "なし (発注点判定・補充量計算の全分岐網羅)"],
    ["config/SupplierProperties.java", "100.0%", "N/A", "2 / 2", "なし (record コンストラクタ・defaults 網羅)"],
]
tbl.draw_flexible(
    xy=(3, 57.5),
    column_widths=[38, 14, 15, 19, 54],
    row_heights=[6.8] + [6.8] * 7,
    data=rows,
)

save()
```
