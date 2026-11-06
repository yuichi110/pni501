# 2. アーキテクチャとソースコード構成

`Member Analytics Portal` (`wp_plugin_messy`) は **`member-analytics-portal.php` を起点に3つのサブファイルを無条件 `require_once` 読み込みする手続き型フック直結モノリス構成（計4ファイル・84 LOC・0クラス・7グローバル関数）** を採っている。PSR-4 名前空間や Service/Repository 層分離は存在せず、全4ファイルで直接 HTTP アクセスを遮断する `if (!defined('ABSPATH')) { exit; }` ガードが欠落している。

```drawlib file=arch_wp_hooks_and_inventory.png caption="観点1: WordPressフック・サブファイル構成ツリーとABSPATH欠落モジュール構成表 (全4ファイル・84 LOC)"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import Panel, Table, TreeNode
from drawlib.styles import Styles

setup(width=146, height=78, dpi=150)

left_panel = Panel(
    "WPプラグイン構成とフック登録",
    "",
    style=Styles.Neutral,
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=9.8),
    icon=phosphor.git_branch,
    icon_style=Styles.White,
    header_height=9.5,
)
left_panel.draw(xy=(2, 3), width=50, height=72)

t_style = Styles.Dark.patch(text_size=8.6)
b_style = Styles.PrimaryBold.patch(text_size=8.8)
d_style = Styles.DangerBold.patch(text_size=8.6)
w_style = Styles.WarningBold.patch(text_size=8.6)

root = TreeNode(
    "wp_plugin_messy/ (composer不在)",
    text_style=b_style,
    line_style=Styles.Neutral,
    line_horizontal_margin=0.8,
    line_horizontal_length=1.8,
    line_vertical_margin=3.4,
)
entry = root.add("member-analytics-portal.php", text_style=d_style)
entry.add("hook: rest_api_init", text_style=t_style)
entry.add("shortcode: member_analytics_badge", text_style=w_style)
inc_node = root.add("includes/ [ABSPATH欠落]", text_style=b_style)
inc_node.add("rest-endpoints.php (/export)", text_style=d_style)
inc_node.add("ajax-handlers.php (nopriv/purge)", text_style=d_style)
adm_node = root.add("admin/ [ABSPATH欠落]", text_style=b_style)
adm_node.add("settings-page.php (admin_menu)", text_style=d_style)
root.add("README.md (2 lines)", text_style=t_style)
root.draw(xy=(4.0, 63.0))

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=8.8),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.0),
    border_style=Styles.NeutralThin,
)
rows = [
    ["モジュールパス", "LOC", "公開関数・登録フックと主要責務・健全性メモ"],
    [
        "admin/\nsettings-page.php",
        "31",
        "map_register_admin_menu, map_render_settings_page\n[Risk 1.00] ABSPATH欠落・read権限・Nonce不在・XSS・外部通信",
    ],
    [
        "includes/\najax-handlers.php",
        "21",
        "map_ajax_search_members, map_ajax_purge_logs\n[Risk 1.00] ABSPATH欠落・nopriv未認証SQLi・DELETE SQLi・XSS",
    ],
    [
        "includes/\nrest-endpoints.php",
        "21",
        "map_register_rest_routes, map_export_all_members\n[Risk 1.00] ABSPATH欠落・whsec直書き・__return_true・SQLi",
    ],
    [
        "member-analytics-\nportal.php",
        "11",
        "map_render_badge_shortcode | Requires PHP: 7.4 (EOL)\n[Risk 1.00] ABSPATH欠落・手動require_once 3件・バッジXSS",
    ],
]
tbl.draw_flexible(
    xy=(53, 75),
    column_widths=[26, 8, 57],
    row_heights=[8.0, 16.0, 16.0, 16.0, 16.0],
    data=rows,
)

save()
```

## REST (`__return_true`)・Admin-AJAX (`nopriv`) から `$wpdb` 生 SQL 結合へ至るデータフロー

実行フロー解析（`ExecutionFlowMap`）により、外部リクエストから WordPress DB（`{$wpdb->users}` / `wp_map_events` / `wp_options`）および HTML レスポンスに至る5本の経路すべてでサニタイズ・認可・プリペアドステートメントが欠落していることが判明した。特に `/wp-json/member-analytics/v1/export` と `wp_ajax_nopriv_map_search_members` は未認証の第三者から直接 `$wpdb->get_results()` の文字列結合クエリへ到達する。

