# 6. PR 単位の実行 WBS と検証・受け入れゲート

Strangler Fig の5フェーズ・4ルート置換を、1 PR ごとに独立テスト・即時切り戻し可能な **計10 PR（`PR-01`〜`PR-10`）** に分割する。`PR-02`（MySQL PDO/Eloquent 基盤）と `PR-03`（Redis 7 セッション/カート & TLS HTTP Client）は `PR-01` 完了後に並列実装が可能である。

```drawlib file=php_pr_wbs_execution_table.png caption="Strangler Fig ルート順 PR 実行 WBS (PR-01 - PR-10) と自動検証コマンド"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=136, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=8.2),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=8.8),
    border_style=Styles.NeutralThin,
)
rows = [
    ["PR / Phase", "規模 / 種別", "PR タイトルと主要変更内容", "依存 PR", "必須検証コマンド (CI Gate)"],
    [
        "PR-01\nPhase 0",
        "M / Manual",
        "Composer / Laravel 11 + Nginx Strangler\nプロキシ基盤と HTTP 特性テスト構築",
        "なし",
        "composer test && phpstan analyse",
    ],
    [
        "PR-02\nPhase 1 (W3)",
        "M / Manual",
        "db.php 秘密情報 .env 外部化と MySQL 8\nEloquent / PDO Repository Port 実装",
        "PR-01",
        "php artisan test --filter=EloquentRepo",
    ],
    [
        "PR-03\nPhase 1 (W3)",
        "S / Manual",
        "Redis 7 セッション・RedisCartStore 実装と\nTLS 検証強制 Partner HTTP Client 構築",
        "PR-01",
        "php artisan test --filter=RedisCart",
    ],
    [
        "PR-04\nPhase 2",
        "XS / Codemod",
        "Rector (PHP 8.3 / strict_types=1 /\nLaravel 11) 自動規約パイプライン導入",
        "PR-02,03",
        "rector --dry-run && phpstan analyse",
    ],
    [
        "PR-05\nPhase 2 (R1)",
        "S / Manual",
        "Route #1: product.php の Laravel 移行\n(?cat= PDO 化・promo Blade エスケープ)",
        "PR-04",
        "artisan test && pytest pentests -k product",
    ],
    [
        "PR-06\nPhase 2 (R2)",
        "M / Manual",
        "Route #2: index.php の Storefront 移行\n(Redis カート切替・?q= XSS/SQLi・LFI 根絶)",
        "PR-05",
        "artisan test && pytest pentests -k lfi",
    ],
    [
        "PR-07\nPhase 3 (R3)",
        "M / Manual",
        "Route #3: login.php の Dual-Verify\nbcrypt 透過移行・'240610708' 突破根絶",
        "PR-06",
        "artisan test && pytest pentests -k auth",
    ],
    [
        "PR-08\nPhase 3 (R4)",
        "S / Manual",
        "Route #4: admin_backup.php の Admin Gate\n+ CSRF + Process Job 化 (RCE 根絶)",
        "PR-07",
        "artisan test && pytest pentests -k backup",
    ],
    [
        "PR-09\nPhase 4",
        "S / Manual",
        "退役済み素 PHP スクリプト全6ファイルと\nNginx 旧フォールバック設定の完全撤去",
        "PR-08",
        "composer test && phpstan --level=6",
    ],
    [
        "PR-10\nPhase 4",
        "S / Hybrid",
        "php:8.3-fpm-alpine 非 root コンテナ・\nCSP/HSTS ヘッダ・19 DAST CI 完成",
        "PR-09",
        "pni run-action web_pentest && trivy",
    ],
]
tbl.draw_flexible(
    xy=(3, 133),
    column_widths=[20, 19, 48, 16, 37],
    row_heights=[8.0, 11.8, 11.8, 12.2, 12.2, 12.2, 12.2, 12.2, 12.2, 12.2, 12.2],
    data=rows,
)

save()
```

## フェーズ完了受け入れ基準（Exit Criteria）と無停止ロールバック戦略

- **Phase 0 & Phase 1 完了条件**: Nginx リバースプロキシ経由で全既存 URL が透過動作し、`composer test` および `phpstan analyse --level=6` がエラーゼロで通過すること。
- **Phase 2 & Phase 3 動的 DAST 受け入れ条件**: `.pni/pentests/examples/php/legacy_shop_messy/` に収録された攻撃プローブ群（`backup_dir=; echo PNI_RCE_CANARY_8842` OS コマンド実行、`'240610708'` マジックハッシュ管理者突破、`?page=../../etc/passwd` LFI、`<script>` XSS 2 箇所、SQLi、未認証バックアップ実行）が **100% 防御成功（PASS）** すること。
- **Phase 4 最終受け入れゲート**: 旧素 PHP ファイル残存数 `0` 件、Trivy スキャンで **`CRITICAL` / `HIGH` 脆弱性・秘密情報露出 0 件**、`web_pentest` 全 19 プローブ **19/19 PASS**、および PNI 健全性再診断（全 8 次元）で **Grade A（85点以上）** を達成すること。Strangler Fig 共存期間中（Phase 2〜3）に万一特定ルートで障害が発生した場合は、`PR-09`（旧ファイル撤去）マージ前であれば Nginx `location` 振り分け設定の即時リロードにより数秒で旧エンドポイントへ切り戻し可能である。
