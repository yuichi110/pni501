# 1. エグゼクティブサマリー

`legacy-billing`（`examples/java/api_spring_messy`）の総合スコアは **66/100（グレード C）**、ルール合格率は **`0/16`（`15 FAIL`・`1 WARN`）** であり、決定論的 AST ベースライン **76/100** に対して全 7 軸で `-10pt` の定性減点が適用されました。実 Docker ランタイム検証・tree-sitter AST 解析・Trivy SCA の横断検証により、**`pom.xml` の未固定指定 `spring-boot-starter-web:LATEST` が Java 1.8 ビルドを即座にクラッシュさせると同時に CRITICAL な Spring4Shell 静的範囲アラートを発火し、JaCoCo カバレッジ計測および動的 HTTP ペネトレーションテスト（DAST）を連鎖的にブロックしている**という明確な因果鎖が実証されました。

```drawlib align=center code=hide file=exec_7axis_radar.png caption="7軸エンジニアリング健全性レーダー（決定論的ベースライン vs. 最終監査スコア）と主要 KPI"
from drawlib.canvas import save, setup
from drawlib.charts.radar import RadarChart
from drawlib.smartarts import KpiCards
from drawlib.styles import Styles

setup(width=146, height=70, dpi=150)

# Left: 7-Axis RadarChart comparing Deterministic Baseline vs Final Score
radar = RadarChart(
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
    axis_text_style=Styles.DarkBold.patch(text_size=9.8),
    grid_style=Styles.MutedThin,
    scale_text_style=Styles.Muted.patch(text_size=8.5),
    radius=20.0,
    width=72.0,
    height=56.0,
    min_value=0.0,
    max_value=100.0,
    levels=5,
    grid_shape="polygon",
    title="7-Axis Health: Baseline (76) vs. Final (66)",
    title_style=Styles.DarkBold.patch(text_size=11.5),
)
radar.add_series(
    "AST Baseline",
    [90, 96, 87, 61, 82, 60, 54],
    style=Styles.SecondaryNeutral,
    fill_alpha=0.22,
    line_style="dashed",
    line_width=1.8,
)
radar.add_series(
    "Final Audited",
    [80, 86, 77, 51, 72, 50, 44],
    style=Styles.PrimaryFlat,
    fill_alpha=0.28,
    line_width=2.2,
)
radar.draw(xy=(4.0, 11.0))
radar.draw_legend(
    xy=(14.0, 4.5),
    text_style=Styles.DarkBold.patch(text_size=9.8),
    orientation="horizontal",
    item_gap=6.0,
)

# Right: Executive headline KPI stack
kpis = KpiCards(
    style=Styles.Neutral.patch(shape_r=2.0),
    metric_style=Styles.DarkBold.patch(text_size=12.5),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Muted.patch(text_size=9.5),
    accent_style=Styles.PrimaryFlat,
    accent_position="left_pill",
    metric_layout="left_column",
    metric_width_ratio=0.31,
    spacing=2.6,
)
kpis.add(
    "66/100",
    "Overall Health (Grade C)",
    "Baseline 76 with -10pt qualitative deduction",
    style=Styles.WarningNeutral.patch(shape_r=2.0),
    metric_style=Styles.WarningBold.patch(text_size=13.0),
    accent_style=Styles.WarningFlat,
)
kpis.add(
    "0 / 16",
    "Rules Passed (15 FAIL)",
    "1 WARN (git_workflow); all 8 steps Grade D",
    style=Styles.DangerNeutral.patch(shape_r=2.0),
    metric_style=Styles.DangerBold.patch(text_size=13.0),
    accent_style=Styles.DangerFlat,
)
kpis.add(
    "FAILED",
    "Container Runtime & DAST",
    "Maven build 61.0 vs 52.0; 0 tests, 0 probes",
    style=Styles.Neutral.patch(shape_r=2.0),
    metric_style=Styles.DangerBold.patch(text_size=12.0),
    accent_style=Styles.DarkFlat,
)
kpis.add(
    "6 CRIT",
    "19 Findings / 14 Locations",
    "CVE-2022-22965, secret, CI, Docker",
    style=Styles.PrimaryNeutral.patch(shape_r=2.0),
    metric_style=Styles.PrimaryBold.patch(text_size=12.5),
    accent_style=Styles.PrimaryFlat,
)
kpis.draw((80.0, 7.0), width=62.0, height=58.0, columns=1)

save()
```

