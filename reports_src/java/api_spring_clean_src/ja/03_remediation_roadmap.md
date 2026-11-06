# 3. 推奨する変更対応

検出された全18件の指摘事項（`CRITICAL: 1`、`HIGH: 2`、`MEDIUM: 9`、`LOW: 6`）を体系的に解消し、総合スコアを Grade B (`78`) から Grade A/S 水準（`90+`）へ引き上げるため、緊急度とリスク低減効果に基づき **P0（最優先セキュリティ遮断：2施策） -> P1（本番信頼性・DAST例外制御・並行安全・テスト強化：6施策） -> P2（セキュリティヘッダ・供給網・ドキュメント完成度向上：4施策）** の計12施策を定義する。

```drawlib file=remediation_priority_roadmap.png caption="優先度フェーズ別 改善ロードマップ (P0 -> P1 -> P2)"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import Roadmap
from drawlib.styles import Styles

setup(width=146, height=58, dpi=150)

rm = Roadmap(
    style=Styles.Neutral,
    text_style=Styles.DarkBold.patch(text_size=10.2),
    description_style=Styles.Dark.patch(text_size=9.4),
    spine_style=Styles.PrimaryBold,
    badge_style=Styles.Danger,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.5),
    direction="horizontal",
    spacing=3.5,
)
rm.add(
    "P0 緊急セキュリティ (2件)",
    "Spring BOM/Tomcat更新(CRIT 8解消)\nPOST予約APIのOAuth2 JWT認可化",
    badge_text="P0",
    style=Styles.DangerNeutral,
    badge_style=Styles.Danger,
    icon=phosphor.lock_key,
    icon_style=Styles.Danger,
)
rm.add(
    "P1 信頼性・DAST・網羅 (6件)",
    "未知SKU 404 ProblemDetail・Actuator\ncompute競合解消・JaCoCo 85%超達成",
    badge_text="P1",
    style=Styles.WarningNeutral,
    badge_style=Styles.Warning,
    icon=phosphor.wrench,
    icon_style=Styles.Warning,
)
rm.add(
    "P2 保安ヘッダ・供給網 (4件)",
    "nosniffヘッダ・mvnw完全ラッパー化\nApache全文・SHA256固定・README拡充",
    badge_text="P2",
    style=Styles.PrimaryNeutral,
    badge_style=Styles.Primary,
    icon=phosphor.rocket_launch,
    icon_style=Styles.Primary,
)
rm.draw(xy=(4, 5), width=138, height=48)

save()
```

## フェーズ別実行計画とトレーサビリティ

- **Phase 1 (`P0` — 外部公開前の必須対応)**: `pom.xml` の `spring-boot-starter-parent` をパッチ適用済み系列（`>= 3.5.14` / `4.0.6`、または Tomcat `>= 10.1.58`・Jackson `>= 2.18.11`）へ更新して CRITICAL `8` 件・HIGH `29` 件を一括解消する。同時に `InventoryController`（57行目の `TODO(security)`、DAST `CWE-306` 実証）に対し `spring-boot-starter-oauth2-resource-server` による JWT スコープ認可と `sku` パターン検証を適用する。
- **Phase 2 (`P1` — 本番運用性・DAST 例外応答・スレッド安全性・テスト拡充)**: `@RestControllerAdvice` による RFC 7807 `ProblemDetail`（未知 SKU `IllegalArgumentException` の `404` 応答化による DAST `CWE-755` 解消、在庫不足の `409` 変換）と `spring-boot-starter-actuator` (`/actuator/health`) を追加し、`SupplierRestClient` の手動 JSON 連結を Jackson `ObjectMapper` へ、`InventoryService.reserveStock` の `get`/`put` を `inventoryStore.compute(...)` へ置換する。併せて Ubuntu ベースイメージ刷新、`.pni/pentests/` 再検証、および MockMvc / HTTP サーバテスト追加により JaCoCo 行網羅率 `85%` 以上を達成する。
- **Phase 3 (`P2` — セキュリティヘッダ・サプライチェーン再現性とドキュメント整備)**: Spring Security 既定ヘッダによる `X-Content-Type-Options: nosniff` 付与（DAST `CWE-693` 解消）、`.mvn/wrapper/maven-wrapper.properties` を備えた完全版 `mvnw` 生成、`LICENSE` への Apache-2.0 全文記載、`Dockerfile` ベースイメージの `@sha256` ダイジェスト固定、および `README.md` の前提環境・設定一覧・`curl` 例追記を行う。

