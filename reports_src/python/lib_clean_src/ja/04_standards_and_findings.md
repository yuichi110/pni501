# 4. 検査指標・ルール適合マトリクスと指摘一覧

`py_lib_clean` ワークフローで実行された全6監査ステップはいずれも **91〜96点**（Grade S）を達成し、評価対象 15 ルールのうち **13 件が PASS、2 件が WARN、0 件が FAIL** となった。検出された指摘事項も重大度 `LOW` 3件・`INFO` 2件の計5件にとどまり、`CRITICAL` / `HIGH` / `MEDIUM` 指摘は 0 件である。

```drawlib file=04_audit_step_scores.png caption="図4-1: 監査ステップ別スコア比較 (昇順: 低スコア順) とルール適合サマリ"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.icons import phosphor
from drawlib.smartarts import KpiCards
from drawlib.styles import Styles

setup(width=146, height=62, dpi=150)

chart = BarChart(
    axis_line_style=Styles.Primary,
    categories=[
        "Test (91)",
        "SecVuln (93)",
        "Repo (94)",
        "LibHyg (95)",
        "Runtime (95)",
        "PyAST (96)",
    ],
    width=85.0,
    height=54.0,
    orientation="horizontal",
    bar_width_ratio=0.62,
    bar_r=0.9,
    title="監査ステップ別スコア (Weakest → Strongest)",
    title_style=Styles.DarkBold.patch(text_size=12.0),
    axis_text_style=Styles.Dark.patch(text_size=9.8),
    grid_style=Styles.MutedDashed,
    value_text_style=Styles.PrimaryBold.patch(text_size=9.6),
    value_format="{:.0f} 点",
    background_style=Styles.Neutral.patch(shape_r=1.6),
)
chart.add_series("Step Score", [91, 93, 94, 95, 95, 96], style=Styles.PrimaryFlat)
chart.configure_x_axis(min_value=0.0, max_value=105.0, tick_step=25.0)
chart.draw(xy=(4.0, 4.0))

kpis = KpiCards(
    style=Styles.Neutral.patch(shape_r=1.5),
    metric_style=Styles.SuccessBold.patch(text_size=17.0),
    text_style=Styles.DarkBold.patch(text_size=10.8),
    description_style=Styles.Muted.patch(text_size=9.5),
    accent_style=Styles.SuccessFlat,
    icon_style=Styles.SuccessBold,
    accent_position="left_pill",
    metric_layout="left_column",
    metric_width_ratio=0.33,
    spacing=3.0,
)
kpis.add("13 / 15", "PASS ルール数", "主要設計・型・動的検証で合格", icon=phosphor.check_circle)
kpis.add(
    "2 件",
    "WARN ルール数",
    "docs / security_vuln",
    icon=phosphor.warning_circle,
    metric_style=Styles.WarningBold.patch(text_size=17.0),
    accent_style=Styles.WarningFlat,
    icon_style=Styles.WarningBold,
)
kpis.add(
    "0 件",
    "FAIL ルール数",
    "規約違反・ブロッカーゼロ",
    icon=phosphor.shield_check,
    metric_style=Styles.PrimaryBold.patch(text_size=17.0),
    accent_style=Styles.PrimaryNeutral,
    icon_style=Styles.PrimaryBold,
)
kpis.draw(xy=(92.0, 4.0), width=51.0, height=54.0, columns=1)

save()
```

## 4.1 ルール適合マトリクス（全15ルール：`FAIL → WARN → PASS` 順）

```drawlib file=04_rule_compliance_matrix.png caption="図4-2: 全15ルールの適合判定マトリクス (WARN 2件 → PASS 13件)"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Colors, Styles

setup(width=146, height=96, dpi=150)

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
tbl.set_style_cell(
    background_color=Colors.WarningNeutral,
    text_style=Styles.DarkBold.patch(text_size=9.5),
    rows=[1, 2],
    columns=[0],
)
tbl.set_style_cell(
    background_color=Colors.SuccessNeutral,
    text_style=Styles.SuccessBold.patch(text_size=9.5),
    rows=list(range(3, 16)),
    columns=[0],
)

rule_rows = [
    ["判定", "ルールID", "監査Step", "主要な検証エビデンス要約"],
    ["WARN", "common/documentation", "act-02", "Docstring 100%達成、READMEに関数1件と開発手順の追記余地"],
    ["WARN", "common/security_vulnerability", "act-13", "uv.lock CVE 0件、コンテナ基盤 pip@25.0.1 に MEDIUM 5件"],
    ["PASS", "common/architecture", "act-04", "循環依存 0件・境界違反 0件、完全な単方向4層DAG構造"],
    ["PASS", "common/git_workflow", "act-02", ".gitignore 完備、GitHub Actions CI が main push/PR を保護"],
    ["PASS", "common/library_guidelines", "act-08", "__all__ 19件明示、内部関数 _ 隠蔽、py.typed、柔軟な下限指定"],
    ["PASS", "common/maintainability", "act-04", "全6ファイル319 LOC (最大92 LOC)、複雑関数・大域状態 0件"],
    ["PASS", "common/production_readiness", "act-11", "外部I/Oゼロ、型付き例外階層完備、握り潰し catch ブロック 0件"],
    ["PASS", "common/runtime_verification", "act-11", "コンテナビルド 5.34s、オフライン pytest 6/6合格、行Cov 96.2%"],
    ["PASS", "common/security", "act-02", "秘密情報 0件、Pydantic frozen/forbid、Prometheus名サニタイズ"],
    ["PASS", "common/supply_chain", "act-02", "uv.lock・LICENSE・SECURITY.md・Dependabot・SHA固定CI完備"],
    ["PASS", "python/code_quality", "act-04", "Docstring 100.0%、シグネチャ不一致 0件、PEP 8 命名準拠"],
    ["PASS", "python/dependencies", "act-02", "PEP 621 準拠、実行依存 pydantic>=2.7.0 と dev グループ分離"],
    ["PASS", "python/modern_stack", "act-04", "Import衛生 100.0%、ワイルドカード・未使用依存 0件、StrEnum活用"],
    ["PASS", "python/testing", "act-09", "3テストファイル・6関数、モジュール網羅 100%、決定論的アサート"],
    ["PASS", "python/typing", "act-04", "型安全性 100.0%、Any・未スコープ ignore 0件、PEP 561 準拠"],
]
tbl.draw_flexible(
    xy=(3.0, 93.0),
    column_widths=[14.0, 39.0, 14.0, 73.0],
    row_heights=[6.2] + [5.5] * 15,
    data=rule_rows,
)

save()
```

