# PNI マイグレーション実行計画: `legacy-billing`

**対象リポジトリ**: `examples/java/api_spring_messy` (`java_api_spring_messy_migration`)  
**移行ターゲット**: Java 1.8 / バージョン未固定 Spring Boot / 循環依存モノリス -> **Java 21 LTS + Spring Boot 3.4 + PostgreSQL 16 + Redis 7 + Clean Architecture**

```drawlib align=center code=hide file=cover_migration_banner.png caption="legacy-billing 向け PNI501 マイグレーション実行計画バナー（ベースライン 66/100 グレード C -> Java 21 + Spring Boot 3.4 + Clean Architecture）"
from drawlib.canvas import save, setup
from drawlib.shapes import rectangle
from drawlib.smartarts import KpiCards, Panel
from drawlib.styles import Colors, Styles
from drawlib.text import text
from drawlib.utils import draw_pni_logo

setup(width=146, height=72, dpi=150)

# Outer cover frame with Google-styled dark blue header band
frame = Panel(
    "",
    style=Styles.Neutral.patch(shape_r=2.5),
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=13.5),
    header_variant="filled",
    header_height=15.0,
)
frame.draw((4, 4), width=138, height=64)

# Header title & subtitle leaving right zone open for PNI501 emblem
text(
    (8.5, 63.2),
    "PNI501 Migration Execution Plan",
    style=Styles.WhiteBold.patch(text_size=13.5, halign="left"),
)
text(
    (8.5, 57.2),
    "legacy-billing  |  based_on: java_api_spring_messy (wf-8177454c)  |  Run: wf-b1c19b56",
    style=Styles.White.patch(text_size=9.5, halign="left"),
)

# Official PNI501 emblem on dark primary header
draw_pni_logo((134.5, 60.5), width=9.0, dark=True)

# Left Hero Target Stack & Baseline-to-Target Card
hero_style = Styles.PrimaryNeutral.patch(
    shape_r=2.5,
    shape_line_color=Colors.GoogleBlue,
    shape_line_width=1.8,
)
rectangle((26.5, 29.0), width=37.0, height=40.0, style=hero_style)
rectangle(
    (26.5, 44.0),
    width=30.0,
    height=5.2,
    style=Styles.PrimaryFlat.patch(shape_r=2.0),
    text="TARGET STACK",
    text_style=Styles.WhiteBold.patch(text_size=9.5),
)
text((26.5, 35.8), "Java 21 LTS", style=Styles.DarkBold.patch(text_size=14.0))
text((26.5, 29.6), "Spring Boot 3.4", style=Styles.PrimaryBold.patch(text_size=12.0))
text(
    (26.5, 22.8),
    "PostgreSQL 16 + Redis 7\nClean Architecture",
    style=Styles.DarkBold.patch(text_size=9.8),
)
text(
    (26.5, 13.8),
    "Baseline: 66/100 (Grade C)\nTarget Gate: >= 85 (Grade A/S)",
    style=Styles.Muted.patch(text_size=9.5),
)

# Right 2x2 executive migration KPIs
kpis = KpiCards(
    style=Styles.Neutral.patch(shape_r=2.0),
    metric_style=Styles.DarkBold.patch(text_size=13.5),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Muted.patch(text_size=9.5),
    accent_style=Styles.PrimaryFlat,
    accent_position="left_pill",
    metric_layout="top_stack",
    spacing=2.8,
)
kpis.add(
    "7 Axes",
    "Multi-Axis Gap Scope",
    "4 CRITICAL | 3 HIGH risk axes",
    style=Styles.DangerNeutral.patch(shape_r=2.0),
    metric_style=Styles.DangerBold.patch(text_size=13.5),
    accent_style=Styles.DangerFlat,
)
kpis.add(
    "4 Waves / 8 PRs",
    "Phased PR Execution",
    "1 codemod | 1 hybrid | 6 manual",
    style=Styles.PrimaryNeutral.patch(shape_r=2.0),
    metric_style=Styles.PrimaryBold.patch(text_size=13.0),
    accent_style=Styles.PrimaryFlat,
)
kpis.add(
    "4 Decisions",
    "Spec vs. Bug Log",
    "ask_human gate prior to Phase 3",
    style=Styles.WarningNeutral.patch(shape_r=2.0),
    metric_style=Styles.WarningBold.patch(text_size=13.0),
    accent_style=Styles.WarningFlat,
)
kpis.add(
    "strict / phased_pr",
    "Compatibility & Strategy",
    "POST /charge JSON contract locked",
    style=Styles.Neutral.patch(shape_r=2.0),
    metric_style=Styles.DarkBold.patch(text_size=12.0),
    accent_style=Styles.SuccessFlat,
)
kpis.draw((48.5, 9.0), width=89.5, height=40.0, columns=2)

save()
```

---

## マイグレーション計画メタデータ・証跡プロベナンス

| 項目 | 値 |
| :--- | :--- |
| **プロジェクト名** | `legacy-billing` (`com.example:legacy-billing:0.0.1-SNAPSHOT`) |
| **対象ルート** | `examples/java/api_spring_messy`（`java`、本番コード 6 ファイル / テスト 1 ファイル） |
| **ワークフロー ID・実行 ID** | `java_api_spring_messy_migration`（`wf-b1c19b56`、`category=migration`、`scope=repo`） |
| **前提ベースライン監査 (`based_on`)** | `java_api_spring_messy`（`wf-8177454c` — **66 / 100・グレード C**、ルール合格 0/16、Docker Maven ビルド失敗） |
| **計画生成日時 (UTC)** | `2026-11-22T11:57:23.102522+00:00`（`main@d1e02277 (dirty)`） |
| **目標アーキテクチャ** | Clean Architecture（`domain` / `port` / `usecase` / `adapter.in.web` / `adapter.out.{gateway,persistence,cache}`） |
| **目標ランタイム・技術スタック** | Java 21 LTS、Spring Boot 3.4.x BOM（Jakarta EE 10）、PostgreSQL 16（JPA + Flyway）、Redis 7（TTL 付き）、Spring `RestClient`、JUnit 5 + Mockito + JaCoCo |
| **変換モード (`transformation_mode`)** | `architectural_restructure` |
| **実行戦略 (`migration_strategy`)** | `phased_pr` — **5 段階ゲート（`Phase 0`..`Phase 4`）**、**4 トポロジカル Wave**、**全 8 PR（`PR-01`..`PR-08`）** |
| **API 互換性・バグ方針** | `POST /charge` の外部 JSON 契約（`customerId`, `amountCents`, `billedCents`）を厳格維持（`strict`）、曖昧な挙動は 4 件の意思決定ログ（`ask_human`）で Phase 3 前に合意 |
| **自動コードモッド基盤** | OpenRewrite（`UpgradeToJava21`, `UpgradeSpringBoot_3_4`, `JUnit4to5Migration`） |
| **最終受入ゲート** | Maven + 非 root Temurin 21 Docker ビルド成功、CRITICAL/HIGH の SCA/IaC/DAST 検出 0 件、PNI 総合スコア **85 以上（グレード A/S）** |

> **ガバナンスおよび機密保護について**: 本マイグレーション実行計画は、PNI501 Workflow v2 の下でベースライン監査 `wf-8177454c`（`java_api_spring_messy`）から直接連携生成されたものです。ソースコード上で検出された認証情報リテラル（`GatewayClient.GATEWAY_SECRET` 等）はすべて `<REDACTED_SECRET>` としてマスク済みであり、既存の曖昧な挙動は Phase 0 ゴールデンマスターテストで固定し、Phase 3 のステークホルダー承認まで暗黙的な仕様変更を行いません。
