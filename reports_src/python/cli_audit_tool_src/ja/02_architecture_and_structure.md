# 2. アーキテクチャとソースコード構成

`logpulse` は **Layered Pipeline CLI Architecture（CLI アダプタ層 -> 表示整形層・アプリケーション処理層 -> 不変ドメインコア層）** を採用しており、全6ソースファイル（計 `207` LOC・4クラス・8関数）が単方向かつ非循環の依存関係で構成されている。

```drawlib file=arch_tree_and_inventory.png caption="ソースディレクトリ構造ツリーとASTモジュールインベントリ (全6ファイル・207 LOC)"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import Panel, Table, TreeNode
from drawlib.styles import Styles

setup(width=146, height=74, dpi=150)

left_panel = Panel(
    "リポジトリ構成ツリー",
    "",
    style=Styles.Neutral,
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=10.5),
    icon=phosphor.git_branch,
    icon_style=Styles.White,
    header_height=9.5,
)
left_panel.draw(xy=(2, 3), width=47, height=68)

t_style = Styles.Dark.patch(text_size=9.5)
b_style = Styles.PrimaryBold.patch(text_size=9.5)
root = TreeNode(
    "cli_audit_tool/",
    text_style=b_style,
    line_style=Styles.Neutral,
    line_horizontal_margin=1.0,
    line_horizontal_length=2.2,
    line_vertical_margin=3.9,
)
root.add("pyproject.toml / uv.lock", text_style=t_style)
root.add("README.md / LICENSE", text_style=t_style)
src_node = root.add("src/logpulse/", text_style=b_style)
src_node.add("cli.py (35 LOC)", text_style=Styles.DangerBold.patch(text_size=9.5))
src_node.add("formatter.py (38 LOC)", text_style=Styles.WarningBold.patch(text_size=9.5))
src_node.add("analyzer.py (48 LOC)", text_style=t_style)
src_node.add("parser.py (52 LOC)", text_style=t_style)
src_node.add("models.py / __init__.py", text_style=t_style)
tst_node = root.add("tests/", text_style=b_style)
tst_node.add("test_parser / test_analyzer", text_style=t_style)
root.draw(xy=(4.5, 58.0))

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=9.5),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.5),
    border_style=Styles.NeutralThin,
)
rows = [
    ["モジュール", "LOC", "公開型・関数シンボルと主要責務"],
    ["parser.py", "52", "parse_severity, parse_jsonl_lines\n耐障害JSONL行解析・重要度正規化"],
    ["analyzer.py", "48", "normalize_signature, build_scan_report\n数値IDの<N>置換・頻度順バースト集計"],
    ["formatter.py", "38", "report_to_dict, render_json_report,\nbuild_rich_table (JSON / Rich表整形)"],
    ["cli.py", "35", "scan_cmd (Typer CLIエントリポイント・\nstdout/stderr分離・終了コード制御)"],
    ["models.py", "32", "SeverityLevel, LogEvent, SignatureGroup,\nScanReport (不変ドメインモデル定義)"],
    ["__init__.py", "2", "パッケージ初期化 (future annotations)"],
]
tbl.draw_flexible(
    xy=(51, 71),
    column_widths=[25, 10, 58],
    row_heights=[8.0, 10.0, 10.0, 10.0, 10.0, 10.5, 8.5],
    data=rows,
)

save()
```

## レイヤー責務分離と境界健全性・ホットスポット分析

AST の内部 import グラフ検証により、循環依存（`circular_dependencies = 0`）およびレイヤー逆流（`boundary_violations = 0`）が完全にゼロであることが確認された。`models.py` は外部依存を持たず、`parser.py`・`analyzer.py`・`formatter.py` は互いに依存せず `models.py` のみを参照し、最上位の `cli.py` がオーケストレーションを担う。一方、指摘密度に基づくモジュールリスクスコア（`module_hotspots`）では、単体テスト未整備と CLI 境界課題が集中する `src/logpulse/cli.py`（`risk_score=0.89`）および `src/logpulse/formatter.py`（`risk_score=0.27`）が主要なホットスポットとなっている。

