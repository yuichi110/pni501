# PNI ソフトウェア健全性診断レポート

**Member Analytics Portal（`wp_plugin_messy` v1.3.0）— WordPress プラグイン監査**

```drawlib align=center code=fold file=cover_scorecard.png caption="Member Analytics Portal（wp_plugin_messy v1.3.0）PNI501 エグゼクティブ診断スコアカード"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import KpiCards, Panel
from drawlib.styles import Colors, Styles
from drawlib.utils import draw_pni_logo

setup(width=146, height=68, dpi=150)

hero = Panel(
    text="PNI501 Diagnostic Scorecard  —  Member Analytics Portal (v1.3.0)",
    description="",
    style=Styles.Neutral.patch(shape_r=2.0, shape_fill_color=Colors.White, shape_line_color=Colors.Gray4),
    header_style=Styles.PrimaryFlat.patch(shape_r=2.0),
    text_style=Styles.WhiteBold.patch(text_size=12.0),
    header_variant="filled",
    header_height=13.5,
    header_align="left",
)
hero.draw((3.0, 4.0), width=140.0, height=60.0)

draw_pni_logo((135.5, 57.2), width=8.5, dark=True)

primary_kpis = KpiCards(
    style=Styles.Neutral.patch(shape_r=1.5, shape_fill_color=Colors.Gray1, shape_line_color=Colors.Gray3),
    metric_style=Styles.DarkBold.patch(text_size=14.0),
    text_style=Styles.DarkBold.patch(text_size=10.0),
    description_style=Styles.Muted.patch(text_size=9.2),
    accent_position="top_bar",
    metric_layout="top_stack",
    spacing=3.0,
)
primary_kpis.add(
    "60 / 100",
    "Overall Score (Grade C)",
    "Baseline 70  |  AI -10pt",
    accent_style=Styles.WarningFlat,
    metric_style=Styles.WarningBold.patch(text_size=14.0),
    icon=phosphor.chart_bar,
    icon_style=Styles.Warning,
)
primary_kpis.add(
    "30 / 100",
    "Security Axis (Grade D)",
    "5 HIGH CWE + 1 Secret",
    accent_style=Styles.DangerFlat,
    metric_style=Styles.DangerBold.patch(text_size=14.0),
    icon=phosphor.shield_warning,
    icon_style=Styles.Danger,
)
primary_kpis.add(
    "0 / 16",
    "Applicable Rules Passed",
    "12 FAIL | 4 WARN | 1 N/A",
    accent_style=Styles.DangerFlat,
    metric_style=Styles.DangerBold.patch(text_size=14.0),
    icon=phosphor.list_checks,
    icon_style=Styles.Danger,
)
primary_kpis.add(
    "15 Total",
    "Audit Findings",
    "4 CRIT | 10 HIGH | 1 MED",
    accent_style=Styles.PrimaryFlat,
    metric_style=Styles.PrimaryBold.patch(text_size=14.0),
    icon=phosphor.warning_octagon,
    icon_style=Styles.Primary,
)
primary_kpis.draw((6.0, 25.0), width=134.0, height=22.0, columns=4)

meta_kpis = KpiCards(
    style=Styles.PrimaryNeutral.patch(shape_r=1.5, shape_line_color=Colors.Gray3),
    metric_style=Styles.PrimaryBold.patch(text_size=11.0),
    text_style=Styles.DarkBold.patch(text_size=9.8),
    description_style=Styles.Muted.patch(text_size=8.8),
    accent_position="left_pill",
    metric_layout="left_column",
    metric_width_ratio=0.31,
    spacing=3.0,
)
meta_kpis.add(
    "4 Files",
    "Codebase (84 LOC)",
    "7 funcs, 0 classes, 0 tests",
    accent_style=Styles.PrimaryFlat,
)
meta_kpis.add(
    "PHP 8.2",
    "Runtime Smoke OK",
    "php -l OK; 5 hooks loaded",
    accent_style=Styles.SuccessFlat,
    metric_style=Styles.SuccessBold.patch(text_size=11.0),
)
meta_kpis.add(
    "0 CVEs",
    "Declared App CVEs",
    "Raw PHP (harness OS excl.)",
    accent_style=Styles.SecondaryFlat,
    metric_style=Styles.SecondaryBold.patch(text_size=11.0),
)
meta_kpis.draw((6.0, 7.5), width=134.0, height=14.5, columns=3)

save()
```

## 監査対象・来歴情報

| 項目 | 値 |
| :--- | :--- |
| **プロジェクト / プラグイン名** | Member Analytics Portal（`wp_plugin_messy` v1.3.0） |
| **監査対象ディレクトリ** | `examples/php/wp_plugin_messy` |
| **主要言語・フレームワーク** | PHP（宣言 `Requires PHP: 7.4` EOL・PHP 8.2 環境で検証） / WordPress プラグイン |
| **ワークフロー / 実行 ID** | `php_wp_plugin_messy` / `wf-3389d5e7`（`category=audit`, `scope=repo`） |
| **評価日時（UTC）** | `2026-11-22T11:29:03.792183+00:00` |
| **Git 来歴** | `main@d1e02277 (dirty)` |
| **総合健全性スコア** | **60 / 100（グレード C）** *(決定論的ベースライン 70 → AI 定性補正 −10pt)* |
| **セキュリティ軸スコア** | **30 / 100（グレード D）** *(HIGH CWE シンク 5 件、ハードコード秘密鍵 1 件、未認証エンドポイント 4/5)* |
| **ルール準拠率** | **適用ルール `0 / 16` 合格**（評価 17 ルール中 `12 FAIL`、`4 WARN`、`1 NOT_APPLICABLE`） |
| **指摘事項の内訳** | **全 15 件**（ユニーク箇所 11 箇所：`CRITICAL 4` / `HIGH 10` / `MEDIUM 1`） |
