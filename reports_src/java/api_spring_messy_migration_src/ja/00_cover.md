# PNI マイグレーション実行計画レポート

本レポートは、レガシー請求処理 Spring Boot API サービス **`legacy-billing` (`0.0.1-SNAPSHOT` / ベース監査 `wf-da941741`: 23/100 Grade D)** に対する PNI 移行設計ワークフロー `java_api_spring_messy_migration`（トポロジカル依存 Wave 抽出・暗黙 API 契約復元・状態/DB/HTTP 境界タッチポイント解析・OpenRewrite レシピ照合・仕様/バグ境界分離・ライブ DAST 検証ゲート設計）に基づき策定された、**Java 21 LTS + Spring Boot 3.4 + PostgreSQL 16 + Redis 7 + Clean Architecture** への段階的移行ブループリントである。

```drawlib file=cover_migration_scorecard.png caption="legacy-billing マルチ軸マイグレーション実行計画サマリカード"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import KpiCards, Panel
from drawlib.styles import Styles

setup(width=146, height=66, dpi=150)

panel = Panel(
    "legacy-billing マイグレーション計画",
    "Run: wf-0bb3750d (Base: wf-da941741) | Phased PR",
    style=Styles.Neutral,
    header_style=Styles.Primary,
    text_style=Styles.WhiteBold.patch(text_size=10.8),
    description_style=Styles.White.patch(text_size=9.0),
    icon=phosphor.rocket_launch,
    icon_style=Styles.White,
    header_height=12.0,
)
panel.draw(xy=(3, 3), width=140, height=60)

kpis = KpiCards(
    style=Styles.White,
    metric_style=Styles.PrimaryBold.patch(text_size=13.5),
    text_style=Styles.DarkBold.patch(text_size=10.2),
    description_style=Styles.Neutral.patch(text_size=9.0),
    accent_style=Styles.Primary,
    icon_style=Styles.Primary,
    metric_width_ratio=0.36,
    spacing=3.5,
)
kpis.add(
    "7 変換軸",
    "マルチ軸モダナイゼーション",
    "Java 21 / Boot 3.4 / PG16 / Redis 7",
    icon=phosphor.arrows_clockwise,
    accent_style=Styles.Primary,
    metric_style=Styles.PrimaryBold.patch(text_size=13.5),
)
kpis.add(
    "4 Layers",
    "Clean Architecture 境界",
    "domain / port / usecase / adapter",
    icon=phosphor.stack,
    accent_style=Styles.Success,
    metric_style=Styles.SuccessBold.patch(text_size=13.5),
    icon_style=Styles.Success,
)
kpis.add(
    "5 Gates",
    "段階的フェーズ検証 (P0-P4)",
    "特性テスト固定 → サイクル切断 → DAST合格",
    icon=phosphor.shield_check,
    accent_style=Styles.Primary,
    metric_style=Styles.PrimaryBold.patch(text_size=13.5),
)
kpis.add(
    "10 PRs",
    "実行可能 WBS & 4 合意論点",
    "OpenRewrite 分離 + PO 承認ゲート",
    icon=phosphor.git_pull_request,
    accent_style=Styles.Warning,
    metric_style=Styles.WarningBold.patch(text_size=13.5),
    icon_style=Styles.Warning,
)
kpis.draw(xy=(7, 6.5), width=132, height=41, columns=2)

save()
```

## 確定済み前提条件（Confirmed Assumptions）と非目標（Non-Goals）

- **移行モード / ロールアウト戦略**: `architectural_restructure` / **`phased_pr`（単一リポジトリ段階的 PR 方式）**・外部 API 互換ポリシー `strict`・仕様曖昧性ポリシー `ask_human`
- **確定済み技術スタック**: **Java 21 LTS** + **Spring Boot 3.4.x BOM**（Jakarta EE 10 / JUnit 5 Jupiter / JaCoCo）+ **PostgreSQL 16**（Spring Data JPA + Flyway）+ **Redis 7**（TTL 15分キャッシュ外部化）+ **Clean Architecture**（`domain` / `port` / `usecase` / `adapter`）
- **確定済み外部契約 & DAST ガードレール**: `POST /charge` の既存 JSON キー（`customerId`, `amountCents`, `billedCents`）を厳格維持し、`String ==` 税率判定・`100L` 固定リトライ・`controllerPing` 診断キー等の Hyrum の法則リスクは Phase 3 前にステークホルダー合意を経る。また `.pni/pentests/examples/java/api_spring_messy/` の 4 プローブスイート（`CWE-306 / CWE-650 / CWE-20 / CWE-693`）全件 PASS を Phase 3/4 の必須セキュリティゲートとする。
- **非目標（Non-Goals）**: マイクロサービス分割、Kafka / RabbitMQ 等の非同期メッセージング基盤導入、および外部決済プロトコル自体の刷新は本移行スコープ外とする（単一デプロイ可能な Maven アーティファクトを維持）。
