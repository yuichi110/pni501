# Live Sample Reports Gallery (Workflow v2)

Explore **bilingual (`English` & `日本語`) HTML and A4 PDF reports** generated end-to-end by **PNI501 Workflow v2** against real polyglot repositories under `examples/`. Every published report combines deterministic AST analysis, isolated Docker container verification, Trivy SCA/IaC scanning, live HTTP DAST penetration testing (where applicable), an action-level **Executed Audit DAG**, **7-axis Deterministic Baseline vs. AI Δ (`±10pt`)** anchoring, and downloadable **ScoreResult v2.0 JSON / ScoreSummary / SARIF 2.1.0** artifacts.

```drawlib align=center code=fold file=sample_reports_portfolio.png caption="Published PNI501 Workflow v2 Sample Report Portfolio Across Python, Java, and PHP"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import KpiCards, Panel
from drawlib.styles import Styles

setup(width=156, height=84, dpi=150)

outer = Panel(
    "PNI501 Live Sample Portfolio — Bilingual (EN / JA) HTML + A4 PDF + JSON / SARIF",
    header_variant="filled",
    style=Styles.PrimaryNeutral.patch(shape_r=2.0),
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=12.0),
)
outer.draw(xy=(3.0, 22.0), width=150.0, height=59.0)

cards = KpiCards(
    style=Styles.Neutral.patch(shape_r=1.8),
    metric_style=Styles.SuccessBold.patch(text_size=13.0),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Dark.patch(text_size=9.8),
    accent_position="left_pill",
    accent_style=Styles.SuccessFlat,
    icon_style=Styles.SuccessBold,
    spacing=3.5,
)
cards.add(
    "94 / S",
    "order-dispatch (Python FastAPI)",
    "Clean 4-layer benchmark: 4/4 tests,\n85.2% cov, Trivy + live DAST (15/19)",
    icon=phosphor.check_circle,
)
cards.add(
    "66 / C",
    "legacy-billing (Java 8 Spring)",
    "AST x Docker x Trivy causal proof:\nLATEST -> 4.2.0 crash, cycle, secret",
    accent_style=Styles.WarningFlat,
    metric_style=Styles.WarningBold.patch(text_size=13.0),
    icon_style=Styles.WarningBold,
    icon=phosphor.warning_circle,
)
cards.add(
    "Plan",
    "Java 8 -> Java 21 Migration",
    "based_on chained To-Be Clean Arch,\nWave DAG, Decision Log & PR WBS",
    accent_style=Styles.PrimaryFlat,
    metric_style=Styles.PrimaryBold.patch(text_size=13.0),
    icon_style=Styles.PrimaryBold,
    icon=phosphor.git_pull_request,
)
cards.add(
    "60 / C",
    "Member Analytics (WP PHP)",
    "Security 30/D: 3x CWE-89 SQLi,\n3x CWE-79 XSS, __return_true PII",
    accent_style=Styles.DangerFlat,
    metric_style=Styles.DangerBold.patch(text_size=13.0),
    icon_style=Styles.DangerBold,
    icon=phosphor.shield_warning,
)
cards.draw(xy=(6.5, 25.0), width=143.0, height=45.5, columns=2)

footer = KpiCards(
    style=Styles.Neutral.patch(shape_r=1.6),
    metric_style=Styles.PrimaryBold.patch(text_size=12.5),
    text_style=Styles.DarkBold.patch(text_size=10.0),
    accent_style=Styles.PrimaryFlat,
    accent_position="top_bar",
    metric_layout="top_stack",
    spacing=3.0,
)
footer.add("3 Languages", "Python / Java / PHP")
footer.add("2 Tracks", "Health Audit + Migration")
footer.add("EN + JA", "HTML Switcher & A4 PDFs")
footer.add("Zero Guess", "_facts/ + SARIF 2.1.0")
footer.draw(xy=(3.0, 3.0), width=150.0, height=16.5, columns=4)
save()
```