```drawlib file=remediation_action_table.png caption="推奨改善アクション計画マトリクス (P0 -> P1 -> P2 全12施策)"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=134, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=8.8),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.2),
    border_style=Styles.NeutralThin,
)
rows = [
    ["優先度", "施策", "対象ファイル", "期待効果", "関連ルール / CWE"],
    [
        "P0",
        "予約POST APIへのOAuth2\nJWT認可とSKU形式検証導入",
        "pom.xml\n.../api/InventoryController.java",
        "無認証での在庫枯渇・外部通信\n誘発リスク(SEC-05)を遮断",
        "common/security_vulnerability\ncommon/security",
    ],
    [
        "P0",
        "Spring Boot BOM・Tomcat・\nJackson のパッチ版更新",
        "pom.xml",
        "Maven推移依存のCRIT 8件・\nHIGH 29件を完全解消(SEC-01)",
        "common/security_vulnerability\nCVE-2025-24813 他",
    ],
    [
        "P1",
        "ProblemDetail例外変換・\n@Validated・Actuator導入",
        "pom.xml, InventoryController,\nSupplierProperties.java",
        "404/409標準応答・起動時設定検証\n/actuator/health プローブ確立",
        "common/production_readiness\njava/frameworks/spring_boot",
    ],
    [
        "P1",
        "Jackson JSON直列化と\nConcurrentHashMap競合解消",
        ".../client/SupplierRestClient.java\n.../service/InventoryService.java",
        "JSONインジェクション防止と\n同時引当時の在庫過販売防止",
        "common/security\njava/code_quality",
    ],
    [
        "P1",
        "未知SKU例外の404変換と\n.pni/pentests DAST全件合格化",
        ".../api/InventoryController.java\n.../service/InventoryService.java",
        "無認証401/403拒否と未知SKU\nHTTP 500解消をDASTで実証",
        "common/security_vulnerability\nCWE-306 / CWE-755",
    ],
    [
        "P1",
        "JREベースイメージ刷新と\nDS-0026 HEALTHCHECK追加",
        "Dockerfile",
        "Ubuntu OS層 HIGH 5件(OpenSSL,\nGnuPG)とDS-0026を解消",
        "common/security_vulnerability\nCVE-2026-45447 / DS-0026",
    ],
    [
        "P1",
        "JaCoCo行(62.7%)・分岐(50%)\n未実行パスのテスト網羅",
        "pom.xml, SupplierRestClient,\nInventoryController, *Test.java",
        "RV-03基準(行85% / 分岐75%)\n達成と jacoco:check 自動検証",
        "common/runtime_verification\njava/testing",
    ],
    [
        "P1",
        "MockMvcスライステスト・\n異常系assertThrows拡充",
        "pom.xml, InventoryServiceTest,\nReorderPolicyTest.java",
        "GET 200/404・@Min(1)・例外境界\nの回帰防止とパッケージ階層整合",
        "java/testing\ncommon/runtime_verification",
    ],
    [
        "P2",
        "完全版 Maven Wrapper 生成と\nApache-2.0 LICENSE全文記載",
        "mvnw, LICENSE,\nDockerfile",
        "SHA256検証付きMaven固定と\nOSSライセンス条項の完全明確化",
        "common/supply_chain\njava/dependencies",
    ],
    [
        "P2",
        "READMEへの前提条件・全設定\nプロパティ・curl例の追記",
        "README.md",
        "コード参照不要での迅速な導入と\ndefault-reorder-batch 設定把握",
        "common/documentation",
    ],
    [
        "P2",
        "X-Content-Type-Options:\nnosniff 保安ヘッダ出力設定",
        ".../api/InventoryController.java\npom.xml",
        "MIMEスニッフィング抑止ヘッダ\n付与で test_baseline_http 合格",
        "common/security_vulnerability\nCWE-693",
    ],
    [
        "P2",
        "Dockerfile @sha256 固定と\nActuatorヘルスプローブ連携",
        "Dockerfile\npom.xml",
        "ベースタグ書き換え耐性向上と\nオーケストレータ自動復旧連携",
        "common/supply_chain\ncommon/runtime_verification",
    ],
]
tbl.draw_flexible(
    xy=(3, 131),
    column_widths=[11, 34, 33, 34, 28],
    row_heights=[7.2] + [9.9] * 12,
    data=rows,
)

save()
```
