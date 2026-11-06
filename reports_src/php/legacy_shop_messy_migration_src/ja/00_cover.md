# PNI マイグレーション実行計画レポート

本レポートは、ベースライン健全性監査（`wf-1abc5e13`: **15/100 Grade D**・ライブ Docker DAST `web_pentest` 19 プローブ中 10 件失敗）で未認証 RCE やマジックハッシュ認証バイパスが実証された手続き型「素 PHP」EC アプリケーション **`legacy_shop_messy`** に対する PNI 移行設計ワークフロー `php_legacy_shop_messy_migration` に基づき策定された、**PHP 8.3 + Laravel 11 + MySQL 8 PDO/Eloquent + Redis 7（Strangler Fig 段階カットオーバー）** の実行ブループリントである。

```drawlib file=cover_php_migration_scorecard.png caption="legacy_shop_messy Strangler Fig マイグレーション実行計画サマリカード"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import KpiCards, Panel
from drawlib.styles import Styles

setup(width=146, height=66, dpi=150)

panel = Panel(
    "legacy_shop_messy 移行計画",
    "Run: wf-20d0b5ba | Base: wf-1abc5e13 (15/D)",
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
    "6 変換軸",
    "脱・素 PHP モダナイズ",
    "PHP 8.3 / Laravel 11 / PDO / Redis 7",
    icon=phosphor.arrows_clockwise,
    accent_style=Styles.Primary,
    metric_style=Styles.PrimaryBold.patch(text_size=13.5),
)
kpis.add(
    "4 Routes",
    "Strangler Fig 段階置換",
    "/product → / → /login → /admin",
    icon=phosphor.git_branch,
    accent_style=Styles.Success,
    metric_style=Styles.SuccessBold.patch(text_size=13.5),
    icon_style=Styles.Success,
)
kpis.add(
    "5 Gates",
    "段階検証 & 19 DAST Probes",
    "Nginx 共存 → DAST 全通過 → 旧撤去",
    icon=phosphor.shield_check,
    accent_style=Styles.Primary,
    metric_style=Styles.PrimaryBold.patch(text_size=13.5),
)
kpis.add(
    "10 PRs",
    "実行可能 WBS & 4 合意論点",
    "Dual-Verify bcrypt + Cookie 刷新",
    icon=phosphor.git_pull_request,
    accent_style=Styles.Warning,
    metric_style=Styles.WarningBold.patch(text_size=13.5),
    icon_style=Styles.Warning,
)
kpis.draw(xy=(7, 6.5), width=132, height=41, columns=2)

save()
```

## 確定済み前提条件（Confirmed Assumptions）と非目標（Non-Goals）

- **移行モード / ロールアウト戦略**: `cross_stack_replacement` / **`strangler_fig`（Nginx リバースプロキシ配下のルート段階カットオーバー方式）**・互換ポリシー `strict`・曖昧性ポリシー `ask_human`
- **確定済み技術スタック**: **PHP 8.3**（`declare(strict_types=1)`）+ **Laravel 11**（Composer PSR-4 / PHPUnit 11 / PHPStan Level 6）+ **MySQL 8.0**（Eloquent / PDO プリペアドステートメント）+ **Redis 7**（暗号化セッション & サーバー側カート保存）
- **確定済みセキュリティ・DAST 回帰ガードレール**: 既存 URL と検索クエリ（`?q=`, `?cat=`）を維持しつつ、ライブ DAST で実証された OS コマンド実行（`PNI_RCE_CANARY_8842`）・マジックハッシュ認証突破（`'240610708'`）・LFI・Reflected XSS・SQLi・Cookie `unserialize` をルート置換と同時に根絶し、`.pni/pentests/examples/php/legacy_shop_messy/` の全 19 DAST プローブを CI ゲートとして再利用する。既存 MD5 会員は Dual-Verify 透過再ハッシュで無停止移行する。
- **非目標（Non-Goals）**: React / Vue 等の SPA フロントエンド分離および別言語リライトはスコープ外とし、自動エスケープを備えた Laravel Blade サーバーサイド描画へまず移行する。
