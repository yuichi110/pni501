# 4. 5 段階ゲート実行ロードマップ

本マイグレーションは **5 つの厳格なゲート付きフェーズ（`Phase 0`..`Phase 4`）** に分割して実行します。各フェーズには決定論的な出口ゲート基準とロールバック・共存条件を定義し、個々の Pull Request 単位で常にビルド可能・検証可能・切り戻し可能な状態を維持します。

```drawlib align=center code=fold file=five_phase_gate_roadmap.png caption="5 段階ゲート付きマイグレーション実行ロードマップ（Phase 0 ビルド復旧〜Phase 4 最終 PNI 監査）"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import Roadmap
from drawlib.styles import Styles
from drawlib.text import text

setup(width=150, height=86, dpi=150)

text(
    (75.0, 81.5),
    "5-Phase Gated Migration Execution Timeline (legacy-billing -> Java 21 + Clean Architecture)",
    style=Styles.DarkBold.patch(text_size=12.0),
)

rm = Roadmap(
    style=Styles.Neutral.patch(shape_r=2.0),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Muted.patch(text_size=9.5),
    spine_style=Styles.DarkBold,
    badge_style=Styles.PrimaryNeutral,
    badge_text_style=Styles.PrimaryBold.patch(text_size=10.0),
    icon_style=Styles.PrimaryBold,
    direction="vertical",
    curve_bend=0.0,
    card_shape="rounded_rect",
    spacing=2.4,
)
rm.add(
    "Phase 0 — Green Build Recovery & Golden Master Harness  [PR-01, PR-02]",
    "Pin Java 21 + Spring Boot 3.4 BOM + mvnw; fix jakarta.servlet; lock POST /charge with >=80% JaCoCo.",
    badge_text="P0",
    icon=phosphor.wrench,
    style=Styles.WarningNeutral.patch(shape_r=2.0),
    badge_style=Styles.WarningFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=10.0),
    icon_style=Styles.WarningBold,
)
rm.add(
    "Phase 1 — Cycle Cut & Clean Architecture Domain / Port Extraction  [PR-03, PR-04]",
    "Wave 1 domain records & Clock; sever circularController; extract Ports/UseCases & constructor DI.",
    badge_text="P1",
    icon=phosphor.code,
)
rm.add(
    "Phase 2 — OpenRewrite Codemods & PG 16 / Redis 7 / RestClient Adapters  [PR-05, PR-06]",
    "Run isolated OpenRewrite recipes; wire JPA+Flyway, Redis TTL, RestClient timeouts (Testcontainers/WireMock).",
    badge_text="P2",
    icon=phosphor.database,
)
rm.add(
    "Phase 3 — Typed @Valid DTOs, Security Hardening & DEC-JAVA-01..04  [PR-07]",
    "Enforce @PostMapping + @Valid records; delete <REDACTED_SECRET>; apply PO-approved decision log fixes.",
    badge_text="P3",
    icon=phosphor.lock_key,
)
rm.add(
    "Phase 4 — Container / CI Hardening & Final PNI Acceptance Audit  [PR-08]",
    "Non-root Temurin 21 Alpine + Actuator HEALTHCHECK; SHA-pinned CI; PNI audit + Trivy + live DAST >= 85.",
    badge_text="P4",
    icon=phosphor.rocket_launch,
    style=Styles.PrimaryNeutral.patch(shape_r=2.0),
    badge_style=Styles.PrimaryFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=10.0),
    icon_style=Styles.PrimaryBold,
)
rm.draw(xy=(4.0, 4.0), width=142.0, height=74.0)

save()
```

## フェーズ別出口ゲート基準とロールバック・共存マトリクス

各フェーズの自動検証ゲートが CI 上ですべて通過するまで、次フェーズへ進んではなりません。

