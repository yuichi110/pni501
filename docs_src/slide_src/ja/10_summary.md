::: block xy=(80, 40) width=1760 height=60
# まとめ — PNI501 が実現するエンジニアリングガバナンス
:::

::: block xy=(80, 135) width=1760 height=810
```drawlib file=summary_cards.svg
from drawlib.canvas import clear, save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import CardList, ChevronProcess, Panel
from drawlib.styles import Styles

clear()
setup(width=176, height=81)

p1 = Panel(
    "1. 根拠ある定量品質評価",
    icon=phosphor.shield_check,
    icon_style=Styles.WhiteBold,
    header_variant="filled",
    header_height=9.0,
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=15.0),
    style=Styles.WhiteBordered.patch(shape_r=2.0),
)
p1.draw(xy=(3, 28), width=54, height=50)

c1 = CardList(
    style=Styles.PrimaryNeutral.patch(shape_r=1.5),
    text_style=Styles.DarkBold.patch(text_size=12.2),
    description_style=Styles.Dark.patch(text_size=10.8),
    badge_shape="none",
    spacing=2.5,
)
c1.add("決定論ツールで死角を排除", "AST・Docker・Trivy・Pentest統合")
c1.add("実在パス照合で幻覚ゼロ", "スキーマ検証と厳格な証跡チェック")
c1.draw(xy=(5.5, 31.5), width=49, height=34.5)

p2 = Panel(
    "2. 3シナリオを一気通貫",
    icon=phosphor.arrows_merge,
    icon_style=Styles.PrimaryBold,
    header_variant="filled",
    header_height=9.0,
    header_style=Styles.PrimaryNeutral,
    text_style=Styles.DarkBold.patch(text_size=15.0),
    style=Styles.WhiteBordered.patch(shape_r=2.0),
)
p2.draw(xy=(61, 28), width=54, height=50)

c2 = CardList(
    style=Styles.Neutral.patch(shape_r=1.5),
    text_style=Styles.DarkBold.patch(text_size=12.2),
    description_style=Styles.Dark.patch(text_size=10.8),
    badge_shape="none",
    spacing=2.5,
)
c2.add("継続測定と既存資産の検査", "日常の品質ゲートから棚卸しまで")
c2.add("検査結果を移行計画へ継承", "定量スコアと証跡を計画へ直結")
c2.draw(xy=(63.5, 31.5), width=49, height=34.5)

p3 = Panel(
    "3. 品質 × 進捗の統合へ",
    icon=phosphor.chart_line_up,
    icon_style=Styles.DarkBold,
    header_variant="filled",
    header_height=9.0,
    header_style=Styles.SecondaryNeutral,
    text_style=Styles.DarkBold.patch(text_size=15.0),
    style=Styles.WhiteBordered.patch(shape_r=2.0),
)
p3.draw(xy=(119, 28), width=54, height=50)

c3 = CardList(
    style=Styles.Neutral.patch(shape_r=1.5),
    text_style=Styles.DarkBold.patch(text_size=12.2),
    description_style=Styles.Dark.patch(text_size=10.8),
    badge_shape="none",
    spacing=2.5,
)
c3.add("現行7項目で多角スコア測定", "設計・品質・型・テスト等を網羅")
c3.add("開発ステータス検査へ拡張", "【構想】Git×ガント差分を統合")
c3.draw(xy=(121.5, 31.5), width=49, height=34.5)

steps = ChevronProcess(
    style=Styles.Neutral,
    text_style=Styles.DarkBold.patch(text_size=13.2),
    description_style=Styles.Dark.patch(text_size=11.2),
    spacing=2.0,
    flat_left_end=True,
)
steps.add("Step 1: pni init", description="規約・ワークフロー配置", style=Styles.Neutral)
steps.add("Step 2: workflows start", description="AI × CLI 定量検査", style=Styles.PrimaryNeutral)
steps.add(
    "Step 3: report build",
    description="7章ベクターPDF共有",
    style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=13.2),
    description_style=Styles.White.patch(text_size=11.2),
)
steps.draw(xy=(3, 4.5), width=170, height=17.5)

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
- 本日のまとめです。PNI501 は3つの柱でエンジニアリングガバナンスを高度化します。
- 1つ目は**根拠ある定量品質評価**。決定論的な静的解析・テスト・セキュリティ監査ツールとAIエージェントを組み合わせ、実在パス照合によってハルシネーションを排除します。
- 2つ目は**3つのユースケースの一気通貫**。日々の継続的な品質測定、既存レガシー資産の棚卸し検査、そして検査データを引き継いだ安全なモダナイゼーション移行計画作成を一つの基盤で支援します。
- 3つ目は**品質と進捗の統合**。実装済みの品質7項目に加え、今後はGitコミット状況とガントチャート差分を掛け合わせた「開発ステータス」検査へと拡張していきます。
- 導入は下段の3ステップ（`pni init` → `workflows start` → `report build`）で即座に開始でき、経営層・開発チーム双方に共有可能な7章構成のベクターPDFレポートを出力できます。
:::
