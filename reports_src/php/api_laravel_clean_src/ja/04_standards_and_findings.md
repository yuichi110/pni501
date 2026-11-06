# 4. 検査指標・ルール適合マトリクスと指摘一覧

本章では、`php_api_laravel_clean` ワークフロー（Run ID: `wf-42f8fbd7`）で実行した全8監査ステップのスコア比較（弱点順）、評価対象となった全17エンジニアリングルールの適合判定マトリクス（`FAIL -> WARN -> PASS -> NOT_APPLICABLE`）、および重要度順に正規化された全12件の指摘事項（`MEDIUM: 1` / `LOW: 6` / `INFO: 5`、`CRITICAL`・`HIGH` 該当なし）を網羅的に提示する。

```drawlib file=audit_dimensions_barchart.png caption="図4-1: 実行監査ステップ別スコア比較 (弱点順: Weakest -> Strongest 全8ステップ)"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.styles import Styles

setup(width=146, height=64, dpi=150)

chart = BarChart(
    axis_line_style=Styles.Neutral,
    grid_style=Styles.NeutralThin,
    axis_text_style=Styles.DarkBold.patch(text_size=8.5),
    value_text_style=Styles.DarkBold.patch(text_size=9.2),
    background_style=Styles.Neutral.patch(shape_r=2.0),
    categories=[
        "動的Web侵入\n(82 / A)",
        "脆弱性・API\n(93 / S)",
        "12-Factor/PRR\n(93 / S)",
        "リポジトリ構造\n(94 / S)",
        "供給網統治\n(94 / S)",
        "コンテナ実行\n(94 / S)",
        "PHPUnit監査\n(95 / S)",
        "PHP AST品質\n(96 / S)",
    ],
    orientation="vertical",
    bar_width_ratio=0.56,
    bar_r=1.0,
    width=134,
    height=54,
    title="全8監査ステップ 健全性スコア比較 (0 - 100点 / Grade A〜S)",
    title_style=Styles.DarkBold.patch(text_size=10.8),
)
chart.add_series("監査ステップスコア", [82, 93, 93, 94, 94, 94, 95, 96], style=Styles.Primary)
chart.draw(xy=(6, 5))

save()
```

## ルール適合マトリクス（全17ルール：`FAIL: 0` / `WARN: 4` / `PASS: 12` / `N/A: 1`）

全評価ルールは最悪ステータス優先で集約されており、`FAIL` 判定は **0件** である。軽微な改善余地として `WARN` となった4ルールはいずれも本番運用基盤・HTTP応答ヘッダ・コンテナ OS 層・CI 自動化の周辺設定（`php -S` 開発サーバ SAPI 起因の `TRACE` 応答・`nosniff` 未付与・`cli-server` URI 解決、Debian 12 OS ベースイメージ更新、`public/index.php` の Clover 集計対象外、`.github/dependabot.yml` 未配置）に限定されており、PHP アプリケーション本体の設計・型安全・テスト・Laravel 規約・12-Factor 構成・コードセキュリティの12ルールはすべて `PASS` を達成している。

```drawlib file=rule_compliance_matrix.png caption="図4-2: エンジニアリングルール適合マトリクス (FAIL -> WARN -> PASS -> N/A 全17ルール)"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=136, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=9.1),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.5),
    border_style=Styles.NeutralThin,
)
rows = [
    ["判定", "ルールID", "代表評価ステップ", "決定的エビデンス要約"],
    ["WARN", "common/production_readiness", "service_readiness_audit", "/up・/healthz・HEALTHCHECK済だが CMD が単一スレッド php -S かつ PSR-3 ログ未導入"],
    ["WARN", "common/runtime_verification", "container_runtime_audit", "PHPUnit 16/16・PCOV 100%(97/97)・/up 200合格。public/ が Clover 計測対象外"],
    ["WARN", "common/security_vulnerability", "web_penetration_audit", "App CVE 0・DAST CRIT/HIGH 0(18 probes)。OS層CVE・TRACE/nosniff/URI解決のみWARN"],
    ["WARN", "common/supply_chain", "repo_structure_audit", "composer.lock・SHA固定CI・UID 10001済だが Dependabot 不在・LICENSE 1行要約"],
    ["PASS", "common/architecture", "php_ast_audit", "循環依存 0件・境界違反 0件。routes -> Controller -> Service -> Repository -> Record"],
    ["PASS", "common/documentation", "repo_structure_audit", "README.md (3見出し14行) と SECURITY.md による構成概要・テスト手順・脆弱性報告窓口"],
    ["PASS", "common/git_workflow", "repo_structure_audit", ".gitignore 完備 (/vendor/, .env, *.sqlite)、main push / PR で GitHub Actions 自動実行"],
    ["PASS", "common/maintainability", "php_ast_audit", "全7ファイル 252 LOC (最大63 LOC)、16関数、複雑関数・過剰引数・グローバル状態 0件"],
    ["PASS", "common/security", "repo_structure_audit", "PDOプリペアド・SKU正規表現・hash_equals定数時間検証・random_bytes(8)・秘密混入 0件"],
    ["PASS", "common/twelve_factor", "service_readiness_audit", "config/fulfillment.php へ環境変数集約、final readonly ステートレス設計、外部PDO注入"],
    ["PASS", "php/code_quality", "php_ast_audit", "Import衛生 100.0%・PHPDoc網羅率 100.0%・シグネチャ不一致 0件・JSON_THROW_ON_ERROR徹底"],
    ["PASS", "php/dependencies", "repo_structure_audit", "php ^8.3・PSR-4 (App\\, Tests\\)・optimize-autoloader=true・未固定依存 0件"],
    ["PASS", "php/frameworks/laravel", "php_ast_audit", "OrderRecord::$fillable 明示許可リスト、auth:sanctum 適用、薄型32 LOC Controller"],
    ["PASS", "php/modern_stack", "repo_structure_audit", "全ファイル strict_types=1、readonly クラス・コンストラクタ昇格、レガシー構文 0件"],
    ["PASS", "php/testing", "php_test_audit", "PHPUnit 10.5 厳格設定 (failOnRisky/Warning)、sqlite::memory: 8テスト・モジュール網羅100%"],
    ["PASS", "php/typing", "php_ast_audit", "ネイティブ型安全率 100.0%、型不備・弱い型・@phpstan-ignore 抑制すべて 0件"],
    ["N/A", "php/frameworks/wordpress", "php_ast_audit", "Laravel / PHPUnit / PHPStan 構成であり WordPress フック・$wpdb は非該当"],
]
tbl.draw_flexible(
    xy=(3, 133),
    column_widths=[12, 34, 31, 63],
    row_heights=[7.4] + [7.2] * 17,
    data=rows,
)

save()
```