```drawlib file=arch_dataflow_sqli_roadmap.png caption="観点2: REST (__return_true) & wp_ajax_nopriv から wpdb 生SQL結合・XSS出力へ至る危険データフロー"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import CardList, Roadmap
from drawlib.styles import Styles

setup(width=146, height=74, dpi=150)

flow = Roadmap(
    style=Styles.Neutral,
    text_style=Styles.DarkBold.patch(text_size=8.9),
    description_style=Styles.Dark.patch(text_size=8.2),
    spine_style=Styles.Danger,
    badge_style=Styles.Danger,
    badge_text_style=Styles.WhiteBold.patch(text_size=8.6),
    direction="horizontal",
    spacing=2.0,
)
flow.add(
    "1. 無認証リクエスト侵入",
    "REST /export (__return_true)\nwp_ajax_nopriv・購読者POST",
    badge_text="In",
    style=Styles.DangerNeutral,
    badge_style=Styles.Danger,
    icon=phosphor.globe,
    icon_style=Styles.Danger,
)
flow.add(
    "2. 境界検証・Nonce欠落",
    "current_user_can / Nonce不在\nGET・POST生値取得 (10箇所)",
    badge_text="Auth",
    style=Styles.WarningNeutral,
    badge_style=Styles.Warning,
    icon=phosphor.warning,
    icon_style=Styles.Warning,
)
flow.add(
    "3. wpdb生SQL・外部通信",
    "LIKE/DELETE生結合 (CWE-89)\nfile_get_contents 同期通信",
    badge_text="Sink",
    style=Styles.DangerNeutral,
    badge_style=Styles.Danger,
    icon=phosphor.database if hasattr(phosphor, "database") else phosphor.bug,
    icon_style=Styles.Danger,
)
flow.add(
    "4. PII漏洩・未エスケープ",
    "wp_usersメール露出・print_r\nesc_html不在のXSS (4箇所)",
    badge_text="Out",
    style=Styles.DangerNeutral,
    badge_style=Styles.Danger,
    icon=phosphor.x_circle,
    icon_style=Styles.Danger,
)
flow.draw(xy=(3, 41), width=140, height=30)

flows_list = CardList(
    style=Styles.Neutral,
    text_style=Styles.DarkBold.patch(text_size=8.8),
    description_style=Styles.Dark.patch(text_size=8.3),
    badge_shape="rounded_rect",
    badge_style=Styles.Danger,
    badge_text_style=Styles.WhiteBold.patch(text_size=8.4),
    spacing=1.8,
)
flows_list.add(
    "Flow 1 & 2: REST /export + wp_ajax_nopriv_map_search_members",
    "未認証で wp_users の user_email を検索・一括取得 + GET['role_filter'] / POST['term'] で SQLi",
    badge_text="CRIT",
    style=Styles.DangerNeutral,
)
flows_list.add(
    "Flow 3 & 4: wp_ajax_purge_logs + 設定画面 options-general.php",
    "Nonce/権限検査なしで wp_map_events DELETE SQLi・update_option 改ざん・60秒無制限 file_get_contents",
    badge_text="CRIT",
    style=Styles.DangerNeutral,
)
flows_list.add(
    "Flow 5: [member_analytics_badge] ショートコード & 設定画面タブ描画",
    "GET['badge_label']・GET['tab']・POST['category'] が未エスケープのまま HTML 出力 (CWE-79)",
    badge_text="HIGH",
    style=Styles.WarningNeutral,
    badge_style=Styles.Warning,
)
flows_list.draw(xy=(3, 3), width=140, height=35)

save()
```

## WordPress プラグイン実行・検証境界トポロジとリスク密度

指摘密度から算出された `module_hotspots` では、**4つのプラグイン `.php` ファイルすべてが `risk_score=1.00`**（`includes/rest-endpoints.php`: CRITICAL 3 / MED 2、`includes/ajax-handlers.php`: CRITICAL 3、`admin/settings-page.php`: CRITICAL 1 / HIGH 2 / MED 1、`member-analytics-portal.php`: HIGH 5 / MED 1 / LOW 1）に達しており、全モジュールがグローバルな `$wpdb` とスーパーグローバル配列に密結合している。

