# 4. 機械的変換（OpenRewrite Codemod）と手動ブロッカー分離計画

マイグレーション失敗の最大要因は、「AST ツールで 100% 機械的に置換できる変更（`javax.* -> jakarta.*`、JUnit 4 → 5 等）」と「人間の設計判断を伴う変更（循環依存の切断、Redis/PostgreSQL アダプタ設計）」が同一 PR の巨大な Diff に混在することである。本計画では、**OpenRewrite による機械的変換を `PR-04` に完全隔離**し、その前段で手動ビルドブロッカー（`BLK-01〜BLK-03`）を解消する。

```drawlib file=codemod_vs_manual_barchart.png caption="変換領域別 自動 Codemod 適用ファイル数 vs 手動設計変更ファイル数"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.styles import Styles

setup(width=146, height=68, dpi=150)

chart = BarChart(
    axis_line_style=Styles.Neutral,
    grid_style=Styles.NeutralThin,
    axis_text_style=Styles.DarkBold.patch(text_size=8.6),
    value_text_style=Styles.DarkBold.patch(text_size=8.8),
    background_style=Styles.Neutral.patch(shape_r=2.0),
    categories=[
        "Java 21\n構文・POM",
        "Spring Boot 3.4\njakarta.* 移行",
        "JUnit 5\nJupiter 移行",
        "Clean Arch\nPort 分離",
        "PG16 / Redis 7\nAdapter 実装",
        "Dockerfile &\nCI 保安化",
    ],
    orientation="vertical",
    bar_width_ratio=0.64,
    bar_r=1.0,
    width=134,
    height=50,
    title="領域別 OpenRewrite 機械変換対象数 vs 手動アーキテクチャ実装対象数",
    title_style=Styles.DarkBold.patch(text_size=10.0),
)
chart.add_series("OpenRewrite 自動変換 (PR-04)", [6, 6, 1, 0, 0, 0], style=Styles.Success)
chart.add_series("手動リファクタ・新規 Adapter 設計", [1, 1, 1, 5, 3, 2], style=Styles.Primary)
chart.draw(xy=(6, 11))
chart.draw_legend(
    xy=(18.0, 4.2),
    text_style=Styles.DarkBold.patch(text_size=8.8),
    orientation="horizontal",
    item_gap=8.0,
)

save()
```

## OpenRewrite 適用レシピと事前解消必須ブロッカー（BLK-01〜03）

OpenRewrite は「対象プロジェクトがコンパイル可能であること」を前提に型解決 AST 変換を実行し、さらに動的ペネトレーション検証（`web_pentest`：`.pni/pentests/examples/java/api_spring_messy/`）もコンテナ起動成功を前提とするため、**Phase 0（`PR-01`）での最小グリーンビルド復旧**および **Phase 1（`PR-03`）での循環依存切断**を完了してから Phase 2 冒頭（`PR-04`）で下記3レシピを一括実行する。

```drawlib file=codemod_and_blocker_table.png caption="OpenRewrite 自動変換レシピ一覧と事前解消必須ブロッカー (BLK-01 - BLK-04)"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=102, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=8.6),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.0),
    border_style=Styles.NeutralThin,
)
rows = [
    ["種別 / ID", "レシピまたはブロッカー項目", "影響範囲", "実行タイミングと解消手順"],
    [
        "Blocker\nBLK-01/04 [CRIT]",
        "コンテナ・Maven ビルド崩壊 & DAST 停止\n(Java 1.8 vs Spring v61 / HttpClient / tx)",
        "pom.xml /\nGatewayClient",
        "Phase 0 (PR-01): target と BOM を整合させ mvn test と\nweb_pentest 隔離ループバック起動を先に復旧する。",
    ],
    [
        "Blocker\nBLK-02/03 [HIGH]",
        "BillingController <-> BillingManager\n双方向 @Autowired 循環依存",
        "Controller &\nBillingManager",
        "Phase 1 (PR-03): Spring Boot 3.x では循環参照が既定禁止\nのため、Codemod 実行前に逆参照を切断する。",
    ],
    [
        "OpenRewrite\nRecipe 1",
        "org.openrewrite.java.migrate.\nUpgradeToJava21",
        "本番 Java 6 ファイル\n+ pom.xml",
        "Phase 2 (PR-04): Java 21 LTS コンパイラ設定、非推奨 JDK\nAPI 置換、型推論モダナイズを機械適用する。",
    ],
    [
        "OpenRewrite\nRecipe 2",
        "org.openrewrite.java.spring.boot3.\nUpgradeSpringBoot_3_4",
        "本番 Java 6 ファイル\n+ pom.xml",
        "Phase 2 (PR-04): javax.servlet.* -> jakarta.servlet.* 置換、\nSpring Boot 3.4 BOM 更新、コンストラクタ DI 化。",
    ],
    [
        "OpenRewrite\nRecipe 3",
        "org.openrewrite.java.testing.junit5.\nJUnit4to5Migration",
        "BillingManagerTest\n(テスト 1 ファイル)",
        "Phase 2 (PR-04): org.junit.Test を JUnit 5 Jupiter API\nへ機械変換（アサーション拡充は手動 PR で実施）。",
    ],
]
tbl.draw_flexible(
    xy=(3, 99),
    column_widths=[25, 45, 24, 46],
    row_heights=[8.0, 17.5, 17.5, 17.0, 17.5, 17.0],
    data=rows,
)

save()
```
