# 1. エグゼクティブサマリと Strangler Fig 移行戦略

`legacy_shop_messy` はベースライン監査（`wf-1abc5e13`: **15/100 Grade D**）およびライブ Docker DAST（`web_pentest`: **0/100 Grade D**、全 19 プローブ中 10 件失敗）において、`admin_backup.php` の未認証 OS コマンド実行（`PNI_RCE_CANARY_8842` 出力）・`login.php` の MD5 マジックハッシュ `'240610708'` による管理者認証バイパス・`?page=` LFI・Reflected XSS 2 箇所が実動実証された EOL `php:7.4-apache` スクリプト群である。インプレース修正や一括凍結リライトのリスクを回避するため、前段に Nginx ルーターを置き **1 エンドポイントずつ Laravel 11 へ無停止置換しつつ `.pni/pentests/` の 19 DAST プローブで段階検証する Strangler Fig（絞め殺しの木）戦略** を採る。

```drawlib file=php_multi_axis_gap_matrix.png caption="As-Is -> To-Be マルチ軸ギャップ分析マトリクス (全6変換軸)"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=102, dpi=150)

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
        "言語・型安全",
        "EOL PHP 7.4・strict_types ゼロ\nマジックハッシュ == 緩い比較",
        "PHP 8.3 FPM (strict_types=1)\nReadonly Class / 厳密比較 ===",
        "Rector + PHPStan Level 6 を\n新規 Laravel 層に強制 [HIGH]",
    ],
    [
        "フレームワーク",
        "composer.json 不在の素 PHP\nSQL と生 HTML echo が混在",
        "Laravel 11 (FormRequest +\nBlade 自動エスケープ + Queue)",
        "Nginx Strangler Fig ルート単位\n段階カットオーバー [CRIT]",
    ],
    [
        "設計思想・構造",
        "db.php <-> helpers.php 循環\n$_GET/$_POST/$_SESSION 直参照",
        "Modular Laravel 4層単方向構造\nHttp -> Action -> Port -> Infra",
        "Phase 1 で共通インフラ層を構築\nスーパーグローバル禁止 [HIGH]",
    ],
    [
        "DB・永続化",
        "生 mysqli_query 文字列結合\nDB_PASSWORD 定数直書き",
        "MySQL 8 Eloquent / PDO Prepared\n.env 注入 + Migrations 管理",
        "既存テーブル互換モデルで共存し\nSQLi を 100% 根絶 [CRIT]",
    ],
    [
        "キャッシュ・状態",
        "unserialize($_COOKIE['shop_cart'])\nHttpOnly 欠落の生 $_SESSION 操作",
        "Redis 7 暗号化セッション &\nRedisCartStore (TTL 7日 JSON)",
        "Object Injection を即時遮断し\nサーバー側カートへ移行 [CRIT]",
    ],
    [
        "認証・保安統治",
        "DAST 実証済み未認証 RCE・'240610708'\n認証突破・LFI・XSS・TLS 無効 cURL",
        "Dual-Verify bcrypt・Admin Gate\nSymfony Process 配列・TLS 強制",
        "19 DAST プローブ回帰ゲートで\n攻撃遮断を継続検証 [CRIT]",
    ],
]
tbl.draw_flexible(
    xy=(3, 99),
    column_widths=[24, 42, 40, 34],
    row_heights=[8.0, 14.5, 14.5, 14.5, 14.5, 14.5, 15.0],
    data=rows,
)

save()
```

## 5フェーズ段階的実行ゲート（Phase 0 → Phase 4）

```drawlib file=php_five_phase_roadmap.png caption="Strangler Fig 5フェーズ段階移行ロードマップ (Phase 0 -> Phase 4)"
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
    "P0 共存プロキシ",
    "Nginx + Laravel 11\nHTTP 特性テスト",
    badge_text="Phase 0",
    style=Styles.PrimaryNeutral,
    badge_style=Styles.Primary,
    icon=phosphor.check_circle,
    icon_style=Styles.Primary,
)
rm.add(
    "P1 共通基盤構築",
    "PDO / Redis 7 Cart\nTLS Partner Client",
    badge_text="Phase 1",
    style=Styles.PrimaryNeutral,
    badge_style=Styles.Primary,
    icon=phosphor.database,
    icon_style=Styles.Primary,
)
rm.add(
    "P2 閲覧・カート置換",
    "product & index 移行\nLFI / XSS DAST 通過",
    badge_text="Phase 2",
    style=Styles.WarningNeutral,
    badge_style=Styles.Warning,
    icon=phosphor.arrows_clockwise,
    icon_style=Styles.Warning,
)
rm.add(
    "P3 認証・管理置換",
    "login Dual-Verify\nRCE / Auth DAST 通過",
    badge_text="Phase 3",
    style=Styles.WarningNeutral,
    badge_style=Styles.Warning,
    icon=phosphor.lock_key,
    icon_style=Styles.Warning,
)
rm.add(
    "P4 旧コード退役",
    "素 PHP 全削除\n19 DAST 全通過完遂",
    badge_text="Phase 4",
    style=Styles.SuccessNeutral,
    badge_style=Styles.Success,
    icon=phosphor.rocket_launch,
    icon_style=Styles.Success,
)
rm.draw(xy=(3, 5), width=140, height=52)

save()
```

- **Phase 0（Nginx 共存基盤 & HTTP 特性テスト）**: 旧スクリプトを無変更のまま Nginx 背後へ配置し、Laravel 11（PHP 8.3）骨格と現行 URL の HTTP スナップショットテストを整備する。
- **Phase 1（循環解消 & Eloquent / Redis 7 基盤構築）**: `db.php <-> helpers.php` 循環依存を解消する形で PDO Repository・`RedisCartStore`・TLS 強制 HTTP クライアントを先行構築する。
- **Phase 2（閲覧・カート系カットオーバー）**: `/product.php` → `/index.php` の順に Nginx 振り分けを Laravel へ切り替え、Cookie `unserialize` と DAST 検出済みの Reflected XSS / `?page=` LFI / SQLi を排除する。
- **Phase 3（認証・管理ジョブ系カットオーバー）**: `login.php`（MD5 → bcrypt 透過再ハッシュ・マジックハッシュ `'240610708'` 排除）と `admin_backup.php`（未認証 `shell_exec` RCE 廃止・Symfony `Process` Job 化）を切り替える。
- **Phase 4（旧スクリプト完全撤去 & DAST 19 プローブ最終監査）**: 稼働安定確認後に旧 `.php` ファイル群を全削除し、`php:8.3-fpm-alpine` 非 root コンテナと `.pni/pentests/` 全 19 DAST プローブ PASS・Grade A を完遂する。
