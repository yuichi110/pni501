# 2. アーキテクチャとソースコード構造

**Member Analytics Portal（`wp_plugin_messy` v1.3.0）** は、4 つの PHP ファイル（総 `84` LOC、手続き型関数 `7` 個、クラス `0` 個）による**手続き型フラット WordPress プラグイン**構造を採用しています。ファイル読み込み自体は循環依存のない非巡回構成ですが、全ハンドラが WordPress のグローバル `$wpdb` や生の HTTP スーパーグローバル（`$_GET`、`$_POST`）へ直接結合しており、OOP/PSR-4 境界、サニタイズ層、認可・Nonce ミドルウェアが一切存在しません。

```drawlib align=center code=fold file=arch_source_tree.png caption="プラグインの物理ディレクトリ構成（PHP 4 ファイル + README）とモジュールインベントリ"
from drawlib.canvas import save, setup
from drawlib.smartarts import Panel, Table, TreeNode
from drawlib.styles import Colors, Styles

setup(width=146, height=64, dpi=150)

left = Panel(
    text="Directory Tree (wp_plugin_messy)",
    style=Styles.Neutral.patch(shape_r=2.0, shape_fill_color=Colors.White, shape_line_color=Colors.Gray4),
    header_style=Styles.PrimaryNeutral.patch(shape_r=2.0),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    header_variant="filled",
    header_height=9.0,
)
left.draw((3.0, 4.0), width=58.0, height=56.0)

tree_text = Styles.Dark.patch(text_size=9.5)
tree_bold = Styles.PrimaryBold.patch(text_size=10.0)
tree_line = Styles.MutedThin

root = TreeNode(
    "wp_plugin_messy/ (84 LOC)",
    text_style=tree_bold,
    line_style=tree_line,
    line_horizontal_margin=2.5,
    line_horizontal_length=4.0,
    line_vertical_margin=5.6,
    children=[
        TreeNode("member-analytics-portal.php (11)", text_style=tree_text, line_style=tree_line),
        TreeNode("README.md (2 lines)", text_style=Styles.Muted.patch(text_size=9.5), line_style=tree_line),
        TreeNode(
            "includes/",
            text_style=Styles.DarkBold.patch(text_size=9.5),
            line_style=tree_line,
            line_horizontal_margin=2.5,
            line_horizontal_length=4.0,
            line_vertical_margin=5.6,
            children=[
                TreeNode("rest-endpoints.php (21)", text_style=tree_text, line_style=tree_line),
                TreeNode("ajax-handlers.php (21)", text_style=tree_text, line_style=tree_line),
            ],
        ),
        TreeNode(
            "admin/",
            text_style=Styles.DarkBold.patch(text_size=9.5),
            line_style=tree_line,
            line_horizontal_margin=2.5,
            line_horizontal_length=4.0,
            line_vertical_margin=5.6,
            children=[
                TreeNode("settings-page.php (31)", text_style=tree_text, line_style=tree_line),
            ],
        ),
    ],
)
root.draw((7.0, 47.0))

right = Panel(
    text="Grounded Module Inventory & Hotspot Risk",
    style=Styles.Neutral.patch(shape_r=2.0, shape_fill_color=Colors.White, shape_line_color=Colors.Gray4),
    header_style=Styles.Neutral.patch(shape_r=2.0),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    header_variant="filled",
    header_height=9.0,
)
right.draw((64.0, 4.0), width=79.0, height=56.0)

tbl = Table(
    cell_style=Styles.Neutral.patch(shape_fill_color=Colors.White),
    text_style=Styles.Dark.patch(text_size=9.5),
    header_cell_style=Styles.PrimaryNeutral,
    header_text_style=Styles.DarkBold.patch(text_size=9.5),
    border_style=Styles.MutedThin,
    has_header=True,
)
data = [
    ["Module File", "LOC", "Public Callables", "Peak Risk"],
    ["member-analytics-\nportal.php", "11", "map_render_badge_\nshortcode", "1.00\n(4 HIGH)"],
    ["includes/\nrest-endpoints.php", "21", "map_register_rest_routes\nmap_export_all_members", "1.00\n(CRIT+HIGH)"],
    ["includes/\najax-handlers.php", "21", "map_ajax_search_members\nmap_ajax_purge_logs", "1.00\n(CRIT+3 HIGH)"],
    ["admin/\nsettings-page.php", "31", "map_register_admin_menu\nmap_render_settings_page", "0.54\n(2 HIGH)"],
]
tbl.draw_flexible(
    xy=(66.5, 48.0),
    column_widths=[25.0, 8.0, 27.0, 14.0],
    row_heights=[6.5, 8.5, 9.0, 9.0, 9.0],
    data=data,
    align="top_left",
)

save()
```

