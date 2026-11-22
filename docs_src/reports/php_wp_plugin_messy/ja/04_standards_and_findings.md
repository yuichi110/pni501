# 4. 監査パイプライン（DAG）・評価基準・指摘事項

本章では、実際に実行された監査パイプライン（DAG）、決定論的ツールの検査スコープ、7 軸スコアのアンカリング（決定論的ベースラインに対する AI 補正 `±10pt` 上限）、全 17 ルールの準拠マトリクス、統合指摘一覧、および機械可読アーティファクトの来歴を透明性高く開示します。

```drawlib align=center code=fold file=audit_pipeline_dag.png caption="実行済み PNI Workflow v2 監査パイプライン DAG（9 論理ステージ・ASK/HYBRID/AI バッジ付き）"
from drawlib.canvas import save, setup
from drawlib.graph import LayerGraph
from drawlib.lines import lines
from drawlib.shapes import rectangle
from drawlib.styles import Styles
from drawlib.text import text

setup(width=198, height=84, dpi=150)

text(
    (99.0, 79.5),
    "Executed Audit Pipeline DAG — php_wp_plugin_messy (wf-3389d5e7)",
    style=Styles.DarkBold.patch(text_size=12.0),
)

g = LayerGraph(
    direction="LR",
    rank_sep=7.2,
    node_sep=3.2,
    edge_routing="orthogonal",
    default_node_width=25.5,
    default_node_height=11.0,
)
g.edge("confirm_plan", "repo_and_deps")
g.edge("repo_and_deps", "ast_and_quality")
g.edge("repo_and_deps", "supply_chain")
g.edge("repo_and_deps", "runtime_verification")
g.edge("repo_and_deps", "security_audit")
g.edge("ast_and_quality", "arch_prr_tests")
g.edge("arch_prr_tests", "output_score")
g.edge("supply_chain", "output_score")
g.edge("runtime_verification", "output_score")
g.edge("security_audit", "output_score")
g.edge("output_score", "create_report")

layout = g.get_layout(width=198.0, height=74.0, margin=5.0)

# Align arch_prr_tests with ast_and_quality (top row) so lower bypass buses stay clear
dy_align = layout["ast_and_quality"].y - layout["arch_prr_tests"].y
layout.offset("arch_prr_tests", dy=dy_align)

bus_in_x = (layout["repo_and_deps"].right + layout["ast_and_quality"].left) / 2.0
bus_out_x = (layout["arch_prr_tests"].right + layout["output_score"].left) / 2.0

def connect_ortho(src_id: str, dst_id: str, mid_x: float | None = None) -> None:
    s = layout[src_id]
    d = layout[dst_id]
    y_shift = 4.5
    if abs(s.y - d.y) < 0.2:
        pts = [(s.right, s.y + y_shift), (d.left, d.y + y_shift)]
    else:
        mx = mid_x if mid_x is not None else (s.right + d.left) / 2.0
        pts = [(s.right, s.y + y_shift), (mx, s.y + y_shift), (mx, d.y + y_shift), (d.left, d.y + y_shift)]
    lines(pts, arrow_head="->", style=Styles.MutedBold)

connect_ortho("confirm_plan", "repo_and_deps")
for mid_id in ["ast_and_quality", "supply_chain", "runtime_verification", "security_audit"]:
    connect_ortho("repo_and_deps", mid_id, mid_x=bus_in_x)
connect_ortho("ast_and_quality", "arch_prr_tests")
connect_ortho("arch_prr_tests", "output_score", mid_x=bus_out_x)
for bypass_id in ["supply_chain", "runtime_verification", "security_audit"]:
    connect_ortho(bypass_id, "output_score", mid_x=bus_out_x)
connect_ortho("output_score", "create_report")

nodes_spec = [
    ("confirm_plan", "[ASK] Confirm Plan\nPlan approved", Styles.SuccessNeutral, Styles.DarkBold),
    ("repo_and_deps", "[HYBRID] Repo/Deps\n4 src, 0 test, 0 dep", Styles.PrimaryNeutral, Styles.DarkBold),
    ("ast_and_quality", "[HYBRID] PHP AST\n5 HIGH CWE, 16 WP", Styles.PrimaryNeutral, Styles.DarkBold),
    ("supply_chain", "[AI] Supply Chain\n3 rules; 1 secret", Styles.SecondaryNeutral, Styles.DarkBold),
    ("runtime_verification", "[HYBRID] Runtime\nphp -l & 5-hook OK", Styles.PrimaryNeutral, Styles.DarkBold),
    ("security_audit", "[HYBRID] Trivy/Sec\n0 app CVEs, 5 sinks", Styles.PrimaryNeutral, Styles.DarkBold),
    ("arch_prr_tests", "[AI] Arch/PRR/Test\n4 layers; 0 PHPUnit", Styles.SecondaryNeutral, Styles.DarkBold),
    ("output_score", "[AI] Emit Score\n60/100 (C) | 15 find", Styles.PrimaryFlat, Styles.WhiteBold),
    ("create_report", "[AI] Report Build\n7-ch EN/JA Drawlib", Styles.Neutral, Styles.DarkBold),
]

for nid, label, box_style, txt_style in nodes_spec:
    n = layout[nid]
    rectangle(
        (n.x, n.y + 4.5),
        width=n.width,
        height=n.height,
        style=box_style.patch(shape_r=1.6),
        text=label,
        text_style=txt_style.patch(text_size=8.4),
    )

legend_items = [
    (31.0, "[ASK] Plan Gate", Styles.SuccessNeutral, Styles.DarkBold),
    (76.0, "[HYBRID] Det. Tool + AI", Styles.PrimaryNeutral, Styles.DarkBold),
    (122.0, "[AI] Qualitative Synthesis", Styles.SecondaryNeutral, Styles.DarkBold),
    (167.0, "Focal: Score Output", Styles.PrimaryFlat, Styles.WhiteBold),
]
for lx, ltxt, lstyle, ltstyle in legend_items:
    rectangle(
        (lx, 5.0),
        width=38.0,
        height=5.2,
        style=lstyle.patch(shape_r=1.2),
        text=ltxt,
        text_style=ltstyle.patch(text_size=8.8),
    )

save()
```

