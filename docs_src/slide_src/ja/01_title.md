::: block xy=(120, 220) width=920 height=640
# PNI501
## AIエージェント主導のソフトウェア品質測定・移行計画基盤

決定論的ファクト抽出 × AI推論で、開発・検査・モダナイズを定量可視化

---

**Project Nemesis Index (v0.1.0)** | Python / Java / PHP 対応
:::

::: block xy=(1040, 150) width=780 height=780
```drawlib file=cover_hero.svg
from drawlib.canvas import clear, save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import CardList, Panel
from drawlib.styles import Colors, Styles

clear()
setup(width=78, height=78)

panel = Panel(
    "4つのコア基盤",
    style=Styles.PrimaryNeutral.patch(shape_fill_color=Colors.White),
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=23.0),
    header_variant="filled",
    header_height=10.8,
    header_align="center",
)
panel.draw(xy=(2, 2), width=74, height=74)
inner_xy, inner_w, inner_h = panel.get_content_box(
    xy=(2, 2), width=74, height=74, padding=(3.8, 3.0)
)

cards = CardList(
    style=Styles.Neutral,
    text_style=Styles.DarkBold.patch(text_size=21.5),
    description_style=Styles.Dark.patch(text_size=18.0),
    badge_shape="rounded_rect",
    badge_style=Styles.PrimaryNeutral,
    icon_style=Styles.PrimaryBold,
    direction="vertical",
    spacing=2.6,
)
cards.add("36 標準規約", "カスケード型ルール管理", icon=phosphor.book_open)
cards.add("決定論アナライザ", "AST・Docker・Trivy・Pentest", icon=phosphor.cpu)
cards.add("SQLite 状態管理", "Pull-Push 厳格検証ループ", icon=phosphor.database)
cards.add("7章ベクターPDF", "7軸スコア & 移行計画出力", icon=phosphor.file_pdf)
cards.draw(xy=inner_xy, width=inner_w, height=inner_h)

save()
```
:::

::: note
**表紙（PNI501 プレゼンテーション導入）**
- 本日は **PNI501（Project Nemesis Index）** をご紹介します。PNI501 は、AI エージェントと決定論的静的・動的解析ツールを融合させた、ソフトウェア品質測定・セキュリティ検査・モダナイゼーション移行計画基盤です。
- 右側のパネルに示した **4つのコア基盤** が PNI501 の特徴を支えています：
  1. **36 標準規約**：共通ルールと言語固有ルール（Python / Java / PHP）をカスケード統合し、プロジェクト独自の上書きにも対応します。
  2. **決定論アナライザ**：AST 解析、隔離 Docker コンテナ上でのテスト実行、Trivy 脆弱性スキャン、Web ペネトレーションテストを CLI が確実に実行します。
  3. **SQLite 状態管理**：AI エージェントが `get-action` / `push-action` でステップを進める Pull-Push 型の状態機械により、ハルシネーションや手順飛ばしを防止します。
  4. **7章ベクターPDF**：Drawlib を活用し、7軸定量グレード（S〜D）や移行ロードマップを図解入りの高品質な A4 ベクター PDF / HTML レポートとして自動出力します。
:::