## 手続き型フック結合とリスクヒートマップ重畳

下図は、4 つの手続き型 PHP モジュールと共有 WordPress グローバル状態（`$wpdb`、`$_GET`、`$_POST`、`wp_options`、`$map_webhook_secret`）の結合関係に対し、`module_hotspots` の正規化リスクスコア（`includes/ajax-handlers.php`・`includes/rest-endpoints.php`・`member-analytics-portal.php` = `1.00`、`admin/settings-page.php` = `0.54`）を重畳表示したものです。

```drawlib align=center code=fold file=arch_coupling_heatmap.png caption="手続き型モジュール依存グラフ・WordPress グローバル状態結合およびリスクヒートマップ重畳"
from drawlib.canvas import save, setup
from drawlib.charts.heatmap import HeatmapOverlay
from drawlib.diagrams.class_diagram import ClassDiagram, ClassNode
from drawlib.styles import Colors, Styles

setup(width=160, height=102, dpi=150)

heat = HeatmapOverlay(
    width=160.0,
    height=102.0,
    min_value=0.0,
    max_value=1.0,
    default_radius=20.0,
    max_alpha=0.40,
    show_contour_lines=False,
    styles=[Styles.SuccessNeutral, Styles.WarningNeutral, Styles.DangerFlat],
)
heat.add_spot((80.0, 80.0), value=1.00, radius=19.0)
heat.add_spot((26.0, 46.0), value=1.00, radius=21.0)
heat.add_spot((80.0, 46.0), value=1.00, radius=21.0)
heat.add_spot((134.0, 46.0), value=0.54, radius=19.0)
heat.draw(xy=(0.0, 0.0))

cd = ClassDiagram(
    node_style=Styles.Neutral.patch(shape_fill_color=Colors.White, shape_line_color=Colors.Gray5),
    edge_style=Styles.DarkBold,
    edge_text_style=Styles.DarkBold.patch(text_size=9.2),
    title="Procedural WordPress Plugin Coupling & Thermal Risk Overlay (Risk 0.54 - 1.00)",
    title_style=Styles.DarkBold.patch(text_size=11.5),
    width=156.0,
    height=98.0,
    margin=4.0,
    header_style=Styles.PrimaryNeutral,
)

entry = ClassNode(
    "member-analytics-portal.php",
    stereotype="entrypoint | risk 1.00",
    width=52.0,
    row_height=3.4,
    style=Styles.Neutral.patch(shape_fill_color=Colors.White, shape_line_color=Colors.Gray5),
    header_style=Styles.DangerNeutral,
)
entry.add_attribute("Requires PHP: 7.4 (EOL) | No ABSPATH", "", visibility="-")
entry.add_method("map_render_badge_shortcode", "atts", "raw HTML")

rest = ClassNode(
    "includes/rest-endpoints.php",
    stereotype="REST API | risk 1.00",
    width=46.0,
    row_height=3.4,
    style=Styles.Neutral.patch(shape_fill_color=Colors.White, shape_line_color=Colors.Gray5),
    header_style=Styles.DangerNeutral,
)
rest.add_attribute("permission_callback", "__return_true", visibility="+")
rest.add_attribute("CWE-89 + print_r()", "L19, L21", visibility="-")
rest.add_method("map_register_rest_routes", "", "void")
rest.add_method("map_export_all_members", "req", "array")

ajax = ClassNode(
    "includes/ajax-handlers.php",
    stereotype="AJAX | risk 1.00",
    width=46.0,
    row_height=3.4,
    style=Styles.Neutral.patch(shape_fill_color=Colors.White, shape_line_color=Colors.Gray5),
    header_style=Styles.DangerNeutral,
)
ajax.add_attribute("wp_ajax_nopriv", "no nonce / no cap", visibility="+")
ajax.add_attribute("2x CWE-89 + CWE-79", "L10, L21, L22", visibility="-")
ajax.add_method("map_ajax_search_members", "", "void")
ajax.add_method("map_ajax_purge_logs", "", "void")

admin = ClassNode(
    "admin/settings-page.php",
    stereotype="Admin UI | risk 0.54",
    width=46.0,
    row_height=3.4,
    style=Styles.Neutral.patch(shape_fill_color=Colors.White, shape_line_color=Colors.Gray5),
    header_style=Styles.WarningNeutral,
)
admin.add_attribute("add_options_page", "cap: 'read'", visibility="+")
admin.add_attribute("CWE-79 + @file_get", "L21, L26, L27", visibility="-")
admin.add_method("map_register_admin_menu", "", "void")
admin.add_method("map_render_settings_page", "", "void")

state = ClassNode(
    "WordPress Global State & External I/O",
    stereotype="shared globals (13 refs)",
    width=78.0,
    row_height=3.4,
    style=Styles.Neutral.patch(shape_fill_color=Colors.White, shape_line_color=Colors.Gray5),
    header_style=Styles.SecondaryNeutral,
)
state.add_attribute("global wpdb", "wp_users & wp_map_events (3 raw SQL)", visibility="+")
state.add_attribute("Superglobals", "10 unsanitized GET / POST reads", visibility="+")
state.add_attribute("Options & Secret", "map_telemetry_url + <REDACTED_SECRET>", visibility="+")

cd.add(entry, xy=(78.0, 77.0))
cd.add(rest, xy=(24.0, 46.0))
cd.add(ajax, xy=(78.0, 46.0))
cd.add(admin, xy=(132.0, 46.0))
cd.add(state, xy=(78.0, 12.0))

cd.connect(entry, rest, "dependency", label="require_once", start_side="left", end_side="top")
cd.connect(entry, ajax, "dependency", label="require_once", start_side="bottom", end_side="top")
cd.connect(entry, admin, "dependency", label="require_once", start_side="right", end_side="top")
cd.connect(rest, state, "association", label="wpdb / GET", start_side="bottom", end_side="left", style=Styles.DangerDashed)
cd.connect(ajax, state, "association", label="wpdb / POST", start_side="bottom", end_side="top", style=Styles.DangerDashed)
cd.connect(admin, state, "association", label="POST / opt", start_side="bottom", end_side="right", style=Styles.WarningDashed)

cd.draw(xy=(2.0, 2.0))

save()
```

