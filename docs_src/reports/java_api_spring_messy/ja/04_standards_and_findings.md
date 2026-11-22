# 4. 監査パイプライン（DAG）・評価基準・検出事項一覧

本章では本監査の完全な透明性と再現性を担保するため、アクションレベルの**実行済み監査パイプライン DAG**、検査対象スコープと決定論的ツール一覧、**7 軸の決定論的ベースライン vs. AI 定性調整（`±10pt`）テーブル**、弱点順の監査ステップ別スコア、全 16 ルールの準拠マトリクス（`FAIL -> WARN`）、重複排除済みの箇所別検出事項一覧、および機械可読アーティファクト参照一覧を提示します。

```drawlib align=center code=hide file=audit_pipeline_dag.png caption="実行済み PNI Workflow v2 監査パイプライン DAG（9 論理ステージ、ASK / HYBRID / AI モードバッジおよび障害ハイライト）"
from drawlib.canvas import save, setup
from drawlib.graph import LayerGraph
from drawlib.lines import line, lines
from drawlib.shapes import rectangle
from drawlib.styles import Styles
from drawlib.text import text

setup(width=146, height=96, dpi=150)

text(
    (73.0, 92.2),
    "Executed Audit Pipeline DAG — java_api_spring_messy (wf-8177454c)",
    style=Styles.DarkBold.patch(text_size=11.5),
)

# Step 1: Solve 5-rank DAG coordinates via LayerGraph (no skip-layer node crossings)
g = LayerGraph(
    direction="LR",
    rank_sep=5.5,
    node_sep=2.2,
    edge_routing="orthogonal",
    default_node_width=24.0,
    default_node_height=11.6,
)
g.node("confirm_plan", layer=0, width=20.5, height=12.0)
g.node("repo_and_deps", layer=1, width=22.5, height=12.0)
g.node("ast_and_quality", layer=2, width=24.5, height=11.6)
g.node("runtime_verification", layer=2, width=24.5, height=11.6)
g.node("security_audit", layer=2, width=24.5, height=11.6)
g.node("web_pentest", layer=2, width=24.5, height=11.6)
g.node("supply_chain", layer=2, width=24.5, height=11.6)
g.node("ast_ai_eval", layer=3, width=23.5, height=11.6)
g.node("output_score", layer=4, width=22.5, height=14.5)

g.edge("confirm_plan", "repo_and_deps")
g.edge("repo_and_deps", "ast_and_quality")
g.edge("repo_and_deps", "runtime_verification")
g.edge("repo_and_deps", "security_audit")
g.edge("repo_and_deps", "web_pentest")
g.edge("repo_and_deps", "supply_chain")
g.edge("ast_and_quality", "ast_ai_eval")

layout = g.get_layout(width=140.0, height=69.0, margin=1.5)

# Align ast_ai_eval with top ast_and_quality row
ast_top_y = layout["ast_and_quality"].y
layout.offset("ast_ai_eval", dy=ast_top_y - layout["ast_ai_eval"].y)

# Place DAG cleanly in y=13..85 band (clear of legend y=4.8 and title y=92.2)
dx, dy = 3.0, 14.0

# Step 2: Render solved edges (re-route ast_and_quality -> ast_ai_eval straight horizontally)
edge_st = Styles.Dark.patch(line_width=1.3)
for e in layout.edges:
    if e.src == "ast_and_quality" and e.dst == "ast_ai_eval":
        continue
    pts = [(px + dx, py + dy) for px, py in e.points]
    lines(pts, arrow_head="->", style=edge_st)

n_ast = layout["ast_and_quality"]
n_ai = layout["ast_ai_eval"]
line(
    (n_ast.right + dx, ast_top_y + dy),
    (n_ai.left + dx, ast_top_y + dy),
    arrow_head="->",
    style=edge_st,
)

# Clean collector bus from ast_ai_eval + lower 4 parallel branches into output_score (zero card crossings)
score_n = layout["output_score"]
bus_x = score_n.left + dx - 4.2
score_in = (score_n.left + dx, score_n.y + dy)
for src_id in ("ast_ai_eval", "runtime_verification", "security_audit", "web_pentest", "supply_chain"):
    sn = layout[src_id]
    sx = sn.right + dx
    sy = sn.y + dy
    lines([(sx, sy), (bus_x, sy), (bus_x, score_in[1]), score_in], arrow_head="->", style=edge_st)

# Step 3: Render stage cards with ASK / HYBRID / AI badges
specs = {
    "confirm_plan": (
        "ASK",
        "Confirm Plan",
        "Auto-approved",
        Styles.Neutral,
        Styles.DarkBold,
        Styles.Dark,
        Styles.MutedFlat,
    ),
    "repo_and_deps": (
        "HYBRID",
        "Repo & Deps",
        "6 src / 1 test\n2 deps (LATEST)",
        Styles.PrimaryNeutral,
        Styles.DarkBold,
        Styles.Dark,
        Styles.PrimaryFlat,
    ),
    "ast_and_quality": (
        "HYBRID",
        "Java AST Audit",
        "187 LOC, 1 cycle\n0 CWE sinks",
        Styles.PrimaryNeutral,
        Styles.DarkBold,
        Styles.Dark,
        Styles.PrimaryFlat,
    ),
    "runtime_verification": (
        "HYBRID",
        "Container Runtime",
        "build=failed\n(61.0 vs 52.0)",
        Styles.DangerNeutral,
        Styles.DangerBold,
        Styles.Dark,
        Styles.DangerFlat,
    ),
    "security_audit": (
        "HYBRID",
        "Trivy SCA & IaC",
        "Trivy 1 CRIT\nunpinned + 3 IaC",
        Styles.DangerNeutral,
        Styles.DangerBold,
        Styles.Dark,
        Styles.DangerFlat,
    ),
    "web_pentest": (
        "HYBRID",
        "Web Pentest",
        "DAST blocked\n(0/0 probes)",
        Styles.WarningNeutral,
        Styles.WarningBold,
        Styles.Dark,
        Styles.WarningFlat,
    ),
    "supply_chain": (
        "AI",
        "Supply Chain & CI",
        "PR_target, @main\nroot Docker",
        Styles.SecondaryNeutral,
        Styles.DarkBold,
        Styles.Dark,
        Styles.SecondaryFlat,
    ),
    "ast_ai_eval": (
        "AI",
        "Arch / PRR / Test",
        "5 layers, 12F\n1 JUnit4 test",
        Styles.SecondaryNeutral,
        Styles.DarkBold,
        Styles.Dark,
        Styles.SecondaryFlat,
    ),
    "output_score": (
        "AI",
        "Score & Report",
        "66/100 (Grade C)\n16 rules, 19 find.",
        Styles.PrimaryFlat,
        Styles.WhiteBold,
        Styles.White,
        Styles.DarkFlat,
    ),
}

for nid, (mode, title, detail, box_st, title_st, body_st, badge_st) in specs.items():
    n = layout[nid]
    cx, cy = n.x + dx, n.y + dy
    rectangle((cx, cy), width=n.width, height=n.height, style=box_st.patch(shape_r=1.8))
    badge_w = 9.8 if mode == "HYBRID" else 6.4
    bx = cx - n.width / 2.0 + badge_w / 2.0 + 1.0
    by = cy + n.height / 2.0 - 2.0
    rectangle(
        (bx, by),
        width=badge_w,
        height=3.0,
        style=badge_st.patch(shape_r=0.9),
        text=mode,
        text_style=Styles.WhiteBold.patch(text_size=7.6),
    )
    text((cx, cy + 1.2), title, style=title_st.patch(text_size=9.2))
    text((cx, cy - 3.1), detail, style=body_st.patch(text_size=8.1))

# Legend strip at bottom with generous horizontal spacing
legend_items = [
    (15.0, 21.0, "ASK: Plan Gate", Styles.Neutral),
    (44.5, 31.0, "HYBRID: Deterministic + AI", Styles.PrimaryNeutral),
    (77.5, 27.0, "AI: Qualitative Eval", Styles.SecondaryNeutral),
    (106.5, 25.0, "Failed / Blocked", Styles.DangerNeutral),
    (132.5, 21.0, "Score Synthesis", Styles.PrimaryFlat),
]
for lx, lw, lbl, st in legend_items:
    t_st = Styles.WhiteBold.patch(text_size=8.8) if st is Styles.PrimaryFlat else Styles.DarkBold.patch(text_size=8.8)
    rectangle((lx, 4.5), width=lw, height=5.0, style=st.patch(shape_r=1.2), text=lbl, text_style=t_st)

save()
```

