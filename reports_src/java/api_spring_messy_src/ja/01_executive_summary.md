# 1. エグゼクティブサマリー

`legacy-billing` (`0.0.1-SNAPSHOT`) の総合健全性スコアは **23/100 (Grade D)** と診断された。`pom.xml` の Java 1.8 設定に対する非固定依存 `spring-boot-starter-web:LATEST`（動的解決された `4.2.0-RC1` の `class version 61.0` 衝突）、Java 11 専用 `java.net.http.HttpClient` の使用、`spring-tx` 未宣言の `@Transactional`、および未定義メソッド呼び出しという4重の要因でビルド自体が破綻している。さらに `LATEST` 非固定指定に起因する Trivy 静的範囲マッチ `CVE-2022-22965`（CVSS 9.8）、ハードコードされた API 秘密情報、無認証の `ANY /charge` エンドポイント、特権 `pull_request_target` CI など、本番稼働を阻害する緊急リスクが集中している。

```drawlib file=exec_radar_summary.png caption="7軸エンジニアリング健全性レーダーと強み・最優先リスク要約"
from drawlib.canvas import save, setup
from drawlib.charts.radar import RadarChart
from drawlib.icons import phosphor
from drawlib.smartarts import CardList
from drawlib.styles import Styles

setup(width=146, height=68, dpi=150)

radar = RadarChart(
    categories=[
        "アーキテクチャ",
        "コード品質",
        "型安全性",
        "テスト健全性",
        "依存関係",
        "セキュリティ",
        "ドキュメント",
    ],
    axis_line_style=Styles.Neutral,
    grid_style=Styles.NeutralThin,
    axis_text_style=Styles.DarkBold.patch(text_size=9.2),
    scale_text_style=Styles.Neutral.patch(text_size=8.2),
    background_style=Styles.Neutral.patch(shape_r=2.0),
    min_value=0.0,
    max_value=100.0,
    levels=5,
    radius=18.5,
    title="7軸健全性バランス (Overall: 23 / Grade D)",
    title_style=Styles.DarkBold.patch(text_size=10.2),
)
radar.add_series(
    "legacy-billing",
    [29, 22, 35, 14, 18, 17, 26],
    style=Styles.Danger,
    fill_alpha=0.28,
    line_width=2.2,
)
radar.add_series(
    "推奨基準(80)",
    [80, 80, 80, 80, 80, 80, 80],
    style=Styles.SuccessDashed,
    fill_alpha=0.04,
    line_width=1.4,
)
radar.draw(xy=(3, 4), width=66, height=60)

cards = CardList(
    style=Styles.Neutral,
    text_style=Styles.DarkBold.patch(text_size=9.5),
    description_style=Styles.Dark.patch(text_size=9.0),
    badge_shape="rounded_rect",
    badge_style=Styles.Primary,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.0),
    spacing=2.0,
)
cards.add(
    "強み1: 不変DTOモデル InvoiceRecord",
    "finalフィールドと正確なJavadocを備えた低リスク設計",
    badge_text="強み",
    style=Styles.PrimaryNeutral,
    badge_style=Styles.Success,
    icon=phosphor.check_circle,
    icon_style=Styles.Success,
)
cards.add(
    "強み2: SQLi/CMDi危険シンク・秘密ファイル0件",
    "CWE-78/89/502シンク0件・.env/秘密鍵コミットなし",
    badge_text="強み",
    style=Styles.PrimaryNeutral,
    badge_style=Styles.Success,
    icon=phosphor.shield_check,
    icon_style=Styles.Success,
)
cards.add(
    "課題1 [CRIT]: 4重のコンパイル破綻と検証停止",
    "LATEST(v61)×Java 8・HttpClient・spring-tx欠落",
    badge_text="P0",
    style=Styles.DangerNeutral,
    badge_style=Styles.Danger,
    icon=phosphor.x_circle,
    icon_style=Styles.Danger,
)
cards.add(
    "課題2 [CRIT]: LATEST範囲CVE・秘密鍵・無認証API",
    "CVE-2022-22965範囲一致・直書き鍵・ANY /charge",
    badge_text="P0",
    style=Styles.DangerNeutral,
    badge_style=Styles.Danger,
    icon=phosphor.lock_key,
    icon_style=Styles.Danger,
)
cards.draw(xy=(72, 4), width=71, height=60)

save()
```

## 7軸評価サマリーと主要診断結論

