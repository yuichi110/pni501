# 3. 推奨改善ロードマップ

`legacy-billing` の改善計画は、**全 11 件の優先度付きアクション（`P0: 5 件`、`P1: 5 件`、`P2: 1 件`）** に段階化されています。まず最優先の `P0` で Java 21 / Spring Boot 3.4 の決定論的ビルド復旧・重大セキュリティ除去・DI 循環解消を達成し、続く `P1` で JUnit 5 特性テストによる安全網を構築した上でリファクタリングおよび DAST 再検証を実施します。

```drawlib align=center code=hide file=remediation_roadmap.png caption="段階的改善ロードマップ（P0 -> P1 -> P2）および後続移行計画 java_api_spring_messy_migration への連携"
from drawlib.canvas import save, setup
from drawlib.smartarts import Roadmap
from drawlib.styles import Styles
from drawlib.text import text

setup(width=146, height=82, dpi=150)

text(
    (73.0, 78.0),
    "Phased Remediation Timeline (P0 Urgent -> P1 Hardening -> P2 Governance -> Migration Plan)",
    style=Styles.DarkBold.patch(text_size=11.5),
)

rm = Roadmap(
    style=Styles.Neutral.patch(shape_r=2.0),
    text_style=Styles.DarkBold.patch(text_size=10.3),
    description_style=Styles.Dark.patch(text_size=9.3),
    spine_style=Styles.PrimaryBold,
    badge_style=Styles.PrimaryFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.3),
    direction="vertical",
    card_shape="rounded_rect",
    spacing=2.6,
)
rm.add(
    "P0 — Unblock Build, Secrets, CI & DI Cycle (5 Actions)",
    "Pin Java 21 LTS + Spring Boot 3.4.x BOM + eclipse-temurin:21 non-root Dockerfile;\nfix pull_request_target CI, delete GATEWAY_SECRET, break BillingController<->BillingManager cycle.",
    badge_text="P0 | NOW",
    style=Styles.DangerNeutral.patch(shape_r=2.0),
    badge_style=Styles.DangerFlat,
)
rm.add(
    "P1 — Characterization Tests, Refactoring & DAST (5 Actions)",
    "JUnit 5 + MockMvc tests (>=80% cov); RestClient timeouts, @ConfigurationProperties & SLF4J;\ndecompose processBatchBilling (cog <=15), adopt java.time, and re-run web_pentest.",
    badge_text="P1 | NEXT",
    style=Styles.WarningNeutral.patch(shape_r=2.0),
    badge_style=Styles.WarningFlat,
)
rm.add(
    "P2 — Documentation & Repository Governance (1 Action)",
    "Expand README.md with architecture, environment config, API contract, and test commands;\ncommit LICENSE, SECURITY.md, .gitignore, and Dependabot configuration.",
    badge_text="P2 | POLISH",
    style=Styles.PrimaryNeutral.patch(shape_r=2.0),
    badge_style=Styles.PrimaryNeutral,
    badge_text_style=Styles.PrimaryBold.patch(text_size=9.3),
)
rm.add(
    "Chained Execution: java_api_spring_messy_migration",
    "Operationalizes P0-P2 as a staged Clean Architecture plan with Stakeholder Decision Log\n(String == tax semantics), verified offline Maven/JaCoCo gates, and live DAST probes.",
    badge_text="MIGRATION",
    style=Styles.PrimaryFlat.patch(shape_r=2.0),
    text_style=Styles.WhiteBold.patch(text_size=10.3),
    description_style=Styles.White.patch(text_size=9.3),
    badge_style=Styles.DarkFlat,
)
rm.draw((6.0, 5.0), width=134.0, height=69.0)

save()
```

---

## 改善対象ドメイン分布とフェーズ完了基準

全 11 件のバックログのうち **55%（6 件）** をセキュリティおよび依存関係安定化が占めており、すべての `P0` 項目が Maven/Docker コンパイル復旧（`RV-01`）、重大な SCA/シークレット解消（`SEC-01..03`）、または Spring Boot 3.x 起動要件（循環依存の排除）の直接のブロッカーとなっています。

