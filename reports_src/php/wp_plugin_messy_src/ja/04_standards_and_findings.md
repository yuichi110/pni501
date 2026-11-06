# 4. 評価指標とルール適合マトリクス

本章では、`php_wp_plugin_messy` ワークフローで実行した7つの評価ステップのスコア比較（弱点順）、全17エンジニアリングルールの適合判定マトリクス（`FAIL -> WARN -> NOT_APPLICABLE`）、および重要度順に正規化された全21件の指摘事項（`CRITICAL -> HIGH -> MEDIUM -> LOW`）を一覧化する。

```drawlib file=audit_dimensions_barchart.png caption="実行監査ステップ別スコア比較 (弱点順: Weakest -> Strongest)"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.styles import Styles

setup(width=146, height=64, dpi=150)

chart = BarChart(
    axis_line_style=Styles.Neutral,
    grid_style=Styles.NeutralThin,
    axis_text_style=Styles.DarkBold.patch(text_size=8.6),
    value_text_style=Styles.DarkBold.patch(text_size=9.2),
    background_style=Styles.Neutral.patch(shape_r=2.0),
    categories=[
        "PHPテスト\n(5 / D)",
        "脆弱性監査\n(8 / D)",
        "PHP AST\n(14 / D)",
        "構造・包装\n(18 / D)",
        "本番稼働準備\n(20 / D)",
        "供給網衛生\n(20 / D)",
        "コンテナ検証\n(45 / D)",
    ],
    orientation="vertical",
    bar_width_ratio=0.56,
    bar_r=1.0,
    width=134,
    height=54,
    title="監査ステップ別 健全性スコア比較 (全7ステップ Grade D: 5 - 45点)",
    title_style=Styles.DarkBold.patch(text_size=10.2),
)
chart.add_series("監査ステップスコア", [5, 8, 14, 18, 20, 20, 45], style=Styles.Danger)
chart.draw(xy=(6, 5))

save()
```

## ルール適合マトリクス（全17ルール：`FAIL: 14` / `WARN: 2` / `PASS: 0` / `N/A: 1`）

評価対象の全17ルールは最悪ステータス優先で集約されており、`php/frameworks/wordpress` を含む **14ルールが `FAIL`**、2ルール（`common/git_workflow`・`common/maintainability`）が **`WARN`**、WordPress プラグインのため対象外となる `php/frameworks/laravel` が **`NOT_APPLICABLE`** となり、`PASS` 達成ルールは `0` 件であった。

```drawlib file=rule_compliance_matrix.png caption="エンジニアリングルール適合マトリクス (FAIL -> WARN -> N/A 全17ルール)"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=134, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=8.5),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=8.9),
    border_style=Styles.NeutralThin,
)
rows = [
    ["判定", "ルールID", "代表評価ステップ", "決定的エビデンス要約"],
    ["FAIL", "common/architecture", "php_ast_audit", "0クラス・7グローバル関数でHTTP入力/wpdb/外部通信/HTMLが混在"],
    ["FAIL", "common/documentation", "repo_structure_audit", "README.md が実質2行のみで前提・REST/AJAX仕様・テスト手順不在"],
    ["FAIL", "common/production_readiness", "service_readiness_audit", "settings-page.php:21 file_get_contents Timeout未設定・@抑制"],
    ["FAIL", "common/runtime_verification", "container_runtime_audit", "php -lと5フック登録は合格するが PHPUnit 0件・実測網羅率未計測"],
    ["FAIL", "common/security", "repo_structure_audit", "whsec直書き・REST '__return_true'・'read'権限・生SQL文字列結合"],
    ["FAIL", "common/security_vulnerability", "php_ast_audit", "CWE-89 SQLi 3件・CWE-79 XSS 4箇所・無認証API境界4件・OS層CVE"],
    ["FAIL", "common/supply_chain", "repo_structure_audit", "composer.json/lock・LICENSE・SECURITY.md・Dependabot・CI全欠落"],
    ["FAIL", "common/twelve_factor", "service_readiness_audit", "秘密鍵/外部URL/wp_map_events直書き・print_r標準出力デバッグ"],
    ["FAIL", "php/code_quality", "php_ast_audit", "PSR-4不在・手動require_once 3件・GET/POST直参照10件・PHPDoc 0%"],
    ["FAIL", "php/dependencies", "repo_structure_audit", "raw_php構成・Requires PHP: 7.4 (EOL) 指定・PSR-4オートロード未導入"],
    ["FAIL", "php/frameworks/wordpress", "php_ast_audit", "WP規約違反16件: ABSPATH欠落・__return_true・nopriv・Nonce不在"],
    ["FAIL", "php/modern_stack", "repo_structure_audit", "EOL PHP 7.4・file_get_contents無制限通信・print_r/echo json"],
    ["FAIL", "php/testing", "php_test_audit", "テストファイル0件・テスト関数0件・WP_UnitTestCase/PHPUnit不在"],
    ["FAIL", "php/typing", "php_ast_audit", "strict_types=1 0/4ファイル・引数/戻り値型宣言 0% (型問題11件)"],
    ["WARN", "common/git_workflow", "repo_structure_audit", "秘密ファイルコミットは0件だが .gitignore 不在でvendor等混入リスク"],
    ["WARN", "common/maintainability", "php_ast_audit", "関数自体は短いが @ エラー抑制・wp_接頭辞直書き・13箇所グローバル結合"],
    ["N/A", "php/frameworks/laravel", "php_ast_audit", "detected_frameworks=['wordpress'] のため Laravel 規約は対象外"],
]
tbl.draw_flexible(
    xy=(3, 131),
    column_widths=[11, 34, 29, 66],
    row_heights=[7.2] + [7.1] * 17,
    data=rows,
)

save()
```