---

## 1. Published Reports Matrix

Each sample report is compiled into a self-contained directory under `docs/reports/<slug>/` with interactive bilingual HTML, printable A4 vector PDFs, and machine-readable JSON/SARIF evidence:

| Sample Target | Track & Stack | Result | Interactive HTML | A4 Vector PDF | Machine-Readable Artifacts |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`order-dispatch`** (`examples/python/api_fastapi_clean`) | **Health Audit**<br>Python 3.11+ / FastAPI | **94 / 100 (Grade S)**<br>12/16 rules PASS | [English](../../reports/py_api_fastapi_clean/en/index.html) / [日本語](../../reports/py_api_fastapi_clean/ja/index.html) | [PDF (EN)](../../reports/py_api_fastapi_clean/py_api_fastapi_clean_en.pdf) / [PDF (JA)](../../reports/py_api_fastapi_clean/py_api_fastapi_clean_ja.pdf) | [Score JSON](../../reports/py_api_fastapi_clean/py_api_fastapi_clean_score.json) · [Summary](../../reports/py_api_fastapi_clean/py_api_fastapi_clean_summary.json) · [SARIF](../../reports/py_api_fastapi_clean/py_api_fastapi_clean_findings.sarif) |
| **`legacy-billing`** (`examples/java/api_spring_messy`) | **Health Audit**<br>Java 8 / Spring Boot | **66 / 100 (Grade C)**<br>Build crash + 19 findings | [English](../../reports/java_api_spring_messy/en/index.html) / [日本語](../../reports/java_api_spring_messy/ja/index.html) | [PDF (EN)](../../reports/java_api_spring_messy/java_api_spring_messy_en.pdf) / [PDF (JA)](../../reports/java_api_spring_messy/java_api_spring_messy_ja.pdf) | [Score JSON](../../reports/java_api_spring_messy/java_api_spring_messy_score.json) · [Summary](../../reports/java_api_spring_messy/java_api_spring_messy_summary.json) · [SARIF](../../reports/java_api_spring_messy/java_api_spring_messy_findings.sarif) |
| **`legacy-billing` Migration** (`based_on: java_api_spring_messy`) | **Migration Plan**<br>Java 21 + Spring Boot 3.4 + Clean Arch | **Phased PR Plan**<br>4 Waves · Phase 0–4 | [English](../../reports/java_api_spring_messy_migration/en/index.html) / [日本語](../../reports/java_api_spring_messy_migration/ja/index.html) | [PDF (EN)](../../reports/java_api_spring_messy_migration/java_api_spring_messy_migration_en.pdf) / [PDF (JA)](../../reports/java_api_spring_messy_migration/java_api_spring_messy_migration_ja.pdf) | [Migration Plan JSON](../../reports/java_api_spring_messy_migration/java_api_spring_messy_migration_plan.json) |
| **`Member Analytics Portal`** (`examples/php/wp_plugin_messy`) | **Health Audit**<br>PHP 7.4 / WordPress Plugin | **60 / 100 (Grade C)**<br>Security **30/D** · 5 CWE sinks | [English](../../reports/php_wp_plugin_messy/en/index.html) / [日本語](../../reports/php_wp_plugin_messy/ja/index.html) | [PDF (EN)](../../reports/php_wp_plugin_messy/php_wp_plugin_messy_en.pdf) / [PDF (JA)](../../reports/php_wp_plugin_messy/php_wp_plugin_messy_ja.pdf) | [Score JSON](../../reports/php_wp_plugin_messy/php_wp_plugin_messy_score.json) · [Summary](../../reports/php_wp_plugin_messy/php_wp_plugin_messy_summary.json) · [SARIF](../../reports/php_wp_plugin_messy/php_wp_plugin_messy_findings.sarif) |

---

## 2. What Each Sample Demonstrates