## 実行時リクエストおよび攻撃フロー

本プラグインは REST API、`admin-ajax.php`、WordPress 管理画面オプションページ、フロントエンドショートコードにわたる **5 つのエントリーポイント** を公開しています。下図は、信頼できない HTTP 入力からデータベースおよびブラウザシンクへ至る主要 3 系統の実行フローを示しています。

```drawlib align=center code=fold file=arch_request_flows.png caption="REST エクスポート・AJAX 検索/削除・管理設定画面における主要実行フロー"
from drawlib.canvas import save, setup
from drawlib.smartarts import CardList, Panel
from drawlib.styles import Colors, Styles

setup(width=146, height=74, dpi=150)

def draw_flow_lane(y_bottom: float, title: str, header_style, steps: list[tuple[str, str, str, object]]) -> None:
    p = Panel(
        text=title,
        style=Styles.Neutral.patch(shape_r=1.8, shape_fill_color=Colors.White, shape_line_color=Colors.Gray4),
        header_style=header_style.patch(shape_r=1.8),
        text_style=Styles.DarkBold.patch(text_size=10.0),
        header_variant="filled",
        header_height=6.8,
    )
    p.draw((3.0, y_bottom), width=140.0, height=21.0)

    cl = CardList(
        style=Styles.Neutral.patch(shape_r=1.2, shape_fill_color=Colors.Gray1, shape_line_color=Colors.Gray3),
        text_style=Styles.DarkBold.patch(text_size=9.5),
        description_style=Styles.Muted.patch(text_size=9.0),
        badge_shape="rounded_rect",
        badge_style=Styles.PrimaryNeutral,
        badge_text_style=Styles.DarkBold.patch(text_size=9.0),
        direction="horizontal",
        spacing=3.5,
        show_arrows=True,
        arrow_style=Styles.DarkBold,
    )
    for badge, heading, desc, b_style in steps:
        t_style = Styles.WhiteBold.patch(text_size=8.0) if b_style == Styles.DangerFlat else Styles.DarkBold.patch(text_size=8.0)
        cl.add(heading, desc, badge_text=badge, badge_style=b_style, badge_text_style=t_style)
    cl.draw((5.5, y_bottom + 1.8), width=135.0, height=11.5)

draw_flow_lane(
    50.0,
    "Flow 1: Unauthenticated REST Member Export  (includes/rest-endpoints.php)",
    Styles.DangerNeutral,
    [
        ("GET", "/wp-json/.../export", "No auth (__return_true)", Styles.DangerFlat),
        ("IN", "GET['role_filter']", "Raw unsanitized param", Styles.WarningNeutral),
        ("SQL", "wpdb->get_results()", "LIKE '%role_filter%'", Styles.DangerFlat),
        ("PII", "wp_users + print_r", "login, email, ?debug", Styles.DangerFlat),
    ],
)

draw_flow_lane(
    26.5,
    "Flow 2: AJAX Member Search & Event Log Purge  (includes/ajax-handlers.php)",
    Styles.DangerNeutral,
    [
        ("REQ", "admin-ajax.php", "nopriv search / session", Styles.DangerFlat),
        ("GAP", "No Nonce / No Cap", "Missing check_ajax_ref", Styles.DangerFlat),
        ("SQL", "SELECT & DELETE SQL", "wp_users & wp_map_events", Styles.DangerFlat),
        ("XSS", "Raw echo POST", "Unescaped category HTML", Styles.WarningNeutral),
    ],
)

draw_flow_lane(
    3.0,
    "Flow 3: Admin Settings Mutation & Telemetry Ping  (admin/settings-page.php)",
    Styles.WarningNeutral,
    [
        ("CAP", "Options Page ('read')", "Any WP subscriber", Styles.WarningNeutral),
        ("OPT", "POST telemetry_url", "No check_admin_referer", Styles.DangerFlat),
        ("I/O", "@file_get_contents()", "No timeout; silent err", Styles.WarningNeutral),
        ("XSS", "echo GET['tab']", "Plus raw <script src>", Styles.DangerFlat),
    ],
)

save()
```