## 検査スコープおよび実行した決定論的ツール

| スコープ項目 | 監査実行値 |
| :--- | :--- |
| **対象ルート・パス** | `examples/php/wp_plugin_messy`（`source=['.']`, `tests=['tests']`, `docs=['README.md']`, `exclude=[]`） |
| **言語・フレームワーク** | 主要言語: `php` ・ 補助言語: なし ・ 検出フレームワーク: `wordpress` |
| **Git 来歴** | `main@d1e02277 (dirty)` |
| **実行した決定論的ツール** | `project_inspect (php)`、`tree-sitter AST (php)`、`container runtime harness (docker: php/raw.dockerfile)`、`Trivy (docker: fs+image)` |
| **論理パイプラインステージ** | 全 11 ステージ（`confirm_plan`, `repo_and_deps`, `supply_chain`, `ast_and_quality`, `runtime_verification`, `security_audit`, `arch_recording`, `service_readiness`, `test_health`, `output_score`, `create_report`）— スキップ 0 件 |

## 7 軸決定論的ベースライン vs. AI 補正（`±10pt`）

PNI は AST・ランタイム・SCA の決定論的ファクトから各軸のベースラインスコアを算出し、AI による定性補正を各軸 `±10pt` 以内に制限します。`wp_plugin_messy` では構造的な WordPress セキュリティ不備、型・テスト欠如、および生 PHP 負債により、全 7 軸で上限の `−10pt` 補正（総合 `70 -> 60`）が適用されました。

