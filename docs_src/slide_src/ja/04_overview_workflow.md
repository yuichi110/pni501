::: block xy=(80, 40) width=1760 height=60
# PNI501 の仕組み — CLI主導の Pull-Push ワークフロー
:::

::: block xy=(80, 125) width=1760 height=70
**CLI が決定論ツールを実行し、AI エージェントは検証済みファクトに基づく推論とレポート執筆に専念**
:::

::: block xy=(80, 210) width=1760 height=730
```drawlib file=workflow_pipeline.svg
from drawlib.canvas import clear, save, setup
from drawlib.icons import phosphor
from drawlib.lines import line
from drawlib.smartarts import CardList, ChevronProcess
from drawlib.styles import Colors, Styles

clear()
setup(width=176, height=73)

# Top Half: 4-Stage Chevron Workflow Pipeline
pipeline = ChevronProcess(
    style=Styles.Neutral,
    text_style=Styles.DarkBold.patch(text_size=13.0),
    description_style=Styles.Dark.patch(text_size=11.0),
    corner_angle=70.0,
    spacing=1.8,
    flat_left_end=True,
)
pipeline.add(
    "1. 決定論ファクト抽出",
    description="AST・隔離Docker\nTrivy・Web Pentest",
    style=Styles.PrimaryNeutral,
)
pipeline.add(
    "2. Pull-Push AI監査",
    description="get-action <-> push-action\n規約照合・実在パス検証",
    style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=13.0),
    description_style=Styles.White.patch(text_size=11.0),
)
pipeline.add(
    "3. 定量集計・計画生成",
    description="aggregator.py 7軸採点\nマイグレーション計画",
    style=Styles.Neutral,
)
pipeline.add(
    "4. ビジュアルレポート",
    description="Drawlib 7章ブループリント\nA4ベクターPDF / HTML",
    style=Styles.SuccessNeutral,
)
pipeline.draw(xy=(2, 38), width=172, height=30)

# Subtle Stage-to-Artifact Vertical Connectors
for cx in (22.0, 66.0, 110.0, 154.0):
    line((cx, 36.8), (cx, 31.2), arrow_head="->", style=Styles.MutedBold)

# Bottom Half: 4 Concrete Persisted Artifacts
artifacts = CardList(
    style=Styles.Neutral.patch(shape_fill_color=Colors.White),
    text_style=Styles.DarkBold.patch(text_size=11.0),
    description_style=Styles.Dark.patch(text_size=11.0),
    badge_shape="circle",
    badge_style=Styles.PrimaryNeutral,
    icon_style=Styles.PrimaryBold,
    direction="horizontal",
    show_arrows=True,
    arrow_style=Styles.PrimaryBold,
    spacing=3.2,
)
artifacts.add(".pni/cache/<wf>/facts.json", "客観ファクト束", icon=phosphor.database)
artifacts.add("workflow_state.db", "SQLite 実行状態", icon=phosphor.git_commit)
artifacts.add("*_score / *_plan.json", "検証済み構造化データ", icon=phosphor.check_square)
artifacts.add(
    "reports/<target>.pdf",
    "経営・開発共有レポート",
    icon=phosphor.file_pdf,
    style=Styles.SuccessNeutral,
    badge_style=Styles.SuccessNeutral.patch(shape_fill_color=Colors.White),
    icon_style=Styles.SuccessBold,
)
artifacts.draw(xy=(1.5, 4), width=173, height=26)

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
**概要②：PNI501 の動作の仕組み（CLI主導の Pull-Push ワークフロー）**
- PNI501 の最大の設計特徴は、**主導権を AI ではなく決定論的な `pni` CLI ステートマシンが握る** 点にあります。
- **ステージ 1（決定論ファクト抽出）**：`pni` CLI が AST 解析、隔離 Docker 環境でのテスト＆カバレッジ計測、Trivy スキャン、動的 Web Pentest を実行し、客観的な証拠データを `.pni/cache/<wf>/facts.json` に保存します。
- **ステージ 2（Pull-Push AI監査）**：AI エージェントは `pni workflow get-action` で次にやるべきタスクとファクトを受け取り、推論結果を `pni workflow push-action` で提出します。提出された JSON スキーマやファイルパスの実在性は SQLite（`workflow_state.db`）上で厳格に検証され、不正な場合は差し戻されます。
- **ステージ 3（定量集計・計画生成）**：すべての検証済みステップが揃うと、`aggregator.py` が決定論的に7軸スコアやマイグレーション計画を集計し、`*_score.json` / `*_plan.json` を確定します。
- **ステージ 4（ビジュアルレポート）**：最後に Drawlib の7章構成レポートブループリントから、経営層にも開発現場にもそのまま共有できる高品質な A4 ベクター PDF（`reports/<target>.pdf`）および HTML レポートを出力します。
:::