```drawlib file=arch_wp_boundary_topology.png caption="観点3: WPプラグイン実行・データストア境界トポロジ × リスク密度オーバーレイ (HeatmapOverlay)"
from drawlib.canvas import save, setup
from drawlib.charts.heatmap import HeatmapOverlay
from drawlib.diagrams.class_diagram import ClassDiagram, ClassNode
from drawlib.styles import Styles

setup(width=146, height=78, dpi=150)

danger_hdr = Styles.Danger.patch(text_color=Styles.WhiteBold.text_color, text_size=8.4)
primary_hdr = Styles.Primary.patch(text_color=Styles.WhiteBold.text_color, text_size=8.4)
warning_hdr = Styles.Warning.patch(text_color=Styles.DarkBold.text_color, text_size=8.4)

diag = ClassDiagram(
    node_style=Styles.Neutral,
    header_style=Styles.PrimaryFlat,
    edge_style=Styles.PrimaryBold,
    edge_text_style=Styles.Dark.patch(text_size=8.6),
    style=Styles.Neutral.patch(shape_r=2.0),
    width=124,
    height=70,
    title="WPプラグイン境界トポロジ × モジュールリスク密度 (全4モジュール Risk 1.00)",
    title_style=Styles.DarkBold.patch(text_size=9.6),
)

n_boot = ClassNode(
    "member-analytics-portal.php",
    stereotype="Bootstrap / Shortcode (11 LOC)",
    width=43,
    header_height=7.8,
    row_height=3.4,
    header_style=danger_hdr,
)
n_boot.add_attribute("ABSPATH Guard", "MISSING")
n_boot.add_method("map_render_badge_shortcode", "atts", "html")

n_rest = ClassNode(
    "includes/rest-endpoints.php",
    stereotype="WP REST API v1 (21 LOC)",
    width=39,
    header_height=7.8,
    row_height=3.4,
    header_style=danger_hdr,
)
n_rest.add_attribute("map_webhook_secret", "HARDCODED")
n_rest.add_method("map_export_all_members", "req", "rows")

n_ajax = ClassNode(
    "includes/ajax-handlers.php",
    stereotype="Admin-AJAX nopriv (21 LOC)",
    width=39,
    header_height=7.8,
    row_height=3.4,
    header_style=danger_hdr,
)
n_ajax.add_method("map_ajax_search_members", "void", "json")
n_ajax.add_method("map_ajax_purge_logs", "void", "html")

n_adm = ClassNode(
    "admin/settings-page.php",
    stereotype="WP Admin cap='read' (31 LOC)",
    width=39,
    header_height=7.8,
    row_height=3.4,
    header_style=danger_hdr,
)
n_adm.add_method("map_register_admin_menu", "void", "void")
n_adm.add_method("map_render_settings_page", "void", "html")

n_db = ClassNode(
    "WordPress wpdb & Options",
    stereotype="Backing MySQL Store",
    width=40,
    header_height=7.8,
    row_height=3.4,
    header_style=primary_hdr,
)
n_db.add_attribute("wp_users / wp_map_events", "Raw SQL")

n_ext = ClassNode(
    "telemetry.example.com",
    stereotype="External HTTPS (No Timeout)",
    width=40,
    header_height=7.8,
    row_height=3.4,
    header_style=warning_hdr,
)
n_ext.add_method("GET /ping?site=...", "@file_get_contents", "60s")

diag.add(n_boot, xy=(63, 52))
diag.add(n_rest, xy=(23, 31))
diag.add(n_ajax, xy=(63, 31))
diag.add(n_adm, xy=(103, 31))
diag.add(n_db, xy=(41, 10))
diag.add(n_ext, xy=(98, 10))

diag.connect(n_boot, n_rest, directed=True)
diag.connect(n_boot, n_ajax, directed=True)
diag.connect(n_boot, n_adm, directed=True)
diag.connect(n_rest, n_db, directed=True)
diag.connect(n_ajax, n_db, directed=True)
diag.connect(n_adm, n_db, directed=True)
diag.connect(n_adm, n_ext, directed=True)
diag.draw(xy=(3, 4))

ov = HeatmapOverlay(
    min_style=Styles.Success,
    max_style=Styles.Danger,
    width=124,
    height=70,
    min_value=0.0,
    max_value=1.0,
    default_radius=13.5,
    max_alpha=0.26,
    show_contour_lines=True,
)
ov.add_spot(xy=(63, 52), value=1.00, radius=13.5)
ov.add_spot(xy=(23, 31), value=1.00, radius=14.5)
ov.add_spot(xy=(63, 31), value=1.00, radius=14.5)
ov.add_spot(xy=(103, 31), value=1.00, radius=14.5)
ov.add_spot(xy=(41, 10), value=0.35, radius=11.0)
ov.add_spot(xy=(98, 10), value=0.55, radius=11.0)
ov.draw(xy=(3, 4))
ov.draw_colorbar(
    xy=(131, 14),
    text_style=Styles.Dark.patch(text_size=9.0),
    length=46.0,
    thickness=2.6,
    orientation="vertical",
    label="Risk",
)

save()
```
