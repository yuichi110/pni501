# 5. 詳細分析: コード品質・テスト・ランタイム検証

Java ソース 6 モジュール（`187 LOC`, `11` 関数）に対する tree-sitter AST 解析と Docker コンテナ実機検証により、クリーンな不変値オブジェクト（`InvoiceRecord.java`）と深刻に劣化した中核処理（`BillingManager.java`・`BillingController.java`・`GatewayClient.java`）との鮮明な乖離が明らかになりました。加えて、Maven/Docker の二重コンパイル失敗によりオフライン単体テストと JaCoCo カバレッジ計測が完全にブロックされています。

```drawlib align=center code=hide file=code_module_fitness_heatmap.png caption="モジュール × 品質軸フィットネスマトリクス（ファイル別 AST 検出に基づく 0–100 評価：クリーンな InvoiceRecord vs. 集中ホットスポット BillingManager）"
from drawlib.canvas import save, setup
from drawlib.charts.heatmap import HeatmapChart
from drawlib.styles import Styles

setup(width=146, height=70, dpi=150)

hm = HeatmapChart(
    styles=[Styles.DangerFlat, Styles.WarningNeutral, Styles.SuccessNeutral],
    x_categories=[
        "Maintainability",
        "Typing",
        "Javadoc",
        "DI / Arch",
        "Modernity",
        "Ops / Sec",
    ],
    y_categories=[
        "InvoiceRecord.java",
        "BillingApp.java",
        "LegacyDateHelper.java",
        "GatewayClient.java",
        "BillingController.java",
        "BillingManager.java",
    ],
    width=126.0,
    height=46.0,
    min_value=0.0,
    max_value=100.0,
    cell_gap=0.9,
    cell_r=0.8,
    value_format="{:.0f}",
    auto_contrast_text=True,
    x_label_position="top",
    y_origin="top",
    axis_text_style=Styles.DarkBold.patch(text_size=9.5),
    value_text_style=Styles.DarkBold.patch(text_size=10.0),
    title="Per-Module Engineering Fitness Matrix (0 = Severe Defects, 100 = Zero AST Issues)",
    title_style=Styles.DarkBold.patch(text_size=11.5),
)
hm.set_data(
    [
        [100, 100, 100, 100, 100, 100],  # InvoiceRecord.java: 0 AST defects
        [100, 100, 50, 100, 100, 100],   # BillingApp.java: missing class Javadoc
        [85, 70, 0, 100, 20, 60],        # LegacyDateHelper.java: Date/SDF/Vector, 0 Javadocs
        [55, 70, 0, 85, 15, 5],          # GatewayClient.java: Java 11 API, secret, no timeout
        [60, 30, 0, 15, 40, 20],         # BillingController.java: cycle, mutable channel, raw Map
        [5, 25, 20, 10, 45, 15],         # BillingManager.java: cog=56, 8 params, ==, empty catch
    ]
)
hm.draw(xy=(12.0, 13.0))
hm.draw_legend(
    xy=(28.0, 4.0),
    text_style=Styles.DarkBold.patch(text_size=9.5),
    orientation="horizontal",
    num_steps=5,
    labels=["0 Critical", "25 Poor", "50 Fair", "75 Good", "100 Clean"],
)

save()
```

---

## 静的 AST 品質・SIG 保守性・12-Factor テレメトリ

| メトリクス区分 | 指標名 | 計測値 | 診断所見 |
| :--- | :--- | :---: | :--- |
| **コードベース規模** | `total_files` / `total_loc` / `total_functions` | `6` / `187` / `11` | 小規模ながら主要 3 ファイルに重大欠陥が極端に集中 |
| **静的網羅率** | `import_hygiene_coverage_pct` | `83.3%` | `GatewayClient.java` に未整列 import 4 件＋ワイルドカード `import java.util.*;` 1 件 |
| **静的網羅率** | `type_safety_coverage_pct` | `81.8%` | 生ジェネリクス署名（`Map`/`List`）2 件、未型付け `Object` 引数 2 件、`@SuppressWarnings("unchecked")` 2 件 |
| **静的網羅率** | `docstring_coverage_pct` | `33.3%` | 公開 Javadoc 欠落 10 件＋`processBatchBilling` の陳腐化 `@param obsoleteToken` 不一致 1 件 |
| **静的網羅率** | `module_test_coverage_pct` | `33.3%` | アサーションなしの JUnit 4 スモークテスト 1 件が `InvoiceRecord` に触れるのみ |
| **SIG 保守性** | `complex_functions` / `excessive_parameters` | `1` / `1` | `BillingManager.processBatchBilling`: `57 行`, `branches=13`, `cognitive=56`, `引数 8 個 (> 6)` |
| **結合・バグ指標** | `circular_dependencies` / `global_state` / `bug_risk_idioms` | `1` / `1` / `7` | `BillingController <-> BillingManager`、静的 `INVOICE_CACHE`、`String ==` 3 件、空 catch、`System.out` 3 件 |
| **互換性** | `undeclared_dependencies` / `language_version_mismatches` | `1` / `1` | `spring-tx` 未宣言の `@Transactional`、Java 1.8 上での Java 11 `java.net.http.HttpResponse` |
| **12-Factor / SRE PRR** | `missing_io_timeouts` / `scattered_env` / `unstructured_logging` | `1` / `1` / `4` | タイムアウトなしの `HttpClient.newHttpClient()`、`System.getenv()`、`System.out` 3 件＋`printStackTrace()` 1 件 |