### 2.1 `order-dispatch` (Python FastAPI Clean — Grade S, 94/100)
- **Clean Microservice Reference**: 100% typing, import hygiene, and Google-style docstrings across 14 modules (435 LOC) with a strict acyclic 4-layer architecture (`api -> services -> domain + infra`).
- **Live Docker Runtime + Trivy + DAST**: 4/4 offline `--network=none` tests pass (`85.2%` line / `62.5%` branch coverage, clean `/healthz -> 200` ASGI boot), 0 CRITICAL/HIGH app CVEs, and 15/19 live HTTP DAST probes pass while catching concrete production gaps (`CWE-306` unauthenticated `POST /v1/orders`, `CWE-200` `/openapi.json`, `CWE-693` missing `X-Content-Type-Options`).
- **Auditable FP Triage**: Demonstrates Workflow v2's `finding_adjustments` log reclassifying 5 build-time `pip@24.2` toolchain CVEs bundled in `python:3.12.6-slim-bookworm` with full justification.

### 2.2 `legacy-billing` (Java 8 Spring Legacy — Grade C, 66/100)
- **AST × Docker × Trivy Causal Correlation**: Proves live why unpinned `spring-boot-starter-web:LATEST` in `pom.xml` is fatal — live Maven resolves `spring-boot-4.2.0.jar` (JDK 17+ bytecode `61.0`) against Java `1.8` (`52.0`) and crashes, `Dockerfile` fails on removed `openjdk:latest`, Trivy flags `CVE-2022-22965` via unpinned static range matching (`is_unpinned_specifier=True`), and DAST is cleanly reported as blocked by buildability.
- **Hotspot Contrast & Baseline Anchoring**: Contrasts `BillingManager.java` (circular `BillingController` DI, cognitive complexity 56, 8 parameters, static `INVOICE_CACHE`, `==` String bugs, empty `catch`, broken private `@Transactional`) against clean immutable `InvoiceRecord.java`, with transparent `-10pt` anchored qualitative deltas across all 7 axes.

### 2.3 `legacy-billing` Migration Execution Plan (`based_on: java_api_spring_messy`)
- **Prerequisite-Gated `based_on` Chaining**: Inherits verified As-Is facts directly from the completed `java_api_spring_messy` audit run in `.pni/cache/workflow_state.db` without re-scanning or inventing symbols.
- **To-Be Clean Architecture & PR WBS**: Maps Java 21 LTS + Spring Boot 3.4 + PostgreSQL 16 (JPA + Flyway) + Redis 7 + Clean Architecture (`domain / port / usecase / adapter`) across deterministic topological waves, a Stakeholder Decision Log for Hyrum's Law quirks (`currency == "USD"`, `controllerPing`, fixed `100L` retry), and Phase 0–4 PR verification gates.

### 2.4 `Member Analytics Portal` (WordPress PHP Plugin — Grade C, 60/100 · Security 30/D)
- **Deep WordPress Security SAST**: Flags all 5 HIGH CWE dangerous sinks (3× `CWE-89` unparameterized `$wpdb` SQL injection querying `wp_users` and deleting `wp_map_events`, 2× `CWE-79` reflected XSS + shortcode `$_GET` XSS), hardcoded webhook secret, unauthenticated REST export (`__return_true`), `wp_ajax_nopriv` search, `'read'`-capability admin settings privilege escalation, missing `ABSPATH` guards, and 0 PHPUnit tests despite passing `php -l` and 5-hook smoke loading.

---

## 3. Unified Portal Architecture (`docs_src/` -> `docs/`)

All official documentation and sample reports live under a single flat Drawlib multi-project source tree (`docs_src/`) and compile into GitHub Pages (`docs/`):

