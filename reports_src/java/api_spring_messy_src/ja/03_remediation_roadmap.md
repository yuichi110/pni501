# 3. 推奨する変更対応

検出された計24件の指摘事項（`CRITICAL` 6件、`HIGH` 12件、`MEDIUM` 4件、`LOW` 2件 / `action_plan` 計15施策：`P0` 8件・`P1` 6件・`P2` 1件）を体系的に解消し、総合スコアを Grade D (`23`) から本番運用可能な Grade A 水準（`85+`）へ引き上げるため、重複施策を統合した **P0（緊急止血・ビルド&保安復旧：5重点施策） -> P1（本番信頼性・DAST通過・テスト整備：4重点施策） -> P2（ドキュメント・統治標準化：1重点施策）** の3フェーズ改善計画を策定する。

```drawlib file=remediation_priority_roadmap.png caption="優先度フェーズ別 改善ロードマップ (P0 -> P1 -> P2)"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import Roadmap
from drawlib.styles import Styles

setup(width=146, height=58, dpi=150)

rm = Roadmap(
    style=Styles.Neutral,
    text_style=Styles.DarkBold.patch(text_size=10.0),
    description_style=Styles.Dark.patch(text_size=9.2),
    spine_style=Styles.PrimaryBold,
    badge_style=Styles.Danger,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.5),
    direction="horizontal",
    spacing=3.5,
)
rm.add(
    "P0 緊急止血・復旧",
    "Java 21+Spring 3.4固定BOM\n秘密除去・API保護・バグ修正",
    badge_text="P0",
    style=Styles.DangerNeutral,
    badge_style=Styles.Danger,
    icon=phosphor.lock_key,
    icon_style=Styles.Danger,
)
rm.add(
    "P1 品質・DAST検証",
    "非root Docker・ライブDAST合格\nTimeout・型安全化・JUnit 5",
    badge_text="P1",
    style=Styles.WarningNeutral,
    badge_style=Styles.Warning,
    icon=phosphor.wrench,
    icon_style=Styles.Warning,
)
rm.add(
    "P2 文書・供給網統治",
    "README API仕様・Javadoc整備\nDependabot・SECURITY・LICENSE",
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

- **Phase 1 (`P0` — 即時対応：ビルド復旧・重大脆弱性と論理バグの根絶)**: `pom.xml` の `LATEST` 指定と Java 1.8 設定を廃止して Java 21 LTS + Spring Boot 3.4.x BOM（`spring-tx` 明示を含む）へ固定し、`CVE-2022-22965` 範囲マッチとバイトコード・Java 11 API 不整合を同時に解消してコンテナ検証および `web_pentest` ループバック起動をアンブロックする。並行して `GatewayClient` のハードコード秘密情報除去、`.github/workflows/build.yml` の `pull_request` 化・`permissions` 制限・SHA 固定、`/charge` の `@PostMapping` + Spring Security + `@Valid` DTO 化、および `BillingManager` の共有 `static Map`・循環依存・`String ==` 比較・未定義メソッド呼び出し・空 `catch` の修正を行う。
- **Phase 2 (`P1` — 短期優先：コンテナハードニング・ライブ DAST 全件 PASS・JUnit 5 カバレッジ確立)**: `Dockerfile` を `eclipse-temurin:21` マルチステージ・非 root `USER`・`HEALTHCHECK` 付きに刷新し、`.pni/pentests/examples/java/api_spring_messy/` の `web_pentest` スイート（`CWE-306` 401/403・`CWE-650` `PUT /charge -> 405`・`CWE-20` 不正数値 `-> 400`・`CWE-693` `nosniff` ヘッダ）を隔離ループバックで全件 PASS させる。さらに `GatewayClient` にタイムアウト・`@ConfigurationProperties`・SLF4J 構造化ログを導入し、Raw 型と旧式 `Date`/`SimpleDateFormat`/`Vector` を刷新の上、JUnit 5 + Mockito + JaCoCo により実測行網羅率 80% 以上を達成する。
- **Phase 3 (`P2` — 継続的ガバナンス向上)**: `README.md` の API 仕様・環境変数ドキュメント化、公開 Javadoc 100% 整備、および `.gitignore`・`LICENSE`・`SECURITY.md`・`.github/dependabot.yml` の追加を完了する。

```drawlib file=remediation_action_table.png caption="推奨改善アクション計画マトリクス (15施策を統合した P0 -> P1 -> P2 主要10重点施策)"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=118, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=8.8),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.2),
    border_style=Styles.NeutralThin,
)
rows = [
    ["優先度", "施策", "対象ファイル", "期待効果", "関連ルール"],
    [
        "P0",
        "Java 21 + Spring Boot 3.4\n固定BOM化・spring-tx明示",
        "pom.xml",
        "LATEST範囲CVE・v61衝突解消\n・テスト/DAST起動アンブロック",
        "java/dependencies\nCVE-2022-22965",
    ],
    [
        "P0",
        "循環依存・String ==比較・\n未定義呼出・空catchの修正",
        "BillingManager.java\nBillingController.java\nLegacyDateHelper.java",
        "コンパイル不全・税率計算バグ\n・共有状態競合を一括解消",
        "common/architecture\ncommon/maintainability",
    ],
    [
        "P0",
        "/charge POST限定・認証保護・\nDTO検証とDASTプローブ合格",
        "BillingController.java",
        "CWE-306/650/20/693根絶と\nweb_pentest 全件PASS達成",
        "common/\nsecurity_vulnerability\nCWE-306/650/20",
    ],
    [
        "P0",
        "ハードコード秘密情報除去と\n外部シークレット注入化",
        "GatewayClient.java",
        "決済APIキーのソース露出\nリスクを完全に排除",
        "common/security\nSEC-03",
    ],
    [
        "P0",
        "GitHub Actions 最小権限化と\nAction コミットSHA固定",
        ".github/workflows/\nbuild.yml",
        "pull_request_target 特権\n悪用リスクの根絶",
        "common/supply_chain\ncommon/security",
    ],
    [
        "P1",
        "マルチステージ・非root・\nHEALTHCHECK付 Dockerfile",
        "Dockerfile\npom.xml",
        "コンテナ起動復旧と Trivy\nDS-0001/0002/0026 全解消",
        "common/\nruntime_verification\nDS-0002 / DS-0001",
    ],
    [
        "P1",
        "HTTP Timeout・設定集約・\nSLF4Jログ・Actuator導入",
        "GatewayClient.java\nBillingManager.java",
        "下流遅延時のスレッド枯渇防止\nと本番可観測性の確立",
        "common/\nproduction_readiness\ncommon/twelve_factor",
    ],
    [
        "P1",
        "JUnit 5 + JaCoCo 移行と\n業務ロジック単体テスト実装",
        "BillingManagerTest.java\npom.xml",
        "オフラインテスト合格と\n実測網羅率 80% 以上の達成",
        "java/testing\ncommon/\nruntime_verification",
    ],
    [
        "P1",
        "Raw型排除と java.time 刷新\n・コンストラクタDI統一",
        "LegacyDateHelper.java\nGatewayClient.java",
        "型安全性100%化と旧Date/\nVector都度生成負債の解消",
        "java/typing\njava/code_quality",
    ],
    [
        "P2",
        "README・Javadoc拡充と\nガバナンス文書一式の整備",
        "README.md\npom.xml",
        "オンボーディング改善と継続的\n脆弱性自動検知体制の確立",
        "common/documentation\ncommon/git_workflow",
    ],
]
tbl.draw_flexible(
    xy=(3, 115),
    column_widths=[10, 33, 29, 35, 33],
    row_heights=[7.5] + [10.4] * 10,
    data=rows,
)

save()
```