---

## 検査スコープおよび実行済み決定論的ツール

| スコープ項目 | 記録された監査構成・実行実績 |
| :--- | :--- |
| **対象ルート・パス** | ルート: `examples/java/api_spring_messy` \| ソース: `['src/main/java']` \| テスト: `['src/test/java']` \| ドキュメント: `['README.md']` \| 除外: `['none']` |
| **言語・フレームワーク** | 主言語: `java` \| 補助言語: `['none']` \| 検出フレームワーク: `spring-boot`, `spring-framework`, `javax-ee`, `junit4` |
| **リポジトリ証跡** | Git ブランチ・コミット: `main@d1e02277 (dirty)` \| 実行 ID: `wf-8177454c` |
| **実行済み決定論的ツール** | `project_inspect (java)`、`tree-sitter AST (java)`、`container runtime harness (docker: java/maven.dockerfile)`、`Trivy (docker: fs, ghcr.io/aquasecurity/trivy:0.69.3)`、`web_pentest (httpx, 0 probes — ビルド失敗によりブロック)` |

---

## 7 軸の決定論的ベースライン vs. AI 定性調整（`±10pt`）

PNI Workflow v2 では、すべての評価軸を決定論的ツール由来のベースラインスコアにアンカー固定した上で、上限 `±10pt` の AI 定性調整を適用します。`legacy-billing` ではビルド不能・循環依存・セキュリティ欠陥が静的指標以上に複合悪化しているため、全 7 軸で最大減点 `-10pt` が適用され、総合スコアは **76 -> 66（グレード C）** となりました。