---

## AST × Docker × Trivy が実証した根本原因チェーン

本監査で最も重要な発見は、ビルド不能・検証不能・深刻なサプライチェーン脆弱性がすべて同一の未固定マニフェストおよび廃止コンテナ基盤に起因している点です。

1. **未固定マニフェスト（`pom.xml`）**: `org.springframework.boot:spring-boot-starter-web` に `<version>LATEST</version>` を指定したまま、EOL の Java `1.8`（バイトコード `52.0`）をターゲットとしており、Maven Wrapper（`mvnw`）も未整備です。
2. **実コンパイラクラッシュ（`harness_build`）**: コンテナ化ビルド検証（`java/maven.dockerfile`, `JAVA_VERSION=8`）において Maven は動的に `spring-boot-4.2.0.jar`（`SpringApplication.class`、JDK 17+ 向けバイトコード `61.0`）を取得し、`class file has wrong version 61.0, should be 52.0` で即座に失敗しました。同時にプロジェクト `Dockerfile` も、Docker Hub から廃止された `docker.io/library/openjdk:latest` の取得失敗（`not found`）により `1.21s` で失敗しました。
3. **検証ゲートの連鎖ブロックと静的 SCA 露出**: ビルド失敗により、オフライン JUnit 実行（`0/0` 件）、JaCoCo カバレッジ計測（`N/A`）、Spring Boot 起動スモーク確認（`blocked`）、動的 Web ペネトレーションテスト（`web_pentest`, `0/0` プローブ）が全面的にブロックされました。一方で Trivy ファイルシステム SCA は未固定の `LATEST` 指定子を全過去バージョン範囲として評価（`is_unpinned_specifier=True`）し、**CRITICAL `CVE-2022-22965`**（Spring4Shell, CVSS 9.8）を検出しました。
4. **ソースコード内の集中ホットスポット**: 187 LOC のコードベース内部では、`BillingManager.java`（`BillingController` との循環依存、`cognitive=56`、引数 8 個、静的 `INVOICE_CACHE`、`String ==` バグ、空 `catch`、無効な `private @Transactional`）、`GatewayClient.java`（ハードコードされた `GATEWAY_SECRET` `<REDACTED_SECRET>`、Java 1.8 上での Java 11 `java.net.http` 不整合、HTTP タイムアウト欠如）、`BillingController.java`（可変シングルトン `channel` の競合状態、未認証 `ANY /charge`）の 3 クラスに負債が集中しています。