```drawlib file=arch_layer_hotspot_diagram.png caption="4層クラス/モジュール依存関係グラフとリスクホットスポット (HeatmapOverlay)"
from drawlib.canvas import save, setup
from drawlib.charts.heatmap import HeatmapOverlay
from drawlib.diagrams.class_diagram import ClassDiagram, ClassNode
from drawlib.styles import Styles

setup(width=146, height=70, dpi=150)

diag = ClassDiagram(
    node_style=Styles.Neutral,
    header_style=Styles.PrimaryFlat,
    edge_style=Styles.PrimaryBold,
    edge_text_style=Styles.Dark.patch(text_size=9.0),
    style=Styles.Neutral.patch(shape_r=2.0),
    width=124,
    height=62,
    title="logpulse 4層モジュール依存グラフ × リスク密度オーバーレイ",
    title_style=Styles.DarkBold.patch(text_size=10.5),
)

n_cli = ClassNode("cli.py", stereotype="CLI Entry (35 LOC)", width=34, row_height=3.4, header_style=Styles.Danger)
n_cli.add_attribute("app", "Typer")
n_cli.add_method("scan_cmd", "log_file", "None")

n_parser = ClassNode("parser.py", stereotype="Processing (52 LOC)", width=34, row_height=3.4)
n_parser.add_method("parse_severity", "str", "SeverityLevel")
n_parser.add_method("parse_jsonl_lines", "lines", "tuple")

n_analyzer = ClassNode("analyzer.py", stereotype="Processing (48 LOC)", width=34, row_height=3.4)
n_analyzer.add_method("normalize_signature", "str", "str")
n_analyzer.add_method("build_scan_report", "events", "ScanReport")

n_fmt = ClassNode("formatter.py", stereotype="Presentation (38 LOC)", width=34, row_height=3.4, header_style=Styles.Warning)
n_fmt.add_method("report_to_dict", "ScanReport", "dict")
n_fmt.add_method("build_rich_table", "ScanReport", "Table")

n_models = ClassNode("models.py", stereotype="Domain Core (32 LOC)", width=46, row_height=3.3, header_style=Styles.Success)
n_models.add_attribute("SeverityLevel", "IntEnum")
n_models.add_attribute("LogEvent / ScanReport", "frozen")

diag.add(n_cli, xy=(45, 42))
diag.add(n_parser, xy=(5, 22))
diag.add(n_analyzer, xy=(45, 22))
diag.add(n_fmt, xy=(85, 22))
diag.add(n_models, xy=(39, 3))

diag.connect(n_cli, n_parser, directed=True)
diag.connect(n_cli, n_analyzer, directed=True)
diag.connect(n_cli, n_fmt, directed=True)
diag.connect(n_parser, n_models, directed=True)
diag.connect(n_analyzer, n_models, directed=True)
diag.connect(n_fmt, n_models, directed=True)
diag.draw(xy=(3, 4))

ov = HeatmapOverlay(
    min_style=Styles.Success,
    max_style=Styles.Danger,
    width=124,
    height=62,
    min_value=0.0,
    max_value=1.0,
    default_radius=14.0,
    max_alpha=0.32,
    show_contour_lines=True,
)
ov.add_spot(xy=(62, 49), value=0.89, radius=15.0)
ov.add_spot(xy=(102, 28), value=0.27, radius=13.0)
ov.add_spot(xy=(22, 28), value=0.06, radius=10.0)
ov.add_spot(xy=(62, 28), value=0.06, radius=10.0)
ov.add_spot(xy=(62, 9), value=0.06, radius=11.0)
ov.draw(xy=(3, 4))
ov.draw_colorbar(
    xy=(131, 12),
    text_style=Styles.Dark.patch(text_size=9.0),
    length=42.0,
    thickness=2.6,
    orientation="vertical",
    label="Risk",
)

save()
```

## CLI 実行データフローと状態・エラー処理モデル

本ツールはデータベースや永続キャッシュを持たないステートレスな単一スレッド実行モデルを採用している。入力ファイルから生成される `LogEvent`・`SignatureGroup`・`ScanReport` はすべて `@dataclass(frozen=True)` として不変化されており、不正な JSON 行は例外停止させずスキップ行数として集計して `stderr` に警告出力する耐障害設計となっている。

```drawlib file=arch_cli_execution_flow.png caption="logpulse scan 実行パイプラインと終了コード制御フロー"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import Roadmap
from drawlib.styles import Styles

setup(width=146, height=58, dpi=150)

flow = Roadmap(
    style=Styles.Neutral,
    text_style=Styles.DarkBold.patch(text_size=9.8),
    description_style=Styles.Dark.patch(text_size=9.5),
    spine_style=Styles.PrimaryBold,
    badge_style=Styles.Primary,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.5),
    direction="horizontal",
    spacing=2.5,
)
flow.add(
    "1. CLI入力確認",
    "Console初期化\nファイル欠損はExit 2",
    badge_text="S1",
    style=Styles.PrimaryNeutral,
    icon=phosphor.terminal_window,
    icon_style=Styles.Primary,
)
flow.add(
    "2. JSONL行解析",
    "LogEvent生成\n不正行はstderr警告",
    badge_text="S2",
    style=Styles.Neutral,
    icon=phosphor.file_text,
    icon_style=Styles.Primary,
)
flow.add(
    "3. 正規化・集計",
    "数値IDを<N>置換\n頻度順に上位抽出",
    badge_text="S3",
    style=Styles.PrimaryNeutral,
    icon=phosphor.chart_bar,
    icon_style=Styles.Primary,
)
flow.add(
    "4. 描画・閾値判定",
    "JSON/Rich表出力\n閾値超過時はExit 1",
    badge_text="S4",
    style=Styles.Neutral,
    icon=phosphor.check_circle,
    icon_style=Styles.Success,
    badge_style=Styles.Success,
)
flow.draw(xy=(3, 5), width=140, height=48)

save()
```
