# 1. エグゼクティブサマリとマルチ軸移行戦略

`legacy-billing` は現状 PNI 健全性診断（`wf-da941741`）で **23 / 100（Grade D・指摘24件）** と評価されており、`pom.xml` の Java 1.8 指定と `spring-boot-starter-web:LATEST`（Spring 6 / class file v61）および Java 11 `HttpClient` の衝突によるビルド崩壊（これに起因して `SEC-06 web_pentest` 隔離ループバック DAST も `status=error` で起動停止）、`BillingManager <-> BillingController` の双方向循環依存、プロセス内 `static Map INVOICE_CACHE`、および秘密鍵ハードコード・無認証 `/charge` 境界を抱えている。本計画では「一括ビッグバン書き換え」を避け、**7つの移行軸**を **Phase 0〜Phase 4 の5段階ゲート**へ分解して安全に移行する。

```drawlib file=multi_axis_gap_matrix.png caption="As-Is -> To-Be マルチ軸ギャップ分析マトリクス (全7変換軸)"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=112, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=8.6),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.0),
    border_style=Styles.NeutralThin,
)
rows = [
    ["変換軸", "As-Is (現状の課題)", "To-Be (目標仕様)", "移行アプローチ / リスク"],
    [
        "言語・ランタイム",
        "Java 1.8 指定 + Java 11 API 混在\nDate / SimpleDateFormat / Vector",
        "Java 21 LTS 統一\n不変 record / java.time (UTC)",
        "Phase 0 整合復旧 → Phase 2\nOpenRewrite 自動変換 [HIGH]",
    ],
    [
        "フレームワーク",
        "Spring Boot LATEST (javax.*)\nフィールド DI / JUnit 4 無検証",
        "Spring Boot 3.4 BOM (jakarta.*)\nコンストラクタ DI / JUnit 5",
        "OpenRewrite 専用 PR 分離\nMockMvc + JaCoCo 検証 [HIGH]",
    ],
    [
        "設計思想・構造",
        "Controller <-> Manager 循環依存\n計算・I/O・状態が単一クラス密結合",
        "Clean Architecture 4層分離\ndomain / port / usecase / adapter",
        "Phase 1 逆参照切断 → Wave 順\nArchUnit で依存方向強制 [CRIT]",
    ],
    [
        "DB・永続化",
        "spring-tx 欠落・無効 @Transactional\n監査ログが標準出力のみで揮発",
        "PostgreSQL 16 + Spring Data JPA\nFlyway V1 バージョン管理 DDL",
        "BillingAuditRepositoryPort 抽出\nTestcontainers PG16 検証 [HIGH]",
    ],
    [
        "キャッシュ・状態",
        "static raw Map INVOICE_CACHE\nController 可変フィールド channel",
        "Redis 7 (TTL 15分・JSON 形式)\n完全ステートレス Controller",
        "InvoiceCachePort アダプタ化\nリクエスト DTO スコープ化 [HIGH]",
    ],
    [
        "認証・通信保安",
        "GATEWAY_SECRET 直書き・Timeout 無\n/charge CWE-306/650/20・DAST停止",
        "@ConfigurationProperties 外部注入\nPOST + Security + DAST全件PASS",
        "Phase 2 Outbound 保安化 →\nPhase 3 DAST プローブ検証 [CRIT]",
    ],
    [
        "コンテナ・CI",
        "openjdk:8 root 実行・Healthcheck 無\npull_request_target 特権 CI",
        "Temurin 21 マルチステージ非 root\n最小権限 pull_request + SHA 固定",
        "Phase 4 インフラ刷新 + Trivy /\nweb_pentest ゼロ違反証明 [MED]",
    ],
]
tbl.draw_flexible(
    xy=(3, 109),
    column_widths=[24, 42, 40, 34],
    row_heights=[8.0, 13.5, 13.5, 14.0, 13.5, 13.5, 14.0, 13.5],
    data=rows,
)

save()
```

## 5フェーズ段階的実行ゲート（Phase 0 → Phase 4）

構造リファクタリング・機械的アップグレード・仕様バグ修正を同一 PR に混在させると、回帰発生時の原因切り分けが不可能になる。そのため以下の **5段階ゲート方式** を厳守する。