```drawlib align=center code=fold file=baseline_vs_final_scores.png caption="7 軸決定論的ベースラインと AI 定性補正（-10pt 上限）後の最終スコア比較"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.styles import Styles
from drawlib.text import text

setup(width=146, height=64, dpi=150)

text(
    (73.0, 59.5),
    "7-Axis Deterministic Baseline vs. Final Score (Overall: 70 -> 60)",
    style=Styles.DarkBold.patch(text_size=11.5),
)

chart = BarChart(
    categories=[
        "Architecture",
        "Code Quality",
        "Typing",
        "Testing",
        "Dependencies",
        "Security",
        "Docs",
    ],
    axis_line_style=Styles.MutedDashed,
    axis_text_style=Styles.DarkBold.patch(text_size=10.0),
    grid_style=Styles.MutedThin,
    width=134.0,
    height=39.0,
    bar_mode="group",
    bar_r=0.8,
    value_text_style=Styles.DarkBold.patch(text_size=9.5),
    value_format="{:.0f}",
)
chart.add_series("Deterministic Baseline", [100.0, 100.0, 46.0, 65.0, 100.0, 40.0, 37.0], style=Styles.SecondaryNeutral)
chart.add_series("Final Score (-10pt AI Delta)", [90.0, 90.0, 36.0, 55.0, 90.0, 30.0, 27.0], style=Styles.PrimaryFlat)
chart.draw(xy=(8.0, 12.0))
chart.draw_legend(
    xy=(44.0, 4.0),
    text_style=Styles.DarkBold.patch(text_size=10.0),
    orientation="horizontal",
    item_gap=8.0,
)

save()
```

| 評価軸 | ベースライン | AI Δ | 最終 | グレード | 補正根拠 |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Architecture** | 100 | −10 | **90** | A | 非巡回の 4 ファイル分割だが、グローバル手続き関数・手動 `require_once`・13 箇所のスーパーグローバル/`$wpdb` 直接参照に依存し OOP/PSR-4 境界が皆無。 |
| **Code Quality** | 100 | −10 | **90** | A | 16 件の WordPress フレームワーク違反、タイムアウト無指定の `@file_get_contents()` エラー抑止、`print_r()` 漏洩、ハードコード `<script src=...>`。 |
| **Typing** | 46 | −10 | **36** | D | 型安全性 `0.0%`：全 4 ファイルで `declare(strict_types=1)` 欠落、全 7 関数で引数・戻り値型宣言なし。 |
| **Testing** | 65 | −10 | **55** | C | PHPUnit/Pest テスト 0 件（計測カバレッジ `0%`）のため、`php -l` と 5 フックスモーク以外の REST・AJAX・DB・管理画面ロジックが完全未検証。 |
| **Dependencies** | 100 | −10 | **90** | A | 宣言 Composer CVE は 0 件だが、EOL PHP `>=7.4` 対象の未管理生 PHP 構成であり CI・`LICENSE`・`SECURITY.md`・Dependabot がすべて欠落。 |
| **Security** | 40 | −10 | **30** | D | 全 4 ファイルにまたがる多面的な WordPress 脆弱性（ハードコード秘密鍵、CWE-89 SQLi 3 件、CWE-79 XSS 3 箇所、未認証 PII 流出、`'read'` 権限昇格、Nonce・`ABSPATH` 欠落）。 |
| **Documentation** | 37 | −10 | **27** | D | わずか 2 行の `README.md` と、全 7 公開関数で `0.0%` の PHPDoc カバレッジ。 |
| **総合スコア** | **70** | **−10** | **60** | **C** | 決定論的ベースラインに対し全軸の定性セキュリティ・品質減点（`−10pt`）を反映した加重総合評価。 |

## 監査ステップ別スコア（低評価順）

個別の全 7 監査ステップはいずれも**グレード D（`10`〜`45/100`）**となり、テスト監査（`10/100`）、セキュリティ脆弱性監査（`14/100`）、PHP AST 監査（`16/100`）が特に低い結果でした。

