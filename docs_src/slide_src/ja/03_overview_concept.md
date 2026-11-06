::: block xy=(80, 40) width=1760 height=60
# なぜ PNI501 か？ — 単発AIプロンプト監査の限界を超える
:::

::: block xy=(80, 135) width=1760 height=810
```drawlib file=why_pni.svg
from drawlib.canvas import clear, save, setup
from drawlib.icons import phosphor
from drawlib.shapes import arrow
from drawlib.smartarts import CardList, KpiCards, Panel
from drawlib.styles import Colors, Styles
from drawlib.text import text

clear()
setup(width=176, height=81)

# Left Panel: Traditional AI Prompt Audit Pitfalls
left_panel = Panel(
    "従来のAIプロンプト監査",
    style=Styles.SecondaryNeutral.patch(shape_fill_color=Colors.White),
    header_style=Styles.SecondaryNeutral,
    text_style=Styles.DarkBold.patch(text_size=14.5),
    header_variant="filled",
    header_height=8.5,
    header_align="center",
)
left_panel.draw(xy=(2, 26), width=77, height=53)
lx, lw, lh = left_panel.get_content_box(xy=(2, 26), width=77, height=53, padding=(3.5, 3.0))

pitfalls = CardList(
    style=Styles.Neutral,
    text_style=Styles.DarkBold.patch(text_size=12.5),
    description_style=Styles.Dark.patch(text_size=11.2),
    badge_shape="rounded_rect",
    badge_style=Styles.WarningNeutral,
    icon_style=Styles.DangerBold,
    direction="vertical",
    spacing=2.5,
)
pitfalls.add("ハルシネーション", "存在しないファイルや行番号を指摘", icon=phosphor.warning_circle)
pitfalls.add("静的読解のみの死角", "テスト成否・CVE・動的挙動が見えない", icon=phosphor.warning_circle)
pitfalls.add("主観スコアのブレ", "実行ごとに評価軸や点数が変動", icon=phosphor.warning_circle)
pitfalls.draw(xy=lx, width=lw, height=lh)

# Central Transformation Arrow
arrow(
    (81.0, 50.0),
    (91.0, 50.0),
    tail_width=4.5,
    head_width=9.0,
    head_length=3.8,
    style=Styles.PrimaryFlat,
)
text((86.0, 57.5), "PNI501", style=Styles.PrimaryBold.patch(text_size=12.5))

# Right Panel: PNI501 Deterministic Facts x AI Reasoning
right_panel = Panel(
    "PNI501（決定論ファクト × AI推論）",
    style=Styles.PrimaryNeutral.patch(shape_fill_color=Colors.White),
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=14.5),
    header_variant="filled",
    header_height=8.5,
    header_align="center",
)
right_panel.draw(xy=(93, 26), width=81, height=53)
rx, rw, rh = right_panel.get_content_box(xy=(93, 26), width=81, height=53, padding=(3.5, 3.0))

solutions = CardList(
    style=Styles.PrimaryNeutral,
    text_style=Styles.DarkBold.patch(text_size=12.5),
    description_style=Styles.Dark.patch(text_size=11.0),
    badge_shape="rounded_rect",
    badge_style=Styles.PrimaryNeutral.patch(shape_fill_color=Colors.White),
    icon_style=Styles.PrimaryBold,
    direction="vertical",
    spacing=2.5,
)
solutions.add("実在パス厳格照合", "ASTインベントリ検証で架空指摘ゼロ", icon=phosphor.check_circle)
solutions.add("隔離コンテナ＆動的解析", "Dockerテスト・Trivy・Pentestを自動実行", icon=phosphor.check_circle)
solutions.add("定量7軸グレード", "SQLite状態管理で再現性あるS〜D評価", icon=phosphor.check_circle)
solutions.draw(xy=rx, width=rw, height=rh)

# Bottom Zone: 4-Column KPI Summary Strip
kpis = KpiCards(
    style=Styles.Neutral,
    metric_style=Styles.PrimaryBold.patch(text_size=17.0),
    text_style=Styles.DarkBold.patch(text_size=11.5),
    accent_style=Styles.PrimaryFlat,
    accent_position="top_bar",
    metric_layout="top_stack",
    spacing=3.5,
)
kpis.add("Py / Java / PHP", "3言語ポリグロット対応")
kpis.add("36 ルール", "共通＋言語別規約")
kpis.add("12 プリミティブ", "6自動解析＋6 AI検証")
kpis.add("S 〜 D", "0–100点 定量グレード")
kpis.draw(xy=(2, 2), width=172, height=19, columns=4)

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
**概要①：なぜ PNI501 が必要なのか？**
- LLM にリポジトリを読ませて「このコードの品質を採点して」と単発プロンプトで依頼する従来のアプローチには、実務運用を阻む **3つの限界** があります：
  1. **ハルシネーション**：実在しないファイルパスやズレた行番号を根拠に指摘を生成してしまう。
  2. **静的読解のみの死角**：コード文字列を読むだけでは、ユニットテストが実際に通るか、依存パッケージに既知 CVE があるか、稼働アプリにインジェクション脆弱性があるかを判定できない。
  3. **主観スコアのブレ**：実行するたびに評価観点や点数が揺れ、時系列比較や組織横断のガバナンス指標として使えない。
- **PNI501 の解決アプローチ（右側）**：
  - **実在パス厳格照合**：AST インベントリで抽出した実在ファイル集合と AI の指摘 JSON を CLI 側で突合し、架空パスの混入をゼロにします。
  - **隔離コンテナ＆動的解析**：Docker サンドボックス内でのテスト・カバレッジ計測、Trivy スキャン、実稼働エンドポイントへの Web ペネトレーションテストを決定論ツールで自動実行します。
  - **定量7軸グレード**：SQLite 状態管理と `aggregator.py` の決定論数式により、誰がいつ実行しても再現性のある 0〜100 点・S〜D グレードを算出します。
- 下段 KPI バーの通り、**Python / Java / PHP の3言語対応**、**36個の標準規約**、**6つの自動解析＋6つのAI検証からなる12プリミティブ** を統合しています。
:::