```drawlib align=center code=fold file=phase_gate_exit_rollback_matrix.png caption="Phase 0..Phase 4 出口ゲート基準・検証コマンドおよびロールバック／共存戦略マトリクス"
from drawlib.canvas import save, setup
from drawlib.preset_colors import CssColors
from drawlib.smartarts import Table
from drawlib.styles import Colors, Styles
from drawlib.text import text

setup(width=156, height=80, dpi=150)

text(
    (78.0, 75.5),
    "Phase Gate Exit Criteria, Verification Commands & Rollback Matrix",
    style=Styles.DarkBold.patch(text_size=12.0),
)

table = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=9.5),
    header_cell_style=Styles.PrimaryFlat,
    header_text_style=Styles.WhiteBold.patch(text_size=10.0),
    border_style=Styles.MutedThin,
)
table.set_style_cell_evenodd(
    even_color=Colors.Light,
    even_text_style=Styles.Dark.patch(text_size=9.5),
    odd_color=Colors.White,
    odd_text_style=Styles.Dark.patch(text_size=9.5),
)
table.set_style_cell_header(
    background_color=Colors.Dark,
    text_style=Styles.WhiteBold.patch(text_size=10.0),
)
table.set_style_cell(
    background_color=Styles.WarningNeutral.shape_fill_color,
    text_style=Styles.WarningBold.patch(text_size=9.5),
    rows=[1],
    columns=[0],
)
table.set_style_cell(
    background_color=Styles.PrimaryNeutral.shape_fill_color,
    text_style=Styles.PrimaryBold.patch(text_size=9.5),
    rows=[2, 3, 4],
    columns=[0],
)
table.set_style_cell(
    background_color=Styles.SuccessNeutral.shape_fill_color,
    text_style=Styles.SuccessBold.patch(text_size=9.5),
    rows=[5],
    columns=[0],
)
table.set_style_border(
    top=Styles.DarkBold.patch(line_width=1.4),
    top2=Styles.DarkBold.patch(line_width=1.0),
    bottom=Styles.DarkBold.patch(line_width=1.4),
    between_rows=Styles.MutedThin.patch(line_color=CssColors.LightGray, line_width=0.6),
    between_columns=Styles.MutedThin.patch(line_color=CssColors.LightGray, line_width=0.5),
)

data = [
    ["Phase", "PRs", "Mandatory Exit Criteria", "Gate Command", "Rollback / Coexistence"],
    [
        "Phase 0\nBuild/Test",
        "PR-01\nPR-02",
        "Offline Docker build passes; >=80% JaCoCo;\nPOST /charge Golden Master keys locked.",
        "./mvnw test\njacoco:report",
        "Single reversible build PR;\nzero runtime schema change.",
    ],
    [
        "Phase 1\nCycle/Ports",
        "PR-03\nPR-04",
        "0 circular dependencies; 0 @Autowired fields;\nPhase 0 Golden Master tests pass unchanged.",
        "./mvnw test\n+ AST cycle=0",
        "In-memory adapter shims;\nsafe to revert per PR.",
    ],
    [
        "Phase 2\nCodemod/IO",
        "PR-05\nPR-06",
        "Flyway PG16, Redis TTL & RestClient timeout\nTestcontainers/WireMock pass; 0 static state.",
        "./mvnw rewrite:run\n&& ./mvnw verify",
        "Spring profile feature-toggle\nduring staging soak test.",
    ],
    [
        "Phase 3\nDTO/Sec",
        "PR-07",
        "0 secrets, 0 raw generics, 0 unchecked;\nDEC-JAVA-01..04 signed off & tested.",
        "./mvnw verify\n(MockMvc + sec)",
        "Canary metrics guarding\nDEC-JAVA-01/02 behavior.",
    ],
    [
        "Phase 4\nDocker/CI",
        "PR-08",
        "0 HIGH/CRIT Docker IaC & app CVEs; live\nDAST 0 CRIT/HIGH; PNI score >= 85 (A/S).",
        "docker build &\nPNI audit + DAST",
        "Blue/green deploy w/ Actuator\n/actuator/health rollback.",
    ],
]

table.draw_flexible(
    xy=(4.0, 71.5),
    column_widths=[18.0, 14.0, 50.0, 28.0, 38.0],
    row_heights=[8.0, 11.8, 11.8, 11.8, 11.8, 11.8],
    data=data,
    align="top_left",
)
save()
```

