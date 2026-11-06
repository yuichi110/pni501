# 5. 詳細分析：コード品質・テスト・動的検証

本章では、Java AST 静的解析によって抽出されたモジュール別のコード品質・SIG 保守性・ジェネリクス型安全性指標と、隔離 Docker コンテナ上で実行された動的ビルド・オフライン単体テスト・JaCoCo カバレッジ・起動スモーク検証（RV-01〜RV-04）の失敗原因を詳細に分析する。

```drawlib file=code_module_quality_heatmap.png caption="モジュール × 品質ディメンション適合度マトリクス (0 - 100%)"
from drawlib.canvas import save, setup
from drawlib.charts.heatmap import HeatmapChart
from drawlib.styles import Styles

setup(width=146, height=68, dpi=150)

hm = HeatmapChart(
    min_style=Styles.DangerNeutral,
    max_style=Styles.Primary,
    x_categories=["import衛生", "厳格型安全", "Javadoc同期", "保守性・非循環", "テスト検証度"],
    y_categories=[
        "BillingManager (78 LOC)",
        "GatewayClient (32 LOC)",
        "BillingController (38 LOC)",
        "LegacyDateHelper (15 LOC)",
        "BillingApp (9 LOC)",
        "InvoiceRecord (15 LOC)",
    ],
    axis_line_style=Styles.Neutral,
    axis_text_style=Styles.DarkBold.patch(text_size=9.0),
    value_text_style=Styles.DarkBold.patch(text_size=9.2),
    background_style=Styles.Neutral.patch(shape_r=2.0),
    width=114,
    height=54,
    min_value=0.0,
    max_value=100.0,
    cell_gap=0.8,
    cell_r=0.8,
    value_format=lambda v: f"{v:.0f}%",
    title="モジュール別 静的コード品質・型安全・テスト検証マトリクス",
    title_style=Styles.DarkBold.patch(text_size=10.2),
)
hm.add_row("BillingManager (78 LOC)", [100.0, 0.0, 0.0, 0.0, 0.0])
hm.add_row("GatewayClient (32 LOC)", [0.0, 50.0, 0.0, 40.0, 0.0])
hm.add_row("BillingController (38 LOC)", [100.0, 0.0, 0.0, 35.0, 0.0])
hm.add_row("LegacyDateHelper (15 LOC)", [100.0, 50.0, 0.0, 50.0, 0.0])
hm.add_row("BillingApp (9 LOC)", [100.0, 100.0, 50.0, 100.0, 0.0])
hm.add_row("InvoiceRecord (15 LOC)", [100.0, 100.0, 100.0, 100.0, 25.0])
hm.draw(xy=(6, 6))
hm.draw_colorbar(
    xy=(126, 13),
    text_style=Styles.Dark.patch(text_size=9.0),
    length=40.0,
    thickness=2.6,
    orientation="vertical",
    label="適合率(%)",
)

save()
```

## 静的コード品質・SIG保守性・JUnit テスト構造の詳細評価

- **SIG 保守性と深刻な論理バグ (`BillingManager.java`)**: `processBatchBilling` は 57 行・分岐数 13・**認知的複雑度 `56`**・引数 `8` 個（SIG 上限 6 超過）の巨大メソッドとなっている。特に `status == "PAID"`（52行目）、`currency == "USD"`（55行目）、`currency == "JPY"`（57行目）の3箇所で文字列リテラルを `==` 参照比較しているため、JSON デシリアライズ等で生成された別インスタンスの文字列に対して税率計算が一切適用されない致命的バグが存在する。さらに 79 行目で `LegacyDateHelper` に未定義の `currentPeriodLabel()` を呼び出し、83 行目の空 `catch (Exception e) {}` で例外を握り潰している。
- **言語ターゲット不整合・未宣言依存・共有状態 vs 旧API負債**:
  - **AST 言語バージョン不整合 (`language_version_mismatches=1`)**: `pom.xml` が `maven.compiler.source=1.8` を宣言しているにもかかわらず、`GatewayClient.java:4-6` で **Java 11 導入の `java.net.http.HttpClient` / `HttpRequest` / `HttpResponse`** を使用している。
  - **マニフェスト未宣言依存 (`undeclared_dependencies=2`)**: `BillingManager.java:12` が `org.springframework.transaction.annotation.Transactional` を import しているが、`pom.xml` には `spring-tx`（または `spring-boot-starter-jdbc` / `data-jpa`）が宣言されていない（さらに 91 行目の `saveAuditTrail` は `private` メソッドのため AOP プロキシも無効）。
  - **スレッド間競合状態と旧 API 負債の峻別**: `BillingController.channel` と `BillingManager.INVOICE_CACHE`（`public static HashMap`）は並行リクエスト間で共有される実働の競合バグである一方、`LegacyDateHelper` の `new SimpleDateFormat(...)` と未使用 `collectAuditTags` の `Vector` はメソッドローカル生成のため直接のスレッド競合ではなく、都度生成コストと旧 `java.util.Date` 系のモダナイゼーション負債に該当する。
