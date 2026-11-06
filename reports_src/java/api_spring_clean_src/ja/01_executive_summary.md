# 1. エグゼクティブサマリー

`inventory-service` (`v1.1.0`) の総合健全性スコアは **78 / 100 (Grade B)** と評価された。Java 21 `record` とコンストラクタ DI に基づく 5パッケージ・180 LOC の明快な非循環レイヤード設計、ならびに Javadoc・ジェネリクス型安全・import 衛生すべて `100.0%` という高い静的品質を備え、マルチステージ Docker ビルド・オフライン JUnit 5 単体テスト・Spring Boot 起動検証、および隔離ループバック環境に対する動的 Web ペネトレーションテスト（`web_pentest`: 全 `16` プローブ中 `12` PASS・CRITICAL/HIGH 脆弱性 `0` 件）に合格している。一方で、`spring-boot-starter-parent:3.3.4` が引き込む推移依存の既知脆弱性（CRITICAL `8` 件・HIGH `29` 件）、ライブ DAST プローブでも実証された状態変更 API `POST /api/v1/items/{sku}/reserve` の無認証実行（`CWE-306`）および未知 SKU 時の未処理 `HTTP 500`（`CWE-755`）、ならびに JaCoCo 実測行網羅率 `62.7%`（分岐 `50.0%`）が最優先の解消課題である。

```drawlib file=exec_radar_summary.png caption="7軸エンジニアリング健全性レーダーと強み・最優先リスク要約"
from drawlib.canvas import save, setup
from drawlib.charts.radar import RadarChart
from drawlib.icons import phosphor
from drawlib.smartarts import CardList
from drawlib.styles import Styles

setup(width=146, height=66, dpi=150)

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
    axis_text_style=Styles.DarkBold.patch(text_size=9.5),
    scale_text_style=Styles.Neutral.patch(text_size=8.5),
    background_style=Styles.Neutral.patch(shape_r=2.0),
    min_value=0.0,
    max_value=100.0,
    levels=5,
    radius=19.0,
    title="7軸健全性バランス (Overall: 78 / B)",
    title_style=Styles.DarkBold.patch(text_size=10.5),
)
radar.add_series(
    "inventory-service",
    [86, 82, 92, 66, 74, 58, 86],
    style=Styles.Primary,
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
radar.draw(xy=(3, 4), width=66, height=58)

cards = CardList(
    style=Styles.Neutral,
    text_style=Styles.DarkBold.patch(text_size=9.8),
    description_style=Styles.Dark.patch(text_size=9.5),
    badge_shape="rounded_rect",
    badge_style=Styles.Primary,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.5),
    spacing=2.2,
)
cards.add(
    "強み1: 純粋ドメイン分離と型安全 (92点)",
    "循環依存0・Java 21 record・Javadoc/型 100%",
    badge_text="強み",
    style=Styles.PrimaryNeutral,
    badge_style=Styles.Success,
    icon=phosphor.stack,
    icon_style=Styles.Success,
)
cards.add(
    "強み2: DAST重大脆弱性0件・堅牢なCI統治",
    "XSS/SQLi/Traversal防御済・SHA固定CI・非root",
    badge_text="強み",
    style=Styles.PrimaryNeutral,
    badge_style=Styles.Success,
    icon=phosphor.shield_check,
    icon_style=Styles.Success,
)
cards.add(
    "課題1 [CRIT]: Spring 3.3.4 推移CVE 75件",
    "Tomcat 10.1.30 / WebMVC / Jackson にCRIT 8件",
    badge_text="P0",
    style=Styles.DangerNeutral,
    badge_style=Styles.Danger,
    icon=phosphor.lock_key,
    icon_style=Styles.Danger,
)
cards.add(
    "課題2 [HIGH]: POST無認証(CWE-306)と網羅62.7%",
    "DASTで無認証500(CWE-755)実証・Client 30.4%",
    badge_text="P0",
    style=Styles.WarningNeutral,
    badge_style=Styles.Warning,
    icon=phosphor.bug,
    icon_style=Styles.Warning,
)
cards.draw(xy=(72, 4), width=71, height=58)

save()
```

## 7軸評価サマリーと主要診断結論