```drawlib align=center code=hide file=exec_causal_chain_risks.png caption="AST × Docker × Trivy 障害因果チェーン（上段）および強み vs. 最優先リスク（下段）"
from drawlib.canvas import save, setup
from drawlib.smartarts import CardList, ChevronProcess, Panel
from drawlib.styles import Styles
from drawlib.text import text

setup(width=146, height=84, dpi=150)

# Section title for causal chain
text(
    (73.0, 80.0),
    "Root-Cause Chain: Unpinned Manifest -> Bytecode Crash -> Blocked Verification & SCA Exposure",
    style=Styles.DarkBold.patch(text_size=11.5),
)

# Top half: 4-stage ChevronProcess causal chain
chain = ChevronProcess(
    style=Styles.Neutral,
    text_style=Styles.DarkBold.patch(text_size=10.2),
    description_style=Styles.Dark.patch(text_size=9.5),
    corner_angle=62.0,
    spacing=1.5,
    flat_left_end=True,
)
chain.add(
    "1. Unpinned Manifest",
    description="pom.xml: LATEST\nJava 1.8 + no mvnw",
    style=Styles.Neutral,
)
chain.add(
    "2. Live Resolution",
    description="Spring Boot 4.2.0\nBytecode 61.0 pulled",
    style=Styles.PrimaryNeutral,
)
chain.add(
    "3. Container Crash",
    description="61.0 vs 52.0 error\nopenjdk:latest 404",
    style=Styles.DangerFlat,
    text_style=Styles.WhiteBold.patch(text_size=10.2),
    description_style=Styles.White.patch(text_size=9.5),
)
chain.add(
    "4. Blocked Gates",
    description="JaCoCo & DAST blocked\nCVE-2022-22965 range",
    style=Styles.WarningNeutral,
)
chain.draw(xy=(4.0, 58.0), width=138.0, height=18.0)

# Bottom-left: Verified Strengths Panel
p_str = Panel(
    "Verified Baseline Strengths (2)",
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.SuccessNeutral,
    text_style=Styles.DarkBold.patch(text_size=10.8),
    header_variant="filled",
    header_height=7.5,
)
p_str.draw((4.0, 4.0), width=66.0, height=49.0)

strengths = CardList(
    style=Styles.SuccessNeutral.patch(shape_r=1.8),
    text_style=Styles.DarkBold.patch(text_size=9.8),
    description_style=Styles.Dark.patch(text_size=9.3),
    badge_shape="rounded_rect",
    badge_style=Styles.SuccessFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.3),
    direction="vertical",
    spacing=3.0,
)
strengths.add(
    "Test Scope Isolation",
    "junit:4.13.2 cleanly scoped to\n<scope>test</scope> in pom.xml.",
    badge_text="OK",
)
strengths.add(
    "Clean Immutable DTO Baseline",
    "InvoiceRecord.java has full Javadocs\nand 0 AST violations.",
    badge_text="OK",
)
strengths.draw((7.0, 7.5), width=60.0, height=34.5)

# Bottom-right: Top Critical Risks Panel
p_risk = Panel(
    "Top Critical Risks Requiring P0 Action (3)",
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.DangerNeutral,
    text_style=Styles.DarkBold.patch(text_size=10.8),
    header_variant="filled",
    header_height=7.5,
)
p_risk.draw((76.0, 4.0), width=66.0, height=49.0)

risks = CardList(
    style=Styles.DangerNeutral.patch(shape_r=1.8),
    text_style=Styles.DarkBold.patch(text_size=9.6),
    description_style=Styles.Dark.patch(text_size=9.2),
    badge_shape="rounded_rect",
    badge_style=Styles.DangerFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.2),
    direction="vertical",
    spacing=2.2,
)
risks.add(
    "CRITICAL CVE-2022-22965 (CVSS 9.8)",
    "Unpinned starter-web@LATEST\nstatic full-range exposure.",
    badge_text="CRIT",
)
risks.add(
    "Hardcoded GATEWAY_SECRET",
    "GatewayClient.java:13 embeds\n<REDACTED_SECRET> in source.",
    badge_text="CRIT",
)
risks.add(
    "CI Token & Root Container Risk",
    "pull_request_target + @main;\nroot openjdk:latest Dockerfile.",
    badge_text="CRIT",
)
risks.draw((79.0, 6.5), width=60.0, height=37.0)

save()
```

---

## エグゼクティブ・スコアカード総括

| 検証ゲート | 判定 | 主な観測証跡 |
| :--- | :--- | :--- |
| **総合健全性スコア** | **66 / 100（グレード C）** | 7 軸スコア: `architecture=80`, `code_quality=86`, `typing=77`, `testing=51`, `dependencies=72`, `security=50`, `documentation=44` |
| **最低スコア監査ステップ** | **10 – 15 / 100（グレード D）** | `container_runtime_audit=10 (D)`, `supply_chain_audit=15 (D)`, `java_test_audit=15 (D)` |
| **コンテナランタイム (`RV-01..04`)** | **`failed`** | `build=failed`, `tests=0/0 (blocked)`, `line_cov=N/A`, `smoke=blocked (web_api)` |
| **Trivy SCA & IaC (`SEC-01..03`)** | **`failed`** | `app_cves=1`（`CRITICAL=1`, `HIGH=0`）、Dockerfile 設定不備 `3` 件（`HIGH=1`, `MED=1`, `LOW=1`）、Trivy シークレット `0` 件（AST ハードコード秘密鍵 `1` 件） |
| **動的 Web ペネトレーション (`SEC-06`)** | **`error`（ブロック）** | `probes=0/0` 合格、`findings=0`。スイートは `.pni/pentests/examples/java/api_spring_messy` に生成済みだが、対象コンテナビルド失敗により未実行 |
| **承認済み監査スコープ** | **リポジトリ全体** | `--auto-approve`（`plan_gate=false`）にて自動承認。本番 6 ファイル（`src/main/java`）、テスト 1 ファイル（`src/test/java`）、`README.md` |
