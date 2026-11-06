# 5. コード品質・型安全性・ランタイム検証詳細

本章では、PHP AST 静的解析によって抽出された4モジュールのコード品質・`declare(strict_types=1)` 型安全性・WordPress 規約適合度と、隔離 Docker コンテナ（PHP 8.2）上で実行された `php -l` 構文検証および WordPress フック登録スモークテスト（RV-01〜RV-04）の結果を詳細に分析する。

```drawlib file=code_module_quality_heatmap.png caption="モジュール × 品質ディメンション適合度マトリクス (0 - 100%)"
from drawlib.canvas import save, setup
from drawlib.charts.heatmap import HeatmapChart
from drawlib.styles import Styles

setup(width=146, height=64, dpi=150)

hm = HeatmapChart(
    min_style=Styles.DangerNeutral,
    max_style=Styles.Primary,
    x_categories=["構文・非循環", "import衛生", "厳格型安全", "PHPDoc整備", "WP規約・テスト"],
    y_categories=[
        "settings-page.php (31 LOC)",
        "ajax-handlers.php (21 LOC)",
        "rest-endpoints.php (21 LOC)",
        "member-analytics-portal (11)",
    ],
    axis_line_style=Styles.Neutral,
    axis_text_style=Styles.DarkBold.patch(text_size=8.8),
    value_text_style=Styles.DarkBold.patch(text_size=9.2),
    background_style=Styles.Neutral.patch(shape_r=2.0),
    width=112,
    height=48,
    min_value=0.0,
    max_value=100.0,
    cell_gap=0.9,
    cell_r=0.8,
    value_format=lambda v: f"{v:.0f}%",
    title="モジュール別 静的コード品質・型安全・WP規約・テスト適合度マトリクス",
    title_style=Styles.DarkBold.patch(text_size=9.8),
)
hm.add_row("settings-page.php (31 LOC)", [80.0, 100.0, 0.0, 0.0, 0.0])
hm.add_row("ajax-handlers.php (21 LOC)", [85.0, 100.0, 0.0, 0.0, 0.0])
hm.add_row("rest-endpoints.php (21 LOC)", [85.0, 100.0, 0.0, 0.0, 0.0])
hm.add_row("member-analytics-portal (11)", [90.0, 0.0, 0.0, 0.0, 0.0])
hm.draw(xy=(6, 7))
hm.draw_colorbar(
    xy=(125, 12),
    text_style=Styles.Dark.patch(text_size=9.0),
    length=38.0,
    thickness=2.6,
    orientation="vertical",
    label="適合率(%)",
)

save()
```

## 静的コード品質・型安全性・WordPress 実装規約の詳細評価

- **EOL ランタイム指定と型安全カバレッジ `0.0%`**: `member-analytics-portal.php:7` はセキュリティサポート終了済みの `Requires PHP: 7.4` を宣言している。全4ファイルで `declare(strict_types=1);` が欠落し、全7関数（`map_render_badge_shortcode`・`map_register_rest_routes`・`map_export_all_members`・`map_ajax_search_members`・`map_ajax_purge_logs`・`map_register_admin_menu`・`map_render_settings_page`）に戻り値型がなく、`$request`（`WP_REST_Request`）や `$atts` の引数型・PHPDoc（`0.0%`）も一切付与されていない。
- **グローバル結合・アセット直書き・ブロッキング外部通信**: 84 LOC 中に `global $wpdb` 結合が `3` 箇所、`$_GET` / `$_POST` の未サニタイズ直参照が `10` 箇所（計 `13` 箇所）存在する。`admin/settings-page.php:27` は `wp_enqueue_script()` を使わず `<script src="/wp-content/plugins/member-analytics-portal/assets/admin-chart.js"></script>` を直書きしており、サブディレクトリ型 WordPress 環境で 404 となる。また同 `21` 行目の `@file_get_contents('https://telemetry.example.com/ping?site=...')` はタイムアウト指定を欠き（デフォルト 60 秒ブロック）、`@` 演算子で通信失敗を無言で握り潰す危険なイディオムとなっている。さらに `includes/rest-endpoints.php:21` では `?debug=1` 時に `print_r($rows)` が JSON 出力を破壊する。

