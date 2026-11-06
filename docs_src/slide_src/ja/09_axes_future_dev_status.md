::: block xy=(80, 40) width=1760 height=60
# 検査項目一覧②：8項目目「開発ステータス」【未実装・構想】
:::

::: block xy=(80, 155) width=630 height=770
## 品質 × 進捗の統合モニタリングへ

> **Status: 未実装（次期ロードマップ構想）**

- **Git コミット動態解析**: 変更集中・停滞・チャーン急増を検知
- **ガントチャート進捗差分**: 計画マイルストーンと実装状況を突合
- **無理な駆け込みの予兆検知**: 遅延回復時の品質急落リスクを警告
:::

::: block xy=(750, 135) width=1090 height=810
```drawlib file=dev_status_gantt.svg
from drawlib.canvas import clear, save, setup
from drawlib.charts.gantt import GanttChart
from drawlib.icons import phosphor
from drawlib.smartarts import CardList, Panel
from drawlib.styles import Styles

clear()
setup(width=109, height=81)

panel = Panel(
    "【構想】Git コミット × ガント差分診断（未実装）",
    header_variant="filled",
    header_height=9.0,
    header_style=Styles.SecondaryNeutral,
    text_style=Styles.DarkBold.patch(text_size=17.0),
    style=Styles.MutedDashed.patch(shape_r=2.0),
)
panel.draw(xy=(1.5, 1.5), width=106, height=78)

gantt = GanttChart(
    columns=["W1", "W2", "W3", "W4", "W5", "W6", "W7", "W8"],
    label_width=24.0,
    row_height=6.6,
    header_height=6.4,
    axis_line_style=Styles.Muted,
    axis_text_style=Styles.DarkBold.patch(text_size=15.0),
    header_style=Styles.PrimaryNeutral,
    grid_style=Styles.MutedThin,
    progress_text_style=Styles.WhiteBold.patch(text_size=13.8),
)
gantt.add_task("認証基盤", 0.0, 2.5, style=Styles.PrimaryFlat, progress=1.0)
gantt.add_task("決済API", 2.0, 5.5, style=Styles.DangerFlat, progress=0.45)
gantt.add_task(
    "管理画面",
    4.0,
    7.0,
    style=Styles.PrimaryNeutral,
    progress=0.20,
    progress_text_style=Styles.DarkBold.patch(text_size=13.5),
)
gantt.add_task("結合テスト", 6.0, 8.0, style=Styles.Neutral, progress=0.0)
gantt.add_marker(
    5.0,
    style=Styles.AccentBold,
    label="現在",
    label_style=Styles.WhiteBold.patch(text_size=12.8),
)
gantt.draw(xy=(5.0, 29.0), width=99.0, height=39.0)

flow = CardList(
    direction="horizontal",
    show_arrows=True,
    spacing=3.0,
    style=Styles.Neutral.patch(shape_r=1.5),
    text_style=Styles.DarkBold.patch(text_size=15.8),
    description_style=Styles.Dark.patch(text_size=14.2),
    badge_style=Styles.WhiteBordered,
    icon_style=Styles.PrimaryBold,
    arrow_style=Styles.PrimaryBold,
)
flow.add("Git コミット", "決済APIチャーン急増", icon=phosphor.git_commit)
flow.add(
    "ガント計画差分",
    "進捗 -35% 遅延",
    icon=phosphor.calendar_x,
    style=Styles.PrimaryNeutral.patch(shape_r=1.5),
)
flow.add(
    "統合リスク診断",
    "駆け込み品質低下警告",
    icon=phosphor.warning,
    style=Styles.DangerNeutral.patch(shape_r=1.5),
    icon_style=Styles.DangerBold,
)
flow.draw(xy=(5.0, 5.0), width=99.0, height=19.5)

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
- 続いて8つ目の検査項目として構想しているのが**「開発ステータス」検査**です。**※この機能は現時点では未実装であり、今後の拡張ロードマップ構想です。**
- コードの静的な品質スナップショットだけでなく、「プロジェクトがいま順調に進んでいるか、無理な駆け込みが起きていないか」を統合診断することを目指しています。
- 具体的には、**Gitのコミット履歴・コードチャーン（変更集中や停滞）**と、**ガントチャート上の計画マイルストーン**を突合します。
- 右図の例のように、Week 5 時点で「決済API」の進捗が遅れつつコミットチャーンが急増している場合、「納期直前の駆け込み実装によってテスト省略や品質急落が起きるリスク」を早期警告できるよう拡張していく計画です。
:::