### 主要ソースコード欠陥の内訳

1. **`BillingManager.processBatchBilling`（`src/main/java/com/example/billing/service/BillingManager.java:33`）**:
   - **SIG 単位サイズ・複雑度・引数過多**: `57` 行、`13` 分岐、認知複雑度 **`56`**（基準 `<= 15`）、引数 **`8` 個**（基準 `<= 6`）にわたり、生 `List items`・複数の真偽フラグ・未型付け `Object extraContext` を混在させています。
   - **文字列参照比較バグ（`String ==`）**: 52 行目（`status == "PAID"`）、55 行目（`currency == "USD"`）、57 行目（`currency == "JPY"`）で `.equals()` ではなく参照同値性 `==` を使用しており、実行時 JSON デシリアライズ文字列で税率計算分岐が意図せずスキップされる欠陥があります。
   - **無音失敗と無効なトランザクション制御**: 83 行目の空 `catch (Exception e) {}` が監査・キャッシュ・コントローラ参照時の例外をすべて握りつぶします（79 行目の未定義メソッド `dateHelper.currentPeriodLabel()` 呼出を含む）。また 91 行目の `private void saveAuditTrail(...)` への `@Transactional` 付与は、Spring AOP プロキシを自己呼び出しおよび `private` 修飾でバイパスし、さらに `pom.xml` に `spring-tx` 依存自体が未宣言です。
   - **Javadoc 署名不一致**: 存在しない `@param obsoleteToken` が残存し、実際の引数 7 個が未記載です。
2. **`GatewayClient.java`（`src/main/java/com/example/billing/client/GatewayClient.java`）**:
   - **言語バージョン API 不整合**: `pom.xml` が `1.8` を宣言する一方で、4〜6 行目で Java 11+ の `java.net.http.{HttpResponse, HttpRequest, HttpClient}` を import しています。
   - **運用・ログ欠陥**: 22 行目の `HttpClient.newHttpClient()` に接続／読み取りタイムアウトがなく、16 行目で直接 `System.getenv("LEGACY_PAYMENT_URL")` を参照し、20 行目の `System.out.println` と 32 行目の `e.printStackTrace()` で非構造出力を行っています。
3. **`LegacyDateHelper.java`（`src/main/java/com/example/billing/util/LegacyDateHelper.java`）**:
   - スレッド非安全な `SimpleDateFormat`、旧 `java.util.Date`、同期化レガシーコレクション生 `Vector` を使用しており、`java.time.Instant`/`DateTimeFormatter` と型付き `List<String>` への置換が必要です。

---

## コンテナランタイム検証とビルド失敗の診断

2 系統のコンテナビルドがいずれもゲート **`RV-01`（ビルド可能性）** で失敗したため、オフライン単体テスト（`RV-02`）、JaCoCo カバレッジ計測（`RV-03`）、Web API 起動スモーク検証（`RV-04`）がすべてブロックされました。

