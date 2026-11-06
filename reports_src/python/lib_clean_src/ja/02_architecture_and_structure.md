# 2. アーキテクチャとソースコード構成

`metrics-kit` は単方向4層レイヤード・アーキテクチャ（Facade → Policy & Formatting → Statistical Core → Domain Models & Exceptions）を採用した純粋インメモリ Python ライブラリである。全6モジュール・319 LOC の内部インポートグラフは完全な有向非巡回グラフ（DAG）を形成し、循環依存やレイヤ逆転は 0 件である。

```drawlib file=02_module_tree_inventory.png caption="図2-1: 物理ディレクトリツリーと AST モジュールインベントリ (全6ファイル・計319 LOC)"
from drawlib.canvas import save, setup
from drawlib.smartarts import Panel, Table, TreeNode
from drawlib.styles import Colors, Styles

setup(width=146, height=68, dpi=150)

tree_panel = Panel(
    "物理ソースツリー (lib_clean)",
    style=Styles.Neutral.patch(shape_r=1.8),
    header_style=Styles.PrimaryNeutral,
    text_style=Styles.DarkBold.patch(text_size=11.0),
    header_variant="filled",
    header_height=8.0,
)
tree_panel.draw((3.0, 4.0), width=45.0, height=60.0)

root = TreeNode(
    "metrics-kit/",
    text_style=Styles.DarkBold.patch(text_size=9.8),
    line_style=Styles.Muted,
    line_horizontal_margin=1.8,
    line_horizontal_length=2.5,
    line_vertical_margin=3.8,
)
root.add("pyproject.toml / uv.lock", text_style=Styles.Muted.patch(text_size=9.5))
src = root.add("src/metrics_kit/", text_style=Styles.PrimaryBold.patch(text_size=9.8))
src.add("__init__.py (34 LOC)")
src.add("exceptions.py (8 LOC)")
src.add("models.py (48 LOC)")
src.add("stats.py (92 LOC)")
src.add("rules.py (79 LOC)")
src.add("formatting.py (58 LOC)")
src.add("py.typed (PEP 561)", text_style=Styles.Muted.patch(text_size=9.5))
tst = root.add("tests/", text_style=Styles.SecondaryBold.patch(text_size=9.8))
tst.add("test_stats / test_rules")
tst.add("test_formatting.py")
root.draw((6.0, 52.0))

tbl = Table(
    cell_style=Styles.White,
    text_style=Styles.Dark.patch(text_size=9.5),
    header_cell_style=Styles.PrimaryFlat,
    header_text_style=Styles.WhiteBold.patch(text_size=9.8),
    border_style=Styles.MutedThin,
)
tbl.set_style_cell_evenodd(
    even_color=Colors.Neutral,
    even_text_style=Styles.Dark.patch(text_size=9.5),
    odd_color=Colors.White,
    odd_text_style=Styles.Dark.patch(text_size=9.5),
)

inv_data = [
    ["モジュール", "LOC", "定義クラス・型", "公開関数・主要責務"],
    ["__init__.py", "34", "再公開 19シンボル", "__all__ パッケージ公開境界"],
    ["exceptions.py", "8", "MetricsKitError 他2", "ドメイン例外階層 (空・不正引数)"],
    ["formatting.py", "58", "-", "Prometheus / Markdown 整形3関数"],
    ["models.py", "48", "MetricPoint 他3型", "Pydantic v2 frozen 不変モデル"],
    ["rules.py", "79", "-", "SLO閾値評価・Zスコア異常検知3関数"],
    ["stats.py", "92", "-", "平均・標準偏差・分位・EWMA 5関数"],
]
tbl.draw_flexible(
    xy=(51.0, 64.0),
    column_widths=[20.0, 9.0, 25.0, 38.0],
    row_heights=[8.5, 8.5, 8.5, 8.5, 8.5, 8.5, 8.5],
    data=inv_data,
)

save()
```

## 2.1 システムプロファイルと単方向4層レイヤ構造