## コンテナ動的検証（PHP 8.2 `php -l`・WordPress 5フック登録スモーク vs テスト不在）

隔離 Docker コンテナ（`php/raw.dockerfile`, `PHP_VERSION=8.2`）を用いた動的検証では、**構文検証と WordPress コアスタブによるプラグインロード自体は正常通過**した一方、**PHPUnit テスト 0 件によりコールバック内部の動的検証と実測カバレッジ計測が完全に欠落**している実態が明確化された。

```drawlib file=runtime_verification_breakdown.png caption="コンテナ動的検証KPIと RV-01〜RV-04 ゲート別実行結果内訳"
from drawlib.canvas import save, setup
from drawlib.smartarts import KpiCards, Table
from drawlib.styles import Styles

setup(width=146, height=84, dpi=150)

kpis = KpiCards(
    style=Styles.Neutral,
    metric_style=Styles.SuccessBold.patch(text_size=11.8),
    text_style=Styles.DarkBold.patch(text_size=9.2),
    description_style=Styles.Neutral.patch(text_size=8.6),
    accent_position="top_bar",
    metric_layout="top_stack",
    spacing=2.5,
)
kpis.add(
    "PASSED (60.24s)",
    "PHP 8.2 ハーネスビルド",
    "php/raw.dockerfile (exit 0)",
    accent_style=Styles.Success,
)
kpis.add(
    "PASSED (0.80s)",
    "php -l 全4ファイル構文",
    "PHP 8.2 パーサ構文エラー0件",
    accent_style=Styles.Success,
)
kpis.add(
    "0 Tests / N/A",
    "オフライン PHPUnit & PCOV",
    "テスト0件・measured=false",
    accent_style=Styles.Danger,
    metric_style=Styles.DangerBold.patch(text_size=11.8),
)
kpis.add(
    "PASSED (0.59s)",
    "WP 5フック登録スモーク",
    "wp-plugin:// 正常初期化 (200)",
    accent_style=Styles.Success,
)
kpis.draw(xy=(3, 61.5), width=140, height=19.5, columns=4)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=8.7),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.0),
    border_style=Styles.NeutralThin,
)
rows = [
    ["検証ゲート", "ステータス", "所要時間", "決定的実行ログ・エビデンスと評価"],
    [
        "RV-01: PHP 8.2\nコンテナビルド",
        "PASSED\n(exit 0)",
        "60.24s",
        "php/raw.dockerfile (PHP 8.2 / Debian 12.15) のクリーンビルドに成功。\nただしリポジトリ自体には composer.json / lockfile が存在しない",
    ],
    [
        "RV-02a: php -l\n構文ゲート",
        "PASSED\n(exit 0)",
        "0.80s",
        "--network=none 環境で全4つの .php ファイルに対する php -l 構文検査が通過。\nPHP 8.2 での致命的な構文非互換はないことを確認",
    ],
    [
        "RV-02b: オフライン\nPHPUnit 実行",
        "FAIL (不在)\ntotal_tests=0",
        "0.00s",
        "'PHP syntax gate (php -l) passed; no PHPUnit tests executed.'\ntests/ ディレクトリおよび *Test.php が0件のためコールバック未検証",
    ],
    [
        "RV-03: PCOV\n実測カバレッジ",
        "UNMEASURED\n(measured=false)",
        "0.00s",
        "line_coverage_pct=null, branch_coverage_pct=null。7関数すべての\nSQL生成・認可・エスケープ経路に対する実測網羅率が 0% 状態",
    ],
    [
        "RV-04: WP フック\nスモーク検証",
        "PASSED\n(5 hooks)",
        "0.59s",
        "ABSPATH・add_action・add_shortcode スタブ下で member-analytics-portal.php\nが正常ロードされ、5フック（REST/Shortcode/AJAX×2/Admin）登録を確認",
    ],
]
tbl.draw_flexible(
    xy=(3, 58.5),
    column_widths=[25, 22, 14, 79],
    row_heights=[7.0, 9.8, 9.8, 9.6, 9.6, 9.8],
    data=rows,
)

save()
```