```drawlib align=center code=hide file=remediation_priority_breakdown.png caption="対象ドメイン別の改善アクション分布（左）とフェーズ別完了基準（右）"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.smartarts import KpiCards
from drawlib.styles import Styles

setup(width=146, height=60, dpi=150)

# Left: Action counts by category (single series)
bar = BarChart(
    axis_line_style=Styles.Dark,
    width=76.0,
    height=46.0,
    categories=["Security", "Code Quality", "Dependencies", "Architecture", "Testing", "Docs"],
    orientation="horizontal",
    bar_width_ratio=0.62,
    bar_r=0.8,
    axis_text_style=Styles.DarkBold.patch(text_size=9.8),
    grid_style=Styles.MutedThin,
    value_text_style=Styles.DarkBold.patch(text_size=9.8),
    value_format="{:.0f}",
    title="11 Remediation Actions by Target Domain",
    title_style=Styles.DarkBold.patch(text_size=11.0),
)
bar.configure_x_axis(min_value=0, max_value=5, tick_step=1, show_grid=True)
bar.add_series("Actions", [4, 2, 2, 1, 1, 1], style=Styles.PrimaryFlat)
bar.draw(xy=(6.0, 7.0))

# Right: Phase exit criteria KPI cards
kpis = KpiCards(
    style=Styles.Neutral.patch(shape_r=2.0),
    metric_style=Styles.DarkBold.patch(text_size=12.5),
    text_style=Styles.DarkBold.patch(text_size=10.0),
    description_style=Styles.Muted.patch(text_size=9.5),
    accent_style=Styles.PrimaryFlat,
    accent_position="left_pill",
    metric_layout="left_column",
    metric_width_ratio=0.28,
    spacing=2.6,
)
kpis.add(
    "5 P0",
    "Phase 0: Unblock & Secure",
    "0 CRIT CVEs/secrets; clean Java 21 build",
    style=Styles.DangerNeutral.patch(shape_r=2.0),
    metric_style=Styles.DangerBold.patch(text_size=12.5),
    accent_style=Styles.DangerFlat,
)
kpis.add(
    "5 P1",
    "Phase 1: Test & Refactor",
    "JUnit 5 >=80% cov; cog <=15; DAST green",
    style=Styles.WarningNeutral.patch(shape_r=2.0),
    metric_style=Styles.WarningBold.patch(text_size=12.5),
    accent_style=Styles.WarningFlat,
)
kpis.add(
    "1 P2",
    "Phase 2: Governance",
    "README, LICENSE, SECURITY, .gitignore",
    style=Styles.PrimaryNeutral.patch(shape_r=2.0),
    metric_style=Styles.PrimaryBold.patch(text_size=12.5),
    accent_style=Styles.PrimaryFlat,
)
kpis.draw((86.0, 8.0), width=56.0, height=45.0, columns=1)

save()
```

---

## アクションプラン・トレーサビリティマトリクス（`P0 -> P1 -> P2`）

下表は `java_api_spring_messy_score.json` の事前ソート順（`P0 -> P1 -> P2` 全 11 件）を厳密に保持し、対象ファイル・期待効果・関連ルール／CVE を対応付けたものです。