```drawlib align=center code=fold file=audit_step_scores.png caption="実行済み監査ステップ別スコア（低評価順）および指摘ソース内訳"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.icons import phosphor
from drawlib.smartarts import KpiCards
from drawlib.styles import Colors, Styles
from drawlib.text import text

setup(width=148, height=64, dpi=150)

text(
    (56.0, 59.5),
    "Audit Step Scores (Weakest -> Strongest, All Grade D)",
    style=Styles.DarkBold.patch(text_size=11.0),
)

bar = BarChart(
    categories=[
        "php_test_audit",
        "security_vuln",
        "php_ast_audit",
        "supply_chain",
        "service_readiness",
        "repo_structure",
        "container_runtime",
    ],
    axis_line_style=Styles.MutedDashed,
    axis_text_style=Styles.DarkBold.patch(text_size=9.2),
    grid_style=Styles.MutedThin,
    width=60.0,
    height=46.0,
    orientation="horizontal",
    bar_r=0.7,
    value_text_style=Styles.DarkBold.patch(text_size=9.5),
    value_format="{:.0f}",
)
bar.add_series("Step Score", [10.0, 14.0, 16.0, 20.0, 20.0, 25.0, 45.0], style=Styles.DangerNeutral)
bar.draw(xy=(30.0, 8.0))

cards = KpiCards(
    style=Styles.Neutral.patch(shape_r=1.5, shape_fill_color=Colors.White, shape_line_color=Colors.Gray3),
    metric_style=Styles.DarkBold.patch(text_size=11.5),
    text_style=Styles.DarkBold.patch(text_size=9.5),
    description_style=Styles.Muted.patch(text_size=8.6),
    accent_position="left_pill",
    metric_layout="left_column",
    metric_width_ratio=0.28,
    spacing=2.6,
)
cards.add(
    "7 / 15",
    "Deterministic Findings",
    "5 CWE sinks, 1 secret, README",
    accent_style=Styles.PrimaryFlat,
    metric_style=Styles.PrimaryBold.patch(text_size=11.5),
    icon=phosphor.code,
    icon_style=Styles.Primary,
)
cards.add(
    "8 / 15",
    "AI Qualitative Findings",
    "WP auth, CSRF, typing, tests",
    accent_style=Styles.SecondaryFlat,
    metric_style=Styles.SecondaryBold.patch(text_size=11.5),
    icon=phosphor.list_magnifying_glass,
    icon_style=Styles.Secondary,
)
cards.add(
    "0 / 0",
    "FP Waivers & Opt-Outs",
    "0 FPs triaged; 0 opt_out waivers",
    accent_style=Styles.SuccessFlat,
    metric_style=Styles.SuccessBold.patch(text_size=11.5),
    icon=phosphor.check_circle,
    icon_style=Styles.Success,
)
cards.draw((96.0, 8.0), width=49.0, height=48.0, columns=1)

save()
```

## ルール準拠マトリクス（`FAIL -> WARN -> N/A`・全 17 ルール）

| 判定 | ルール ID | 評価ステップ | 根拠サマリー |
| :-: | :--- | :--- | :--- |
| **FAIL** | `common/documentation` | `repo_structure_audit` | `README.md` は 2 行のみで、導入要件・ショートコード/REST 仕様・セキュリティ/開発手順が欠落。 |
| **FAIL** | `common/production_readiness` | `container_runtime_audit` | `admin/settings-page.php:21` がタイムアウト無指定で `@file_get_contents()` を呼びエラーを抑止、`includes/rest-endpoints.php:21` が `print_r()` で生データを出力。 |
| **FAIL** | `common/runtime_verification` | `container_runtime_audit` | ビルド・`php -l`・5 フックスモークは合格だが、PHPUnit テストが `0` 件で `coverage.measured=False`。 |
| **FAIL** | `common/security` | `repo_structure_audit` | ハードコード `$map_webhook_secret`（`<REDACTED_SECRET>`）、SQLi 3 件、XSS 3 箇所（ショートコード `$_GET['badge_label']` 含む）、未認証 PII 流出、CSRF/権限欠落、`ABSPATH` 欠落。 |
| **FAIL** | `common/security_vulnerability` | `php_ast_audit` | `SEC-01` 宣言アプリ CVE 0（ハーネス OS 除外）・`SEC-02` N/A・`SEC-03` FAIL（ハードコード秘密鍵）・`SEC-04` FAIL（HIGH CWE 5 件）・`SEC-05` FAIL（未認証エンドポイント 4/5）。 |
| **FAIL** | `common/supply_chain` | `repo_structure_audit` | `composer.json`/`composer.lock`、`LICENSE`、`SECURITY.md`、CI ワークフロー、Dependabot がすべて欠落し、EOL PHP `>=7.4` を対象。 |
| **FAIL** | `php/code_quality` | `php_ast_audit` | 全 7 関数で PHPDoc `0.0%`、スーパーグローバル/グローバル `$wpdb` 直接参照 13 箇所、`print_r()` 出力、`@file_get_contents()` エラー抑止。 |
| **FAIL** | `php/dependencies` | `repo_structure_audit` | Composer や PSR-4 オートロードを持たない生 PHP 構成で、`member-analytics-portal.php` の手動 `require_once` と EOL `Requires PHP: 7.4` に依存。 |
| **FAIL** | `php/frameworks/wordpress` | `php_ast_audit` | 16 件の WordPress 違反：全 4 ファイルの `ABSPATH` 欠落、REST `__return_true`、`wp_ajax_nopriv`、`'read'` 権限の管理画面、Nonce/権限チェックゼロ、生 `$wpdb` SQL、直書き `<script>`、未エスケープ `echo`。 |
| **FAIL** | `php/modern_stack` | `repo_structure_audit` | EOL PHP `>=7.4`、`declare(strict_types=1)`・型宣言欠落、手動 `require_once`、タイムアウト無指定 HTTP、`print_r()`、テストランナー未構成。 |
| **FAIL** | `php/testing` | `php_test_audit` | 4 モジュールに対しテストファイル `0` 件・PHPUnit テスト `0` 件（`coverage.measured=False`）。 |
| **FAIL** | `php/typing` | `php_ast_audit` | 型安全性 `0.0%`：全 4 ファイルで `declare(strict_types=1)` 欠落、全 7 関数で引数・戻り値型が未宣言。 |
| **WARN** | `common/architecture` | `php_ast_audit` | 非巡回の 4 ファイル分割だが、手動 `require_once`・クラス 0 件・13 箇所のグローバル状態アクセスに依存。 |
| **WARN** | `common/git_workflow` | `repo_structure_audit` | `.gitignore` および PR 時の PHPCS/PHPStan/PHPUnit 自動検査 CI ゲートが欠落。 |
| **WARN** | `common/maintainability` | `php_ast_audit` | 関数自体は短く複雑度ホットスポットは `0` だが、グローバル強結合（13 箇所）と `@` エラー抑止がテスト容易性を阻害。 |
| **WARN** | `common/twelve_factor` | `service_readiness_audit` | `rest-endpoints.php:3` での `$map_webhook_secret` ハードコードおよび 21 行目の無構造 `print_r()` 出力。 |
| **N/A** | `php/frameworks/laravel` | `php_ast_audit` | 単体 WordPress プラグイン（`detected_frameworks=['wordpress']`）のため Laravel は適用対象外。 |

