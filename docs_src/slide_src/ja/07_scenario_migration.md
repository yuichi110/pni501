::: block xy=(80, 40) width=1760 height=60
# 利用シナリオ③：マイグレーション計画の作成
:::

::: block xy=(80, 125) width=1760 height=70
**品質検査ファクト（`based_on`）をそのまま継承し、安全ゲート付きの段階的移行計画・PR分割WBSを生成**
:::

::: block xy=(80, 210) width=1760 height=730
```drawlib file=migration_plan_flow.svg
from drawlib.canvas import clear, save, setup
from drawlib.diagrams.architecture import ArchitectureDiagram, Node, PhosphorIcon
from drawlib.smartarts import CardList
from drawlib.styles import Colors, Styles

clear()
setup(width=176, height=73)

diag = ArchitectureDiagram(
    node_style=Styles.DarkBold,
    node_text_style=Styles.DarkBold.patch(text_size=12.6, text_line_spacing=1.35),
    edge_style=Styles.PrimaryBold,
    edge_text_style=Styles.Dark.patch(text_size=11.5),
    width=176,
    height=73,
)

stages = [
    (
        22.5,
        "1. 品質検査の継承\n(based_on: <audit_id>)",
        "As-Is 構造・7軸スコア\n脆弱性ファクトを再利用",
        PhosphorIcon.DATABASE,
        Styles.PrimaryBold,
        Styles.DarkBold.patch(text_size=12.6, text_line_spacing=1.35),
        Styles.PrimaryNeutral.patch(shape_r=2.0),
    ),
    (
        66.2,
        "2. トポロジカル依存解析\n(migration_analyze)",
        "Wave 1〜4 移行順序\n循環依存(SCC)切断点",
        PhosphorIcon.GIT_BRANCH,
        Styles.DarkBold,
        Styles.DarkBold.patch(text_size=12.6, text_line_spacing=1.35),
        Styles.Neutral.patch(shape_r=2.0),
    ),
    (
        109.8,
        "3. 仕様 vs バグ判定ログ\n(Hyrumの法則 DEC-XX)",
        "暗黙契約の維持・修正を\n人間と合意してピン留め",
        PhosphorIcon.SCALES,
        Styles.SecondaryBold,
        Styles.DarkBold.patch(text_size=12.6, text_line_spacing=1.35),
        Styles.SecondaryNeutral.patch(shape_r=2.0),
    ),
    (
        153.5,
        "4. 実行計画 JSON & PDF\n(Phase 0〜4 / PR WBS)",
        "安全検証ゲート付き\nPR単位の作業分解書",
        PhosphorIcon.FILE_PDF,
        Styles.WhiteBold,
        Styles.WhiteBold.patch(text_size=12.5, text_line_spacing=1.35),
        Styles.PrimaryFlat.patch(shape_r=2.0),
    ),
]

stage_nodes = []
for cx, title_txt, desc_txt, icon_enum, icon_st, txt_st, card_st in stages:
    s_node = diag.add(
        Node(
            text=title_txt,
            width=37.5,
            height=22.5,
            icon=icon_enum,
            icon_size=5.4,
            style=icon_st,
            text_style=txt_st,
            card_style=card_st,
        ),
        xy=(cx, 58.5),
    )
    diag.add(
        Node(
            text=desc_txt,
            width=37.5,
            height=12.0,
            text_style=Styles.Dark.patch(text_size=11.5, text_line_spacing=1.35),
            card_style=Styles.Neutral.patch(shape_fill_color=Colors.White, shape_r=1.6),
        ),
        xy=(cx, 39.0),
    )
    stage_nodes.append(s_node)

for idx in range(len(stage_nodes) - 1):
    diag.connect(stage_nodes[idx], stage_nodes[idx + 1], padding=0.6)

diag.draw(xy=(0, 0))

archetypes = CardList(
    style=Styles.Neutral,
    text_style=Styles.DarkBold.patch(text_size=13.2),
    description_style=Styles.Dark.patch(text_size=11.8),
    badge_shape="circle",
    badge_style=Styles.PrimaryNeutral,
    badge_text_style=Styles.PrimaryBold.patch(text_size=12.5),
    direction="horizontal",
    spacing=4.0,
)
archetypes.add(
    "アーキテクチャ再構築 (同一言語モダナイズ)",
    description="例: Legacy Spring -> Clean Hexagonal (段階的PR)",
    badge_text="A",
    style=Styles.Neutral,
)
archetypes.add(
    "クロススタック刷新 (言語・FW移行)",
    description="例: Legacy PHP -> Laravel / Modern API (Strangler Fig)",
    badge_text="B",
    style=Styles.PrimaryNeutral,
    badge_style=Styles.PrimaryNeutral.patch(shape_fill_color=Colors.White),
)
archetypes.draw(xy=(4.0, 4.0), width=168.0, height=23.0)

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
- 3つ目のシナリオは、品質検査の次のステップとなる**段階的マイグレーション計画の作成**です。コードを一から再調査するのではなく、完了済みの品質検査ワークフロー（`based_on: <audit_id>`）の As-Is 構造・7軸スコア・脆弱性ファクトを SQLite ステートからそのまま継承します。
- ステージ2の `migration_analyze` では、内部インポートグラフのトポロジカルソートと強連結成分（SCC）検出を実行し、どこから手を付ければ波及範囲を最小化できるか（Wave 1〜4 の移行順序と循環依存の切断点）を決定論的に算出します。
- ステージ3では **Hyrum の法則**（既存のバグや暗黙の挙動に外部クライアントが依存しているリスク）に対処するため、AI が勝手に仕様変更せず、暗黙契約を維持するか修正するかを人間と合意して `DEC-XX` 判定ログとしてピン留めします。
- ステージ4では、テストハーネス整備（Phase 0）から段階的移行・旧コード撤去（Phase 4）までの**安全検証ゲート付き PR 単位 WBS（JSON および 7章構成 PDF 計画書）**を出力します。
- 下段の通り、同一言語内でのクリーンアーキテクチャ再構築（段階的 PR）と、言語やフレームワーク自体を刷新するクロススタック移行（Strangler Fig パターン）の双方に対応しています。
:::