## 重要度順 指摘事項一覧（全12件：`CRITICAL: 0` / `HIGH: 0` / `MEDIUM: 1` / `LOW: 6` / `INFO: 5`）

すべての指摘は実在するリポジトリ相対パス・行番号・決定的ファクト（および `.pni/pentests/` プローブ結果）に紐付けられている。高深刻度（`CRITICAL` / `HIGH`）の欠陥は一切検出されておらず、`Dockerfile`・`public/index.php`・`.github/workflows/ci.yml`・`phpunit.xml`・`LICENSE` を中心とした局所的・非破壊な改善で全項目を解消できる。

```drawlib file=findings_evidence_table.png caption="図4-3: 重要度順 検出指摘一覧 (MEDIUM 1件 -> LOW 6件 -> INFO 5件 / 計12件)"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=134, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=8.6),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.1),
    border_style=Styles.NeutralThin,
)
rows = [
    ["重要度", "ルールID", "該当箇所", "検出事象・決定的根拠", "推奨修正策"],
    ["MED", "common/\nsecurity_vulnerability", "Dockerfile:20", "DAST SEC-06: php -S が TRACE / -> 200\n応答(CWE-693)かつ X-Powered-By 露出", "本番SAPI移行で TRACE 405 遮断\nおよび expose_php=Off 適用"],
    ["LOW", "common/\nproduction_readiness", "Dockerfile:20", "CMD が単一ワーカー php -S であり\nService に PSR-3 監査ログが未導入", "PHP-FPM / FrankenPHP 移行と\nLoggerInterface JSON監査ログ注入"],
    ["LOW", "common/supply_chain", ".github/workflows/\nci.yml:1", "Dependabot 設定が不在で CI が\nPHPUnit のみ (PHPStan/Pint 未実行)", "dependabot.yml 追加と CI での\nphpstan analyse / pint --test 実行"],
    ["LOW", "common/supply_chain", "LICENSE:1", "LICENSE が Apache-2.0 の1行要約\nのみで SPDX 標準条項全文が未記載", "Apache License 2.0 公式全文と\n著作権 APPENDIX へ拡充"],
    ["LOW", "common/\nsecurity_vulnerability", "Dockerfile:1", "App CVE 0件だが debian 12.7 OS層に\nCRIT 28件・libsqlite3-dev 残存", "最新 php:8.3-bookworm 更新と\nマルチステージビルドで dev 除外"],
    ["LOW", "common/\nsecurity_vulnerability", "public/index.php:31", "DAST: cli-server下で REQUEST_URI が\n'/'(200)へフォールバック・nosniff欠落", "$_SERVER['REQUEST_URI'] 参照化と\nX-Content-Type-Options: nosniff付与"],
    ["LOW", "common/\nruntime_verification", "phpunit.xml:12", "<source> が app/ のみで index.php\n(28 LOC) が Clover 計測対象外", "public/ を <include> に追加し\nbuildHealthResponse 単体テスト追加"],
    ["INFO", "common/architecture", ".../Repositories/\nOrderRepository.php:24", "__construct 内で CREATE TABLE を\n実行し具象クラスを直接注入", "DDL をマイグレーションへ分離し\nOrderRepositoryInterface を抽出"],
    ["INFO", "php/dependencies", "composer.lock:7", "require-dev 3件に対し lock 側の\npackages-dev が空配列のまま", "composer update --lock を実行し\n開発ツールのハッシュも完全固定"],
    ["INFO", "common/documentation", "README.md:14", "README 14行に Docker 起動手順や\nHTTP リクエスト/応答例が未記載", "docker build/run と Sanctum 付き\nPOST /api/orders curl 例を追記"],
    ["INFO", "php/testing", "tests/OrderFulfillment\nServiceTest.php:54", "qty=0 は検証済だが qty=1001 上限と\nヘルス 404 分岐の単体検証が未追加", "DataProvider で qty=1001・LIMIT\nクランプ・404 応答テストを追加"],
    ["INFO", "php/typing", ".../Models/\nOrderRecord.php:38", "$status が plain string 型であり\nController 戻り値が array<string,mixed>", "OrderStatus: string Backed Enum と\n配列シェイプ PHPDoc を導入"],
]
tbl.draw_flexible(
    xy=(3, 131),
    column_widths=[13, 27, 29, 39, 32],
    row_heights=[7.4] + [9.9] * 12,
    data=rows,
)

save()
```
