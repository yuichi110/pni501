::: block xy=(80, 40) width=1760 height=60
# 利用シナリオ②：既存・レガシーソフトウェアの品質検査
:::

::: block xy=(80, 160) width=640 height=760
## ブラックボックス資産の多角診断

- **仕様書不要の全体把握**: 3視点で現行アーキテクチャを復元
- **実行時＆脆弱性の可視化**: Docker・Trivy・Pentest で死角排除
- **改修優先度の定量化**: ホットスポット密度と P0〜P2 算出
:::

::: block xy=(760, 140) width=1080 height=800
```drawlib file=legacy_audit_arch.svg
from drawlib.canvas import clear, save, setup
from drawlib.diagrams.architecture import ArchitectureDiagram, Node, NodeGroup, PhosphorIcon
from drawlib.styles import Colors, Styles

clear()
setup(width=108, height=80)

diag = ArchitectureDiagram(
    node_style=Styles.DarkBold,
    node_text_style=Styles.DarkBold.patch(text_size=16.5, text_line_spacing=1.32),
    edge_style=Styles.PrimaryBold,
    edge_text_style=Styles.Dark.patch(text_size=14.5),
    width=108,
    height=80,
)

repo = diag.add(
    Node(
        text="既存リポジトリ\n(Python / Java / PHP)",
        width=68.0,
        height=14.6,
        icon=PhosphorIcon.FOLDER_OPEN,
        icon_size=4.8,
        style=Styles.DarkBold,
        card_style=Styles.WhiteBordered.patch(shape_line_color=Colors.Muted, shape_r=2.0),
    ),
    xy=(54.0, 71.5),
)

layers = diag.add(
    NodeGroup(
        title="4層の決定論＆動的インスペクション",
        width=98.0,
        height=38.8,
        style=Styles.WhiteBordered.patch(
            shape_line_color=Colors.Muted,
            shape_line_style="dashed",
            shape_line_width=1.4,
            shape_r=2.2,
        ),
        text_style=Styles.PrimaryBold.patch(text_size=16.8, halign="left", valign="top"),
    ),
    xy=(5.0, 22.0),
)

layers.add(
    Node(
        text="AST 構造・複雑度",
        width=44.5,
        height=12.8,
        icon=PhosphorIcon.TREE_STRUCTURE,
        icon_size=4.6,
        style=Styles.DarkBold,
        card_style=Styles.Neutral.patch(shape_r=1.8),
    ),
    xy=(25.5, 25.0),
)
layers.add(
    Node(
        text="隔離 Docker テスト",
        width=44.5,
        height=12.8,
        icon=PhosphorIcon.CUBE,
        icon_size=4.6,
        style=Styles.DarkBold,
        card_style=Styles.Neutral.patch(shape_r=1.8),
    ),
    xy=(72.5, 25.0),
)
layers.add(
    Node(
        text="Trivy CVE・秘密情報",
        width=44.5,
        height=12.8,
        icon=PhosphorIcon.SHIELD_CHECK,
        icon_size=4.6,
        style=Styles.PrimaryBold,
        card_style=Styles.PrimaryNeutral.patch(shape_r=1.8),
    ),
    xy=(25.5, 8.8),
)
layers.add(
    Node(
        text="Web Pentest 診断",
        width=44.5,
        height=12.8,
        icon=PhosphorIcon.BUG,
        icon_size=4.6,
        style=Styles.SecondaryBold,
        card_style=Styles.SecondaryNeutral.patch(shape_r=1.8),
    ),
    xy=(72.5, 8.8),
)

output = diag.add(
    Node(
        text="7軸定量スコア & 7章診断PDF\n(S〜D グレード / P0〜P2 計画)",
        width=84.0,
        height=14.6,
        icon=PhosphorIcon.FILE_PDF,
        icon_size=5.0,
        style=Styles.WhiteBold,
        text_style=Styles.WhiteBold.patch(text_size=16.0, text_line_spacing=1.32),
        card_style=Styles.PrimaryFlat.patch(shape_r=2.0),
    ),
    xy=(54.0, 9.6),
)

diag.connect(repo, layers, padding=0.7)
diag.connect(layers, output, padding=0.7)

diag.draw(xy=(0, 0))
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
- 2つ目の主要シナリオは、引き継ぎ案件やドキュメントが失われた**既存・レガシーソフトウェア（ブラックボックス資産）の品質検査**です。Python・Java・PHP などのマルチ言語リポジトリに対応しています。
- 仕様書が存在しなくても、PNI501 は `purpose_and_stack`（目的・技術構成）、`layers_and_modules`（レイヤ・責務境界）、`flows_and_state`（データフロー・状態管理）の**3視点アーキテクチャ理解ステップ**を通じて、実在ファイルパスに裏付けられた現行設計図を自動復元します。
- さらに右図中央の4層インスペクションにより、静的解析だけでは見抜けない死角を排除します：(1) AST による構造・循環的複雑度・依存グラフ解析、(2) 隔離 Docker コンテナ内でのビルド・テスト実行検証、(3) Trivy による既知 CVE とハードコード秘密情報の検出、(4) ループバック起動した Web アプリへの `httpx` ペネトレーションテストです。
- 最終成果物として、**7軸の定量スコア（S〜D グレード）**とホットスポット密度分析、そして経営層・開発現場の双方がそのまま意思決定に使える**7章構成のビジュアル診断 PDF レポート（P0〜P2 改善計画付き）**を出力します。
:::
