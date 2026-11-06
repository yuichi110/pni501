# 6. PR 単位の実行 WBS と検証・受け入れゲート

5フェーズ・7変換軸の全作業を、1 PR あたりレビュー容易な粒度（`S`〜`M` サイズ）かつトポロジカル依存順の **計10 PR（`PR-01`〜`PR-10`）** に分割する。`PR-05`（Gateway 保安化）、`PR-06`（PostgreSQL + Flyway）、`PR-07`（Redis キャッシュ）はすべて `PR-04`（OpenRewrite 完了）のみに依存するため、**3並列で開発・レビューが可能**である。

```drawlib file=pr_wbs_execution_table.png caption="トポロジカル順序付き PR 実行 WBS (PR-01 - PR-10) と自動検証コマンド"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=136, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=8.2),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=8.8),
    border_style=Styles.NeutralThin,
)
rows = [
    ["PR / Phase", "規模 / 種別", "PR タイトルと主要変更内容", "依存 PR", "必須検証コマンド (CI Gate)"],
    [
        "PR-01\nPhase 0",
        "S / Manual",
        "最小グリーンビルド・DAST起動復旧と\n/charge Golden Master 特性テスト追加",
        "なし",
        "mvn clean test (server_booted=true)",
    ],
    [
        "PR-02\nPhase 1 (W1)",
        "S / Manual",
        "Wave 1 ドメインモデル抽出\n(Invoice record / Money / java.time)",
        "PR-01",
        "mvn test -Dtest=*Domain*,*Invoice*",
    ],
    [
        "PR-03\nPhase 1 (W3)",
        "M / Manual",
        "Controller<->Manager 循環依存切断と\nClean Arch Port / UseCase / ArchUnit 導入",
        "PR-02",
        "mvn test (SCC cycle = 0 & ArchUnit)",
    ],
    [
        "PR-04\nPhase 2 (W1)",
        "M / Codemod",
        "OpenRewrite 専用 PR: Java 21 LTS +\nSpring Boot 3.4 (jakarta.*) + JUnit 5",
        "PR-03",
        "mvn rewrite:run && mvn clean test",
    ],
    [
        "PR-05\nPhase 2 (W2)",
        "S / Manual",
        "HttpPaymentGatewayAdapter 実装\n(@ConfigurationProperties + Timeout 3s/5s)",
        "PR-04",
        "mvn test -Dtest=*Gateway* (WireMock)",
    ],
    [
        "PR-06\nPhase 2 (W2)",
        "M / Manual",
        "PostgreSQL 16 + Spring Data JPA +\nFlyway V1 永続化アダプタ実装",
        "PR-04",
        "mvn verify -Dtest=*JpaBillingAudit*",
    ],
    [
        "PR-07\nPhase 2 (W2)",
        "S / Manual",
        "Redis 7 キャッシュアダプタ (TTL 15m) と\nstatic INVOICE_CACHE の完全撤去",
        "PR-04",
        "mvn verify -Dtest=*RedisInvoiceCache*",
    ],
    [
        "PR-08\nPhase 3 (W4)",
        "M / Manual",
        "BillingController ステートレス化・@Valid\nDTO・Spring Security & DAST CWE 防御",
        "PR-05,06,07",
        "mvn test && pni ... web_pentest (PASS)",
    ],
    [
        "PR-09\nPhase 3 (W3)",
        "S / Manual",
        "PO 合意済み Decision Log (DEC-01〜04)\n税率 Enum 判定・リトライ規約反映",
        "PR-08",
        "mvn clean verify jacoco:check (>=85%)",
    ],
    [
        "PR-10\nPhase 4 (W4)",
        "S / Hybrid",
        "Temurin 21 非 root マルチステージ Docker\n・CI 最小権限化・OpenAPI/README 整備",
        "PR-09",
        "docker build && trivy && web_pentest",
    ],
]
tbl.draw_flexible(
    xy=(3, 133),
    column_widths=[20, 18, 48, 17, 37],
    row_heights=[8.0, 11.8, 11.8, 12.2, 12.2, 12.2, 12.2, 12.2, 12.2, 12.2, 12.2],
    data=rows,
)

save()
```

## フェーズ完了受け入れ基準（Exit Criteria）とロールバック戦略

- **Phase 0 完了条件**: `mvn clean test` が Exit Code 0 で完走し、隔離ループバック DAST（`web_pentest`：`server_booted=true`）が起動可能になり、`/charge` の現行 JSON 入出力スナップショットテストが 100% PASS すること。
- **Phase 1 完了条件**: AST 内部 import グラフの循環依存が `0` 件となり、ArchUnit テストにより `domain` / `usecase` 層のフレームワーク非依存が CI 保証されること。
- **Phase 2 完了条件**: Testcontainers 上の PostgreSQL 16（Flyway V1 適用）および Redis 7（TTL 15分失効確認）統合テストが全件 PASS し、ソース内ハードコード秘密鍵および `static Map` が `0` 件であること。
- **Phase 3 & Phase 4 最終受け入れゲート**: JaCoCo カバレッジ **85% 以上**、`.pni/pentests/examples/java/api_spring_messy/` のライブ DAST ペネトレーション検証が **全件 PASS（`failed_probes=0`：無認証 `401/403` `CWE-306`・`PUT /charge -> 405` `CWE-650`・不正数値 `-> 400` `CWE-20`・`nosniff` ヘッダ `CWE-693`）**、Trivy スキャンで **`CRITICAL` / `HIGH` 指摘 0 件**、および PNI 健全性再診断（`java_api_spring_messy`）で **Grade A（85点以上）** を達成すること。万一デプロイ後に異常が検知された場合は、イミュータブルなコンテナタグ切り戻しと Flyway 後方互換スキーマ維持により無停止ロールバックを実行する。