- **形骸化した JUnit 4 テスト**: `BillingManagerTest.java` は JUnit 4 (`org.junit.Test`) を使用し、`com.example.billing` パッケージ直下に置かれている上、`testSmokeRun` 内で `InvoiceRecord` を生成して `getAmountCents()` の戻り値を捨てるのみで **アサーションが 0 件** である。

## コンテナ動的検証（RV-01〜RV-04 ビルド失敗原文と4重のコンパイル阻害要因）

隔離 Docker 環境における動的検証（`run_check`）では、同梱 `Dockerfile` ビルド（`openjdk:latest` 解決失敗）と PNI Maven ハーネスビルドの双方が失敗し、後続の単体テスト・JaCoCo カバレッジ・起動確認がすべて `BLOCKED` となった。Maven ハーネスのコンパイラ出力原文（抜粋）は以下の通りである。

- **コンパイラ失敗ログ原文 (`harness_build`)**:
  - `bad class file: /m2repo/org/springframework/boot/spring-boot/4.2.0-RC1/spring-boot-4.2.0-RC1.jar(org/springframework/boot/SpringApplication.class)`
  - `class file has wrong version 61.0, should be 52.0`
- **解消すべき4つの独立したコンパイル阻害要因**: `javac` は最初のクラスファイル読込エラー（`version 61.0 vs 52.0`）で停止しているが、静的 AST 解析により **(1) `LATEST` -> `4.2.0-RC1` のバイトコード衝突** に加え、**(2) `GatewayClient.java` の Java 11 `java.net.http.*` 使用**、**(3) `BillingManager.java` の `spring-tx` 依存欠落**、**(4) `dateHelper.currentPeriodLabel()` 未定義メソッド呼び出し** の計4箇所を同時に解消しなければクリーンビルドおよび後続の隔離ループバック DAST（`web_pentest`：`15.74s` エラー停止）に到達しないことが確定している。

```drawlib file=runtime_verification_breakdown.png caption="コンテナ動的検証KPIと RV-01〜RV-04 ゲート別失敗・ブロック内訳"
from drawlib.canvas import save, setup
from drawlib.smartarts import KpiCards, Table
from drawlib.styles import Styles

setup(width=146, height=86, dpi=150)

kpis = KpiCards(
    style=Styles.Neutral,
    metric_style=Styles.DangerBold.patch(text_size=12.0),
    text_style=Styles.DarkBold.patch(text_size=9.2),
    description_style=Styles.Neutral.patch(text_size=8.8),
    accent_position="top_bar",
    metric_layout="top_stack",
    spacing=2.5,
)
kpis.add(
    "FAILED (1.51s)",
    "同梱 Dockerfile ビルド",
    "openjdk:latest 解決失敗",
    accent_style=Styles.Danger,
)
kpis.add(
    "FAILED (25.76s)",
    "Maven ハーネスビルド",
    "v61 vs v52 + AST 3要因",
    accent_style=Styles.Danger,
)
kpis.add(
    "BLOCKED",
    "オフライン JUnit 実行",
    "--network=none 未到達",
    accent_style=Styles.Warning,
    metric_style=Styles.WarningBold.patch(text_size=12.0),
)
kpis.add(
    "UNMEASURED",
    "JaCoCo 網羅率 & Smoke",
    "ビルド停止により計測不能",
    accent_style=Styles.Warning,
    metric_style=Styles.WarningBold.patch(text_size=12.0),
)
kpis.draw(xy=(3, 63.5), width=140, height=19.5, columns=4)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=8.7),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.0),
    border_style=Styles.NeutralThin,
)
rows = [
    ["検証ゲート", "ステータス", "所要時間", "決定的エラー出力・原因エビデンス"],
    ["RV-01a: 同梱\nDockerfile", "FAILED\n(exit 1)", "1.51s", "FROM openjdk:latest メタデータ解決失敗。加えて mvn package 工程が\nなく存在しない billing.jar を CMD 指定しているため起動不能"],
    ["RV-01b: Maven\nクリーンビルド", "FAILED\n(exit 1)", "25.76s", "bad class file: spring-boot-4.2.0-RC1.jar (wrong version 61.0, should\nbe 52.0)。他に Java 11 HttpClient・spring-tx欠落・未定義呼出も潜在"],
    ["RV-02: オフライン\n単体テスト", "BLOCKED", "0.00s", "ハーネスビルド失敗によりブロック。加えて静的解析上も JUnit 4 テスト\n1件・アサーション 0件であり実質的な検証能力を欠く"],
    ["RV-03: JaCoCo\n実測カバレッジ", "UNMEASURED\n(measured=false)", "0.00s", "jacoco-maven-plugin:0.8.12 準備段階でコンパイル停止したため\n行・分岐網羅率は未計測 (静的テスト対応率も 33.3% に留まる)"],
    ["RV-04: Web API\nスモーク起動", "BLOCKED\n(web_api)", "0.00s", "ビルド失敗により ApplicationContext 起動未到達 (SEC-06 web_pentest\nも同様のビルドエラーで停止)。循環DIエラーリスクも併存"],
]
tbl.draw_flexible(
    xy=(3, 60.5),
    column_widths=[24, 21, 14, 81],
    row_heights=[7.0, 10.2, 10.4, 9.6, 9.6, 9.6],
    data=rows,
)

save()
```