```drawlib align=center code=hide file=runtime_build_failure_diag.png caption="RV-01 における二重コンテナビルド失敗と JUnit / JaCoCo / スモーク検証の連鎖ブロック診断"
from drawlib.canvas import save, setup
from drawlib.lines import line, lines
from drawlib.shapes import rectangle
from drawlib.smartarts import Panel
from drawlib.styles import Styles
from drawlib.text import text

setup(width=146, height=74, dpi=150)

text(
    (73.0, 70.0),
    "Container Runtime Diagnostic: Dual RV-01 Build Crashes Blocking RV-02..RV-04",
    style=Styles.DarkBold.patch(text_size=11.5),
)

# Top-left Track A: Project Dockerfile Failure
p_a = Panel(
    "Track A: Project Dockerfile — FAILED (1.21s)",
    style=Styles.DangerNeutral.patch(shape_r=2.0),
    header_style=Styles.DangerFlat,
    text_style=Styles.WhiteBold.patch(text_size=9.8),
    header_variant="filled",
    header_height=7.0,
)
p_a.draw((4.0, 38.0), width=66.0, height=28.0)
text(
    (37.0, 52.5),
    "examples/java/api_spring_messy/Dockerfile:1\nFROM openjdk:latest",
    style=Styles.DarkBold.patch(text_size=9.8),
)
text(
    (37.0, 43.0),
    "ERROR: docker.io/library/openjdk:latest: not found\nDeprecated base image removed from Docker Hub",
    style=Styles.DangerBold.patch(text_size=9.3),
)

# Top-right Track B: Java 8 Maven Harness Failure
p_b = Panel(
    "Track B: Maven Harness (JDK 8) — FAILED (23.98s)",
    style=Styles.DangerNeutral.patch(shape_r=2.0),
    header_style=Styles.DangerFlat,
    text_style=Styles.WhiteBold.patch(text_size=9.8),
    header_variant="filled",
    header_height=7.0,
)
p_b.draw((76.0, 38.0), width=66.0, height=28.0)
text(
    (109.0, 52.5),
    "pom.xml: Java 1.8 + spring-boot-starter-web:LATEST\nResolves spring-boot-4.2.0.jar (SpringApplication.class)",
    style=Styles.DarkBold.patch(text_size=9.5),
)
text(
    (109.0, 43.0),
    "ERROR: bad class file — wrong version 61.0, should be 52.0\nJDK 17+ bytecode cannot compile under Java 8 javac",
    style=Styles.DangerBold.patch(text_size=9.3),
)

# Convergence bus from both failed tracks down to RV-02, RV-03, RV-04 blocked gates
line((37.0, 38.0), (37.0, 31.5), style=Styles.DangerBold)
line((109.0, 38.0), (109.0, 31.5), style=Styles.DangerBold)
line((26.0, 31.5), (120.0, 31.5), style=Styles.DangerBold)
line((26.0, 31.5), (26.0, 26.2), arrow_head="->", style=Styles.DangerBold)
line((73.0, 31.5), (73.0, 26.2), arrow_head="->", style=Styles.DangerBold)
line((120.0, 31.5), (120.0, 26.2), arrow_head="->", style=Styles.DangerBold)

# Bottom 3 blocked downstream verification gates
gates = [
    (26.0, "RV-02: Offline JUnit Tests", "BLOCKED (0 / 0)\nBillingManagerTest.testSmokeRun\n(JUnit 4, 0 assertions) never ran"),
    (73.0, "RV-03: JaCoCo Coverage", "BLOCKED (N/A)\nLine/Branch coverage unmeasured\nStatic module coverage: 33.3%"),
    (120.0, "RV-04: Web API Smoke", "BLOCKED (web_api)\nSpring Boot never started\nBlocks DAST on ANY /charge"),
]
for gx, title, body in gates:
    rectangle((gx, 15.0), width=42.0, height=21.0, style=Styles.WarningNeutral.patch(shape_r=2.0))
    rectangle(
        (gx, 22.5),
        width=38.0,
        height=4.8,
        style=Styles.WarningFlat.patch(shape_r=1.2),
        text=title,
        text_style=Styles.WhiteBold.patch(text_size=9.5),
    )
    text((gx, 12.2), body, style=Styles.Dark.patch(text_size=9.2))

save()
```

### コンパイラおよび Docker エラー出力抜粋（原文）

**1. プロジェクト Dockerfile ビルド失敗（`examples/java/api_spring_messy/Dockerfile`, `1.21s`, 終了コード `1`）**:

```text
#2 ERROR: docker.io/library/openjdk:latest: not found
Dockerfile:1
   1 | >>> FROM openjdk:latest
ERROR: failed to build: failed to solve: openjdk:latest: failed to resolve source metadata
for docker.io/library/openjdk:latest: docker.io/library/openjdk:latest: not found
```

**2. Java 8 Maven ハーネスコンパイル失敗（`.pni/dockerfiles/examples/java/api_spring_messy/Dockerfile`, `23.98s`, 終了コード `1`）**:

```text
9.861 [ERROR]   bad class file: /m2repo/org/springframework/boot/spring-boot/4.2.0/spring-boot-4.2.0.jar(org/springframework/boot/SpringApplication.class)
9.861 [ERROR]     class file has wrong version 61.0, should be 52.0
9.861 [ERROR]     Please remove or make sure it appears in the correct subdirectory of the classpath.
ERROR: failed to build: failed to solve: process "/bin/sh -c mvn -B -Dmaven.repo.local=/m2repo
  org.jacoco:jacoco-maven-plugin:${JACOCO_VERSION}:prepare-agent test ...
  org.jacoco:jacoco-maven-plugin:${JACOCO_VERSION}:report ..." did not complete successfully: exit code: 1
```

---

## テストスイート健全性評価（`java/testing`）

| テスト評価項目 | 観測値 | 評価 |
| :--- | :---: | :--- |
| **テストフレームワーク** | JUnit 4（`junit:4.13.2`, `<scope>test</scope>`） | レガシー JUnit 4。JUnit 5（`junit-jupiter`）への移行が必要 |
| **テストファイル／メソッド数** | `1` ファイル（`BillingManagerTest.java`）／`1` メソッド（`testSmokeRun`） | 本番 6 クラスに対してテストが極端に不足 |
| **アサーションなしテスト** | `1 / 1`（`100%`） | `testSmokeRun` は `InvoiceRecord` を生成し `getAmountCents()` を呼ぶだけで `assert*` 検証が皆無 |
| **静的／実測カバレッジ** | 静的 `33.3%` ／ 実測 `N/A` | `BillingManager`・`BillingController`・`GatewayClient`・`LegacyDateHelper` への直接検証がなく、JaCoCo は `RV-01` 失敗でブロック |
