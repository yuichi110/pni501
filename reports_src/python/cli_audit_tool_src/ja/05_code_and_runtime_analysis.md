# 5. 詳細分析：コード品質・テスト・動的検証

本章では、AST 静的解析によって計測されたモジュール単位のコード品質・SIG 保守性・型安全性指標と、隔離 Docker コンテナ（Python 3.12）上で実行された動的ビルド・オフライン `pytest`・`pytest-cov` 実測カバレッジ・CLI スモーク検証の結果を詳細に分析する。

```drawlib file=code_module_quality_heatmap.png caption="モジュール × 品質ディメンション適合度マトリクス (0 - 100%)"
from drawlib.canvas import save, setup
from drawlib.charts.heatmap import HeatmapChart
from drawlib.styles import Styles

setup(width=146, height=66, dpi=150)

hm = HeatmapChart(
    min_style=Styles.DangerNeutral,
    max_style=Styles.Primary,
    x_categories=["import衛生", "厳格型安全", "Docstring率", "実測行網羅率", "実測分岐網羅率"],
    y_categories=[
        "cli.py (35 LOC)",
        "formatter.py (38 LOC)",
        "parser.py (52 LOC)",
        "analyzer.py (48 LOC)",
        "models.py (32 LOC)",
        "__init__.py (2 LOC)",
    ],
    axis_line_style=Styles.Neutral,
    axis_text_style=Styles.DarkBold.patch(text_size=9.5),
    value_text_style=Styles.DarkBold.patch(text_size=9.5),
    background_style=Styles.Neutral.patch(shape_r=2.0),
    width=114,
    height=52,
    min_value=0.0,
    max_value=100.0,
    cell_gap=0.8,
    cell_r=0.8,
    value_format=lambda v: f"{v:.1f}%",
    title="モジュール別 静的品質・動的テストカバレッジ適合マトリクス",
    title_style=Styles.DarkBold.patch(text_size=10.5),
)
hm.add_row("cli.py (35 LOC)", [100.0, 100.0, 100.0, 0.0, 0.0])
hm.add_row("formatter.py (38 LOC)", [100.0, 66.7, 33.3, 55.6, 0.0])
hm.add_row("parser.py (52 LOC)", [100.0, 100.0, 100.0, 87.5, 66.7])
hm.add_row("analyzer.py (48 LOC)", [100.0, 100.0, 100.0, 100.0, 100.0])
hm.add_row("models.py (32 LOC)", [100.0, 100.0, 100.0, 100.0, 100.0])
hm.add_row("__init__.py (2 LOC)", [100.0, 100.0, 100.0, 100.0, 100.0])
hm.draw(xy=(6, 6))
hm.draw_colorbar(
    xy=(126, 12),
    text_style=Styles.Dark.patch(text_size=9.0),
    length=40.0,
    thickness=2.6,
    orientation="vertical",
    label="適合率(%)",
)

save()
```

## 静的コード品質・SIG保守性・型安全性の詳細評価

- **SIG 保守性・モジュール結合度**: 全6ファイル合計 `207` LOC（最大は `parser.py` の `52` LOC）と極めて簡潔であり、複雑関数（`complex_functions = 0`）、過剰パラメータ関数（`excessive_parameters = 0`）、可変グローバル状態（`global_state_usages = 0`）、バグリスクイディオム（`bug_risk_idioms = 0`）はいずれもゼロである。
- **型安全性とドキュメンテーション品質**: 全公開関数にパラメータ・戻り値型注釈が付与されており（`type_safety_coverage_pct = 100.0%`）、import 整列率も `100.0%` を達成している。一方、`src/logpulse/formatter.py` の `report_to_dict`（13行目）が `dict[str, Any]` を返却している点、同ファイル13行目・30行目（`render_json_report`）で Google スタイルの Docstring が欠落している点（全体 Docstring 率 `88.9%`）、および PEP 561 `py.typed` マーカーと開発依存での静的型チェッカー（`ty` 等）が未設定である点が改善余地として残る。
- **CLI I/O・境界処理の実運用課題**: `src/logpulse/cli.py` の `scan_cmd`（34行目）は `log_file.read_text(encoding="utf-8").splitlines()` でファイル全体を一度にメモリ展開しており、大容量 `.jsonl` ログでメモリ逼迫を招くほか、読込権限エラーや文字コード不正時に `README.md` で約束された終了コード `2` ではなく未処理例外を送出する。`parser.py` 側は既に `Iterable[str]` を受け取る純粋ストリーム設計となっているため、`log_file.open()` を直接渡す改修が極めて有効である。

