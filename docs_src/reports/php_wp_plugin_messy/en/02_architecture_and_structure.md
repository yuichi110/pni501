# 2. Architecture & Source Code Structure

**Member Analytics Portal (`wp_plugin_messy` v1.3.0)** follows a **Procedural Flat WordPress Plugin** layout across 4 PHP files (`84` total LOC, `7` procedural functions, `0` classes). While file inclusion is strictly acyclic, every handler couples directly to global WordPress database handles (`$wpdb`) and raw HTTP superglobals (`$_GET`, `$_POST`) without OOP/PSR-4 boundaries, sanitization middleware, or authorization guards.

```drawlib align=center code=fold file=arch_source_tree.png caption="Plugin Directory Tree (4 PHP Modules + README) and Grounded Module Inventory"
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

## Procedural Hook Coupling & Thermal Risk Overlay

The dependency diagram below models the 4 procedural PHP modules alongside the shared WordPress global state surface (`$wpdb`, `$_GET`, `$_POST`, `wp_options`, and `$map_webhook_secret`), overlaid with normalized `module_hotspots` risk intensity (`1.00` on `includes/ajax-handlers.php`, `includes/rest-endpoints.php`, and `member-analytics-portal.php`; `0.54` on `admin/settings-page.php`).

```drawlib align=center code=fold file=arch_coupling_heatmap.png caption="Procedural Module Dependency Graph, Global WordPress State Coupling, and Thermal Risk Overlay"
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

## Runtime Request & Attack Execution Flows

The plugin exposes **5 entry points** across REST, `admin-ajax.php`, WordPress Admin Options, and frontend shortcodes. The diagram below traces the three primary request execution chains directly from untrusted HTTP input to database and browser sinks.

```drawlib align=center code=fold file=arch_request_flows.png caption="Primary Runtime Request Flows Across REST Export, AJAX Search/Purge, and Admin Settings"
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

## Layer Architecture & Boundary Assessment

| Layer | Paths | Allowed Dependencies | Responsibility & Health Assessment |
| :--- | :--- | :--- | :--- |
| **Plugin Bootstrap & Shortcode Entrypoint** | `member-analytics-portal.php` | REST, AJAX, Admin modules | Manual `require_once` loading, hook registration (`rest_api_init`, shortcode), and `[member_analytics_badge]` rendering. Missing `ABSPATH` guard; EOL PHP 7.4 header; `$_GET['badge_label']` XSS. |
| **REST Endpoint Module** | `includes/rest-endpoints.php` | *(none)* | Registers `/wp-json/member-analytics/v1/export` and queries `$wpdb->users`. Hardcoded `$map_webhook_secret` (`<REDACTED_SECRET>`), `__return_true`, CWE-89 SQLi, and `print_r()` debug leak. |
| **AJAX Handler Module** | `includes/ajax-handlers.php` | *(none)* | Registers `wp_ajax_nopriv_map_search_members` and `wp_ajax_map_purge_logs`. Unparameterized `SELECT`/`DELETE` SQLi, missing nonces/capabilities, and unescaped `echo` XSS. |
| **Admin Settings Module** | `admin/settings-page.php` | *(none)* | Registers WP options page (`'read'` cap), persists `map_telemetry_url`, pings `https://telemetry.example.com/ping` via `@file_get_contents()`, and renders inline HTML/JS. |

## Pre-Sorted Module Hotspots (`module_hotspots`)

PNI aggregates both deterministic AST file paths (`examples/php/wp_plugin_messy/...`) and AI qualitative relative module paths; both exact hotspot records are preserved below in descending risk order:

| File Path | LOC | Risk Score | Findings | Top Rules / CWEs |
| :--- | :---: | :---: | :--- | :--- |
| `examples/php/wp_plugin_messy/includes/ajax-handlers.php` | 21 | **1.00** | 3 HIGH | `CWE-79`, `CWE-89` |
| `examples/php/wp_plugin_messy/includes/rest-endpoints.php` | 21 | **1.00** | 1 CRIT, 1 HIGH | `common/security`, `CWE-89` |
| `member-analytics-portal.php` | — | **1.00** | 4 HIGH | `php/dependencies`, `common/security`, `common/runtime_verification`, `php/typing` |
| `includes/rest-endpoints.php` | — | **0.90** | 2 CRIT | `common/security`, `php/frameworks/wordpress` |
| `examples/php/wp_plugin_messy/admin/settings-page.php` | 31 | **0.54** | 1 HIGH | `CWE-79` |
| `includes/ajax-handlers.php` | — | **0.45** | 1 CRIT | `php/frameworks/wordpress` |
| `admin/settings-page.php` | — | **0.28** | 1 HIGH | `php/frameworks/wordpress` |
| `examples/php/wp_plugin_messy/member-analytics-portal.php` | 11 | **0.14** | 0 | *(deterministic AST baseline)* |

## State, Storage & Concurrency Model

- **Database State**: Directly queries WordPress MySQL tables (`$wpdb->users` and `wp_map_events`) via `global $wpdb` without `$wpdb->prepare()`.
- **Option Persistence**: Mutates `wp_options` key `map_telemetry_url` via `update_option()` with unsanitized `$_POST['map_telemetry_url']` and zero CSRF verification.
- **Global Secret**: Hardcodes `$map_webhook_secret = '<REDACTED_SECRET>'` at module scope in `includes/rest-endpoints.php:3`.
- **Error & Concurrency Model**: Synchronous PHP request-per-process model under WordPress with silent failure suppression (`@file_get_contents()`), unstructured `print_r()` debug dumps, and no defensive input validation or exception handling.
