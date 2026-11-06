# 4. 機械的変換（Rector Codemod）と手動ブロッカー分離計画

素 PHP から Laravel 11 へのクロススタック置換（`cross_stack_replacement`）では、Rector 単体でスパゲッティ HTML + 生 SQL スクリプトを自動的に MVC クラスへ分割することはできない。そのため、**ルート分割・Repository/Redis 設計は手動 PR（`PR-02`〜`PR-03`, `PR-05`〜`PR-08`）** で行い、切り出された PHP クラス群に対する **`declare(strict_types=1)` 付与・PHP 8.3 型プロモーション・Laravel 11 規約標準化を Rector 自動パイプライン（`PR-04`）** に担わせる役割分担を徹底する。

```drawlib file=php_codemod_vs_manual_barchart.png caption="変換領域別 Rector 自動規約適用数 vs 手動 Strangler 実装対象数"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.styles import Styles

setup(width=146, height=68, dpi=150)

chart = BarChart(
    axis_line_style=Styles.Neutral,
    grid_style=Styles.NeutralThin,
    axis_text_style=Styles.DarkBold.patch(text_size=8.5),
    value_text_style=Styles.DarkBold.patch(text_size=8.8),
    background_style=Styles.Neutral.patch(shape_r=2.0),
    categories=[
        "PHP 8.3\n構文・型宣言",
        "strict_types=1\n自動付与",
        "Laravel 11\n規約標準化",
        "Eloquent / PDO\nSQLi 根絶",
        "Redis Cart &\nDual-Verify",
        "Nginx Proxy &\nPHP 8.3 Docker",
    ],
    orientation="vertical",
    bar_width_ratio=0.64,
    bar_r=1.0,
    width=134,
    height=50,
    title="領域別 Rector 自動 Codemod 対象数 vs 手動 Strangler Fig 実装対象数",
    title_style=Styles.DarkBold.patch(text_size=10.0),
)
chart.add_series("Rector 自動規約強制 (PR-04 / CI)", [6, 6, 6, 0, 0, 0], style=Styles.Success)
chart.add_series("手動 Strangler ルート・Adapter 実装", [1, 0, 2, 4, 3, 2], style=Styles.Primary)
chart.draw(xy=(6, 11))
chart.draw_legend(
    xy=(18.0, 4.2),
    text_style=Styles.DarkBold.patch(text_size=8.8),
    orientation="horizontal",
    item_gap=8.0,
)

save()
```

## 事前解消必須ブロッカー（BLK-01 〜 BLK-03）と Rector 適用レシピ

```drawlib file=php_codemod_and_blocker_table.png caption="事前解消必須ブロッカー (BLK-01 - BLK-03) と Rector 自動変換レシピ一覧"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=96, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=8.6),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.0),
    border_style=Styles.NeutralThin,
)
rows = [
    ["種別 / ID", "レシピまたはブロッカー項目", "対象範囲", "実行タイミングと運用ルール"],
    [
        "Blocker\nBLK-03 [HIGH]",
        "composer.json / PSR-4 オートローダ\nおよびテストハーネスの完全不在",
        "プロジェクト全体",
        "Phase 0 (PR-01): Composer・Laravel 11 骨格・PHPUnit 11\n・PHPStan Level 6 を初期化してから移行開始する。",
    ],
    [
        "Blocker\nBLK-01/02 [HIGH]",
        "includes/db.php <-> helpers.php\n双方向 include_once 循環依存",
        "includes/ 配下\n2ファイル",
        "Phase 1 (PR-02, PR-03): Eloquent 設定と Partner HTTP\nクライアントを独立 Adapter として分離構築する。",
    ],
    [
        "Rector\nSet 1",
        "Rector\\Set\\ValueObject\\\nLevelSetList::UP_TO_PHP_83",
        "新規・抽出 PHP\n全クラス",
        "Phase 2 (PR-04) 以降 CI 常時強制: Readonly プロパティ、\nコンストラクタ昇格、PHP 8.3 標準構文へ統一。",
    ],
    [
        "Rector\nRule 2",
        "DeclareStrictTypesRector\n(declare(strict_types=1))",
        "app/ config/\ntests/ 全ファイル",
        "Phase 2 (PR-04): 暗黙の型ジャグリング (0e... 緩い比較)\nが二度と混入しないよう全ファイル先頭へ機械挿入。",
    ],
    [
        "Rector\nSet 3",
        "RectorLaravel\\Set\\\nLaravelSetList::LARAVEL_110",
        "Controller / Action\n/ Model 全般",
        "Phase 2 (PR-04): Laravel 11 のスリム Application 構成・\n型付き Casts メソッド規約を機械維持。",
    ],
]
tbl.draw_flexible(
    xy=(3, 93),
    column_widths=[24, 44, 24, 48],
    row_heights=[8.0, 16.5, 16.5, 16.5, 16.5, 16.0],
    data=rows,
)

save()
```