```drawlib align=center code=hide file=baseline_vs_final_comparison.png caption="7 軸の決定論的 AST ベースラインと上限 -10pt の AI 定性調整後スコアの比較"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.styles import Styles

setup(width=146, height=62, dpi=150)

chart = BarChart(
    axis_line_style=Styles.Dark,
    width=132.0,
    height=44.0,
    categories=[
        "Architecture",
        "Code Quality",
        "Typing",
        "Testing",
        "Dependencies",
        "Security",
        "Documentation",
    ],
    orientation="vertical",
    bar_mode="group",
    bar_width_ratio=0.72,
    bar_r=0.8,
    axis_text_style=Styles.DarkBold.patch(text_size=9.8),
    grid_style=Styles.MutedThin,
    value_text_style=Styles.DarkBold.patch(text_size=9.5),
    value_format="{:.0f}",
    title="7-Axis Deterministic Baseline (Avg 76) vs. Final Audited Score (Avg 66)",
    title_style=Styles.DarkBold.patch(text_size=11.5),
)
chart.configure_y_axis(min_value=0, max_value=105, tick_step=20, show_grid=True)
chart.add_series("Deterministic AST Baseline", [90, 96, 87, 61, 82, 60, 54], style=Styles.SecondaryNeutral)
chart.add_series("Final Audited Score (-10pt AI Adj.)", [80, 86, 77, 51, 72, 50, 44], style=Styles.PrimaryFlat)
chart.draw(xy=(8.0, 12.0))
chart.draw_legend(
    xy=(36.0, 4.0),
    text_style=Styles.DarkBold.patch(text_size=10.0),
    orientation="horizontal",
    item_gap=10.0,
)

save()
```

