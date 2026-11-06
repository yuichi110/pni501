::: block xy=(80, 40) width=1760 height=60
# 利用シナリオ①：開発中ソフトウェアの継続的な品質測定
:::

::: block xy=(80, 160) width=640 height=760
## 開発の原点：負債を溜めない定点観測

- **スプリント定点測定**: `quick_check` で品質低下を即検知
- **チーム規約の自動浸透**: `.pni/rules/` で設計標準を維持
- **負債の早期解消**: 深刻化する前に P0/P1 を特定
:::

::: block xy=(760, 140) width=1080 height=800
```drawlib file=continuous_trend.svg
from drawlib.canvas import clear, save, setup
from drawlib.charts.line import LineChart, Series
from drawlib.styles import Colors, Styles

clear()
setup(width=108, height=80)

chart = LineChart(
    categories=["Sprint 1", "Sprint 2", "Sprint 3", "Sprint 4", "Sprint 5"],
    title="スプリント進行に伴う品質スコア推移（イメージ）",
    title_style=Styles.DarkBold.patch(text_size=18.5),
    axis_line_style=Styles.Muted,
    axis_text_style=Styles.DarkBold.patch(text_size=15.2),
    grid_style=Styles.MutedThin,
    value_text_style=Styles.DarkBold.patch(text_size=14.5),
    background_style=Styles.Neutral.patch(shape_fill_color=Colors.White, shape_r=2.2),
)
chart.configure_y_axis(min_value=0, max_value=100, tick_step=20)

s_pni: Series = chart.add_series(
    "PNI501 継続測定あり",
    [72, 80, 86, 91, 94],
    style=Styles.PrimaryBold,
    line_width=3.2,
    point_size=1.15,
)
s_debt: Series = chart.add_series(
    "品質検査なし（負債蓄積）",
    [72, 62, 49, 36, 24],
    style=Styles.DangerDashedBold,
    line_width=2.8,
    line_style="dashed",
    point_shape="square",
    point_size=1.05,
)

chart.draw(xy=(5, 15), width=98, height=59)
chart.draw_legend(
    xy=(13, 5.5),
    text_style=Styles.DarkBold.patch(text_size=15.2),
    orientation="horizontal",
    item_gap=7.0,
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
- PNI501 のもともとの開発目的は、**新規・継続開発中のソフトウェアにおいて技術的負債を溜め込まないための定点観測基盤**です。
- 機能追加が優先される通常のスプリント開発では、気づかないうちに循環依存・複雑度肥大・型やテストの欠落が進行し、後から大規模な手戻りが発生しがちです（右グラフの赤破線）。
- PNI501 をスプリントごと・マイルストーンごとに回すことで、`quick_check` による軽量なヘルスチェックやフル診断を通じて品質低下を即座に検知できます。
- `.pni/rules/` にプロジェクト固有の設計標準やコーディング規約を定義しておけば、AI エージェントが一貫した基準でレビュー・採点するため、チーム全体に規約が自然に浸透します。
- 問題が小さなうちに P0 / P1 の優先度付き改善項目として特定・解消できるため、開発速度を落とさずに高い品質スコア（S / A グレード）を維持・向上できます（右グラフの青実線）。
:::
