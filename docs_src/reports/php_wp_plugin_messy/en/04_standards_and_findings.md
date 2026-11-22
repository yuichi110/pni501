# 4. Audit Pipeline (DAG), Standards & Findings

This chapter documents the exact executed audit pipeline, deterministic tooling scope, 7-axis score anchoring (`±10pt` deterministic-to-AI guardrail), full rule compliance matrix, consolidated evidence index, and machine-readable artifact provenance.

```drawlib align=center code=fold file=audit_pipeline_dag.png caption="Executed PNI Workflow v2 Audit Pipeline DAG (9 Logical Stages with ASK/HYBRID/AI Badges)"
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

## Inspection Scope & Deterministic Tools Executed

| Scope Parameter | Audited Value |
| :--- | :--- |
| **Target Root & Paths** | `examples/php/wp_plugin_messy` (`source=['.']`, `tests=['tests']`, `docs=['README.md']`, `exclude=[]`) |
| **Languages & Frameworks** | Primary: `php` · Companions: `none` · Detected Frameworks: `wordpress` |
| **Git Provenance** | `main@d1e02277 (dirty)` |
| **Deterministic Tools Executed** | `project_inspect (php)`, `tree-sitter AST (php)`, `container runtime harness (docker: php/raw.dockerfile)`, `Trivy (docker: fs+image)` |
| **Logical DAG Stages** | 11 pipeline stages (`confirm_plan`, `repo_and_deps`, `supply_chain`, `ast_and_quality`, `runtime_verification`, `security_audit`, `arch_recording`, `service_readiness`, `test_health`, `output_score`, `create_report`) — 0 stages skipped |

## 7-Axis Deterministic Baseline vs. AI Adjustment (`±10pt`)

PNI computes deterministic baseline scores directly from AST, runtime, and SCA facts, then caps qualitative AI adjustments strictly within `±10pt` per axis. Across `wp_plugin_messy`, systemic WordPress security gaps, missing typing/tests, and raw PHP debt warranted a consistent `-10pt` adjustment on every axis (`70 -> 60`).

```drawlib align=center code=fold file=baseline_vs_final_scores.png caption="7-Axis Deterministic Baseline vs. Final Score After AI Qualitative Adjustment (-10pt Cap)"
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

| Axis | Baseline | AI Δ | Final | Grade | Anchoring Rationale |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Architecture** | 100 | −10 | **90** | A | Acyclic 4-file inclusion, but global procedural functions, manual `require_once`, and 13 direct superglobal/global `$wpdb` accesses with zero OOP/PSR-4 boundaries. |
| **Code Quality** | 100 | −10 | **90** | A | 16 WordPress framework violations, `@file_get_contents()` error suppression without timeout, `print_r()` debug leak, and hardcoded `<script src=...>`. |
| **Typing** | 46 | −10 | **36** | D | `0.0%` PHP type safety: missing `declare(strict_types=1)` in all 4 files and zero parameter/return type declarations across all 7 functions. |
| **Testing** | 65 | −10 | **55** | C | Zero PHPUnit/Pest tests (`0%` measured coverage), leaving all REST, AJAX, DB, and admin paths unverified beyond `php -l` and 5-hook load smoke. |
| **Dependencies** | 100 | −10 | **90** | A | `0` declared Composer CVEs, but unmanaged Composer-less raw PHP targeting EOL PHP `>=7.4` with zero CI, `LICENSE`, `SECURITY.md`, or Dependabot. |
| **Security** | 40 | −10 | **30** | D | Severe multi-vector WordPress flaws across all 4 files: hardcoded `$map_webhook_secret`, 3 `CWE-89` SQLi, 3 `CWE-79` XSS, unauth REST/AJAX PII leak, `'read'`-cap escalation, zero nonces, no `ABSPATH`. |
| **Documentation** | 37 | −10 | **27** | D | 2-line `README.md` and `0.0%` PHPDoc coverage across all 7 public functions. |
| **Overall** | **70** | **−10** | **60** | **C** | Weighted synthesis anchored by deterministic baseline with full `−10pt` qualitative security/hygiene deduction. |

## Executed Audit Step Scores (Weakest-First)

Every individual audit step scored **Grade D (`10`–`45/100`)**, with test completeness (`10/100`), security vulnerability review (`14/100`), and PHP AST inspection (`16/100`) recording the steepest penalties.