## フェーズ別実行プレイブック

### Phase 0 — グリーンビルド復旧およびゴールデンマスター特性テスト基盤（`PR-01`, `PR-02`）
- **目的**: 破綻している Maven/Docker コンパイル（Java 1.8 と Spring Boot 4.2.0 バイトコード `61.0` の衝突）を最小限の挙動差分で解消し、JUnit 5 + MockMvc テストで `POST /charge` の現行契約を固定する。
- **主要タスク**:
  1. `pom.xml` に Spring Boot 3.4.x BOM と Java 21 コンパイラターゲットを固定し、Maven Wrapper（`mvnw`）をコミットする。
  2. Spring Boot 3.4 でクリーンにコンパイルできるよう `BillingController.java` の `javax.servlet` を `jakarta.servlet` へ更新する。
  3. アサーション不在の `BillingManagerTest.testSmokeRun` を、JUnit 5 + MockMvc によるゴールデンマスターテスト（`customerId`, `amountCents`, `billedCents`、課税分岐、リトライ挙動を検証）へ置き換える。
- **出口基準**:
  - Docker 内のオフライン環境で `./mvnw test` が成功し、既存課金フローの JaCoCo 行カバレッジが `80%` 以上であること。
  - 構造リファクタリング前に `POST /charge` の全暗黙入出力キーがゴールデンマスターテストで固定されていること。
- **ロールバック**: 単一の可逆ビルド PR のみで、ランタイムスキーマやエンドポイント契約変更はゼロ。

### Phase 1 — 循環依存の切断および Clean Architecture ドメイン／Port 抽出（`PR-03`, `PR-04`）
- **目的**: Wave 1（末端モデル・時刻ユーティリティ）および Wave 3 の循環切断を実行し、`BillingController <-> BillingManager` を分離してフレームワーク非依存の `domain` / `port` / `usecase` パッケージを確立する。
- **主要タスク**:
  1. `InvoiceRecord` と `LegacyDateHelper` を純粋な Java 21 ドメインレコード（`Invoice`, `Money`, `BillingSummary`）および `BillingPeriodFormatter`（`DateTimeFormatter` + `Clock`）へ移行する。
  2. インバウンド Port（`ChargeCustomerUseCase`, `ProcessBatchBillingUseCase`）およびアウトバウンド Port（`PaymentGatewayPort`, `InvoiceCachePort`, `BillingAuditRepositoryPort`）を定義する。
  3. `BillingManager` の `@Autowired circularController` と `BillingController.channel` 可変フィールドを削除し、`processBatchBilling` を分解（`cognitive <= 15`, `params <= 6`）してコンストラクタ DI へ移行。既存のインメモリキャッシュと監査出力は一時アダプタシム配下に隔離する。
- **出口基準**:
  - 循環依存ゼロ（`AstFacts.circular_dependencies == 0`）および `@Autowired` フィールド注入ゼロ。
  - Phase 0 のゴールデンマスター特性テストが一切修正なしで全件パスすること。
- **ロールバック**: インメモリ・アダプタシムを用いた挙動保存型リファクタリングのため、PR 単位で安全にリバート可能。

### Phase 2 — OpenRewrite コードモッドおよび PostgreSQL 16 / Redis 7 / RestClient アダプタ実装（`PR-05`, `PR-06`）
- **目的**: 機械的な OpenRewrite アップグレードを独立 PR で適用した上で、一時シムを本番対応の PostgreSQL 16（JPA + Flyway）、Redis 7（TTL 付き）、およびタイムアウト制限付き Spring `RestClient` アダプタへ置換する。
- **主要タスク**:
  1. 専用機械 PR（`PR-05`）で OpenRewrite の `UpgradeToJava21`, `UpgradeSpringBoot_3_4`, `JUnit4to5Migration` を実行する。
  2. Flyway `V1__create_billing_audit.sql` と public `@Transactional` 境界を持つ `JpaBillingAuditAdapter` を実装し、無効な `private @Transactional` スタブを置換する。
  3. Testcontainers および WireMock で検証済みの `RedisInvoiceCacheAdapter`（明示的 TTL）と `RestClientPaymentGatewayAdapter`（明示的接続・読取タイムアウト + `@ConfigurationProperties`）を実装する。