| 評価軸 | 決定論的ベースライン | AI 調整 (`±10pt`) | 最終スコア | 定性調整の根拠 |
| :--- | :---: | :---: | :---: | :--- |
| **アーキテクチャ (`Architecture`)** | `90` | **`-10`** | **`80`** | `BillingController <-> BillingManager` 実行時循環依存、`@Autowired` フィールド注入、可変シングルトン `BillingController.channel`、プロセス内静的 `HashMap INVOICE_CACHE`。 |
| **コード品質 (`Code Quality`)** | `96` | **`-10`** | **`86`** | `BillingManager.processBatchBilling` 巨大メソッド（`cognitive=56`, 引数 8 個, 57 LOC）、`String ==` 参照比較バグ 3 箇所、空 `catch`、無効な `private @Transactional` 自己呼び出し、`System.out`/`printStackTrace` 4 箇所。 |
| **型安全性 (`Typing`)** | `87` | **`-10`** | **`77`** | `BillingController` / `BillingManager` の生 `Map`/`List` ジェネリクス、未型付け `Object` 引数（`traceHint`, `extraContext`）、`@SuppressWarnings("unchecked")`、Java 1.8 上での Java 11 `java.net.http` 不整合。 |
| **テスト (`Testing`)** | `61` | **`-10`** | **`51`** | 唯一の JUnit 4 テスト（`BillingManagerTest.testSmokeRun`）がアサーションなし、静的モジュール網羅率 `33.3%`、Java 8 vs. Spring Boot 4.2.0 ビルド失敗により Maven/JaCoCo 実行が完全ブロック。 |
| **依存関係 (`Dependencies`)** | `82` | **`-10`** | **`72`** | 未固定 `spring-boot-starter-web:LATEST`（Spring Boot 4.2.0 バイトコード `61.0` を取得し Java 1.8 ビルドを破壊）、EOL `javax.servlet`/JUnit 4、`mvnw` および Dependabot 欠如。 |
| **セキュリティ (`Security`)** | `60` | **`-10`** | **`50`** | ハードコード `GATEWAY_SECRET`（`<REDACTED_SECRET>`）、特権 `pull_request_target` + `actions/checkout@main` CI、root `openjdk:latest` Dockerfile（`DS-0001`/`DS-0002`/`DS-0026`）、未固定 CRITICAL `CVE-2022-22965` 範囲露出、未認証 `ANY /charge`、DAST ブロック。 |
| **ドキュメント (`Documentation`)** | `54` | **`-10`** | **`44`** | わずか 2 行の `README.md`、`33.3%` の Javadoc 網羅率（公開 Javadoc 10 件欠落）、陳腐化した `@param obsoleteToken` 不一致、`LICENSE`/`SECURITY.md` 欠如。 |
| **総合スコア** | **`76`** | **`-10`** | **`66 (C)`** | **ビルド・セキュリティ・アーキテクチャの複合欠陥により総合評価はグレード C。** |

---

## 実行済み監査ステップ別スコアと検出ソース内訳

全 8 つの実行済み監査ステップはいずれも **グレード D（`10`〜`25 / 100`）** となり、`container_runtime_audit (10)`、`supply_chain_audit (15)`、`java_test_audit (15)` が特に低い結果となりました。

