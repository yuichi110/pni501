# 5. 詳細分析：コード品質・テスト・ランタイム検証

全 4 モジュール（`84` LOC・手続き型関数 `7` 個・クラス `0` 個）に対する静的 PHP AST 解析の結果、表面的な構文の正当性と深刻な品質・テスト負債の乖離が鮮明になりました。全ファイルが PHP 8.2 環境で `php -l` を通過し 5 つの WordPress フックを正常登録する一方、型安全性（`0.0%`）、PHPDoc（`0.0%`）、WordPress フレームワーク衛生（`16` 件の違反）、および自動テストカバレッジ（PHPUnit テスト `0` 件）はすべてゼロ水準に留まっています。

```drawlib align=center code=fold file=module_quality_heatmap.png caption="モジュール × 品質・セキュリティ適合度マトリクス（0 = 重大ギャップ、100 = 健全）"
from drawlib.canvas import save, setup
from drawlib.charts.heatmap import HeatmapChart
from drawlib.styles import Styles

setup(width=146, height=62, dpi=150)

hm = HeatmapChart(
    styles=[Styles.DangerFlat, Styles.WarningNeutral, Styles.SuccessNeutral],
    x_categories=["Modularity", "Strict Types", "PHPDoc", "ABSPATH", "Sec Hygiene", "Test Cov"],
    axis_line_style=Styles.MutedThin,
    width=104.0,
    height=44.0,
    min_value=0.0,
    max_value=100.0,
    cell_gap=0.8,
    cell_r=0.8,
    value_format="{:.0f}",
    auto_contrast_text=True,
    x_label_position="top",
    axis_text_style=Styles.DarkBold.patch(text_size=9.5),
    value_text_style=Styles.DarkBold.patch(text_size=10.0),
    title="Module x Quality/Security Fitness Matrix (0-100 Score per Dimension)",
    title_style=Styles.DarkBold.patch(text_size=11.5),
)
hm.add_row("member-analytics-portal.php", [80, 0, 0, 0, 20, 0])
hm.add_row("includes/rest-endpoints.php", [85, 0, 0, 0, 5, 0])
hm.add_row("includes/ajax-handlers.php", [85, 0, 0, 0, 5, 0])
hm.add_row("admin/settings-page.php", [75, 0, 0, 0, 15, 0])
hm.draw(xy=(38.0, 6.0))

save()
```

## PHP 8.2 ランタイムスモーク検証 vs. テストカバレッジゼロ診断

PNI は隔離された Docker PHP 8.2 ランタイムハーネス（`.pni/dockerfiles/examples/php/wp_plugin_messy/Dockerfile`、テンプレート `php/raw.dockerfile`）で検証を実施しました。コンテナビルド（`49.1s`）、構文ゲート（`php -l`、`0.72s`）、および WordPress スタブ環境でのプラグイン起動スモーク（`0.64s`・5 フック登録）はいずれも成功したものの、**PHPUnit/Pest テストが 1 件も存在しない**ため `coverage.measured=False` となり、今後のセキュリティ修正に対する自動回帰保護が完全に欠如しています。

```drawlib align=center code=fold file=runtime_vs_coverage_diagnostic.png caption="Docker PHP 8.2 ランタイムゲート結果 vs. 静的 AST 品質・カバレッジ指標"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.icons import phosphor
from drawlib.smartarts import CardList, Panel
from drawlib.styles import Colors, Styles
from drawlib.text import text

setup(width=148, height=66, dpi=150)

left = Panel(
    text="Docker PHP 8.2 Runtime Harness Gates (RV-01 .. RV-04)",
    style=Styles.Neutral.patch(shape_r=2.0, shape_fill_color=Colors.White, shape_line_color=Colors.Gray4),
    header_style=Styles.PrimaryNeutral.patch(shape_r=2.0),
    text_style=Styles.DarkBold.patch(text_size=10.2),
    header_variant="filled",
    header_height=9.0,
)
left.draw((3.0, 4.0), width=68.0, height=58.0)

gates = CardList(
    style=Styles.Neutral.patch(shape_r=1.4, shape_fill_color=Colors.Gray1, shape_line_color=Colors.Gray3),
    text_style=Styles.DarkBold.patch(text_size=9.5),
    description_style=Styles.Muted.patch(text_size=8.6),
    badge_shape="rounded_rect",
    direction="vertical",
    spacing=2.2,
)
gates.add(
    "RV-01 Harness Build (49.1s)",
    "php/raw.dockerfile (PHP 8.2) built, exit 0",
    badge_text="PASS",
    badge_style=Styles.SuccessNeutral,
    badge_text_style=Styles.SuccessBold.patch(text_size=9.0),
    icon=phosphor.check_circle,
    icon_style=Styles.Success,
)
gates.add(
    "RV-02 Syntax Lint vs. Tests (0.72s)",
    "php -l OK (4/4 files); 0 PHPUnit tests found",
    badge_text="WARN",
    badge_style=Styles.WarningNeutral,
    badge_text_style=Styles.WarningBold.patch(text_size=9.0),
    icon=phosphor.warning_circle,
    icon_style=Styles.Warning,
)
gates.add(
    "RV-03 PCOV Line Coverage",
    "coverage.measured=False (no tests/ suite)",
    badge_text="FAIL",
    badge_style=Styles.DangerNeutral,
    badge_text_style=Styles.DangerBold.patch(text_size=9.0),
    icon=phosphor.x_circle,
    icon_style=Styles.Danger,
)
gates.add(
    "RV-04 WP Hook Smoke Probe (0.64s)",
    "Entrypoint loaded cleanly; 5 hooks active",
    badge_text="PASS",
    badge_style=Styles.SuccessNeutral,
    badge_text_style=Styles.SuccessBold.patch(text_size=9.0),
    icon=phosphor.plug,
    icon_style=Styles.Success,
)
gates.draw((5.5, 6.5), width=63.0, height=44.5)

text(
    (116.0, 59.0),
    "Static Quality & Coverage Metrics (%)",
    style=Styles.DarkBold.patch(text_size=10.5),
)

bar = BarChart(
    categories=[
        "Import Hygiene",
        "Strict Typing",
        "PHPDoc",
        "ABSPATH Guard",
        "Unit Test Cov",
    ],
    axis_line_style=Styles.MutedDashed,
    axis_text_style=Styles.DarkBold.patch(text_size=9.2),
    grid_style=Styles.MutedThin,
    width=46.0,
    height=46.0,
    orientation="horizontal",
    bar_r=0.7,
    value_text_style=Styles.DarkBold.patch(text_size=9.5),
    value_format="{:.0f}%",
)
bar.add_series("Measured %", [75.0, 0.0, 0.0, 0.0, 0.0], style=Styles.PrimaryFlat)
bar.draw(xy=(96.0, 8.0))

save()
```

