::: block xy=(80, 40) width=1760 height=60
# 検査項目一覧①：現在の品質7項目【実装済み】
:::

::: block xy=(80, 135) width=820 height=810
```drawlib file=seven_axes_list.svg
from drawlib.canvas import clear, save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import CardList, Panel
from drawlib.styles import Styles

clear()
setup(width=82, height=81)

panel = Panel(
    "実装済み 7評価軸（各 0–100点）",
    header_variant="filled",
    header_height=9.0,
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=20.5),
    style=Styles.WhiteBordered.patch(shape_r=2.0),
)
panel.draw(xy=(1.5, 1.5), width=79, height=78)

cards = CardList(
    style=Styles.Neutral.patch(shape_r=1.5),
    text_style=Styles.DarkBold.patch(text_size=18.5),
    description_style=Styles.Dark.patch(text_size=16.2),
    badge_style=Styles.WhiteBordered,
    icon_style=Styles.PrimaryBold,
    spacing=1.1,
)
cards.add("Architecture", "層分離・循環依存・責務境界", icon=phosphor.git_fork, style=Styles.PrimaryNeutral.patch(shape_r=1.5))
cards.add("Code Quality", "複雑度・重複排除・保守性", icon=phosphor.code)
cards.add("Typing", "型注釈率・静的型安全性", icon=phosphor.brackets_angle, style=Styles.PrimaryNeutral.patch(shape_r=1.5))
cards.add("Testing", "隔離テスト実行・カバレッジ", icon=phosphor.flask)
cards.add("Dependencies", "Lockfile健全性・依存鮮度", icon=phosphor.package, style=Styles.PrimaryNeutral.patch(shape_r=1.5))
cards.add("Security", "CVE脆弱性・秘密情報・Pentest", icon=phosphor.shield_check)
cards.add("Documentation", "README・仕様書・運用手順", icon=phosphor.book_open, style=Styles.PrimaryNeutral.patch(shape_r=1.5))
cards.draw(xy=(4.0, 3.2), width=74, height=67.5)

save()
```
:::

::: block xy=(930, 135) width=910 height=810
```drawlib file=seven_axes_radar.svg
from drawlib.canvas import clear, save, setup
from drawlib.charts.radar import RadarChart, Series
from drawlib.shapes import rectangle
from drawlib.styles import Styles

clear()
setup(width=91, height=81)

rectangle((45.5, 40.5), width=88, height=78, style=Styles.WhiteBordered.patch(shape_r=2.0))

chart = RadarChart(
    categories=[
        "Architecture",
        "Code Quality",
        "Typing",
        "Testing",
        "Dependencies",
        "Security",
        "Docs",
    ],
    min_value=0,
    max_value=100,
    levels=5,
    radius=20.2,
    title="実測ベンチマーク比較（Clean vs Legacy）",
    title_style=Styles.DarkBold.patch(text_size=19.5),
    axis_line_style=Styles.Muted,
    axis_text_style=Styles.DarkBold.patch(text_size=17.0),
    grid_style=Styles.MutedThin,
    scale_text_style=Styles.Dark.patch(text_size=14.0),
)
_clean_series: Series = chart.add_series(
    "Clean実装例 (95 / S)",
    [98, 96, 99, 93, 95, 94, 91],
    style=Styles.PrimaryBold,
    fill_alpha=0.25,
    line_width=3.0,
)
_legacy_series: Series = chart.add_series(
    "Legacy例 (20 / D)",
    [22, 24, 26, 12, 18, 12, 28],
    style=Styles.DangerBold,
    fill_alpha=0.20,
    line_width=2.6,
    line_style="dashed",
)
chart.draw(xy=(5.5, 13.5), width=80, height=62)
chart.draw_legend(
    xy=(8.5, 5.5),
    text_style=Styles.DarkBold.patch(text_size=17.0),
    orientation="horizontal",
    item_gap=5.5,
)

save()
```
:::

::: block xy=(80, 1010) width=1580 height=30 font_size=14px
*PNI501 — AIエージェント主導のソフトウェア品質測定・移行計画基盤*
:::

::: block xy=(1700, 1010) width=140 height=30
```drawlib file=page.svg
from drawlib.slide import draw_page_number

draw_page_number()
```
:::

::: note
- 現在 PNI501 に**実装済み**の検査項目は、こちらの **7つの品質評価軸**（各0〜100点）です。
- 左側のパネルにある通り、**Architecture（設計・層分離）**、**Code Quality（複雑度・保守性）**、**Typing（静的型安全性）**、**Testing（隔離テスト実行・カバレッジ）**、**Dependencies（Lockfileと依存鮮度）**、**Security（CVE脆弱性・秘密情報・必要に応じたPentest）**、**Documentation（README・仕様書・運用手順）**を網羅しています。
- 右側のレーダーチャートは、PNI501 の実測ベンチマーク結果です。クリーンなリファレンス実装（`py_lib_clean`、総合95点・Sランク）と、技術的負債が蓄積したレガシーAPI（`py_api_legacy_messy`、総合20点・Dランク）のどこに弱点があるかを一目で定量比較できます。
:::