```drawlib align=center code=hide file=audit_step_scores_bar.png caption="弱点順に並んだ監査ステップ別スコア（左）および検出ソース・トリアージ証跡（右）"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.smartarts import KpiCards
from drawlib.styles import Styles

setup(width=146, height=66, dpi=150)

# Left: Horizontal BarChart of all 8 audit steps (weakest-first bottom to top -> weakest visually prominent)
bar = BarChart(
    axis_line_style=Styles.Dark,
    width=70.0,
    height=52.0,
    categories=[
        "Java AST",
        "Repo Structure",
        "Web Pentest",
        "Security SCA",
        "Service PRR",
        "Java Testing",
        "Supply Chain",
        "Container Runtime",
    ],
    orientation="horizontal",
    bar_width_ratio=0.62,
    bar_r=0.8,
    axis_text_style=Styles.DarkBold.patch(text_size=9.5),
    grid_style=Styles.MutedThin,
    value_text_style=Styles.DarkBold.patch(text_size=9.5),
    value_format="{:.0f}",
    title="Audit Step Scores (0-100, All Grade D)",
    title_style=Styles.DarkBold.patch(text_size=11.0),
)
bar.configure_x_axis(min_value=0, max_value=100, tick_step=20, show_grid=True)
bar.add_series("Step Score", [25, 24, 20, 18, 16, 15, 15, 10], style=Styles.DangerFlat)
bar.draw(xy=(22.0, 7.0))

# Right: Provenance & Triage KPIs
kpis = KpiCards(
    style=Styles.Neutral.patch(shape_r=2.0),
    metric_style=Styles.DarkBold.patch(text_size=12.0),
    text_style=Styles.DarkBold.patch(text_size=9.8),
    description_style=Styles.Muted.patch(text_size=9.2),
    accent_style=Styles.PrimaryFlat,
    accent_position="left_pill",
    metric_layout="left_column",
    metric_width_ratio=0.30,
    spacing=2.4,
)
kpis.add(
    "7 Det.",
    "Deterministic Analyzers",
    "AST, manifest, Docker, Trivy",
    style=Styles.PrimaryNeutral.patch(shape_r=2.0),
    metric_style=Styles.PrimaryBold.patch(text_size=12.0),
    accent_style=Styles.PrimaryFlat,
)
kpis.add(
    "12 AI",
    "AI Qualitative Findings",
    "Cross-file architecture & PRR",
    style=Styles.SecondaryNeutral.patch(shape_r=2.0),
    metric_style=Styles.DarkBold.patch(text_size=12.0),
    accent_style=Styles.SecondaryFlat,
)
kpis.add(
    "14 Locs",
    "Consolidated Index",
    "Deduplicated from 19 raw items",
    style=Styles.Neutral.patch(shape_r=2.0),
    accent_style=Styles.DarkFlat,
)
kpis.add(
    "0 / 0",
    "FP Triage & Waivers",
    "0 waived FPs; 0 [[opt_out]]",
    style=Styles.Neutral.patch(shape_r=2.0),
    accent_style=Styles.MutedFlat,
)
kpis.draw((96.0, 8.0), width=46.0, height=50.0, columns=1)

save()
```

### 検出ソース内訳・誤検知トリアージ・例外承認ログ

- **検出ソース内訳**: 決定論的アナライザー = `7` 件、AI 定性評価 = `12` 件、合計 = `19` 件（統合後 `14` 固有箇所）。
- **AI 誤検知トリアージログ**: 決定論的事前検出の除外・再分類 = `0` 件。
- **設定済み設計例外（`pni.toml [[opt_out]]`）**: アクティブな例外設定 = `0` 件。

---

## ルール準拠マトリクス（`FAIL -> WARN` 全 16 ルール）