- **出口基準**:
  - Testcontainers / WireMock による PostgreSQL Flyway マイグレーション、Redis TTL 結合テスト、`RestClient` タイムアウトテストが全件パスすること。
  - I/O タイムアウト未設定および静的・可変共有状態（`INVOICE_CACHE`）がゼロであること。
- **ロールバック**: ステージングのソーク検証中、Spring プロファイルで永続化／キャッシュのアダプタ Bean をフィーチャートグル可能。

### Phase 3 — 型付き `@Valid` DTO、セキュリティ強化および承認済み意思決定項目の適用（`PR-07`）
- **目的**: HTTP 境界の堅牢化、ハードコード秘密鍵の完全排除、およびステークホルダー承認済みの意思決定ログ（`DEC-JAVA-01`..`04`）を実装する。
- **主要タスク**:
  1. raw `Map` ペイロードと全メソッド許可 `@RequestMapping("/charge")` を、`@PostMapping("/charge")` および厳格な JSON キーを保持する `@Valid ChargeRequest` / `ChargeResponse` レコードへ置換する。
  2. `GatewayClient` のハードコード `GATEWAY_SECRET` リテラル（`<REDACTED_SECRET>`）を削除し、認証情報をローテーションした上で `@ConfigurationProperties` 経由で注入する。
  3. ステークホルダー承認済みの `DEC-JAVA-01`..`04`（列挙型 / `.equals()` 比較、設定可能なリトライ金額、`controllerPing` の扱い、SLF4J 構造化ロギングと PostgreSQL フェイルファスト／Redis 警告フォールバック）を適用する。
- **出口基準**:
  - ハードコード機密情報ゼロ、raw `Map`/`List` ジェネリクスゼロ、`@SuppressWarnings("unchecked")` ゼロ、認証・入力検証 MockMvc テスト全件合格。
  - 4 件の意思決定ログがすべて承認され、単体・結合テストで網羅されていること。
- **ロールバック**: 挙動変更を伴う `DEC-JAVA-01` / `DEC-JAVA-02` は、全面展開前にカナリア課金メトリクスで監視・保護する。

### Phase 4 — コンテナ / CI 強化および最終 PNI 受入監査（`PR-08`）
- **目的**: 破綻した root 実行の `openjdk:latest` Dockerfile と特権 `pull_request_target` CI を刷新し、PNI v2 フル監査・Trivy・ライブ HTTP DAST の最終受入ゲートを通過する。
- **主要タスク**:
  1. `.dockerignore` と Spring Boot Actuator `/actuator/health` `HEALTHCHECK` を備えたマルチステージ非 root `eclipse-temurin:21-jdk` / `eclipse-temurin:21-jre-alpine` Dockerfile を作成する。
  2. `.github/workflows/build.yml` を `pull_request` トリガー・明示的 `permissions: { contents: read }`・コミット SHA 固定アクションへ刷新し、`LICENSE`, `SECURITY.md`, `.gitignore`, Dependabot 設定を追加する。
  3. コンテナ化 Maven/Docker 検証・Trivy SCA/IaC スキャン・ライブ HTTP DAST ペネトレーション検証を含む完全な PNI `java_api_spring_messy` 監査を再実行する。
- **出口基準**:
  - Docker イメージが正常ビルドされ、HIGH/CRITICAL の Dockerfile 構成ミスおよび未固定アプリ CVE が `0` 件であること。
  - ライブ DAST（`.pni/pentests/examples/java/api_spring_messy`）が正常起動して CRITICAL/HIGH 検出 `0` 件で通過し、PNI 総合スコア **`85` 以上（グレード A/S）** を達成すること。
- **ロールバック**: `/actuator/health` レディネスプローブをトリガーとしたブルー／グリーンコンテナデプロイによる自動切り戻し。