```drawlib align=center code=fold file=sample_reports_portal_layout.png caption="Unified Documentation & Sample Reports Publishing Architecture (docs_src/ -> docs/)"
from drawlib.canvas import save, setup
from drawlib.diagrams.architecture import ArchitectureDiagram, Node, NodeGroup, PhosphorIcon
from drawlib.styles import Styles

setup(width=158, height=74, dpi=150)

diag = ArchitectureDiagram(
    node_style=Styles.PrimaryBold,
    node_text_style=Styles.DarkBold.patch(text_size=10.0),
    edge_style=Styles.DarkBold,
    edge_text_style=Styles.DarkBold.patch(text_size=9.5),
    node_card_style=Styles.WhiteBordered.patch(shape_r=1.5),
)

g_src = diag.add(
    NodeGroup(
        title="1. Source of Truth (docs_src/)",
        width=46.0,
        height=66.0,
        style=Styles.Neutral.patch(shape_r=2.0),
        text_style=Styles.DarkBold.patch(text_size=10.5, halign="left", valign="top"),
    ),
    xy=(3.0, 4.0),
)
n_site_src = g_src.add(
    Node(
        "docs_src/site/\ndrawlib site (en + ja)",
        width=40.0,
        height=18.0,
        icon=PhosphorIcon.BOOK_OPEN_TEXT,
        icon_size=5.4,
        card_style=Styles.PrimaryNeutral.patch(shape_r=1.5),
    ),
    xy=(23.0, 46.0),
)
n_rep_src = g_src.add(
    Node(
        "docs_src/reports/<slug>/\ndrawlib doc + _facts/ + en/ja",
        width=40.0,
        height=18.0,
        icon=PhosphorIcon.FILE_TEXT,
        icon_size=5.4,
        style=Styles.SecondaryBold,
        card_style=Styles.SecondaryNeutral.patch(shape_r=1.5),
    ),
    xy=(23.0, 17.0),
)

g_build = diag.add(
    NodeGroup(
        title="2. Build & Verify",
        width=38.0,
        height=66.0,
        style=Styles.Neutral.patch(shape_r=2.0),
        text_style=Styles.DarkBold.patch(text_size=10.5, halign="left", valign="top"),
    ),
    xy=(58.0, 4.0),
)
n_build = g_build.add(
    Node(
        "./docs_src/build.sh\npni report build\n+ drawlib serve --check",
        width=32.0,
        height=26.0,
        icon=PhosphorIcon.GEAR,
        icon_size=5.6,
        style=Styles.WhiteBold,
        text_style=Styles.WhiteBold.patch(text_size=10.0),
        card_style=Styles.PrimaryFlat.patch(shape_r=1.5),
    ),
    xy=(19.0, 31.5),
)

g_out = diag.add(
    NodeGroup(
        title="3. GitHub Pages (docs/)",
        width=49.0,
        height=66.0,
        style=Styles.Neutral.patch(shape_r=2.0),
        text_style=Styles.DarkBold.patch(text_size=10.5, halign="left", valign="top"),
    ),
    xy=(106.0, 4.0),
)
n_site_out = g_out.add(
    Node(
        "docs/{en,ja}/ + index.html\nwww.pni501.com",
        width=43.0,
        height=18.0,
        icon=PhosphorIcon.GLOBE,
        icon_size=5.4,
        card_style=Styles.PrimaryNeutral.patch(shape_r=1.5),
    ),
    xy=(24.5, 46.0),
)
n_rep_out = g_out.add(
    Node(
        "docs/reports/<slug>/\nHTML + EN/JA PDF + JSON/SARIF",
        width=43.0,
        height=18.0,
        icon=PhosphorIcon.FILE_PDF,
        icon_size=5.4,
        style=Styles.SuccessBold,
        card_style=Styles.SuccessNeutral.patch(shape_r=1.5),
    ),
    xy=(24.5, 17.0),
)

diag.connect(n_site_src, n_build, label="site html")
diag.connect(n_rep_src, n_build, label="pdf + html")
diag.connect(n_build, n_site_out, label="portal")
diag.connect(n_build, n_rep_out, label="reports")
diag.draw()
save()
```

To regenerate the entire portal and validate zero broken links locally:

```bash
./docs_src/build.sh
./docs_src/serve.sh
```
