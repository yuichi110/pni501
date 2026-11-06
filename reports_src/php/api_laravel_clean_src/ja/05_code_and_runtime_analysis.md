# 5. 詳細分析：コード品質・テスト・動的検証

本章では、PHP AST 静的解析によって計測された全7モジュールのコード品質・SIG 保守性・厳格型安全性・12-Factor 運用準備指標と、隔離 Docker コンテナ（PHP `8.3.36` / Composer / PHPUnit `10.5.66` + PCOV `1.0.12`）上で実行された `Dockerfile` クリーンビルド、オフライン構文検査・単体テスト、PCOV 実測カバレッジ、および `php -S` 起動スモーク検証の結果を詳細に分析する。

```drawlib file=code_module_quality_heatmap.png caption="図5-1: 全7ソースモジュール × 品質ディメンション適合度マトリクス (0 - 100%)"
from drawlib.canvas import save, setup
from drawlib.charts.heatmap import HeatmapChart
from drawlib.styles import Styles

setup(width=146, height=70, dpi=150)

hm = HeatmapChart(
    min_style=Styles.WarningNeutral,
    max_style=Styles.Primary,
    x_categories=["strict_types", "Import衛生", "厳格型安全", "PHPDoc率", "PCOV行網羅"],
    y_categories=[
        "public/index.php (28)",
        "routes/api.php (8)",
        "OrderRepository (63)",
        "OrderFulfillmentSvc (50)",
        "OrderPayload (33)",
        "OrderController (32)",
        "OrderRecord (38)",
    ],
    axis_line_style=Styles.Neutral,
    axis_text_style=Styles.DarkBold.patch(text_size=9.5),
    value_text_style=Styles.DarkBold.patch(text_size=9.5),
    background_style=Styles.Neutral.patch(shape_r=2.0),
    width=114,
    height=56,
    min_value=0.0,
    max_value=100.0,
    cell_gap=0.8,
    cell_r=0.8,
    value_format=lambda v: f"{v:.1f}%",
    title="全7モジュール 静的AST品質・PCOV動的カバレッジ適合マトリクス",
    title_style=Styles.DarkBold.patch(text_size=10.5),
)
hm.add_row("public/index.php (28)", [100.0, 100.0, 100.0, 100.0, 0.0])
hm.add_row("routes/api.php (8)", [100.0, 100.0, 100.0, 100.0, 0.0])
hm.add_row("OrderRepository (63)", [100.0, 100.0, 100.0, 100.0, 100.0])
hm.add_row("OrderFulfillmentSvc (50)", [100.0, 100.0, 100.0, 100.0, 100.0])
hm.add_row("OrderPayload (33)", [100.0, 100.0, 100.0, 100.0, 100.0])
hm.add_row("OrderController (32)", [100.0, 100.0, 100.0, 100.0, 100.0])
hm.add_row("OrderRecord (38)", [100.0, 100.0, 100.0, 100.0, 100.0])
hm.draw(xy=(6, 6))
hm.draw_colorbar(
    xy=(126, 12),
    text_style=Styles.Dark.patch(text_size=9.2),
    length=42.0,
    thickness=2.6,
    orientation="vertical",
    label="適合率(%)",
)

save()
```

## 静的コード品質・SIG 保守性・型安全性・12-Factor 評価

- **SIG 保守性・Import 衛生・PHPDoc 網羅率 (`100.0%`)**: 全7ファイル合計 `252` LOC（最大は `OrderRepository.php` の `63` LOC、平均 `36` LOC）と極めて高い凝集度を維持している。循環複雑度超過（`complex_functions = 0`）・過剰パラメータ（`excessive_parameters = 0`）・グローバル状態参照（`global_state_usages = 0`）・バグリスクイディオム（`bug_risk_idioms = 0`）はいずれもゼロであり、PSR-4 Import 衛生・PHPDoc カバレッジともに `100.0%`（シグネチャ不一致 `0` 件）を達成している。
- **厳格型安全性 (`declare(strict_types=1)` 100%)**: 全7ファイルの先頭（3行目）に `declare(strict_types=1);` が宣言され、すべての引数・戻り値・プロパティに PHP 8.3 ネイティブ型が付与されている（`type_safety_coverage_pct = 100.0%`、`weak_type_usages = 0`、`unscoped_type_ignores = 0`）。金額計算も浮動小数点を排し整数セント（`int $unitPriceCents`, `int $totalCents`）で統一されている。
- **12-Factor 運用準備性**: 環境変数読み取り（`APP_NAME`, `DB_DSN`）と Webhook タイムアウト（`webhook_timeout_seconds = 5`）は `config/fulfillment.php` の1箇所に集約され（`scattered_env_access = 0`、`missing_io_timeouts = 0`、`unstructured_logging = 0`）、ドメイン層・コントローラ層は完全にステートレスな `final readonly class` として実装されている。

