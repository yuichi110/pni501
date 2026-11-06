# 5. コード品質・型安全性・ランタイム検証詳細

本章では、PHP AST 静的解析から得られたコード品質・型安全性指標（`import_hygiene=0.0%`, `type_safety=0.0%`, `docstring=0.0%`）の内訳と、隔離 Docker コンテナ上で実行されたビルド・`php -l` 構文検査・自動テスト・`php -S` 起動スモーク検証（RV-01〜RV-04）の決定的結果を詳細に分析する。

```drawlib file=code_module_quality_heatmap.png caption="モジュール × 品質ディメンション適合度マトリクス (0 - 100%)"
from drawlib.canvas import save, setup
from drawlib.charts.heatmap import HeatmapChart
from drawlib.styles import Styles

setup(width=146, height=68, dpi=150)

hm = HeatmapChart(
    min_style=Styles.DangerNeutral,
    max_style=Styles.Primary,
    x_categories=["PSR-4 import", "strict_types・型", "PHPDoc整備", "保守性・非循環", "PHPUnit検証度"],
    y_categories=[
        "index.php (29 LOC)",
        "login.php (20 LOC)",
        "includes/db.php (16 LOC)",
        "product.php (15 LOC)",
        "includes/helpers.php (15 LOC)",
        "admin_backup.php (12 LOC)",
    ],
    axis_line_style=Styles.Neutral,
    axis_text_style=Styles.DarkBold.patch(text_size=8.8),
    value_text_style=Styles.DarkBold.patch(text_size=9.2),
    background_style=Styles.Neutral.patch(shape_r=2.0),
    width=114,
    height=54,
    min_value=0.0,
    max_value=100.0,
    cell_gap=0.8,
    cell_r=0.8,
    value_format=lambda v: f"{v:.0f}%",
    title="全6 PHPファイル 静的品質・厳格型・テスト検証マトリクス",
    title_style=Styles.DarkBold.patch(text_size=10.2),
)
hm.add_row("index.php (29 LOC)", [0.0, 0.0, 0.0, 15.0, 0.0])
hm.add_row("login.php (20 LOC)", [0.0, 0.0, 0.0, 20.0, 0.0])
hm.add_row("includes/db.php (16 LOC)", [0.0, 0.0, 0.0, 10.0, 0.0])
hm.add_row("product.php (15 LOC)", [0.0, 0.0, 0.0, 20.0, 0.0])
hm.add_row("includes/helpers.php (15 LOC)", [0.0, 0.0, 0.0, 15.0, 0.0])
hm.add_row("admin_backup.php (12 LOC)", [0.0, 0.0, 0.0, 25.0, 0.0])
hm.draw(xy=(6, 6))
hm.draw_colorbar(
    xy=(126, 13),
    text_style=Styles.Dark.patch(text_size=9.0),
    length=40.0,
    thickness=2.6,
    orientation="vertical",
    label="適合率(%)",
)

save()
```

## 静的コード品質・厳格型安全性・保守性の欠陥詳細

- **`declare(strict_types=1)` カバレッジ 0% とネイティブ型不在 (`php/typing`)**: 全6ファイル（`index.php:1`, `product.php:1`, `login.php:1`, `admin_backup.php:1`, `includes/db.php:1`, `includes/helpers.php:1`）で `declare(strict_types=1);` が宣言されておらず、PHP の暗黙スカラー型変換が全面的に有効となっている。また定義されている2つの関数 `get_db_conn()`（`includes/db.php:9`）と `fetch_partner_catalog($endpoint)`（`includes/helpers.php:4`）にも引数型・戻り値型および `/** ... */` PHPDoc が一切付与されていない（`type_safety_coverage_pct=0.0%`, `docstring_coverage_pct=0.0%`）。
- **スーパーグローバル直参照16箇所 + `global` 変数結合 (`php/code_quality`, `common/maintainability`)**: リクエスト抽象化層が存在せず、`$_GET`（8箇所）・`$_POST`（5箇所）・`$_COOKIE`（2箇所）・`$_SERVER`（1箇所）・`$_SESSION` に加え、`includes/db.php:11` の `global $LAST_DB_ERR;` を含む計 **17箇所の可変グローバル状態結合** が確認された。特に `login.php:6` の `extract($_POST);` は任意の POST キーでローカルシンボルテーブルを上書きできる危険なレガシーイディオムである。
- **`@mysqli_connect` エラー握り潰し・`die()`・cURL タイムアウト欠如 (`common/production_readiness`)**: `includes/db.php:12` は `@mysqli_connect(...)` の `@` 演算子で接続失敗の原因（認証エラー・DNS失敗・ソケット枯渇）を完全に握り潰す一方、`product.php:9` は `die("Database query failed: " . mysqli_error($conn));` で内部 SQL エラーメッセージをそのままクライアントへ返してプロセスを強制終了する。さらに `includes/helpers.php:7-13` は `CURLOPT_CONNECTTIMEOUT` / `CURLOPT_TIMEOUT` 未設定のまま外部通信を行い、`$_GET['debug']` 指定時に生レスポンスを `var_dump($raw)` で出力している。