## 統合指摘事項一覧（`CRITICAL -> MEDIUM`・全 11 箇所）

- **指摘ソース内訳**: 決定論的アナライザー `7` 件 + AI 定性監査 `8` 件 = **計 15 件**を **11 ユニーク箇所**へ統合。
- **AI 誤検知トリアージ / 設計例外（Waiver）**: 決定論的検出の除外・再分類 `0` 件、有効な `pni.toml [[opt_out]]` 設計例外 `0` 件。

| # | 重要度 | 該当箇所 | ルール / CWE | 根拠および是正内容 |
| :-: | :-: | :--- | :--- | :--- |
| 1 | **CRITICAL** | `examples/php/wp_plugin_messy/includes/rest-endpoints.php:3` | `common/security` | `$map_webhook_secret` へ秘密鍵リテラル（`<REDACTED_SECRET>`）をハードコード。即時削除・鍵ローテーションの上、環境変数またはシークレット管理へ移行。 |
| 2 | **CRITICAL** | `includes/ajax-handlers.php` | `php/frameworks/wordpress` | `map_ajax_search_members` が `wp_ajax_nopriv` 経由で `wp_users` SQLi を公開、`map_ajax_purge_logs` が Nonce/権限なしで `DELETE` SQLi と生 `$_POST['category']` 出力を実行。`nopriv` 削除・`check_ajax_referer()`・`manage_options`・`$wpdb->prepare()`・`wp_send_json_success()` を適用。 |
| 3 | **CRITICAL** | `includes/rest-endpoints.php` | `common/security`, `php/frameworks/wordpress` | `$map_webhook_secret`（`<REDACTED_SECRET>`）ハードコードに加え、`GET /wp-json/member-analytics/v1/export` が `__return_true`・`$_GET['role_filter']` 生 SQL 結合・`?debug` `print_r()` 出力を実行。`manage_options`、`$request->get_param()`、`$wpdb->prepare()`、および `print_r()` 削除を実施。 |
| 4 | **HIGH** | `admin/settings-page.php` | `php/frameworks/wordpress` | `add_options_page` が `'read'` 権限（全購読者）を許可し、Nonce/権限検証なしで `map_telemetry_url` 更新・無制限 `@file_get_contents()`・生 `$_GET['tab']` 出力・直書き `<script src=...>` を実行。`manage_options`、`check_admin_referer()`、`esc_url_raw()`、`wp_remote_get(['timeout'=>5])`、`esc_html()`/`esc_attr()`、`wp_enqueue_script()` を導入。 |
| 5 | **HIGH** | `examples/php/wp_plugin_messy/admin/settings-page.php:26` | `CWE-79` | `echo $_GET['tab'] ?? 'general';` による未エスケープ出力。許可リスト検証および `esc_html()` で防御。 |
| 6 | **HIGH** | `examples/php/wp_plugin_messy/includes/ajax-handlers.php:10` | `CWE-89` | `$wpdb->get_results("SELECT ID, display_name, user_email FROM {$wpdb->users} ...")` の非パラメータ化 SQL。`$wpdb->prepare()` + `$wpdb->esc_like()` へ置換。 |
| 7 | **HIGH** | `examples/php/wp_plugin_messy/includes/ajax-handlers.php:21` | `CWE-89` | `$wpdb->query("DELETE FROM wp_map_events WHERE category = ...")` の非パラメータ化 SQL。`$wpdb->prepare()` へ置換。 |
| 8 | **HIGH** | `examples/php/wp_plugin_messy/includes/ajax-handlers.php:22` | `CWE-79` | `echo "Purged category: " . $_POST['category'];` による未エスケープ出力。`esc_html()` または `wp_send_json_success()` を使用。 |
| 9 | **HIGH** | `examples/php/wp_plugin_messy/includes/rest-endpoints.php:19` | `CWE-89` | `$wpdb->get_results($sql)` の非パラメータ化 SQL。`$wpdb->prepare()` + `$wpdb->esc_like()` へ置換。 |
| 10 | **HIGH** | `member-analytics-portal.php` | `php/dependencies`, `common/security`, `common/runtime_verification`, `php/typing` | EOL `Requires PHP: 7.4`・手動 `require_once`・ショートコードの未エスケープ `$_GET['badge_label']`・PHPUnit テスト 0 件・全 4 ファイルでの `ABSPATH`/`strict_types=1`/型/PHPDoc 欠落。`ABSPATH`、`esc_html()`、Composer PHP 8.2+ PSR-4、PHPUnit を導入。 |
| 11 | **MEDIUM** | `README.md` | `common/documentation` | 2 行のみの最小 README（`has_readme=True, lines=2`）。アーキテクチャ、要件、REST/AJAX 仕様、セキュリティ設定および開発手順を追記。 |