## 4.2 重大度順・指摘事項一覧（全5件：`LOW → INFO` 順）

```drawlib file=04_findings_index_table.png caption="図4-3: 重大度順・指摘事項エビデンス一覧 (LOW 3件 → INFO 2件)"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Colors, Styles

setup(width=146, height=64, dpi=150)

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
tbl.set_style_cell(
    background_color=Colors.WarningNeutral,
    text_style=Styles.DarkBold.patch(text_size=9.5),
    rows=[1, 2, 3],
    columns=[0],
)
tbl.set_style_cell(
    background_color=Colors.PrimaryNeutral,
    text_style=Styles.PrimaryBold.patch(text_size=9.5),
    rows=[4, 5],
    columns=[0],
)

findings_data = [
    ["重大度", "ルールID", "箇所", "実証エビデンスと推奨修正"],
    [
        "LOW",
        "common/security",
        "models.py:26",
        "allow_inf_nan=False 未設定・isfinite 未検証 → 非有限値拒否を追加",
    ],
    [
        "LOW",
        "common/documentation",
        "README.md:37",
        "公開関数1件の記載漏れ・開発手順未記載 → API一覧とコマンドを追記",
    ],
    [
        "LOW",
        "security_vulnerability",
        "uv.lock:13",
        "推移的ハッシュ未記録・基盤 pip CVE 5件 → uv lock更新・pip>=26.2.0",
    ],
    [
        "INFO",
        "common/supply_chain",
        "ci.yml:18",
        "CI で --locked と uv run ty check 未実行 → ワークフローへ追加",
    ],
    [
        "INFO",
        "python/testing",
        "test_rules.py:42",
        "ComparisonOp.LT・単一要素・分散0等の未網羅 → parametrize 追加",
    ],
]
tbl.draw_flexible(
    xy=(3.0, 60.5),
    column_widths=[12.0, 31.0, 23.0, 74.0],
    row_heights=[8.5, 9.6, 9.6, 9.6, 9.6, 9.6],
    data=findings_data,
)

save()
```

### 指摘事項の補足詳細
1. **`[LOW]` `common/security` (`src/metrics_kit/models.py:26`)**: `ConfigDict(frozen=True, extra="forbid")` に `allow_inf_nan=False` が未指定であり、`stats.py:12` の `_require_non_empty` でも `math.isfinite` を検査していないため、`NaN`/`Inf` 混入時に `sorted(values)` の順序破綻や生の `ValueError` が生じ得る。
2. **`[LOW]` `common/documentation` (`README.md:37`)**: `__init__.py:34` で公開されている `sanitize_prometheus_name` が `README.md` の API Reference に未記載であり、開発・テストコマンド節も不足している。
3. **`[LOW]` `common/security_vulnerability` (`uv.lock:13`)**: `uv.lock` に推移的依存と wheel SHA-256 ハッシュが含まれておらず、コンテナ検証イメージのシステム `pip@25.0.1` に MEDIUM CVE 5件（修正版 `26.2.0`）が検出された。
4. **`[INFO]` `common/supply_chain` (`.github/workflows/ci.yml:18`)**: `pyproject.toml:24` に `ty>=0.0.35` が定義されているが、CI 上で `--locked` フラグおよび `uv run ty check` が未実行である。
5. **`[INFO]` `python/testing` (`tests/test_rules.py:42`)**: `rules.py` の行 `28, 91, 93, 99`（`ComparisonOp.LT`、`z_threshold <= 0`、点数 `< 2`、標準偏差 `0`）および `stats.py` の行 `66, 109`（単一要素パーセンタイル、空白メトリクス名）の単体テスト追加余地がある。
