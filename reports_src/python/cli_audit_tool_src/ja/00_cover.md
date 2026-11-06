# PNI ソフトウェア健全性診断レポート

本レポートは、構造化 `.jsonl` ログ解析 CLI ツール **`logpulse` (`v0.2.1`)** に対して、PNI ステートフル監査ワークフロー `py_cli_audit_tool`（静的 AST 解析・アーキテクチャ構造抽出・隔離コンテナでのオフライン `pytest` / カバレッジ計測・Trivy 脆弱性スキャン）を実行した包括的診断結果である。

```drawlib file=cover_hero_scorecard.png caption="logpulse (v0.2.1) PNI 総合健全性スコアカード"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import KpiCards, Panel
from drawlib.styles import Styles

setup(width=146, height=64, dpi=150)

panel = Panel(
    "logpulse v0.2.1 — PNI 健全性診断スコアカード",
    "Run: wf-7f0bbfdb",
    style=Styles.Neutral,
    header_style=Styles.Primary,
    text_style=Styles.WhiteBold.patch(text_size=11.5),
    description_style=Styles.White.patch(text_size=9.5),
    icon=phosphor.shield_check,
    icon_style=Styles.White,
    header_height=11.5,
)
panel.draw(xy=(3, 3), width=140, height=58)

kpis = KpiCards(
    style=Styles.White,
    metric_style=Styles.PrimaryBold.patch(text_size=14.0),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Neutral.patch(text_size=9.5),
    accent_style=Styles.Primary,
    icon_style=Styles.Primary,
    metric_width_ratio=0.35,
    spacing=3.5,
)
kpis.add(
    "77 / 100",
    "総合スコア (Grade B)",
    "設計90 / 型84 / テスト64",
    icon=phosphor.chart_bar,
    accent_style=Styles.Primary,
    metric_style=Styles.PrimaryBold.patch(text_size=14.0),
)
kpis.add(
    "Py 3.11+",
    "対象言語・CLI構成",
    "uv / Typer / Rich (207 LOC)",
    icon=phosphor.terminal_window,
    accent_style=Styles.Success,
    metric_style=Styles.SuccessBold.patch(text_size=13.5),
    icon_style=Styles.Success,
)
kpis.add(
    "4 / 15",
    "ルール適合 (PASS)",
    "PASS 4 / WARN 9 / FAIL 2",
    icon=phosphor.check_circle,
    accent_style=Styles.Warning,
    metric_style=Styles.WarningBold.patch(text_size=14.0),
    icon_style=Styles.Warning,
)
kpis.add(
    "12 件",
    "検出指摘 (Findings)",
    "HIGH 2 / MED 6 / LOW 4",
    icon=phosphor.bug,
    accent_style=Styles.Danger,
    metric_style=Styles.DangerBold.patch(text_size=14.0),
    icon_style=Styles.Danger,
)
kpis.draw(xy=(7, 6.5), width=132, height=40, columns=2)

save()
```

## 診断メタデータ概要

- **対象プロジェクト**: `logpulse` (`v0.2.1` / 対象ルート: `examples/python/cli_audit_tool`)
- **対象言語・ビルド基盤**: `python` (`>=3.11`, `uv` / `uv_build`, CLI フレームワーク `typer` + `rich`)
- **診断ワークフロー / Run ID**: `py_cli_audit_tool` / `wf-7f0bbfdb`
- **評価実施日時**: `2026-10-24T07:35:17.310642+00:00`
- **総合スコア・グレード**: **77 / 100 (Grade B)**
- **エンジニアリングルール適合率**: `4 / 15` ルール PASS（`WARN`: 9件、`FAIL`: 2件）