```drawlib file=five_phase_roadmap.png caption="5フェーズ段階的マイグレーション実行ゲート (Phase 0 -> Phase 4)"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import Roadmap
from drawlib.styles import Styles

setup(width=146, height=62, dpi=150)

rm = Roadmap(
    style=Styles.Neutral,
    text_style=Styles.DarkBold.patch(text_size=9.2),
    description_style=Styles.Dark.patch(text_size=8.3),
    spine_style=Styles.PrimaryBold,
    badge_style=Styles.Primary,
    badge_text_style=Styles.WhiteBold.patch(text_size=8.8),
    direction="horizontal",
    spacing=2.2,
)
rm.add(
    "P0 特性テスト固定",
    "最小ビルド・DAST起動\n/charge 契約固定",
    badge_text="Phase 0",
    style=Styles.PrimaryNeutral,
    badge_style=Styles.Primary,
    icon=phosphor.check_circle,
    icon_style=Styles.Primary,
)
rm.add(
    "P1 循環切断・Port",
    "SCC 逆参照の解消\nClean Arch 境界抽出",
    badge_text="Phase 1",
    style=Styles.PrimaryNeutral,
    badge_style=Styles.Primary,
    icon=phosphor.git_Diff if hasattr(phosphor, "git_Diff") else phosphor.git_branch,
    icon_style=Styles.Primary,
)
rm.add(
    "P2 基盤刷新",
    "Java 21 / Boot 3.4\nPG16 & Redis 7 実装",
    badge_text="Phase 2",
    style=Styles.WarningNeutral,
    badge_style=Styles.Warning,
    icon=phosphor.database,
    icon_style=Styles.Warning,
)
rm.add(
    "P3 型検証・DAST合格",
    "@Valid DTO + 認証\nCWEプローブ全PASS",
    badge_text="Phase 3",
    style=Styles.WarningNeutral,
    badge_style=Styles.Warning,
    icon=phosphor.lock_key,
    icon_style=Styles.Warning,
)
rm.add(
    "P4 コンテナ・完遂",
    "Temurin 21 非root\nTrivy/DAST/PNI 85+",
    badge_text="Phase 4",
    style=Styles.SuccessNeutral,
    badge_style=Styles.Success,
    icon=phosphor.rocket_launch,
    icon_style=Styles.Success,
)
rm.draw(xy=(3, 5), width=140, height=52)

save()
```

- **Phase 0（最小グリーンビルド復旧 & Golden Master 固定）**: ロジックには触れず `pom.xml` のバージョン衝突を最小解消して隔離ループバック起動（`web_pentest` 実行基盤）をアンブロックし、`POST /charge` の現行 JSON 挙動をスナップショットテストで固定する。
- **Phase 1（循環依存切断 & Domain / Port 抽出）**: 挙動 100% 保全のまま `BillingManager -> BillingController` 逆参照を切断し、フレームワーク非依存の `domain` / `port` / `usecase` を確立する。
- **Phase 2（OpenRewrite 機械変換 & PostgreSQL / Redis アダプタ実装）**: Codemod 専用 PR（Java 21 / Spring Boot 3.4 / JUnit 5）を先行マージ後、JPA + Flyway・Redis TTL・Timeout 付き Gateway アダプタを実装する。
- **Phase 3（型安全 DTO・認証保護・DAST 合格 & PO 合意仕様反映）**: ステークホルダー承認済みの Decision Log（税率 `.equals()` 比較・リトライ規約等）と `@PostMapping("/charge")` + `@Valid` DTO + Spring Security を導入し、`.pni/pentests/examples/java/api_spring_messy/` の `CWE-306 / CWE-650 / CWE-20 / CWE-693` プローブを全件 PASS させる。
- **Phase 4（コンテナ・CI ハードニング & 最終監査）**: `eclipse-temurin:21` 非 root マルチステージ化と GitHub Actions 最小権限化を完了し、Trivy・ライブ DAST（`web_pentest`）・PNI 最終ゲート（Grade A `85+`）を通過させる。