## コンテナ動的検証（クリーンビルド・オフライン PHPUnit・PCOV 100%・起動検証・DAST連動）

PNI の `run_check`（`status = "passed"`）により、リポジトリ同梱 `Dockerfile` のビルド（`1.54s`、`passed`）および PHP `8.3.36` + Composer + PCOV `1.0.12` 検証ハーネスビルド（`0.92s`、`passed`）を実行した。ネットワーク完全遮断（`--network=none`）環境下での `php -l` 全ファイル構文検査と PHPUnit `10.5.66` 実行（`8` テストメソッド / `19` アサーション / JUnit `16` ノード、`1.61s`）は失敗ゼロで完走し、PCOV Clover 計測対象である `app/` 配下全5クラスすべてで **実測行カバレッジ `100.0%`（`97 / 97` ステートメント、未実行行 `0`）** を達成した。さらに Web API 起動スモーク検証（`smoke_check`）も `GET /up -> HTTP 200`（`0.98s`、`status = "passed"`）で合格し、続く `web_pentest`（`.pni/pentests/examples/php/api_laravel_clean/`、全18 HTTP プローブ）によって `public/index.php` や `/api/orders` の実 HTTP 応答まで一貫検証された。なお図5-1の通り `phpunit.xml` の `<source>` が `app` のみを指定しているため、`public/index.php` と `routes/api.php` は Clover カバレッジ集計対象外となっている。

```drawlib file=runtime_verification_breakdown.png caption="図5-2: コンテナ動的検証KPIとPCOV実測カバレッジ内訳 (app/ 全5クラス 97/97行 = 100.0%)"
from drawlib.canvas import save, setup
from drawlib.smartarts import KpiCards, Table
from drawlib.styles import Styles

setup(width=146, height=84, dpi=150)

kpis = KpiCards(
    style=Styles.Neutral,
    metric_style=Styles.SuccessBold.patch(text_size=12.0),
    text_style=Styles.DarkBold.patch(text_size=9.5),
    description_style=Styles.Dark.patch(text_size=9.0),
    accent_position="top_bar",
    metric_layout="top_stack",
    spacing=2.5,
)
kpis.add(
    "PASSED (1.54s)",
    "Dockerfile クリーンビルド",
    "PHP 8.3ハーネスも合格 (0.92s)",
    accent_style=Styles.Success,
)
kpis.add(
    "8テスト / 19検証",
    "オフライン PHPUnit 10.5",
    "--network=none / 1.61s / 失敗0",
    accent_style=Styles.Success,
)
kpis.add(
    "100.0% (97/97)",
    "PCOV 実測行カバレッジ",
    "app/ 全5クラス 未実行行 0件",
    accent_style=Styles.Success,
)
kpis.add(
    "PASSED (200 OK)",
    "起動スモーク & 18 Probes",
    "GET /up -> 200 + DAST 13/18合格",
    accent_style=Styles.Success,
)
kpis.draw(xy=(3, 62), width=140, height=19, columns=4)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=9.2),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.5),
    border_style=Styles.NeutralThin,
)
rows = [
    ["対象モジュール", "PCOV行網羅率", "実行 / 総ステートメント", "検証済みロジック・Cloverスコープ備考"],
    ["app/Repositories/OrderRepository.php", "100.0%", "36 / 36", "未実行行なし (DDL初期化・プリペアドINSERT・LIMITクランプSELECT)"],
    ["app/Services/OrderFulfillmentService.php", "100.0%", "23 / 23", "未実行行なし (通常計算・10%割引・単価<=0例外・HMAC定数時間検証)"],
    ["app/DTO/OrderPayload.php", "100.0%", "14 / 14", "未実行行なし (fromArray・空顧客ID・SQLi風不正SKU・qty<=0例外)"],
    ["app/Http/Controllers/OrderController.php", "100.0%", "14 / 14", "未実行行なし (store 201応答・listRecent配列シリアライズ往復)"],
    ["app/Models/OrderRecord.php", "100.0%", "10 / 10", "未実行行なし (readonly生成・fillableColumns・toArray変換)"],
    ["public/index.php & routes/api.php", "対象外 (DAST検証)", "phpunit.xml <source>外", "smoke(/up->200)とweb_pentest 18プローブで検証・P2でClover追加"],
]
tbl.draw_flexible(
    xy=(3, 59),
    column_widths=[44, 20, 24, 52],
    row_heights=[7.2] + [7.8] * 6,
    data=rows,
)

save()
```
