# 5. 詳細分析：コード品質・テスト・動的検証

AST静的解析および隔離コンテナ動的検証の結果、全6モジュール・13関数において型安全性・Import衛生・Docstringカバレッジすべて **100.0%**、SIG保守性違反（高複雑度関数・過剰引数・グローバル状態）**0 件**を達成し、オフライン単体テスト `6/6` 合格・実測行カバレッジ **96.2%**（`153/159` statements）を記録した。

```drawlib file=05_module_fitness_heatmap.png caption="図5-1: モジュール × 品質・カバレッジ適応度マトリクス (HeatmapChart)"
from drawlib.canvas import save, setup
from drawlib.charts.heatmap import HeatmapChart
from drawlib.styles import Styles

setup(width=146, height=68, dpi=150)

hm = HeatmapChart(
    styles=[Styles.WarningNeutral, Styles.PrimaryNeutral, Styles.PrimaryFlat],
    x_categories=["型安全性", "Import衛生", "Docstring", "SIG低複雑度", "実測行Cov", "実測分岐Cov"],
    axis_line_style=Styles.Primary,
    axis_text_style=Styles.DarkBold.patch(text_size=9.6),
    value_text_style=Styles.DarkBold.patch(text_size=9.5),
    width=126.0,
    height=46.0,
    min_value=70.0,
    max_value=100.0,
    cell_gap=0.8,
    cell_r=0.6,
    title="モジュール別 静的品質・動的カバレッジ適合度マトリクス (%)",
    title_style=Styles.DarkBold.patch(text_size=12.5),
    value_format="{:.1f}%",
)
hm.add_row("rules.py", [100.0, 100.0, 100.0, 100.0, 89.7, 72.2])
hm.add_row("stats.py", [100.0, 100.0, 100.0, 100.0, 95.6, 83.3])
hm.add_row("formatting.py", [100.0, 100.0, 100.0, 100.0, 100.0, 83.3])
hm.add_row("models.py", [100.0, 100.0, 100.0, 100.0, 100.0, 100.0])
hm.add_row("__init__.py", [100.0, 100.0, 100.0, 100.0, 100.0, 100.0])
hm.add_row("exceptions.py", [100.0, 100.0, 100.0, 100.0, 100.0, 100.0])

hm.draw(xy=(10.0, 16.0))
hm.draw_colorbar(
    xy=(46.0, 4.5),
    text_style=Styles.Muted.patch(text_size=9.5),
    length=54.0,
    thickness=2.0,
    value_format="{:.0f}%",
    label="適合度 / カバレッジ (%)",
)

save()
```

## 5.1 AST 静的コード品質・SIG 保守性・12-Factor 運用適性

- **静的品質カバレッジ (`python_ast_audit`: 96/100)**:
  - `total_files=6`, `total_loc=319`（最大モジュール `stats.py` でも `92 LOC` と高い凝集度を維持）、公開・内部関数 `13` 個・クラス `8` 個。
  - `import_hygiene_coverage_pct=100.0%`（未整列 Import `0`、ワイルドカード Import `0`、未使用・未宣言依存 `0`）。
  - `type_safety_coverage_pct=100.0%`（`Any` 使用 `0`、未スコープ `type: ignore` `0`、PEP 561 `py.typed` マーカー配置済み）。
  - `docstring_coverage_pct=100.0%`（欠落・空 Docstring `0`、引数シグネチャ不一致 `0`）。
- **SIG 保守性・12-Factor 運用準備度**:
  - 循環的複雑度超過関数 `0` 件、過剰パラメータ関数 `0` 件、グローバル可変状態 `0` 件、バグリスクイディオム（ミュータブルデフォルト引数・裸の `except:` 等）`0` 件。
  - 外部 I/O タイムアウト漏れ `0` 件、散在する環境変数参照 `0` 件、非構造化 `print` ログ出力 `0` 件。

## 5.2 隔離コンテナ動的検証とモジュール別実測カバレッジ