```drawlib align=center code=fold file=audit_step_scores.png caption="Executed Audit Step Scores (Weakest-First) and Finding Source Breakdown"
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

## Rule Compliance Matrix (`FAIL -> WARN -> N/A`, 17 Rules)

| Status | Rule ID | Source Audit | Evidence Summary |
| :-: | :--- | :--- | :--- |
| **FAIL** | `common/documentation` | `repo_structure_audit` | `README.md` has only 2 lines with no installation, shortcode/REST reference, or security/dev instructions. |
| **FAIL** | `common/production_readiness` | `container_runtime_audit` | `admin/settings-page.php:21` calls `@file_get_contents()` without timeout and suppresses errors; `includes/rest-endpoints.php:21` leaks rows via `print_r()`. |
| **FAIL** | `common/runtime_verification` | `container_runtime_audit` | `build=passed`, `php -l` passed, 5-hook smoke passed, but `0` PHPUnit tests exist and `coverage.measured=False`. |
| **FAIL** | `common/security` | `repo_structure_audit` | Hardcoded `$map_webhook_secret` (`<REDACTED_SECRET>`), 3 SQLi sinks, 3 XSS points (including shortcode `$_GET['badge_label']`), unauth REST/AJAX PII leak, zero CSRF/capability checks, and missing `ABSPATH`. |
| **FAIL** | `common/security_vulnerability` | `php_ast_audit` | `SEC-01` 0 declared app CVEs (harness OS excluded); `SEC-02` N/A; `SEC-03` FAIL hardcoded secret; `SEC-04` FAIL 5 HIGH CWE sinks; `SEC-05` FAIL 4/5 unauthenticated endpoints. |
| **FAIL** | `common/supply_chain` | `repo_structure_audit` | Missing `composer.json`/`composer.lock`, `LICENSE`, `SECURITY.md`, CI workflows, and Dependabot; targets EOL PHP `>=7.4`. |
| **FAIL** | `php/code_quality` | `php_ast_audit` | `0.0%` PHPDoc across 7 functions, 13 superglobal/global `$wpdb` accesses, `print_r()` debug output, and `@file_get_contents()` error suppression. |
| **FAIL** | `php/dependencies` | `repo_structure_audit` | Composer-less raw PHP with manual `require_once` in `member-analytics-portal.php` and EOL `Requires PHP: 7.4`. |
| **FAIL** | `php/frameworks/wordpress` | `php_ast_audit` | 16 WordPress violations: missing `ABSPATH` in all 4 files, REST `__return_true`, `wp_ajax_nopriv`, `'read'`-cap admin page, zero nonces/capabilities, raw `$wpdb` SQL, hardcoded `<script>`, unescaped `echo`. |
| **FAIL** | `php/modern_stack` | `repo_structure_audit` | EOL PHP `>=7.4`, missing `declare(strict_types=1)` and types, manual `require_once`, missing HTTP timeout, `print_r()`, and no PHPUnit/Pest config. |
| **FAIL** | `php/testing` | `php_test_audit` | `0` test files and `0` PHPUnit tests across 4 modules (`coverage.measured=False`); only `php -l` and hook smoke ran. |
| **FAIL** | `php/typing` | `php_ast_audit` | `0.0%` type safety: missing `declare(strict_types=1)` in all 4 files and untyped parameters/returns across all 7 functions. |
| **WARN** | `common/architecture` | `php_ast_audit` | Acyclic 4-file procedural split, but relies on manual `require_once`, 0 classes/namespaces, and 13 global/superglobal state accesses. |
| **WARN** | `common/git_workflow` | `repo_structure_audit` | Missing `.gitignore` and CI pull-request quality/security workflow gates. |
| **WARN** | `common/maintainability` | `php_ast_audit` | Compact functions (`0` complexity hotspots), but heavy global/superglobal coupling (`13`) and `@` error suppression hinder testability. |
| **WARN** | `common/twelve_factor` | `service_readiness_audit` | Hardcodes `$map_webhook_secret` (`rest-endpoints.php:3`) and emits unstructured `print_r()` (`rest-endpoints.php:21`). |
| **N/A** | `php/frameworks/laravel` | `php_ast_audit` | Standalone WordPress plugin (`detected_frameworks=['wordpress']`); Laravel is not used. |

## Consolidated Location Findings Index (`CRITICAL -> MEDIUM`)

- **Finding Source Split**: `7` deterministic analyzer findings + `8` AI qualitative findings = **15 total findings** consolidated into **11 unique locations**.
- **AI False-Positive Triage & Design Waivers**: `0` deterministic pre-findings waived or reclassified; `0` active `pni.toml [[opt_out]]` design waivers.

| # | Severity | Location | Rules / CWEs | Grounded Evidence & Remediation |
| :-: | :-: | :--- | :--- | :--- |
| 1 | **CRITICAL** | `examples/php/wp_plugin_messy/includes/rest-endpoints.php:3` | `common/security` | Hardcoded secret literal (`<REDACTED_SECRET>`) assigned to `$map_webhook_secret`. Remove, rotate key, and load via env/secret manager. |
| 2 | **CRITICAL** | `includes/ajax-handlers.php` | `php/frameworks/wordpress` | `map_ajax_search_members` exposes `wp_users` via `wp_ajax_nopriv` + SQLi; `map_ajax_purge_logs` runs raw `DELETE` SQLi without nonce/capability and echoes raw `$_POST['category']`. Remove `nopriv`, add `check_ajax_referer()` + `manage_options` + `$wpdb->prepare()` + `wp_send_json_success()`. |
| 3 | **CRITICAL** | `includes/rest-endpoints.php` | `common/security`, `php/frameworks/wordpress` | Hardcoded `$map_webhook_secret` (`<REDACTED_SECRET>`); `GET /wp-json/member-analytics/v1/export` uses `__return_true`, concatenates `$_GET['role_filter']` into `$wpdb->users` SQL, and dumps via `print_r()`. Enforce `manage_options`, `$request->get_param()`, `$wpdb->prepare()`, and remove `print_r()`. |
| 4 | **HIGH** | `admin/settings-page.php` | `php/frameworks/wordpress` | `add_options_page` grants `'read'` cap (subscriber), mutates `map_telemetry_url` without nonce/cap, calls unbounded `@file_get_contents()`, echoes raw `$_GET['tab']`, and hardcodes `<script src=...>`. Require `manage_options`, `check_admin_referer()`, `esc_url_raw()`, `wp_remote_get(['timeout'=>5])`, `esc_html()`/`esc_attr()`, and `wp_enqueue_script()`. |
| 5 | **HIGH** | `examples/php/wp_plugin_messy/admin/settings-page.php:26` | `CWE-79` | Unescaped request input rendered via `echo $_GET['tab'] ?? 'general';`. Sanitize and escape with `esc_html()`. |
| 6 | **HIGH** | `examples/php/wp_plugin_messy/includes/ajax-handlers.php:10` | `CWE-89` | Unparameterized SQL in `$wpdb->get_results("SELECT ID, display_name, user_email FROM {$wpdb->users} ...")`. Parameterize with `$wpdb->prepare()` + `$wpdb->esc_like()`. |
| 7 | **HIGH** | `examples/php/wp_plugin_messy/includes/ajax-handlers.php:21` | `CWE-89` | Unparameterized SQL in `$wpdb->query("DELETE FROM wp_map_events WHERE category = ...")`. Parameterize with `$wpdb->prepare()`. |
| 8 | **HIGH** | `examples/php/wp_plugin_messy/includes/ajax-handlers.php:22` | `CWE-79` | Unescaped request input rendered via `echo "Purged category: " . $_POST['category'];`. Escape with `esc_html()` or return JSON via `wp_send_json_success()`. |
| 9 | **HIGH** | `examples/php/wp_plugin_messy/includes/rest-endpoints.php:19` | `CWE-89` | Unparameterized SQL in `$wpdb->get_results($sql)`. Parameterize with `$wpdb->prepare()` + `$wpdb->esc_like()`. |
| 10 | **HIGH** | `member-analytics-portal.php` | `php/dependencies`, `common/security`, `common/runtime_verification`, `php/typing` | Declares EOL `Requires PHP: 7.4` with manual `require_once`; shortcode interpolates raw `$_GET['badge_label']`; 0 PHPUnit tests; all 4 files lack `ABSPATH`, `strict_types=1`, types, and PHPDoc. Add `ABSPATH`, `esc_html()`, Composer PHP 8.2+ PSR-4, and PHPUnit suite. |
| 11 | **MEDIUM** | `README.md` | `common/documentation` | Minimal 2-line README (`has_readme=True, lines=2`). Document architecture, requirements, REST/AJAX endpoints, security setup, and dev workflow. |

## Machine-Readable Evidence Artifacts

Raw JSON/SARIF payloads are intentionally omitted from this narrative report and archived at the repository-relative paths below for CI automation, GitHub Code Scanning, and audit reproducibility:

| Artifact Path | Schema / Format | Purpose |
| :--- | :--- | :--- |
| `docs/reports/php_wp_plugin_messy/php_wp_plugin_messy_score.json` | `ScoreResult` v2.0 (JSON) | Full 7-axis scores, baseline deltas, findings, runtime & Trivy facts |
| `docs/reports/php_wp_plugin_messy/php_wp_plugin_messy_summary.json` | `ScoreSummary` (JSON) | Lightweight CI / dashboard summary record |
| `docs/reports/php_wp_plugin_messy/php_wp_plugin_messy_findings.sarif` | `SARIF 2.1.0` | GitHub Code Scanning & IDE inline finding annotations |
| `docs_src/reports/php_wp_plugin_messy/_facts/plan.json` | `ReconPlan` (JSON) | Pre-flight recon plan and validated Mermaid execution DAG |
| `docs_src/reports/php_wp_plugin_messy/_facts/facts.json` | Deterministic Facts Bundle | Raw `project_inspect`, tree-sitter AST, runtime harness, and Trivy facts |
| `docs_src/reports/php_wp_plugin_messy/_facts/architecture.json` | `ArchitectureRecord` (JSON) | Grounded layers, modules, entry points, execution flows, and state map |
