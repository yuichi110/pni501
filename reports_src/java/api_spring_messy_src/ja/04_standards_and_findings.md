# 4. 検査指標・ルール適合マトリクスと指摘一覧

本章では、`java_api_spring_messy` ワークフローで実行した8つの評価ステップのスコア比較（弱点順）、全15エンジニアリングルールの適合判定マトリクス（`FAIL -> WARN -> PASS`）、および全24件の正規化指摘を同一箇所（`file:line`）単位で統合した **18箇所の集約指摘一覧（`consolidated_findings`: `CRITICAL -> HIGH -> MEDIUM -> LOW`）** を示す。

```drawlib file=audit_dimensions_barchart.png caption="実行監査ステップ別スコア比較 (弱点順: Weakest -> Strongest 全8ステップ)"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.styles import Styles

setup(width=146, height=66, dpi=150)

chart = BarChart(
    axis_line_style=Styles.Neutral,
    grid_style=Styles.NeutralThin,
    axis_text_style=Styles.DarkBold.patch(text_size=8.4),
    value_text_style=Styles.DarkBold.patch(text_size=9.0),
    background_style=Styles.Neutral.patch(shape_r=2.0),
    categories=[
        "コンテナ実行\n(10 / D)",
        "脆弱性監査\n(15 / D)",
        "JUnitテスト\n(15 / D)",
        "Web Pentest\n(15 / D)",
        "供給網衛生\n(18 / D)",
        "本番稼働準備\n(20 / D)",
        "リポジトリ構造\n(22 / D)",
        "Java AST\n(25 / D)",
    ],
    orientation="vertical",
    bar_width_ratio=0.56,
    bar_r=1.0,
    width=134,
    height=55,
    title="監査ステップ別 健全性スコア比較 (全8ステップ Grade D: 10 - 25点)",
    title_style=Styles.DarkBold.patch(text_size=10.5),
)
chart.add_series("監査ステップスコア", [10, 15, 15, 15, 18, 20, 22, 25], style=Styles.Danger)
chart.draw(xy=(6, 5))

save()
```

## ルール適合マトリクス（全15ルール：`FAIL: 14` / `WARN: 1` / `PASS: 0`）

全評価ルールは最悪ステータス優先で集約されており、15ルール中 **14ルールが `FAIL`**、残り1ルール（`common/git_workflow`：秘密情報ファイルのコミットはないが `.gitignore` 不在）が **`WARN`** となり、`PASS` 達成ルールは `0` 件であった。

```drawlib file=rule_compliance_matrix.png caption="エンジニアリングルール適合マトリクス (FAIL -> WARN -> PASS 全15ルール)"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=120, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=8.8),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.2),
    border_style=Styles.NeutralThin,
)
rows = [
    ["判定", "ルールID", "代表評価ステップ", "決定的エビデンス要約"],
    ["FAIL", "common/architecture", "java_ast_audit", "BillingController <-> BillingManager の双方向循環依存"],
    ["FAIL", "common/documentation", "project_structure", "README.md が実質2行のみで前提・API仕様・テスト手順不在"],
    ["FAIL", "common/maintainability", "java_ast_audit", "processBatchBilling 認知複雑度56・8引数・==比較・空catch"],
    ["FAIL", "common/production_readiness", "service_readiness_audit", "HttpClient タイムアウト未設定・即時リトライ・Actuator不在"],
    ["FAIL", "common/runtime_verification", "container_runtime_audit", "Dockerfile/Maven ビルド失敗でテスト・網羅率・起動全ブロック"],
    ["FAIL", "common/security", "supply_chain_audit", "GATEWAY_SECRET 直書き・pull_request_target・無検証Map入力"],
    ["FAIL", "common/security_vulnerability", "web_penetration_audit", "CVE-2022-22965・DS不備3件・ANY /charge・DAST起動エラー(15.7s)"],
    ["FAIL", "common/supply_chain", "supply_chain_audit", "LATEST依存・checkout@main・permissions不在・統治文書全欠落"],
    ["FAIL", "common/twelve_factor", "service_readiness_audit", "System.getenv直参照・static生HashMap状態・System.out出力"],
    ["FAIL", "java/code_quality", "java_ast_audit", "Javadoc率33.3%・@param不整合・未定義呼出・* /未整列import"],
    ["FAIL", "java/dependencies", "project_structure", "Java 1.8 と LATEST/Java 11 API/spring-tx欠落の不整合"],
    ["FAIL", "java/frameworks/spring_boot", "java_ast_audit", "@AutowiredフィールドDI 3箇所・共有可変状態・private @Transactional"],
    ["FAIL", "java/testing", "java_test_audit", "JUnit 4 テスト1件のみ・アサーション0件・パッケージ階層不一致"],
    ["FAIL", "java/typing", "java_ast_audit", "Raw Map/List/Vector・Object引数・@SuppressWarnings乱用"],
    ["WARN", "common/git_workflow", "project_structure", "秘密鍵コミットはないが .gitignore 不在で成果物混入リスク"],
]
tbl.draw_flexible(
    xy=(3, 117),
    column_widths=[11, 39, 30, 60],
    row_heights=[7.2] + [7.1] * 15,
    data=rows,
)

save()
```

