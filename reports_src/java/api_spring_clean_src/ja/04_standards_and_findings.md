# 4. 検査指標・ルール適合マトリクスと指摘一覧

本章では、`java_api_spring_clean` ワークフローで実行した全8監査ステップのスコア比較（弱点順）、評価対象となった全15エンジニアリングルールの適合判定マトリクス（`FAIL -> WARN -> PASS`）、および重要度順に正規化された全18件の指摘事項（`CRITICAL: 1` / `HIGH: 2` / `MEDIUM: 9` / `LOW: 6`）を網羅的に提示する。

```drawlib file=audit_dimensions_barchart.png caption="実行監査ステップ別スコア比較 (弱点順: Weakest -> Strongest 全8ステップ)"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.styles import Styles

setup(width=146, height=64, dpi=150)

chart = BarChart(
    axis_line_style=Styles.Neutral,
    grid_style=Styles.NeutralThin,
    axis_text_style=Styles.DarkBold.patch(text_size=8.5),
    value_text_style=Styles.DarkBold.patch(text_size=9.2),
    background_style=Styles.Neutral.patch(shape_r=2.0),
    categories=[
        "脆弱性・API\n(56 / D)",
        "JUnit監査\n(68 / C)",
        "動的DAST\n(72 / B)",
        "コンテナ実行\n(76 / B)",
        "12-Factor/PRR\n(78 / B)",
        "Java AST\n(81 / A)",
        "ビルド構造\n(84 / A)",
        "供給網統治\n(86 / A)",
    ],
    orientation="vertical",
    bar_width_ratio=0.58,
    bar_r=1.0,
    width=134,
    height=54,
    title="監査ステップ別 健全性スコア比較 (0 - 100点 / 全8ステップ)",
    title_style=Styles.DarkBold.patch(text_size=11.0),
)
chart.add_series("監査ステップスコア", [56, 68, 72, 76, 78, 81, 84, 86], style=Styles.Primary)
chart.draw(xy=(6, 5))

save()
```

## ルール適合マトリクス（全15ルール：`FAIL: 1` / `WARN: 10` / `PASS: 4`）

全評価ルールは最悪ステータス優先で集約されており、Maven 推移依存の CRITICAL `8` 件・HIGH `29` 件および状態変更 `POST` ルートの認証欠如（ライブ DAST でも `CWE-306` / `CWE-755` / `CWE-693` を実証）により `common/security_vulnerability` の1件が `FAIL` 判定となった。一方、`common/architecture`・`common/git_workflow`・`common/maintainability`・`java/typing` の4ルールは違反ゼロで `PASS` を達成している。

```drawlib file=rule_compliance_matrix.png caption="エンジニアリングルール適合マトリクス (FAIL -> WARN -> PASS 全15ルール)"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=118, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=9.0),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.4),
    border_style=Styles.NeutralThin,
)
rows = [
    ["判定", "ルールID", "代表評価ステップ", "決定的エビデンス要約"],
    ["FAIL", "common/security_vulnerability", "security_vulnerability_audit", "Maven CVE 75件(CRIT 8/HIGH 29)・DAST CWE-306/755/693検出"],
    ["WARN", "common/documentation", "repo_structure_audit", "Diataxis 4章構成済だが前提環境・defaultReorderBatch・応答例が未記載"],
    ["WARN", "common/production_readiness", "service_readiness_audit", "HTTP timeout 設定済だが Actuator 不在・ドメイン例外が 500 応答"],
    ["WARN", "common/runtime_verification", "container_runtime_audit", "ビルド/テスト/起動合格も JaCoCo 実測行 62.7%・分岐 50.0%"],
    ["WARN", "common/security", "java_ast_audit", "秘密漏洩0件だが SupplierRestClient:45 で手動 JSON 文字列連結"],
    ["WARN", "common/supply_chain", "repo_structure_audit", "SHA固定CI・Dependabot済だが mvnw/LICENSE スタブ・DS-0026 LOW"],
    ["WARN", "common/twelve_factor", "service_readiness_audit", "@ConfigurationProperties 集約済だが ConcurrentHashMap インメモリ保持"],
    ["WARN", "java/code_quality", "java_ast_audit", "Javadoc/import 100% だが InventoryService:65 で get/put 非アトミック更新"],
    ["WARN", "java/dependencies", "repo_structure_audit", "Java 21・BOM固定済だが Actuator / spring-boot-starter-test / JaCoCo 不在"],
    ["WARN", "java/frameworks/spring_boot", "java_ast_audit", "コンストラクタDI徹底だが @Validated と ProblemDetail 例外変換が欠落"],
    ["WARN", "java/testing", "java_test_audit", "@Test 2件のみ。SupplierRestClient・GET /{sku}・例外境界が未テスト"],
    ["PASS", "common/architecture", "java_ast_audit", "循環依存 0件・境界違反 0件。api -> service -> domain/client/config"],
    ["PASS", "common/git_workflow", "repo_structure_audit", ".gitignore 整備済み(target/, .idea/)、main PR 自動テストゲート稼働"],
    ["PASS", "common/maintainability", "java_ast_audit", "全7ファイル 180 LOC(最大43 LOC)、複雑関数・過剰引数・大域状態 0件"],
    ["PASS", "java/typing", "java_ast_audit", "型安全率 100.0%、Optional<StockItem>・総称型徹底、raw型・キャスト0件"],
]
tbl.draw_flexible(
    xy=(3, 115),
    column_widths=[12, 36, 32, 60],
    row_heights=[7.2] + [7.0] * 15,
    data=rows,
)

save()
```

## 重要度順 指摘事項一覧（全18件：`CRITICAL: 1` / `HIGH: 2` / `MEDIUM: 9` / `LOW: 6`）

