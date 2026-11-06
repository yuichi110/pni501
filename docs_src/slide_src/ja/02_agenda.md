::: block xy=(80, 40) width=1760 height=60
# アジェンダ
:::

::: block xy=(240, 140) width=1440 height=800
```drawlib file=agenda_roadmap.svg
from drawlib.canvas import clear, save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import Roadmap
from drawlib.styles import Styles

clear()
setup(width=144, height=80)

rm = Roadmap(
    style=Styles.Neutral,
    text_style=Styles.DarkBold.patch(text_size=15.5),
    description_style=Styles.Dark.patch(text_size=12.8),
    spine_style=Styles.PrimaryBold,
    badge_style=Styles.PrimaryFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=14.0),
    icon_style=Styles.PrimaryBold,
    direction="vertical",
    curve_bend=-0.16,
    card_shape="pill",
    spacing=3.6,
)
rm.add(
    "1. PNI501 概要",
    "従来のAIプロンプト監査の課題と「決定論ファクト × AI推論」の仕組み",
    badge_text="01",
    icon=phosphor.compass,
    style=Styles.PrimaryNeutral,
)
rm.add(
    "2. 3つの利用シナリオ",
    "開発中の継続的な品質測定・既存ソフトウェア検査・マイグレーション計画作成",
    badge_text="02",
    icon=phosphor.git_branch,
)
rm.add(
    "3. 検査項目一覧",
    "実装済みの品質7項目と、次期拡張「開発ステータス（Git × ガント差分）」構想",
    badge_text="03",
    icon=phosphor.list_checks,
)
rm.add(
    "4. まとめ",
    "エンジニアリングガバナンスの導入効果と今後のロードマップ",
    badge_text="04",
    icon=phosphor.rocket_launch,
)
rm.draw(xy=(12, 5), width=124, height=70)

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
**アジェンダ（本日の構成・全4パート）**
1. **PNI501 概要**：従来の単発 AI プロンプトによるコード監査が抱える「ハルシネーション」「動的挙動の死角」「主観スコアのブレ」という課題を整理し、CLI 主導の Pull-Push ワークフローがどう解決するかを解説します。
2. **3つの利用シナリオ**：新規・進行中開発での「継続的な品質測定」、レガシー資産に対する「ブラックボックス／ホワイトボックス検査」、および刷新プロジェクト向けの「マイグレーション計画策定」の3つの実践シナリオを紹介します。
3. **検査項目一覧**：現在実装済みの7つの検査カテゴリ（構造・複雑度、規約準拠、テスト・カバレッジ、CVE・ライセンス、静的セキュリティ、動的ペネトレーション、移行計画）と、今後追加予定の開発ステータス計測について説明します。
4. **まとめ**：PNI501 導入による定量ガバナンスの確立効果と、今後のエコシステム展開をまとめます。
:::