## 機械可読エビデンス・アーティファクト一覧

生の JSON/SARIF ペイロードは本レポート本文には貼り付けず、CI 自動化・GitHub Code Scanning・監査再現性のために以下のリポジトリ相対パスへ保管しています。

| アーティファクトパス | スキーマ / 形式 | 用途 |
| :--- | :--- | :--- |
| `docs/reports/php_wp_plugin_messy/php_wp_plugin_messy_score.json` | `ScoreResult` v2.0 (JSON) | 7 軸スコア・ベースライン差分・全指摘・ランタイム/Trivy 結果 |
| `docs/reports/php_wp_plugin_messy/php_wp_plugin_messy_summary.json` | `ScoreSummary` (JSON) | CI / ポータル向け軽量サマリー |
| `docs/reports/php_wp_plugin_messy/php_wp_plugin_messy_findings.sarif` | `SARIF 2.1.0` | GitHub Code Scanning / IDE インライン警告連携 |
| `docs_src/reports/php_wp_plugin_messy/_facts/plan.json` | `ReconPlan` (JSON) | 事前偵察計画および検証済み Mermaid 実行 DAG |
| `docs_src/reports/php_wp_plugin_messy/_facts/facts.json` | 決定論的ファクトバンドル | `project_inspect`・tree-sitter AST・ランタイム・Trivy の生データ |
| `docs_src/reports/php_wp_plugin_messy/_facts/architecture.json` | `ArchitectureRecord` (JSON) | 根拠付きレイヤー・モジュール・エントリーポイント・実行フロー記録 |