- **高評価領域（型安全性 `92`・アーキテクチャ `86`・ドキュメント `86`・コード品質 `82`）**: `api` -> `service` -> `domain` + `client` + `config` の単方向 DAG が徹底され、`StockItem`・`ReorderPolicy` のドメイン層は Spring フレームワーク依存を一切持たない。GitHub Actions の 40文字 SHA ピン留め（`contents: read`）、Dependabot 週次更新、`SECURITY.md`、ハードコード秘密情報ゼロ、危険な CWE コードシンクゼロに加え、`.pni/pentests/` によるライブ HTTP 侵入プローブでも不正数値の `400` 拒否（`CWE-20`）と XSS / SQLi / トラバーサル耐性が実証された。
- **優先改善領域（セキュリティ `58`・テスト健全性 `66`・依存関係 `74`）**: 全8監査ステップでは `security_vulnerability_audit` (`56 / D`)、`java_test_audit` (`68 / C`)、`web_penetration_audit` (`72 / B`)、`container_runtime_audit` (`76 / B`) が相対的な弱点となった。`pom.xml` の Spring Boot `3.3.4`（Tomcat `10.1.30`、Spring WebMVC `6.1.13`、Jackson `2.17.2`）更新、予約 `POST` エンドポイントへの OAuth2 JWT 認可導入と未知 SKU 例外の `404 ProblemDetail` 変換（`CWE-306` / `CWE-755`）、`X-Content-Type-Options: nosniff` ヘッダ付与（`CWE-693`）、`ConcurrentHashMap` のアトミック更新化、および HTTP クライアント・異常系のテスト拡充が急務である。

```drawlib file=exec_runtime_security_kpis.png caption="コンテナ動的検証・Trivyスキャン・Webペネトレーション検証の主要指標"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import KpiCards, Panel
from drawlib.styles import Styles

setup(width=146, height=60, dpi=150)

panel = Panel(
    "動的コンテナ検証・Trivy 監査 & Web ペネトレーション (DAST) ヘッドライン",
    "Docker Java 21 / JaCoCo 0.8.12 / Trivy 0.69.3 / httpx DAST",
    style=Styles.Neutral,
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=10.6),
    description_style=Styles.White.patch(text_size=9.2),
    header_height=11.0,
)
panel.draw(xy=(3, 3), width=140, height=54)

kpis = KpiCards(
    style=Styles.White,
    metric_style=Styles.PrimaryBold.patch(text_size=13.5),
    text_style=Styles.DarkBold.patch(text_size=10.0),
    description_style=Styles.Neutral.patch(text_size=9.3),
    metric_width_ratio=0.35,
    spacing=3.0,
)
kpis.add(
    "2 / 2 PASS",
    "隔離オフライン JUnit 5",
    "Docker 44.4s・テスト11.0s・起動4.5s合格",
    icon=phosphor.check_circle,
    accent_style=Styles.Success,
    metric_style=Styles.SuccessBold.patch(text_size=13.5),
    icon_style=Styles.Success,
)
kpis.add(
    "62.7%",
    "JaCoCo 行網羅率 (分岐 50.0%)",
    "42/67行 (Client 30.4% / API 62.5%)",
    icon=phosphor.chart_bar,
    accent_style=Styles.Warning,
    metric_style=Styles.WarningBold.patch(text_size=14.0),
    icon_style=Styles.Warning,
)
kpis.add(
    "8 / 29 件",
    "Maven App CRIT / HIGH CVE",
    "計75件 (Tomcat 10.1.30 / Jackson 2.17)",
    icon=phosphor.package,
    accent_style=Styles.Danger,
    metric_style=Styles.DangerBold.patch(text_size=13.5),
    icon_style=Styles.Danger,
)
kpis.add(
    "12 / 16 PASS",
    "動的 DAST (CRIT/HIGH 0件)",
    "CWE-306/755(MED 2)・CWE-693(LOW 1)",
    icon=phosphor.shield_check,
    accent_style=Styles.Primary,
    metric_style=Styles.PrimaryBold.patch(text_size=13.0),
    icon_style=Styles.Primary,
)
kpis.draw(xy=(7, 6), width=132, height=37.5, columns=2)

save()
```

## エグゼクティブ結論

- **強み (Verified Strengths)**: コンストラクタ DI と Java 21 `record` による高い凝集度、明示的な HTTP 接続・読取タイムアウト（`SupplierRestClient`）、非 root コンテナ実行（`USER spring`, `UID 10001`）とループバックバインド（`127.0.0.1`）、ライブ DAST で確認された型変換バリデーション（`quantity=not-an-int -> 400`）とインジェクション耐性、および Diátaxis 4象限に沿った簡潔なドキュメント構成が確認された。
- **優先対応 (Top Actionable Priorities)**: **P0** で Spring Boot BOM / Tomcat / Jackson のパッチ版更新と `POST /api/v1/items/{sku}/reserve` の OAuth2 JWT スコープ保護を実施し、**P1** で `@RestControllerAdvice` (`ProblemDetail` による未知 SKU `404` / 在庫不足 `409` 変換)・Actuator `/actuator/health` 導入、`SupplierRestClient` の Jackson シリアライズ化と `InventoryService` の `compute(...)` アトミック化、および JaCoCo 網羅率 `85%` 以上へのテスト拡充、さらに **P2** で `X-Content-Type-Options: nosniff` ヘッダ付与と供給網・文書整備を行うことで、本番外部公開に耐える Grade A 水準へ到達できる。