| 判定 | ルール ID | 評価元アクション | 根拠サマリー |
| :---: | :--- | :--- | :--- |
| **`FAIL`** | `common/architecture` | `java_ast_audit` | 実行時循環依存 1 件（`BillingController -> BillingManager -> BillingController`）、`@Autowired circularController` による上向き結合、可変静的 `INVOICE_CACHE`。 |
| **`FAIL`** | `common/documentation` | `repo_structure_audit` | `README.md` がわずか 2 行（`# Legacy Billing` / `Run mvn spring-boot:run`）のみで、設計・環境設定・API 仕様・テスト手順が欠落。 |
| **`FAIL`** | `common/maintainability` | `java_ast_audit` | `BillingManager.processBatchBilling` が SIG 単位サイズ（57 行）・複雑度（`branches=13`, `cognitive=56`）・引数数（8 > 6）を超過し、静的 `INVOICE_CACHE` と 83 行目の空 catch を内包。 |
| **`FAIL`** | `common/production_readiness` | `container_runtime_audit` | ビルド・起動不可。`GatewayClient.java:22` の `connectTimeout` 欠如、`BillingManager.java:83` の空 catch、非構造ログ 4 箇所、Actuator `/healthz` 欠如、未認証 `ANY /charge`。 |
| **`FAIL`** | `common/runtime_verification` | `deterministic_baseline` | `harness_build=failed`。`RV-01` 失敗（`openjdk:latest not found` および Java 8 Maven での `spring-boot-4.2.0.jar` バイトコード `61.0` vs `52.0` 衝突）により `RV-02`/`RV-03`/`RV-04` がブロック。 |
| **`FAIL`** | `common/security` | `repo_structure_audit` | `GatewayClient.java:13` のハードコード `GATEWAY_SECRET`（`<REDACTED_SECRET>`）、特権 `pull_request_target` CI、root `openjdk:latest` コンテナ、未検証生 `Map` 入力、未認証 `ANY /charge`。 |
| **`FAIL`** | `common/security_vulnerability` | `java_ast_audit` | `SEC-01`: 未固定 `spring-boot-starter-web:LATEST` の CRITICAL `CVE-2022-22965`（CVSS 9.8）。`SEC-02`: Dockerfile `DS-0002`/`DS-0001`/`DS-0026`。`SEC-03`: ハードコード秘密鍵。`SEC-05`: 未認証 `ANY /charge`。`SEC-06`: DAST `error`（ビルド失敗で 0 プローブ）。 |
| **`FAIL`** | `common/supply_chain` | `repo_structure_audit` | `LICENSE`・`SECURITY.md`・Dependabot・`mvnw`/ロックファイル欠如、未固定 `LATEST`、`pull_request_target` + `@main`（`permissions:` 欠如）、root `openjdk:latest`（`.dockerignore` 欠如）。 |
| **`FAIL`** | `common/twelve_factor` | `service_readiness_audit` | Factor III 違反（`GatewayClient.java:16` の直接 `System.getenv`）、Factor VI 違反（静的 `INVOICE_CACHE` とシングルトン `channel`）、Factor XI 違反（`System.out`/`printStackTrace` 4 箇所）。 |
| **`FAIL`** | `java/code_quality` | `java_ast_audit` | Javadoc 網羅率 `33.3%`（欠落 10 件、陳腐化 `@param obsoleteToken` 1 件）、`String ==` リテラル比較バグ 3 箇所（`"PAID"`, `"USD"`, `"JPY"`）、空 catch、`System.out`/`printStackTrace` 4 箇所。 |
| **`FAIL`** | `java/dependencies` | `repo_structure_audit` | `pom.xml` が EOL Java `1.8` を指定、`spring-boot-starter-web:LATEST` の動的参照、レガシー `javax.servlet:4.0.1`・JUnit 4（`4.13.2`）、`mvnw` 欠如。 |
| **`FAIL`** | `java/frameworks/spring_boot` | `java_ast_audit` | `@Autowired` フィールド注入 3 箇所、リクエスト毎に書き換わるシングルトン `channel`、無制限 `@RequestMapping("/charge")`、`spring-tx` 欠如の `private @Transactional`、レガシー `javax.servlet`。 |
| **`FAIL`** | `java/modern_stack` | `java_ast_audit` | Java `1.8` 宣言と `GatewayClient.java:4` の Java 11 `java.net.http.HttpClient` の矛盾、`LegacyDateHelper` の非スレッド安全 `SimpleDateFormat`・`Date`・`Vector`、未整列 import 4 件＋ワイルドカード import 1 件。 |
| **`FAIL`** | `java/testing` | `java_test_audit` | レガシー JUnit 4、アサーションなしのテストメソッド 1 件（`BillingManagerTest.testSmokeRun`）、静的モジュール網羅率 `33.3%`、ビルド失敗による JUnit/JaCoCo 実行ブロック。 |
| **`FAIL`** | `java/typing` | `java_ast_audit` | 型安全網羅率 `81.8%`：`BillingController`/`BillingManager` の生 `Map`/`List`、未型付け `Object` 引数（`traceHint`, `extraContext`）、`@SuppressWarnings("unchecked")`。 |
| **`WARN`** | `common/git_workflow` | `repo_structure_audit` | `.gitignore` 欠如、および `.github/workflows/build.yml` が安全な `pull_request` ではなく `pull_request_target` 上で `mvn package` を実行。 |

