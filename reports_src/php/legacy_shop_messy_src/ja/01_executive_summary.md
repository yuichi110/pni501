# 1. エグゼクティブサマリー

レガシー素PHP EC・管理アプリケーション `legacy_shop_messy` の総合健全性スコアは **15/100 (Grade D)** と診断された。`composer.json` / `composer.lock`・PSR-4 オートローディング・`declare(strict_types=1)`・自動テストスイートがいずれも未導入（`0%`）である上、隔離ループバック DAST（`web_pentest`：全`19`プローブ中 `9` PASS / `10` FAIL）により、無認証 `POST /admin_backup.php` における OS コマンド実行（`PNI_RCE_CANARY_8842` 出力、`CWE-78`/`CWE-306` CRITICAL）と `POST /login.php` の MD5 マジックハッシュ `'240610708'` 管理者認証突破（`'Logged in as admin'`、`CWE-697` CRITICAL）、`/index.php` の LFI トラバーサル露出（`CWE-22` HIGH）、`/index.php`・`/product.php` の反射型 XSS（`CWE-79` HIGH×2）が実 HTTP 通信で完全実証された。さらに SQLi 3箇所（`CWE-89`）、Cookie `unserialize`（`CWE-502`）、`includes/db.php` の本番 DB パスワード・Stripe Live 秘密鍵直書き（`CWE-798`）、EOL `php:7.4-apache` root コンテナ上の **12,051件の OS 層脆弱性（CRITICAL 62件、HIGH 1,940件）** が複合しており、即時封じ込めと PHP 8.3 モダン構成への刷新が必須である。

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
    title="7軸健全性バランス (Overall: 15 / Grade D)",
    title_style=Styles.DarkBold.patch(text_size=10.2),
)
radar.add_series(
    "legacy_shop_messy",
    [18, 19, 12, 10, 18, 5, 24],
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
    description_style=Styles.Dark.patch(text_size=8.8),
    badge_shape="rounded_rect",
    badge_style=Styles.Primary,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.0),
    spacing=2.0,
)
cards.add(
    "強み1: 極小規模(107 LOC)で全面刷新が容易",
    "全6ファイル・2関数のみで責務棚卸しとPSR-4再設計が短期完遂可能",
    badge_text="強み",
    style=Styles.PrimaryNeutral,
    badge_style=Styles.Success,
    icon=phosphor.check_circle,
    icon_style=Styles.Success,
)
cards.add(
    "強み2: PHP 8.3 構文検査(php -l)は全件通過",
    "Dockerビルド2種・PHP 8.3.36構文検査・HTTP起動応答が成功",
    badge_text="強み",
    style=Styles.PrimaryNeutral,
    badge_style=Styles.Success,
    icon=phosphor.shield_check,
    icon_style=Styles.Success,
)
cards.add(
    "課題1 [CRIT]: ライブ実証済み無認証RCE・認証突破",
    "DASTで PNI_RCE_CANARY_8842 実行と '240610708' 管理者突破を実証",
    badge_text="P0",
    style=Styles.DangerNeutral,
    badge_style=Styles.Danger,
    icon=phosphor.bug,
    icon_style=Styles.Danger,
)
cards.add(
    "課題2 [CRIT]: 秘密鍵直書き & EOL OS脆弱性1.2万件",
    "Stripe/DB鍵平文埋込・php:7.4-apache root実行・CRIT CVE 62件",
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

- **全7軸が25点未満に沈む重大リスクプロファイル**: セキュリティ（`5`）・テスト健全性（`10`）・型安全性（`12`）が特に低く、アーキテクチャ（`18`）・依存関係（`18`）・コード品質（`19`）・ドキュメント（`24`）も含め、推奨基準（80点）との乖離が極めて大きい。全8監査ディメンションのすべてが Grade D（`web_penetration_audit` および `php_test_audit` は `0` 点）、適用可能15ルールのすべてが `FAIL`（`0/17` PASS）となった。
- **ライブ実証された RCE / 認証バイパスとコンテナ root 権限の危険な結合**: `.pni/pentests/examples/php/legacy_shop_messy/` による実 HTTP プローブで、`POST /admin_backup.php` の無認証シェル実行（`PNI_RCE_CANARY_8842`）と `POST /login.php` の `'240610708'` マジックハッシュ突破が実際に成立した。これが `Dockerfile` の `root` 実行（Trivy `DS-0002`）および `includes/db.php` の平文 DB パスワード・Stripe Live 秘密鍵と直結しており、単一リクエストで完全掌握に至る。

```drawlib file=exec_runtime_security_kpis.png caption="コンテナ動的検証・Trivyスキャン・ライブWebペネトレーションの主要指標"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import KpiCards, Panel
from drawlib.styles import Styles

setup(width=146, height=60, dpi=150)

panel = Panel(
    "動的コンテナ検証・Trivy 監査・ライブ DAST ヘッドライン",
    "Docker PHP 8.3 Harness & Trivy 0.69.3 & .pni/pentests (19 HTTP Probes)",
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
    description_style=Styles.Neutral.patch(text_size=8.8),
    metric_width_ratio=0.36,
    spacing=3.0,
)
kpis.add(
    "10 / 19 FAIL",
    "動的Webペネトレーション",
    "CRIT 2 (RCE・0e突破) / HIGH 4",
    icon=phosphor.x_circle,
    accent_style=Styles.Danger,
    metric_style=Styles.DangerBold.patch(text_size=13.0),
    icon_style=Styles.Danger,
)
kpis.add(
    "0 件 (N/A)",
    "PHPUnit テスト・網羅率",
    "php -l・HTTP起動OK / カバレッジ未計測",
    icon=phosphor.warning,
    accent_style=Styles.Warning,
    metric_style=Styles.WarningBold.patch(text_size=13.0),
    icon_style=Styles.Warning,
)
kpis.add(
    "12,051 件",
    "コンテナ OS 層 CVE",
    "CRIT 62 / HIGH 1,940 (Debian 11 EOL)",
    icon=phosphor.bug,
    accent_style=Styles.Danger,
    metric_style=Styles.DangerBold.patch(text_size=13.0),
    icon_style=Styles.Danger,
)
kpis.add(
    "2 / 13 / 4",
    "秘密鍵 / CWEシンク / 無認証API",
    "Stripe+DB鍵・13危険シンク・全4公開",
    icon=phosphor.shield_warning if hasattr(phosphor, "shield_warning") else phosphor.warning,
    accent_style=Styles.Danger,
    metric_style=Styles.DangerBold.patch(text_size=12.8),
    icon_style=Styles.Danger,
)
kpis.draw(xy=(7, 6), width=132, height=37.5, columns=2)

save()
```

## エグゼクティブ結論

- **強み (Verified Strengths)**: 総コード量が6ファイル・`107` LOC（関数2個）と極めてコンパクトであり、隔離コンテナ内での PHP 8.3.36 構文チェック（`php -l`、`1.01s`）および HTTP 起動応答（`1.06s`）も通過した。またサードパーティの脆弱な Composer パッケージ負債も抱えていないため（`app_vuln_counts=0`）、短期集中での全面モダナイゼーションが現実的である。
- **最優先アクション (P0 Priorities)**: (1) ライブ DAST で悪用実証された `admin_backup.php` の無認証 `shell_exec` 廃止・認可強制、`login.php` の `extract()` / `0e` マジックハッシュ撤廃と `password_verify()` 化、`index.php` の `unserialize` / 動的 `include` 撤廃、全 SQL の PDO プリペアド化、全 HTML 出力エスケープと `.pni/pentests/` 回帰ゲート化、(2) `includes/db.php` の DB パスワード・Stripe Live 秘密鍵の即時失効ローテーションと環境変数化、(3) `Dockerfile` の `php:8.3-apache-bookworm` + 非 root `USER www-data` + `.dockerignore` への刷新を最優先で断行すべきである。
