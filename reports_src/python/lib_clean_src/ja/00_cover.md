# PNI ソフトウェア健全性診断レポート

**対象プロジェクト**: `metrics-kit` v0.4.2（軽量テレメトリ統計・SLO閾値評価 Python ライブラリ）  
**診断ワークフロー**: `py_lib_clean`（隔離コンテナ動的検証・Trivy 脆弱性スキャン統合フル監査）

```drawlib file=00_cover_scorecard.png caption="PNI 総合健全性スコアカード — metrics-kit v0.4.2 (Grade S: 95/100)"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import KpiCards, Panel
from drawlib.styles import Styles

setup(width=146, height=62, dpi=150)

hero = Panel(
    "metrics-kit v0.4.2 — 総合健全性スコアカード (Run: wf-7ef694c9)",
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=12.5),
    icon=phosphor.shield_check,
    icon_style=Styles.WhiteBold,
    header_variant="filled",
    header_height=10.0,
)
hero.draw((3.0, 4.0), width=140.0, height=54.0)
inner_xy, inner_w, inner_h = hero.get_content_box((3.0, 4.0), width=140.0, height=54.0, padding=(4.0, 3.2))

kpis = KpiCards(
    style=Styles.White.patch(shape_r=1.5),
    metric_style=Styles.PrimaryBold.patch(text_size=18.0),
    text_style=Styles.DarkBold.patch(text_size=11.2),
    description_style=Styles.Muted.patch(text_size=9.8),
    accent_style=Styles.PrimaryFlat,
    icon_style=Styles.PrimaryBold,
    accent_position="left_pill",
    metric_layout="left_column",
    metric_width_ratio=0.32,
    spacing=3.5,
)
kpis.add(
    "95 / 100",
    "総合健全性スコア (Grade S)",
    "全7評価軸で 91〜99点の高水準を達成",
    icon=phosphor.medal,
)
kpis.add(
    "Python",
    "対象言語・実行プロファイル",
    "Python >=3.11 / 純粋関数 319 LOC",
    icon=phosphor.code,
    metric_style=Styles.DarkBold.patch(text_size=16.5),
    accent_style=Styles.PrimaryNeutral,
    icon_style=Styles.DarkBold,
)
kpis.add(
    "13 / 15",
    "エンジニアリング規約適合率",
    "PASS 13件 / WARN 2件 / FAIL 0件",
    icon=phosphor.check_circle,
    metric_style=Styles.SuccessBold.patch(text_size=18.0),
    accent_style=Styles.SuccessFlat,
    icon_style=Styles.SuccessBold,
)
kpis.add(
    "5 件",
    "検出事項合計 (重大指摘 0件)",
    "CRITICAL 0 / HIGH 0 / LOW 3 / INFO 2",
    icon=phosphor.magnifying_glass,
    metric_style=Styles.DarkBold.patch(text_size=18.0),
    accent_style=Styles.SecondaryNeutral,
    icon_style=Styles.SecondaryBold,
)
kpis.draw(inner_xy, width=inner_w, height=inner_h, columns=2)

save()
```

- **診断対象**: `examples/python/lib_clean`（`metrics-kit` `v0.4.2` / Apache-2.0 / `pydantic>=2.7.0`）
- **実行ワークフロー / Run ID**: `py_lib_clean` / `wf-7ef694c9`（評価日時: `2026-10-24T07:36:17Z`）
- **総合判定**: **95 / 100 (Grade S)** — ルール適合 `13/15`・オフライン `pytest` `6/6` 合格（行カバレッジ `96.2%`）・直接依存 CVE `0` 件