---

## 統合済み箇所別検出事項インデックス（固有 14 箇所）

| # | 重要度 | 対象箇所 | 関連ルール | 証跡および推奨対策 |
| :---: | :---: | :--- | :--- | :--- |
| 1 | **`CRITICAL`** | `.github/workflows/build.yml` | `common/supply_chain` | `permissions:` なしで `pull_request_target` を起動し可変 `actions/checkout@main` を使用。**対策**: `pull_request` へ切替、`permissions: { contents: read }` 追加、フル SHA 固定。 |
| 2 | **`CRITICAL`** | `examples/java/api_spring_messy/src/main/java/com/example/billing/client/GatewayClient.java:13` | `common/security` | `GATEWAY_SECRET` にハードコードされた秘密鍵リテラル（`<REDACTED_SECRET>`, OWASP ASVS）。**対策**: 環境変数またはシークレットマネージャへ移行し鍵をローテーション。 |
| 3 | **`CRITICAL`** | `pom.xml` | `common/security_vulnerability`, `common/runtime_verification`, `java/dependencies` | 未固定 `spring-boot-starter-web@LATEST` が Trivy `CVE-2022-22965` 範囲一致と Maven コンパイル失敗（`spring-boot-4.2.0.jar` バイトコード `61.0` vs Java 1.8 `52.0`）を同時誘発。`javax.servlet`/JUnit 4・`mvnw` 欠如も併存。**対策**: Java 21 LTS + Spring Boot 3.4.x BOM + JUnit 5 へ固定し `mvnw` をコミット。 |
| 4 | **`CRITICAL`** | `src/main/java/com/example/billing/client/GatewayClient.java` | `common/security`, `java/modern_stack` | ハードコード `GATEWAY_SECRET`（`<REDACTED_SECRET>`）、Java 1.8 上の Java 11 `java.net.http` 矛盾、タイムアウト欠如、`System.getenv`、スタックトレース出力。**対策**: 秘密鍵削除・外部化、Java 21 + タイムアウト付き `RestClient`、`@ConfigurationProperties`、SLF4J、import 整列。 |
| 5 | **`CRITICAL`** | `—` *（依存 SCA）* | `CVE-2022-22965` | `org.springframework.boot:spring-boot-starter-web@LATEST (pom)` が Spring4Shell 履歴範囲に一致。**対策**: 修正済み版（最小 `2.5.12, 2.6.6`、推奨 Spring Boot 3.4.x BOM）へ固定。 |
| 6 | **`HIGH`** | `Dockerfile` | `common/supply_chain` | 廃止・可変 `openjdk:latest` を使用し、`.dockerignore` なしで全ファイルをコピーし `root` で実行。**対策**: マルチステージ `eclipse-temurin:21-jdk` / `21-jre-alpine`、非 root `USER`、`.dockerignore` を導入。 |
| 7 | **`HIGH`** | `src/main/java/com/example/billing/controller/BillingController.java` | `common/security_vulnerability`, `java/frameworks/spring_boot` | ビルド失敗により `ANY /charge` への `web_pentest` がブロック。シングルトン `channel` の毎リクエスト書き換え、無制限 `@RequestMapping`、生 `Map` の無検証受付。**対策**: `channel` 削除、`@PostMapping("/charge")` + `@Valid` Java `record` + 認証導入後、`web_pentest` を再実行。 |
| 8 | **`HIGH`** | `src/main/java/com/example/billing/service/BillingManager.java` | `common/architecture`, `java/code_quality` | `@Autowired circularController` 循環依存、静的生 `INVOICE_CACHE`、`processBatchBilling`（`cognitive=56`, 引数 8 個, 陳腐化 `@param obsoleteToken`, 52/55/57 行目の `String ==`, 83 行目の空 catch, 無効な `private @Transactional`）。**対策**: コンストラクタ注入、キャッシュ外部化、メソッド分割、`.equals()`、SLF4J、専用リポジトリ Bean 化。 |
| 9 | **`HIGH`** | `src/test/java/com/example/billing/BillingManagerTest.java` | `java/testing` | `testSmokeRun` が `InvoiceRecord` 生成と `getAmountCents()` 呼出のみでアサーションも主要クラス検証も皆無。**対策**: JUnit 5 + Mockito + `MockMvc` 特性テスト群へ移行し JaCoCo `>=80%` を達成。 |
| 10 | **`HIGH`** | `—` *（Import グラフ）* | `common/architecture` | 循環インポート: `BillingController -> BillingManager -> BillingController`。**対策**: 上向き依存を除去し共通モデル／インタフェースを下位層へ抽出。 |
| 11 | **`MEDIUM`** | `examples/java/api_spring_messy/src/main/java/com/example/billing/service/BillingManager.java:33` | `common/maintainability` | `processBatchBilling`: `length=57 lines`, `branches=13`, `cognitive=56`。**対策**: 単一責務ヘルパーへ分割（`cognitive <= 15`）。 |
| 12 | **`MEDIUM`** | `—` *（ドキュメント）* | `common/documentation` | `has_readme=True`, `lines=2`。**対策**: `README.md` にアーキテクチャ、環境構築、API 仕様、テスト手順を記載。 |
| 13 | **`MEDIUM`** | `—` *（ロックファイル）* | `common/supply_chain` | `manifests=['pom.xml']`, `lockfiles=[]`。**対策**: BOM 固定および Maven Wrapper（`mvnw`）／依存検証メタデータをコミット。 |
| 14 | **`LOW`** | `—` *（バージョン境界）* | `common/supply_chain` | `unpinned=['org.springframework.boot:spring-boot-starter-web:LATEST']`。**対策**: 明示的なバージョン固定により再現可能なビルドを担保。 |