## レイヤー構成と境界評価

| レイヤー | 対象パス | 許可依存先 | 責務および健全性評価 |
| :--- | :--- | :--- | :--- |
| **プラグイン起動・ショートコード層** | `member-analytics-portal.php` | REST・AJAX・Admin 各モジュール | 手動 `require_once`、フック登録（`rest_api_init`・ショートコード）、`[member_analytics_badge]` 描画を担当。`ABSPATH` ガード欠落、EOL PHP 7.4 宣言、`$_GET['badge_label']` XSS が存在。 |
| **REST エンドポイント層** | `includes/rest-endpoints.php` | *(なし)* | `/wp-json/member-analytics/v1/export` を登録し `$wpdb->users` を検索。`$map_webhook_secret`（`<REDACTED_SECRET>`）のハードコード、`__return_true`、CWE-89 SQLi、`print_r()` デバッグ漏洩を含む。 |
| **AJAX ハンドラ層** | `includes/ajax-handlers.php` | *(なし)* | `wp_ajax_nopriv_map_search_members` および `wp_ajax_map_purge_logs` を登録。非パラメータ化 `SELECT`/`DELETE` SQLi、Nonce/権限検証欠落、未エスケープ `echo` XSS が集中。 |
| **管理設定画面層** | `admin/settings-page.php` | *(なし)* | `'read'` 権限で管理オプション画面を登録し、`map_telemetry_url` 保存・`@file_get_contents()` による外部テレメトリ通信・インライン HTML/JS 出力を実行。 |

## リスク降順モジュールホットスポット（`module_hotspots`）

PNI は決定論的 AST パス（`examples/php/wp_plugin_messy/...`）と AI 定性相対パスの双方を集計しています。全 8 エントリをリスク降順で以下に示します。

| ファイルパス | LOC | リスクスコア | 指摘件数 | 主要ルール / CWE |
| :--- | :---: | :---: | :--- | :--- |
| `examples/php/wp_plugin_messy/includes/ajax-handlers.php` | 21 | **1.00** | HIGH 3 | `CWE-79`, `CWE-89` |
| `examples/php/wp_plugin_messy/includes/rest-endpoints.php` | 21 | **1.00** | CRIT 1, HIGH 1 | `common/security`, `CWE-89` |
| `member-analytics-portal.php` | — | **1.00** | HIGH 4 | `php/dependencies`, `common/security`, `common/runtime_verification`, `php/typing` |
| `includes/rest-endpoints.php` | — | **0.90** | CRIT 2 | `common/security`, `php/frameworks/wordpress` |
| `examples/php/wp_plugin_messy/admin/settings-page.php` | 31 | **0.54** | HIGH 1 | `CWE-79` |
| `includes/ajax-handlers.php` | — | **0.45** | CRIT 1 | `php/frameworks/wordpress` |
| `admin/settings-page.php` | — | **0.28** | HIGH 1 | `php/frameworks/wordpress` |
| `examples/php/wp_plugin_messy/member-analytics-portal.php` | 11 | **0.14** | 0 | *(決定論的 AST ベースライン)* |

## 状態管理・永続化およびエラー処理モデル

- **データベース状態**: `global $wpdb` を経由し `$wpdb->prepare()` を使わずに WordPress MySQL テーブル（`$wpdb->users` および `wp_map_events`）へ直接クエリを発行。
- **オプション永続化**: サニタイズや Nonce 検証なしに `$_POST['map_telemetry_url']` を `update_option('map_telemetry_url', ...)` へ永続化。
- **グローバル秘密鍵**: `includes/rest-endpoints.php:3` のモジュールスコープで `$map_webhook_secret = '<REDACTED_SECRET>'` をハードコード。
- **エラー・並行処理モデル**: WordPress 配下の同期リクエスト処理であり、`@file_get_contents()` によるサイレントエラー抑止と `print_r()` による無構造出力が行われ、防御的バリデーションや例外処理が存在しません。