- **全7軸が基準値（80点）を大幅に下回る緊急改善プロファイル**: 相対的に高いのは型安全性（`35`）とアーキテクチャ（`29`）のみであり、テスト健全性（`14`）・セキュリティ（`17`）・依存関係（`18`）・コード品質（`22`）・ドキュメント（`26`）はいずれも深刻な技術的負債を抱えている。
- **ビルド不全とランタイム・DAST ペネトレーション検証の複合連鎖**: `pom.xml` の `spring-boot-starter-web:LATEST` 指定は、Trivy 静的解析では基準値 `0.0.0` 扱いで `CVE-2022-22965` の範囲マッチを引き起こす一方、Maven 実行時は Java 17+ 必須の `spring-boot-4.2.0-RC1.jar`（`class version 61.0` vs `52.0`）を解決してコンパイルを停止させる。さらに Java 11 API `java.net.http.*`・未宣言依存 `spring-tx`・未定義メソッド `currentPeriodLabel()` も内在しており、単体テスト・JaCoCo カバレッジ・起動確認（`RV-01〜RV-04`）のみならず、`.pni/pentests/examples/java/api_spring_messy/`（計4プローブファイル整備済み）を用いた隔離ループバック動的 Web ペネトレーション監査（`SEC-06 / web_pentest`：`status=error`, `15.74s`）までもが完全にブロックされている。

```drawlib file=exec_runtime_security_kpis.png caption="コンテナ動的検証・Trivyスキャン・動的Webペネトレーション監査のヘッドライン指標"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import KpiCards, Panel
from drawlib.styles import Styles

setup(width=146, height=60, dpi=150)

panel = Panel(
    "動的コンテナ検証・Trivy・Web Pentest (DAST) ヘッドライン",
    "Docker Maven Harness / Trivy 0.69.3 / Loopback DAST",
    style=Styles.Neutral,
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=11.0),
    description_style=Styles.White.patch(text_size=9.2),
    header_height=11.0,
)
panel.draw(xy=(3, 3), width=140, height=54)

kpis = KpiCards(
    style=Styles.White,
    metric_style=Styles.DangerBold.patch(text_size=13.0),
    text_style=Styles.DarkBold.patch(text_size=9.8),
    description_style=Styles.Neutral.patch(text_size=9.0),
    metric_width_ratio=0.36,
    spacing=3.0,
)
kpis.add(
    "FAILED",
    "コンテナ & Maven ビルド",
    "Dockerfile 1.5s / Harness 25.8s失敗",
    icon=phosphor.x_circle,
    accent_style=Styles.Danger,
    metric_style=Styles.DangerBold.patch(text_size=13.5),
    icon_style=Styles.Danger,
)
kpis.add(
    "ERROR / BLOCK",
    "単体テスト・網羅率・DAST",
    "JUnit未計測・DAST起動停止(15.7s)",
    icon=phosphor.warning,
    accent_style=Styles.Warning,
    metric_style=Styles.WarningBold.patch(text_size=12.2),
    icon_style=Styles.Warning,
)
kpis.add(
    "CRIT 1 件*",
    "非固定 LATEST 範囲マッチ",
    "CVE-2022-22965 (*0.0.0静的照合)",
    icon=phosphor.bug,
    accent_style=Styles.Danger,
    metric_style=Styles.DangerBold.patch(text_size=13.5),
    icon_style=Styles.Danger,
)
kpis.add(
    "1 / 3 / 1",
    "Secret / IaC不備 / 無認証API",
    "秘密鍵1・DS不備3・ANY /charge公開",
    icon=phosphor.shield_warning if hasattr(phosphor, "shield_warning") else phosphor.warning,
    accent_style=Styles.Danger,
    metric_style=Styles.DangerBold.patch(text_size=13.0),
    icon_style=Styles.Danger,
)
kpis.draw(xy=(7, 6), width=132, height=37.5, columns=2)

save()
```

## エグゼクティブ結論

- **強み (Verified Strengths)**: 標準 Maven ディレクトリ構成（`src/main/java`, `src/test/java`）と不変 DTO `InvoiceRecord` が維持されており、SQLi/CMDi 等の危険コードシンクや `.env`/秘密鍵ファイルの誤コミットは 0 件である。また `.pni/pentests/examples/java/api_spring_messy/` には `/charge` 固有脆弱性（`CWE-306` / `CWE-650` / `CWE-20`）とベースライン防御を検証する 4 本の自動 DAST プローブが整備済みであり、`187` LOC の小規模コードベースに対する短期再生と回帰検証が直ちに実行可能である。
- **最優先アクション (P0 Priorities)**: (1) `pom.xml` を Java 21 LTS + Spring Boot 3.4.x 固定 BOM（`spring-tx` 明示を含む）へ刷新して `CVE-2022-22965` 範囲マッチと4重のコンパイル不全を解消し、コンテナテストおよび `web_pentest` ライブ DAST をアンブロックすること、(2) `GatewayClient` のハードコード秘密情報除去・`build.yml` の `pull_request_target` 廃止・`/charge` の `@PostMapping` + 認証 + `@Valid` DTO バリデーション化を実施すること、(3) `BillingManager` / `BillingController` の共有可変状態・循環依存・`String ==` 比較・未定義メソッド・空 `catch` を修正することが最優先である。