## 箇所集約 指摘事項一覧（18箇所に集約 / 正規化指摘計24件：`CRITICAL: 4箇所` / `HIGH: 8箇所` / `MEDIUM: 4箇所` / `LOW: 2箇所`）

`pom.xml:20`（3ルール重複）、`Dockerfile:1`（4件重複）、`.github/workflows/build.yml:4`（2件重複）などの同一 `file:line` 指摘を `consolidated_findings` により1行へ統合し、`CRITICAL -> HIGH -> MEDIUM -> LOW` の順序で以下に示す（個別ルール単位の全24件は `score.json` の `findings` に保持）。

```drawlib file=findings_evidence_table.png caption="箇所集約 検出指摘一覧 (18箇所 / 元指摘24件を file:line 単位で統合)"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=166, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=8.3),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=8.7),
    border_style=Styles.NeutralThin,
)
rows = [
    ["重要度", "関連ルールID (集約)", "該当箇所", "統合エビデンス・検出事象", "統合推奨修正策"],
    ["CRIT", "common/supply_chain (x2)", "build.yml:4", "pull_request_target + 権限無制限 +\nactions/checkout@main で mvn 実行", "pull_request化・contents:read明記\n・checkout をフルSHA固定"],
    ["CRIT", "common/runtime_verification\ncommon/security_vulnerability\njava/dependencies", "pom.xml:20", "LATEST指定で静的CVE-2022-22965一致&\n4.2-RC1(v61)×Java 8・HttpClient衝突", "Java 21 + Spring 3.4 BOM 固定化\n・spring-tx明示・mvnw追加"],
    ["CRIT", "common/security", "GatewayClient:13", "GATEWAY_SECRET 本番形式鍵の定数直書き", "定数削除・鍵更新・外部Secret注入"],
    ["CRIT", "java/code_quality", "BillingManager:79", "未定義 currentPeriodLabel() 呼出と空catch", "java.time 期間生成実装と空catch廃止"],
    ["HIGH", "common/supply_chain (x2)\ncommon/runtime_verification\ncommon/security_vulnerability", "Dockerfile:1", "openjdk:latest解決失敗・JAR工程不在・\nDS-0002(root)/DS-0001/DS-0026不備", "temurin:21 マルチステージ化・非root\nUSER・HEALTHCHECK・.dockerignore"],
    ["HIGH", "common/security_vulnerability", "pom.xml:13", "Java 1.8不整合でコンテナ構築失敗(15.7s)\nweb_pentest ライブDAST実行がエラー停止", "Java 21 + Spring 3.4化で起動復旧し\n.pni/pentests DASTスイートを有効化"],
    ["HIGH", "common/production_readiness", "GatewayClient:22", "HttpClient 都度生成・Timeout未設定", "Timeout付シングルトンBean再利用"],
    ["HIGH", "common/security_vulnerability", "BillingController:22", "ANY /charge 無認証公開・動詞無制限", "@PostMapping・認証認可(CWE-306/650)"],
    ["HIGH", "java/frameworks/spring_boot", "BillingManager:17", "共有static生HashMap・\nprivate @Transactional", "並行安全Bean管理・\npublic境界 + spring-tx"],
    ["HIGH", "common/architecture", "BillingManager:22", "BillingController を逆方向 @Autowired", "逆参照削除・DTOでチャネル情報伝達"],
    ["HIGH", "common/maintainability", "BillingManager:52", "String == 比較3箇所・複雑度56・8引数", "equals/Enum化・Command DTO分割"],
    ["HIGH", "java/testing", "BillingManagerTest:8", "JUnit 4・アサーション0件・階層不一致", "JUnit 5 + Mockito + JaCoCo 80%整備"],
    ["MED", "common/documentation", "README.md:1", "2行のみで前提・API仕様・テスト未記載", "Standard Readme 構成で仕様を明記"],
    ["MED", "common/twelve_factor", "GatewayClient:16", "System.getenv直参照・System.out出力", "@ConfigurationProperties・SLF4J化"],
    ["MED", "java/typing", "BillingController:24", "Raw Map/List/Vector・Object・unchecked", "record DTO と型パラメータ化を徹底"],
    ["MED", "common/security_vulnerability", "BillingController:27", "未検証Mapに Long.parseLong 直呼出\n不正文字列で未処理500例外(CWE-20)", "@Valid ChargeRequest DTO導入と\n@RestControllerAdvice 400応答化"],
    ["LOW", "common/supply_chain", "pom.xml:1", "LICENSE/SECURITY/Dependabot/ignore欠落", "ガバナンス文書と自動更新設定を追加"],
    ["LOW", "java/code_quality", "BillingManager:31", "Javadoc欠落10箇所・obsoleteToken残存", "公開APIのJavadoc記述とタグ同期"],
]
tbl.draw_flexible(
    xy=(3, 162),
    column_widths=[10, 38, 23, 36, 33],
    row_heights=[7.2, 9.0, 10.2, 7.8, 7.8, 10.2, 8.4, 7.8, 7.8, 8.6, 7.8, 7.8, 7.8, 7.8, 7.8, 7.8, 8.4, 7.8, 7.8],
    data=rows,
)

save()
```