- **ランタイム種別・技術スタック**: 純粋インメモリ Python ライブラリ（`Python >=3.11`、`Pydantic >=2.7.0`、`uv_build`、`pytest` / `pytest-cov`、`Ruff`、`Ty`）。外部ネットワーク通信やファイルシステム I/O を一切伴わず、Prometheus Text Exposition 形式および Markdown サマリ文字列を純粋関数で生成する。
- **レイヤ責務と境界検証**:
  1. **Public API Facade Layer (`src/metrics_kit/__init__.py`)**: 公開クラス・関数・例外の計19シンボルを `__all__` で明示再エクスポートする。
  2. **Policy & Formatting Layer (`src/metrics_kit/rules.py`, `src/metrics_kit/formatting.py`)**: SLO閾値ルール評価・Zスコア異常値検出、および Prometheus / Markdown 文字列整形を担う。
  3. **Statistical Aggregation Layer (`src/metrics_kit/stats.py`)**: 算術平均・母標準偏差・線形補間パーセンタイル・EWMA平滑化・時系列サマリ生成を純粋関数で実行する。
  4. **Domain Models & Exceptions Layer (`src/metrics_kit/models.py`, `src/metrics_kit/exceptions.py`)**: `ConfigDict(frozen=True, extra="forbid")` による不変モデルと型付き例外階層を定義し、内部依存を持たない基底層を構成する。

```drawlib file=02_layer_hotspot_diagram.png caption="図2-2: 4層モジュール依存グラフ (ClassDiagram) とホットスポットリスク分布 (HeatmapOverlay: 全モジュール risk=0.06)"
from drawlib.canvas import save, setup
from drawlib.charts.heatmap import HeatmapOverlay
from drawlib.diagrams.class_diagram import ClassDiagram, ClassNode
from drawlib.styles import Styles

setup(width=146, height=78, dpi=150)

cd = ClassDiagram(
    node_style=Styles.White,
    header_style=Styles.PrimaryNeutral,
    edge_style=Styles.Dark,
    edge_text_style=Styles.Dark.patch(text_size=9.5),
    title="4層モジュール依存関係とリスク密度オーバーレイ (risk_score = 0.06)",
    title_style=Styles.DarkBold.patch(text_size=12.5),
    width=140.0,
    height=61.0,
)

facade = cd.add(
    ClassNode("__init__.py (34 LOC)", width=36.0, style=Styles.PrimaryNeutral)
    .add_attribute("__all__", "list[str] (19 symbols)"),
    xy=(70.0, 52.5),
)

rules_mod = cd.add(
    ClassNode("rules.py (79 LOC)", width=35.0, style=Styles.Neutral)
    .add_method("evaluate_rule", "stats, rule", "Verdict")
    .add_method("detect_zscore_anomalies", "pts", "list"),
    xy=(22.5, 32.5),
)

fmt_mod = cd.add(
    ClassNode("formatting.py (58 LOC)", width=35.0, style=Styles.Neutral)
    .add_method("to_prometheus_lines", "stats", "list[str]")
    .add_method("format_markdown_summary", "stats", "str"),
    xy=(117.5, 32.5),
)

stats_mod = cd.add(
    ClassNode("stats.py (92 LOC)", width=36.0, style=Styles.SecondaryNeutral)
    .add_method("compute_percentile", "vals, q", "float")
    .add_method("summarize_series", "pts", "SummaryStats"),
    xy=(70.0, 30.5),
)

models_mod = cd.add(
    ClassNode("models.py (48 LOC)", width=36.0, style=Styles.Neutral)
    .add_attribute("MetricPoint / SummaryStats", "frozen")
    .add_attribute("ThresholdRule / AlertVerdict", "frozen"),
    xy=(104.0, 10.0),
)

exc_mod = cd.add(
    ClassNode("exceptions.py (8 LOC)", width=36.0, style=Styles.Neutral)
    .add_attribute("MetricsKitError", "Exception")
    .add_attribute("EmptySample / InvalidParam", "Error"),
    xy=(36.0, 10.0),
)

cd.connect(facade, rules_mod, "dependency", start_side="left", end_side="top")
cd.connect(facade, fmt_mod, "dependency", start_side="right", end_side="top")
cd.connect(facade, stats_mod, "dependency", start_side="bottom", end_side="top")
cd.connect(rules_mod, stats_mod, "dependency", start_side="right", end_side="left")
cd.connect(rules_mod, exc_mod, "dependency", start_side="bottom", end_side="top")
cd.connect(fmt_mod, models_mod, "dependency", start_side="bottom", end_side="top")
cd.connect(stats_mod, models_mod, "dependency", start_side="bottom", end_side="top")
cd.connect(stats_mod, exc_mod, "dependency", start_side="bottom", end_side="top")

cd.draw(xy=(3.0, 9.5))

overlay = HeatmapOverlay(
    styles=[Styles.BlueNeutral, Styles.WarningFlat, Styles.DangerFlat],
    min_value=0.0,
    max_value=1.0,
    mode="smooth",
    default_radius=13.0,
    max_alpha=0.32,
)
for node in (stats_mod, rules_mod, fmt_mod, models_mod, facade, exc_mod):
    overlay.add_spot(node, value=0.06, radius=13.0)
overlay.draw(xy=(3.0, 9.5))
overlay.draw_colorbar(
    xy=(46.0, 3.2),
    text_style=Styles.Muted.patch(text_size=9.5),
    length=54.0,
    thickness=2.0,
    label="Module Hotspot Risk (0.00 - 1.00)",
)

save()
```