## 重要度順 指摘事項一覧（全21件：`CRITICAL: 7` / `HIGH: 7` / `MEDIUM: 6` / `LOW: 1`）

各ステップから抽出・重複排除された全21件の指摘事項を `CRITICAL -> HIGH -> MEDIUM -> LOW` の確定順序で以下に示す。

```drawlib file=findings_evidence_table.png caption="重要度順 検出指摘一覧 (CRITICAL -> HIGH -> MEDIUM -> LOW 全21件)"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=174, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=7.9),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=8.6),
    border_style=Styles.NeutralThin,
)
rows = [
    ["重要度", "ルールID", "該当箇所", "検出事象・決定的根拠", "推奨修正策"],
    ["CRIT", "common/security", "rest-endpoints:3", "map_webhook_secret ハードコード直書き", "鍵失効・wp-config/getenv注入・hash_equals"],
    ["CRIT", "common/security_vulnerability", "ajax-handlers:3", "wp_ajax_nopriv 公開 + POST['term'] SQLi", "nopriv廃止・Nonce/権限・wpdb->prepare"],
    ["CRIT", "common/security_vulnerability", "ajax-handlers:10", "SEC-04/05: 未認証 admin-ajax LIKE SQL結合", "current_user_can + esc_like + prepare"],
    ["CRIT", "common/security_vulnerability", "rest-endpoints:7", "SEC-04/05: /export __return_true + SQLi", "list_users権限・args検証・prepare適用"],
    ["CRIT", "php/frameworks/wordpress", "settings-page:10", "cap='read'登録 + Nonce不在のオプション更新", "manage_options化 + check_admin_referer"],
    ["CRIT", "php/frameworks/wordpress", "ajax-handlers:17", "purge_logs Nonce/権限欠落 + DELETE SQLi/XSS", "check_ajax_referer + prefix + prepare"],
    ["CRIT", "php/frameworks/wordpress", "rest-endpoints:10", "REST __return_true で全会員メールPII露出", "permission_callback厳格化・print_r削除"],
    ["HIGH", "common/production_readiness", "settings-page:21", "file_get_contents Timeout未設定・@抑制", "wp_safe_remote_get(timeout=3) + 非同期化"],
    ["HIGH", "php/dependencies", "portal.php:7", "Requires PHP: 7.4 (EOL)・composer/PSR-4不在", "PHP ^8.2 + composer.json/lock + PSR-4化"],
    ["HIGH", "common/security_vulnerability", "settings-page:26", "GET['tab'] の <h1> / input value 未エスケープ", "sanitize_key + esc_html / esc_attr 徹底"],
    ["HIGH", "php/frameworks/wordpress", "portal.php:1", "全4ファイルで先頭 ABSPATH 直接実行ガード欠落", "全PHP先頭に if(!defined('ABSPATH')) exit"],
    ["HIGH", "php/frameworks/wordpress", "portal.php:20", "ショートコード GET['badge_label'] 反射XSS", "shortcode_atts + sanitize + esc_html"],
    ["HIGH", "common/runtime_verification", "portal.php:15", "5フック登録合格に対し単体テスト0・網羅率未計測", "PHPUnit + PCOV でオフライン網羅率80%+"],
    ["HIGH", "php/testing", "portal.php:1", "WP_UnitTestCase/PHPUnit 自動テスト完全不在", "認可401/403・Nonce・SQL境界テスト追加"],
    ["MED", "php/code_quality", "settings-page:27", "<script>タグ直書き・13箇所グローバル状態結合", "wp_enqueue_script化・Repository分離"],
    ["MED", "common/twelve_factor", "rest-endpoints:21", "?debug=1 で print_r(rows) 生データ標準出力", "print_r削除・PSR-3 構造化JSONログ導入"],
    ["MED", "common/supply_chain", "README.md:1", "LICENSE / SECURITY.md / Dependabot / ignore不在", "GPLv2+ LICENSE・SECURITY・CI整備"],
    ["MED", "common/supply_chain", "portal.php:1", "CIワークフロー不在で静的/動的検査が未自動化", "最小権限 GitHub Actions CI の追加"],
    ["MED", "common/documentation", "README.md:1", "2行のみで前提・REST/AJAX仕様・テスト手順欠落", "Standard Readme 準拠で仕様・手順明記"],
    ["MED", "php/typing", "rest-endpoints:14", "strict_types=1 0件・全7関数の型宣言欠落(0%)", "declare(strict_types=1) + ネイティブ型付与"],
    ["LOW", "common/security_vulnerability", "portal.php:7", "composer.lock不在・Debian OS層 285件高深刻CVE", "composerロック化・最小PHP 8.3+ベース採用"],
]
tbl.draw_flexible(
    xy=(3, 170.5),
    column_widths=[10, 31, 21, 40, 38],
    row_heights=[7.0] + [7.6] * 21,
    data=rows,
)

save()
```