すべての指摘は実在するリポジトリ相対パス・行番号・決定的ファクト（`.pni/pentests/` ライブ HTTP 応答を含む）に紐付けられている。特に `pom.xml`、`InventoryController.java`、`SupplierRestClient.java`、`InventoryService.java`、`Dockerfile` の5ファイルに重要指摘が集約されており、変更影響を局所化したまま迅速に改修できる。

```drawlib file=findings_evidence_table.png caption="重要度順 検出指摘一覧 (CRITICAL -> HIGH -> MEDIUM -> LOW 全18件)"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=168, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=8.6),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.0),
    border_style=Styles.NeutralThin,
)
rows = [
    ["重要度", "ルールID", "該当箇所", "検出事象・根拠", "推奨修正策"],
    ["CRITICAL", "common/\nsecurity_vulnerability", "pom.xml:10", "Spring Boot 3.3.4 推移依存に\nCRIT 8件・HIGH 29件(計75件)", "Spring Boot >=3.5.14 更新と\nTomcat 10.1.58 / Jackson固定"],
    ["HIGH", "common/\nsecurity_vulnerability", ".../api/\nInventoryController.java:52", "POST /{sku}/reserve が無認証\n(57行目に TODO(security))", "OAuth2 Resource Server 導入\n＋SKU @Pattern 形式検証"],
    ["HIGH", "java/testing", ".../inventory/\nInventoryServiceTest.java:27", "Stub上書きで HTTP クライアント・\nGET・例外パスのテストが0件", "HttpServer・@WebMvcTest・\nassertThrows テストを追加"],
    ["MEDIUM", "common/\nproduction_readiness", ".../api/\nInventoryController.java:58", "未知SKU・在庫不足の例外が\n未捕捉で HTTP 500 応答化", "@RestControllerAdvice で\n404/409 ProblemDetail 変換"],
    ["MEDIUM", "java/frameworks/\nspring_boot", ".../config/\nSupplierProperties.java:12", "@ConfigurationProperties に\n@Validated・制約注釈が不在", "@Validated と @NotBlank /\n@Positive で起動時検証"],
    ["MEDIUM", "java/code_quality", ".../service/\nInventoryService.java:65", "ConcurrentHashMap への get/put\n分離による同時引当競合リスク", "inventoryStore.compute(...)\nで引当計算をアトミック化"],
    ["MEDIUM", "common/supply_chain", "mvnw:3", "exec mvn のみの4行スタブで\nMaven版・SHA256が未固定", "mvn wrapper:wrapper で\nmaven-wrapper.properties 生成"],
    ["MEDIUM", "common/security", ".../client/\nSupplierRestClient.java:45", "文字列連結による手動 JSON 組立\nで JSON 構造注入リスク", "RestockRequest record を\nJackson ObjectMapper 直列化"],
    ["MEDIUM", "common/\nsecurity_vulnerability", "Dockerfile:7", "jammy JRE に HIGH 5件(OpenSSL,\nGnuPG)＋DS-0026 HEALTHCHECK欠落", "パッチ済 noble JRE 更新と\nHEALTHCHECK 命令の追加"],
    ["MEDIUM", "common/\nsecurity_vulnerability", ".../api/\nInventoryController.java:57", "[DAST CWE-306] 無認証 POST が\nフィルタ不在で reserveStock 到達", "Spring Security JWT 認可強制\n(未認証時は 401/403 拒否)"],
    ["MEDIUM", "common/\nsecurity_vulnerability", ".../service/\nInventoryService.java:64", "[DAST CWE-755] 未知SKU引当で\nIllegalArgumentException -> 500", "ExceptionHandler で未知SKUを\n404 ProblemDetail へ変換"],
    ["MEDIUM", "common/\nruntime_verification", ".../client/\nSupplierRestClient.java:44", "JaCoCo 行 62.7%・分岐 50.0%\n(Client 30.4% / API 62.5%)", "未実行行(Client 45-55行等)を\n網羅し jacoco:check 設定"],
    ["LOW", "common/twelve_factor", ".../service/\nInventoryService.java:23", "インメモリ ConcurrentHashMap\n直保持で複数レプリカ共有不可", "InventoryRepository 抽出と\nserver.shutdown=graceful 設定"],
    ["LOW", "common/supply_chain", "LICENSE:1", "Apache-2.0 見出し3行のみで\n許諾条項・免責全文が欠落", "SPDX 標準の Apache-2.0\nライセンス全文を記載"],
    ["LOW", "common/documentation", "README.md:14", "JDK 21/Docker 前提・一部設定・\ncurl リクエスト/応答例が未記載", "前提環境・全3設定項目・\nHTTP ステータス例を追記"],
    ["LOW", "common/\nsecurity_vulnerability", ".../api/\nInventoryController.java:18", "[DAST CWE-693] 応答ヘッダに\nX-Content-Type-Options 不在", "nosniff および no-store\nセキュリティヘッダを付与"],
    ["LOW", "common/supply_chain", "Dockerfile:7", "ベースイメージがタグ指定のみで\n@sha256 ダイジェスト未固定", "builder / JRE 双方のイメージを\n@sha256 ダイジェストで固定"],
    ["LOW", "java/testing", ".../inventory/\nReorderPolicyTest.java:1", "テスト2クラスがルート直下に置かれ\napi/service/domain と不一致", "src/test/java 配下のパッケージを\nsrc/main/java 階層に整合"],
]
tbl.draw_flexible(
    xy=(3, 165),
    column_widths=[14, 28, 30, 36, 32],
    row_heights=[7.2] + [8.6] * 18,
    data=rows,
)

save()
```