## 2.2 主要実行フローと並行・状態管理モデル

公開エントリポイント（`src/metrics_kit/__init__.py`、`stats.py`、`rules.py`、`formatting.py`）はすべてステートレスかつスレッドセーフに動作する。全データモデルが `frozen=True` で不変であり、異常時は `sys.exit` や標準出力汚染を行わず `EmptySampleError` / `InvalidParameterError` を送出する。

```drawlib file=02_execution_flows_roadmap.png caption="図2-3: 主要ランタイム実行フロー (SLO閾値評価パイプラインおよびEWMA・異常値検出フロー)"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import Panel, Roadmap
from drawlib.styles import Styles

setup(width=146, height=62, dpi=150)

flow_panel = Panel(
    "主要実行フロー: テレメトリ時系列集計 → SLO閾値ルール評価 → レポート出力 (Flow 1 & Flow 2)",
    style=Styles.Neutral.patch(shape_r=1.8),
    header_style=Styles.PrimaryNeutral,
    text_style=Styles.DarkBold.patch(text_size=11.0),
    icon=phosphor.flow_arrow,
    icon_style=Styles.PrimaryBold,
    header_variant="filled",
    header_height=8.5,
)
flow_panel.draw((3.0, 4.0), width=140.0, height=54.0)
f_xy, f_w, f_h = flow_panel.get_content_box((3.0, 4.0), width=140.0, height=54.0, padding=(3.5, 3.0))

rm = Roadmap(
    style=Styles.White.patch(shape_r=1.4),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Muted.patch(text_size=9.5),
    spine_style=Styles.PrimaryBold,
    badge_style=Styles.PrimaryNeutral,
    badge_text_style=Styles.PrimaryBold.patch(text_size=10.0),
    icon_style=Styles.PrimaryBold,
    direction="horizontal",
    alternating=True,
)
rm.add(
    "1. 不変モデル検証",
    "models.py: MetricPoint &\nThresholdRule 生成",
    badge_text="Step 1",
    icon=phosphor.cube,
    badge_style=Styles.PrimaryFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.8),
)
rm.add(
    "2. 記述統計・EWMA",
    "stats.py: summarize_series\n& compute_ewma 算出",
    badge_text="Step 2",
    icon=phosphor.chart_line_up,
)
rm.add(
    "3. 閾値・Zスコア判定",
    "rules.py: evaluate_ruleset\n& Zスコア異常抽出",
    badge_text="Step 3",
    icon=phosphor.scales,
)
rm.add(
    "4. 監視フォーマット整形",
    "formatting.py: Prometheus\n行・Markdown 出力",
    badge_text="Step 4",
    icon=phosphor.file_text,
    badge_style=Styles.SuccessFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.8),
)
rm.draw(f_xy, width=f_w, height=f_h)

save()
```