## 静的 AST 品質・運用レディネス定量テレメトリ

| カテゴリ | 指標 | 観測値 | 評価 |
| :--- | :--- | :---: | :--- |
| **コード規模** | PHP ファイル数 / LOC / 関数数 / クラス数 | `4` / `84` / `7` / `0` | コンパクトな手続き型構成だが、OOP 名前空間・クラス境界が皆無。 |
| **インポート衛生** | `import_hygiene_coverage_pct` / 循環依存 | `75.0%` / `0` | 非巡回構成だが、`member-analytics-portal.php:11-13` が Composer PSR-4 ではなく手動 `require_once` 3 件を使用。 |
| **型安全性** | `type_safety_coverage_pct` / 型指摘件数 | `0.0%` / `11` | 全 4 ファイルで `declare(strict_types=1)` 欠落、全 7 関数で戻り値型欠落、`$request`・`$atts` 引数も未型付け。 |
| **ドキュメント** | `docstring_coverage_pct` / PHPDoc 欠落 | `0.0%` / `7` | 全公開関数で `/** ... */` PHPDoc ブロックが皆無、`README.md` は 2 行。 |
| **SIG 保守性** | 高複雑度関数 / 過多引数 / グローバル状態 | `0` / `0` / `13` | 関数は短いが、`global $wpdb` 3 箇所と `$_GET`/`$_POST` 直接参照 10 箇所がグローバル状態へ強結合。 |
| **WordPress 衛生** | `framework_issues_count` / `modernization_hints` | `16` / `1` | `ABSPATH` 欠落 4 件、CSRF Nonce 欠落 3 件、`current_user_can()` 欠落 3 件、未サニタイズ入力 6 件、直書き `<script>` 1 件。 |
| **12-Factor / PRR** | バグ誘発慣用 / I/O タイムアウト欠落 / 無構造ログ | `1` / `1` / `1` | `@file_get_contents()` によるタイムアウト無指定・エラー抑止（`admin/settings-page.php:21`）と `print_r($rows)` 出力（`includes/rest-endpoints.php:21`）。 |

## コンテナランタイム検証・フック登録スモーク詳細

| ゲート | 判定 | 所要時間 | 実行内容および観測結果 |
| :--- | :-: | :-: | :--- |
| **RV-01 ハーネスビルド** | **PASS** | `49.1s` | `.pni/dockerfiles/examples/php/wp_plugin_messy/Dockerfile`（`php/raw.dockerfile`、`PHP_VERSION=8.2`）を終了コード `0` でビルド完了。なおプラグインヘッダは EOL `Requires PHP: 7.4` のまま。 |
| **RV-02 構文チェック・単体テスト** | **WARN** | `0.72s` | 全 4 `.php` ファイルで `php -l` 合格。一方 `tests/` や `*Test.php` が存在せず `total_tests=0`（`passed=0`, `failed=0`）。 |
| **RV-03 カバレッジ計測** | **FAIL** | — | `coverage.measured=False`（PHPUnit テストスイート不在のため PCOV 未実行）。 |
| **RV-04 WP フックスモーク** | **PASS** | `0.64s` | WordPress 登録 API スタブ下で `member-analytics-portal.php` を正常読込（`HTTP 200` 相当）。`rest_api_init`、`member_analytics_badge`、`wp_ajax_nopriv_map_search_members`、`wp_ajax_map_purge_logs`、`admin_menu` の**計 5 フック**登録を確認。 |