```drawlib file=05_runtime_coverage_breakdown.png caption="図5-2: モジュール別実測カバレッジ昇順比較 (BarChart) と隔離コンテナ検証ゲート (RV-01〜RV-04)"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.icons import phosphor
from drawlib.smartarts import KpiCards
from drawlib.styles import Styles

setup(width=146, height=66, dpi=150)

chart = BarChart(
    axis_line_style=Styles.Primary,
    categories=["rules.py", "stats.py", "format.py", "models.py", "__init__", "except.py"],
    width=84.0,
    height=50.0,
    orientation="vertical",
    bar_mode="group",
    bar_width_ratio=0.72,
    bar_r=0.8,
    title="モジュール別 実測行・分岐カバレッジ昇順比較 (%)",
    title_style=Styles.DarkBold.patch(text_size=12.0),
    axis_text_style=Styles.Dark.patch(text_size=9.5),
    grid_style=Styles.MutedDashed,
    background_style=Styles.Neutral.patch(shape_r=1.6),
)
chart.add_series("行カバレッジ", [89.7, 95.6, 100.0, 100.0, 100.0, 100.0], style=Styles.PrimaryFlat)
chart.add_series("分岐カバレッジ", [72.2, 83.3, 83.3, 100.0, 100.0, 100.0], style=Styles.SecondaryFlat)
chart.configure_y_axis(min_value=0.0, max_value=110.0, tick_step=25.0, unit="%")
chart.draw(xy=(3.0, 11.0))
chart.draw_legend(
    xy=(16.0, 4.2),
    text_style=Styles.Dark.patch(text_size=9.5),
    orientation="horizontal",
    item_gap=8.0,
)

kpis = KpiCards(
    style=Styles.Neutral.patch(shape_r=1.5),
    metric_style=Styles.SuccessBold.patch(text_size=15.5),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Muted.patch(text_size=9.5),
    accent_style=Styles.SuccessFlat,
    icon_style=Styles.SuccessBold,
    accent_position="left_pill",
    metric_layout="left_column",
    metric_width_ratio=0.30,
    spacing=2.4,
)
kpis.add("5.34s", "RV-01 ハーネスビルド", "Python 3.12 コンテナ exit 0", icon=phosphor.package)
kpis.add("6 / 6", "RV-02 オフライン単体テスト", "--network=none 全件合格 (3.12s)", icon=phosphor.check_circle)
kpis.add(
    "96.2%",
    "RV-03 実測カバレッジ",
    "153/159 行・分岐 77.8% 計測",
    icon=phosphor.chart_bar,
    metric_style=Styles.PrimaryBold.patch(text_size=15.5),
    accent_style=Styles.PrimaryFlat,
    icon_style=Styles.PrimaryBold,
)
kpis.add("1.22s", "RV-04 スモーク検証", "metrics_kit クリーン import 成功", icon=phosphor.lightning)
kpis.draw(xy=(90.0, 5.0), width=53.0, height=56.0, columns=1)

save()
```

| モジュール（カバレッジ昇順） | ステートメント | 実測行カバレッジ | 実測分岐カバレッジ | 未通過行番号（`missing_lines`）と該当処理 |
| :--- | :---: | :---: | :---: | :--- |
| `src/metrics_kit/rules.py` | `35 / 39` | `89.7%` | `72.2%` | `[28, 91, 93, 99]`（`ComparisonOp.LT`、`z_threshold<=0`、点数`<2`、標準偏差`0`） |
| `src/metrics_kit/stats.py` | `43 / 45` | `95.6%` | `83.3%` | `[66, 109]`（単一要素 `compute_percentile`、空白 `metric_name` 例外分岐） |
| `src/metrics_kit/formatting.py` | `22 / 22` | `100.0%` | `83.3%` | `[]`（全ステートメント通過、空文字フォールバック分岐1箇所のみ） |
| `src/metrics_kit/models.py` | `42 / 42` | `100.0%` | `100.0%`（分岐なし） | `[]`（全モデル定義通過） |
| `src/metrics_kit/__init__.py` | `7 / 7` | `100.0%` | `100.0%`（分岐なし） | `[]`（全公開シンボル再エクスポート通過） |
| `src/metrics_kit/exceptions.py` | `4 / 4` | `100.0%` | `100.0%`（分岐なし） | `[]`（全例外クラス定義通過） |