## コンテナ動的検証（ビルド・オフラインテスト・カバレッジ・Smoke）

PNI の `run_check` によりキャッシュ用ハーネス（`python/uv.dockerfile`, Python 3.12）でクリーンビルド（`18.2s`）を実行し、ネットワーク完全遮断（`--network=none`）環境で `pytest` と `logpulse --help` スモークチェックを実行した結果、すべてエラーゼロで正常完了した。ただし `pytest-cov` による実測カバレッジは行 `67.0%`（`75 / 112` 文）・分岐 `33.3%` であり、`cli.py`（`0.0%`）と `formatter.py` の `build_rich_table`（43〜50行目未実行で `55.6%`）が網羅率を押し下げている。

```drawlib file=runtime_verification_breakdown.png caption="コンテナ動的検証KPIとモジュール別実測カバレッジ内訳 (pytest-cov)"
from drawlib.canvas import save, setup
from drawlib.smartarts import KpiCards, Table
from drawlib.styles import Styles

setup(width=146, height=74, dpi=150)

kpis = KpiCards(
    style=Styles.Neutral,
    metric_style=Styles.SuccessBold.patch(text_size=12.5),
    text_style=Styles.DarkBold.patch(text_size=9.5),
    description_style=Styles.Neutral.patch(text_size=9.0),
    accent_position="top_bar",
    metric_layout="top_stack",
    spacing=2.5,
)
kpis.add(
    "PASSED (18.2s)",
    "ハーネスクリーンビルド",
    "uv.dockerfile (Py3.12)",
    accent_style=Styles.Success,
)
kpis.add(
    "2 / 2 PASS",
    "オフライン pytest",
    "--network=none (2.61s)",
    accent_style=Styles.Success,
)
kpis.add(
    "67.0% / 33.3%",
    "実測 行 / 分岐網羅率",
    "75 / 112 ステートメント",
    accent_style=Styles.Warning,
    metric_style=Styles.WarningBold.patch(text_size=12.5),
)
kpis.add(
    "EXIT 0 (1.33s)",
    "CLI スモーク起動検証",
    "logpulse --help 正常応答",
    accent_style=Styles.Primary,
    metric_style=Styles.PrimaryBold.patch(text_size=12.5),
)
kpis.draw(xy=(3, 52), width=140, height=19, columns=4)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=9.5),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.5),
    border_style=Styles.NeutralThin,
)
rows = [
    ["対象モジュール (昇順)", "行網羅率", "分岐網羅率", "実行文 / 総文数", "未実行行プレビュー (missing_lines)"],
    ["src/logpulse/cli.py", "0.0%", "0.0%", "0 / 26", "3, 5, 6, 8, 9, 11, 12, 13, 15, 18 (全体未実行)"],
    ["src/logpulse/formatter.py", "55.6%", "0.0%", "10 / 18", "43, 44, 45, 46, 47, 48, 49, 50 (build_rich_table)"],
    ["src/logpulse/parser.py", "87.5%", "66.7%", "21 / 24", "47 (空行スキップ), 54, 55 (非dict JSON行)"],
    ["src/logpulse/models.py", "100.0%", "N/A", "27 / 27", "なし (全データクラス定義・列挙値を網羅)"],
    ["src/logpulse/analyzer.py", "100.0%", "100.0%", "16 / 16", "なし (正規化・フィルタ・ソート全分岐網羅)"],
    ["src/logpulse/__init__.py", "100.0%", "N/A", "1 / 1", "なし"],
]
tbl.draw_flexible(
    xy=(3, 49),
    column_widths=[34, 15, 16, 21, 54],
    row_heights=[6.6, 6.6, 6.6, 6.6, 6.5, 6.5, 6.0],
    data=rows,
)

save()
```