## コンテナ動的検証（`php -l` 構文通過・テスト0件・`php -S` 起動スモーク結果）

隔離 Docker 環境における動的検証（`run_check`）では、同梱 `Dockerfile` ビルド（`1.11s`）、PHP 8.3 ハーネスビルド（`0.94s`）、PHP 8.3.36 構文検査（`php -l`、`1.01s`）、および `php -S` 組込みサーバ起動スモーク応答（`smoke_check: status=passed`、`/up -> 200` フォールバック応答、`1.06s`）は通過したが、PHPUnit テストが `0` 件のため実測カバレッジは完全に未計測（`measured=False`）であり、専用の `/healthz` ルートや `Dockerfile` の `HEALTHCHECK` 命令も欠如している。

```drawlib file=runtime_verification_breakdown.png caption="コンテナ動的検証KPIと RV-01〜RV-04 ゲート別実行結果内訳"
from drawlib.canvas import save, setup
from drawlib.smartarts import KpiCards, Table
from drawlib.styles import Styles

setup(width=146, height=86, dpi=150)

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
    "PASSED (1.11s)",
    "同梱 Dockerfile ビルド",
    "php:7.4-apache + mysqli",
    accent_style=Styles.Success,
)
kpis.add(
    "PASSED (1.01s)",
    "PHP 8.3 構文検査 (php -l)",
    "Harness 0.94s / 6件構文OK",
    accent_style=Styles.Success,
)
kpis.add(
    "0 TESTS (N/A)",
    "オフライン PHPUnit",
    "自動テスト0件・pcov未計測",
    accent_style=Styles.Warning,
    metric_style=Styles.WarningBold.patch(text_size=11.8),
)
kpis.add(
    "PASSED* (1.06s)",
    "Web 起動スモーク応答",
    "/up -> 200 (index.php fallback)",
    accent_style=Styles.Warning,
    metric_style=Styles.WarningBold.patch(text_size=11.6),
)
kpis.draw(xy=(3, 63.5), width=140, height=19.5, columns=4)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=8.6),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.0),
    border_style=Styles.NeutralThin,
)
rows = [
    ["検証ゲート", "ステータス", "所要時間", "決定的実行結果・ログエビデンス"],
    ["RV-01a: 同梱\nDockerfile", "PASSED\n(exit 0)", "1.11s", "FROM php:7.4-apache 上で docker-php-ext-install mysqli が成功。\nただし EOL ランタイム・root 実行・OS CVE 12,051件を内包"],
    ["RV-01b: PHP 8.3\nハーネスビルド", "PASSED\n(exit 0)", "0.94s", "php/raw.dockerfile (PHP_VERSION=8.3) のクリーンイメージビルドが\nエラーなく完了"],
    ["RV-02: オフライン\n構文・単体試験", "PASSED*\n(0 tests)", "1.01s", "--network=none 下で全6ファイルの php -l (PHP 8.3.36) 構文検査は\n通過したが、tests/ 不在のため実行された PHPUnit テストは 0 件"],
    ["RV-03: pcov\n実測カバレッジ", "UNMEASURED\n(measured=false)", "0.00s", "PHPUnit テストが 0 件のため Clover カバレッジは未生成 (line=None%,\nbranch=None%, 0/0 statements) であり回帰防止能力は皆無"],
    ["RV-04: Web API\nスモーク起動", "PASSED*\n(HTTP 200)", "1.06s", "php -S (127.0.0.1:18080) が /up -> 200 を返したが index.php HTML\nへのフォールバック応答であり、専用 /healthz と HEALTHCHECK は不在"],
]
tbl.draw_flexible(
    xy=(3, 60.5),
    column_widths=[24, 21, 14, 81],
    row_heights=[7.0, 10.0, 9.5, 10.2, 10.2, 10.2],
    data=rows,
)

save()
```