| # | 優先度 | カテゴリ | アクション内容 | 対象ファイル | 期待効果 | 関連ルール / CVE |
| :---: | :---: | :--- | :--- | :--- | :--- | :--- |
| 1 | **`P0`** | `architecture` | **`BillingController<->BillingManager` 循環解消と可変シングルトン／静的状態の排除**: `circularController` と `BillingController.channel` を削除し、コンストラクタ注入へ移行するとともに `INVOICE_CACHE` を外部化する。 | `src/main/java/com/example/billing/controller/BillingController.java`, `src/main/java/com/example/billing/service/BillingManager.java` | Spring DI 循環依存および並列リクエスト間のデータ競合を解消。 | `common/architecture`, `java/frameworks/spring_boot` |
| 2 | **`P0`** | `dependencies` | **Java 21 LTS + Spring Boot 3.4 BOM + `eclipse-temurin:21` 固定による Maven / Docker ビルド復旧**: Java 1.8 と `spring-boot-starter-web:LATEST` を Java 21 + 固定版 Spring Boot 3.4.x 親 POM/BOM へ置換し、廃止された `openjdk:latest` を `eclipse-temurin:21-jdk/jre` へ移行する。 | `pom.xml`, `Dockerfile` | 決定論的コンパイル、JaCoCo カバレッジ計測、起動検証を復旧。 | `common/runtime_verification`, `java/dependencies` |
| 3 | **`P0`** | `security` | **GitHub Actions CI トリガーと root `Dockerfile` の堅牢化**: `pull_request_target` を `pull_request` + 最小権限 `permissions:` + SHA 固定アクションへ置換し、`Dockerfile` を非 root `eclipse-temurin:21-jre` と `.dockerignore` 構成へ移行する。 | `.github/workflows/build.yml`, `Dockerfile` | CI トークン奪取および可変 root コンテナ露出リスクを解消。 | `common/supply_chain`, `common/security` |
| 4 | **`P0`** | `security` | **Spring Boot 3.4.x BOM 固定と `Dockerfile` root/`:latest` 設定不備の解消**: 親 POM/BOM により Spring Boot 3.4.x を固定して `CVE-2022-22965` 範囲一致を解消し、`Dockerfile` の `DS-0001`・`DS-0002`・`DS-0026` を是正する。 | `pom.xml`, `Dockerfile` | CRITICAL の未固定 SCA 露出と HIGH の root コンテナ設定不備を解消。 | `common/security_vulnerability`, `SEC-01`, `SEC-02`, `CVE-2022-22965` |
| 5 | **`P0`** | `security` | **ハードコードされた `GATEWAY_SECRET` の削除と `@ConfigurationProperties` 注入**: 13 行目の定数を削除し認証情報をローテーションした上で、外部環境変数／Vault から `@ConfigurationProperties` 経由で注入する。 | `src/main/java/com/example/billing/client/GatewayClient.java` | ソースコード管理上の CRITICAL 認証情報漏えいを解消。 | `common/security`, `common/supply_chain` |
| 6 | **`P1`** | `code_quality` | **`RestClient` タイムアウト、`@ConfigurationProperties`、SLF4J ログ、Actuator `/healthz` の導入**: `System.getenv` と `HttpClient.newHttpClient()` をタイムアウト付き `RestClient` へ置換し、`System.out`/`printStackTrace`・空 catch を SLF4J へ統一し、Actuator ヘルスプローブを有効化する。 | `src/main/java/com/example/billing/client/GatewayClient.java`, `src/main/java/com/example/billing/service/BillingManager.java` | 外部ゲートウェイ応答遅延時のスレッド枯渇を防ぎ 12-Factor 可観測性を回復。 | `common/twelve_factor`, `common/production_readiness` |
| 7 | **`P1`** | `code_quality` | **`processBatchBilling` 分割、`String ==`・空 catch・`private @Transactional` 修正、レガシー `Date`/`Vector` 置換**: 生 `Map`/`List` を型付き Java `record` DTO へ置換し、`processBatchBilling` を分割（`cognitive <=15`, `params <=6`）、`.equals()` と SLF4J、および `java.time`/`List` を適用する。 | `src/main/java/com/example/billing/service/BillingManager.java`, `src/main/java/com/example/billing/util/LegacyDateHelper.java` | バグ混入リスクを大幅に低減し、型安全性と可読性を回復。 | `common/maintainability`, `java/code_quality`, `java/typing`, `java/modern_stack` |
| 8 | **`P1`** | `dependencies` | **Maven ビルドの Java 21 LTS・Spring Boot 3.4 BOM・`mvnw` 刷新**: `pom.xml` を Java 1.8 / `LATEST` / `javax` / JUnit 4 から Java 21 LTS + Spring Boot 3.4 BOM + JUnit 5 へ移行し、`mvnw` をコミットする。 | `pom.xml` | 再現可能なビルドと長期サポート（LTS）セキュリティ更新基盤を確立。 | `java/dependencies`, `common/supply_chain` |
| 9 | **`P1`** | `security` | **Java 21 + Spring Boot 3.4 コンテナ復旧後の `web_pentest` 再実行**: `pom.xml` と `Dockerfile` のビルド復旧後、`.pni/pentests/examples/java/api_spring_messy` を実行し、POST 限定・入力検証・セキュリティヘッダーを動的検証する。 | `pom.xml`, `src/main/java/com/example/billing/controller/BillingController.java` | 継続的な動的セキュリティ検証（`SEC-06`）を復旧。 | `common/security_vulnerability`, `SEC-06` |
| 10 | **`P1`** | `testing` | **アサーションなし JUnit 4 スモークテストを JUnit 5 + `MockMvc` 特性テスト群へ刷新**: リファクタリング着手前に JUnit 5 Jupiter へ移行し、`BillingController`・`BillingManager`・`GatewayClient` に対する実アサーション付き特性テストを追加する。 | `src/test/java/com/example/billing/BillingManagerTest.java` | Java 21 / Clean Architecture 移行の安全網を構築しカバレッジ `>=80%` を達成。 | `java/testing` |
| 11 | **`P2`** | `documentation` | **`README.md` 拡充とリポジトリ基本ガバナンスファイルの追加**: セットアップ・環境変数・API エンドポイント・テスト実行手順を `README.md` に整備し、`LICENSE`・`SECURITY.md`・`.gitignore` を追加する。 | `README.md` | オンボーディング品質とリポジトリガバナンス準拠を向上。 | `common/documentation`, `common/git_workflow` |

---

## 後続マイグレーション計画（`java_api_spring_messy_migration`）への接続

本診断ロードマップは、Clean Architecture 移行実行計画 **`java_api_spring_messy_migration`** へ以下の 3 ウェーブ構成で直接引き継がれます。

1. **Wave 1（安定化とバージョン固定 — アクション #2, #3, #4, #5）**: Java 21 LTS + Spring Boot 3.4.x BOM + `mvnw` の固定、`.github/workflows/build.yml` および `Dockerfile` の堅牢化、`GATEWAY_SECRET` の外部化を実施。
2. **Wave 2（安全網と仕様合意 — アクション #10, #7）**: JUnit 5 + `MockMvc` 特性テストを確立し、`String ==` 税率分岐（`PAID`, `USD`, `JPY`）の仕様変更についてステークホルダー合意ログ（Stakeholder Decision Log）で確認。
3. **Wave 3（Clean Architecture 移行と PRR — アクション #1, #6, #7, #8, #9, #11）**: `BillingController <-> BillingManager` 循環の解消、Java `record` DTO とリポジトリ／ゲートウェイポートの抽出、`@PostMapping("/charge")` + `@Valid` + 認証の導入、`web_pentest` と JaCoCo（`>=80%`）の実測検証、ガバナンス文書整備を完了。