---

## 機械可読アーティファクト参照一覧

CI ゲート連携および IDE 診断向けに、すべての構造化メトリクス・検出事項・DAG・決定論的スキャン出力は以下の機械可読ファイルへ永続化されています。

| アーティファクトパス | 形式 / スキーマ | 用途 |
| :--- | :--- | :--- |
| `docs/reports/java_api_spring_messy/java_api_spring_messy_score.json` | `ScoreResult` v2.0 (JSON) | 7 軸スコア・ルール準拠・検出事項・改善計画の完全構造化データ |
| `docs/reports/java_api_spring_messy/java_api_spring_messy_summary.json` | `ScoreSummary` (JSON) | CI / ポータル表示用の軽量サマリーメトリクス |
| `docs/reports/java_api_spring_messy/java_api_spring_messy_findings.sarif` | `SARIF 2.1.0` | GitHub Code Scanning および IDE 向けインライン診断結果 |
| `docs_src/reports/java_api_spring_messy/_facts/plan.json` | PNI Plan v2.0 (JSON) | 事前偵察計画および検証済みワークフロー DAG |
| `docs_src/reports/java_api_spring_messy/_facts/facts.json` | 決定論的ファクト束 (JSON) | AST・Maven/Docker ランタイム・Trivy SCA・ペネトレーション生証跡 |
| `docs_src/reports/java_api_spring_messy/_facts/architecture.json` | `ArchitectureRecord` (JSON) | コード裏付け済みの 5 層アーキテクチャ・シンボル・実行フロー記録 |
