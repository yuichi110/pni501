# 3. 推奨する改善ロードマップ

検出された計33件の指摘事項（`CRITICAL` 10件、`HIGH` 12件、`MEDIUM` 9件、`LOW` 2件）を体系的に解消し、総合スコアを Grade D (`15`) から本番運用可能な Grade A 水準（`85+`）へ引き上げるため、PNI が優先度順に正規化した **Phase 1（P0 緊急脆弱性封じ込め・DAST実証経路遮断・秘密鍵失効・PHP 8.3 非 root コンテナ刷新：4重点施策） -> Phase 2（P1 Composer PSR-4 レイヤ分離・PDO/password_hash・12-Factor/専用Health 整備：4重点施策） -> Phase 3（P2 `strict_types=1`・PHPUnit 自動テスト・OpenSSF ガバナンス確立：3重点施策）** の3段階ロードマップを策定する。

```drawlib file=remediation_priority_roadmap.png caption="優先度フェーズ別 改善ロードマップ (Phase 1 [P0] -> Phase 2 [P1] -> Phase 3 [P2])"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import Roadmap
from drawlib.styles import Styles

setup(width=146, height=58, dpi=150)

rm = Roadmap(
    style=Styles.Neutral,
    text_style=Styles.DarkBold.patch(text_size=10.0),
    description_style=Styles.Dark.patch(text_size=9.0),
    spine_style=Styles.PrimaryBold,
    badge_style=Styles.Danger,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.5),
    direction="horizontal",
    spacing=3.5,
)
rm.add(
    "Phase 1: 緊急封じ込め",
    "DAST実証RCE/0e突破/LFI遮断\n秘密鍵失効・PHP 8.3非root化",
    badge_text="P0",
    style=Styles.DangerNeutral,
    badge_style=Styles.Danger,
    icon=phosphor.lock_key,
    icon_style=Styles.Danger,
)
rm.add(
    "Phase 2: 構造・信頼性刷新",
    "Composer PSR-4・PDO・Argon2id\nTimeout・PSR-3ログ・/healthz",
    badge_text="P1",
    style=Styles.WarningNeutral,
    badge_style=Styles.Warning,
    icon=phosphor.wrench,
    icon_style=Styles.Warning,
)
rm.add(
    "Phase 3: 型安全・自動検証",
    "strict_types=1・PHPStan Lv8\nPHPUnit+pcov 80%・CI/統治整備",
    badge_text="P2",
    style=Styles.PrimaryNeutral,
    badge_style=Styles.Primary,
    icon=phosphor.rocket_launch,
    icon_style=Styles.Primary,
)
rm.draw(xy=(4, 5), width=138, height=48)

save()
```

## フェーズ別実行計画とトレーサビリティ

- **Phase 1 (`P0` — 即時対応：ライブ実証脆弱性の緊急遮断・秘密情報ローテーション・EOL コンテナ廃止)**:
  1. `Dockerfile` を `php:7.4-apache` から現役サポートの `php:8.3-apache-bookworm` + `USER www-data` + `.dockerignore` + `HEALTHCHECK` へ刷新し、OS 層 CVE `12,051` 件（`CRITICAL` 62件、`HIGH` 1,940件）と `DS-0002`（root 実行）を一括解消する。
  2. `includes/db.php` に直書きされた MySQL パスワードと Stripe Live 秘密鍵を即時失効（ローテーション）し、環境変数 / Secret Manager 注入へ切り替える。
  3. ライブ DAST で悪用実証された `POST /admin_backup.php` の無認証 `shell_exec`（`PNI_RCE_CANARY_8842`）と `POST /login.php` の `'240610708'` マジックハッシュ突破、`index.php` の LFI・反射型 XSS、`product.php` の `promo_html` XSS、HTTP セキュリティヘッダ欠落を緊急修正し、`.pni/pentests/examples/php/legacy_shop_messy/` 全19プローブの PASS を CI リリースゲート化する。
  4. 残る SAST 危険シンク（`index.php:4` の `unserialize($_COOKIE)`、全3箇所の生 SQL 連結、`includes/helpers.php:9` の `CURLOPT_SSL_VERIFYPEER=false`）を PDO プリペアド化・署名付き JSON / サーバセッション化・TLS 検証強制で全面封鎖する。
- **Phase 2 (`P1` — 短期優先：Composer PSR-4 レイヤ分離・12-Factor 設定・専用 `/healthz` 整備)**:
  `composer.json` / `composer.lock` を導入して `public/index.php` 単一フロントコントローラ + `src/`（`Controller -> Service -> Repository`）の単方向 PSR-4 構造へ再編し、`includes/` の相互 `include_once` 循環とドキュメントルート露出を解消する。併せて `AppConfig` による環境変数集約、cURL / DB タイムアウト設定、Monolog PSR-3 構造化ログ、専用の `/healthz`・`/readyz` JSON エンドポイントを実装する。
- **Phase 3 (`P2` — 中期定着：`strict_types=1`・PHPUnit 自動テスト・OpenSSF ガバナンス)**:
  全 PHP ファイルへの `declare(strict_types=1);` とネイティブ型宣言・PHPStan (level 8) の適用、インメモリ `pdo_sqlite` を用いたオフライン PHPUnit 11 + `pcov`（カバレッジ 80% 以上）の整備、および `.gitignore`・`LICENSE`・`SECURITY.md`・最小権限 GitHub Actions CI + Dependabot の導入を完了する。

```drawlib file=remediation_action_table.png caption="推奨改善アクション計画マトリクス (P0 -> P1 -> P2 全11施策)"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=128, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=8.5),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.0),
    border_style=Styles.NeutralThin,
)
rows = [
    ["優先度", "施策タイトル", "対象ファイル", "期待効果 (Impact)", "関連ルール / CVE"],
    [
        "P0",
        "PHP 8.3 非rootセキュア\nコンテナへの即時刷新",
        "Dockerfile",
        "OS CVE 12,051件(CRIT 62)と\nDS-0002 root実行を一括解消",
        "security_vulnerability\nCVE-2023-25690 / DS-0002",
    ],
    [
        "P0",
        "DBパスワード・Stripe本番\n秘密鍵の失効と環境変数化",
        "includes/db.php",
        "平文認証情報の漏洩リスク\n(CWE-798)を完全に根絶",
        "common/security\nSEC-03",
    ],
    [
        "P0",
        "ライブ実証RCE・0e突破・LFI\n・XSS遮断とDAST回帰ゲート化",
        "admin_backup / login /\nindex / product / Docker",
        "実HTTP再現した全10件の動的\n脆弱性根絶とCI 19プローブ監視",
        "security_vulnerability\nSEC-06 (.pni/pentests)",
    ],
    [
        "P0",
        "CMDi・LFI・unserialize・\nSQLi・TLS無効化の全面封鎖",
        "admin_backup / index /\nproduct / login / helpers",
        "無認証RCE・Object注入・SQLi\n・MITMの全13 CWEシンク遮断",
        "security_vulnerability\nphp/modern_stack",
    ],
    [
        "P1",
        "HTML+SQL分離と相互include\n循環解消 (PSR-4レイヤ化)",
        "index / product / login\nincludes/db, helpers",
        "Controller/Service/Repository\n分離とグローバル状態結合解消",
        "common/architecture\nphp/code_quality",
    ],
    [
        "P1",
        "12-Factor設定集約・I/O\nTimeout・PSR-3ログ導入",
        "includes/db, helpers\nproduct / admin_backup",
        "cURLハングによるワーカー枯渇\n防止とJSON構造化ログ確立",
        "common/twelve_factor\nproduction_readiness",
    ],
    [
        "P1",
        "専用 /healthz・/readyz 実装\nと Dockerfile HEALTHCHECK",
        "index.php / Dockerfile\nincludes/db.php",
        "Apache本番環境での確実な\n起動ヘルス検証と自動復旧確立",
        "runtime_verification\nproduction_readiness",
    ],
    [
        "P1",
        "Composer (composer.lock)\n導入と公開ルート隔離",
        "Dockerfile\nincludes/db, helpers",
        "再現可能な依存固定と公開Web\nルートからの内部コード隔離",
        "php/dependencies\ncommon/supply_chain",
    ],
    [
        "P2",
        "OpenSSFガバナンス文書と\n最小権限CI・Dependabot整備",
        "Dockerfile\nREADME.md",
        ".gitignore/LICENSE/SECURITY\n整備と継続的脆弱性自動検知",
        "common/supply_chain\ncommon/git_workflow",
    ],
    [
        "P2",
        "PHPUnit 11 + pcov オフライン\n自動テストスイート構築",
        "login / index /\nproduct / admin_backup",
        "pdo_sqliteオフラインテストで\n実測カバレッジ 80% 以上達成",
        "php/testing\nruntime_verification",
    ],
    [
        "P2",
        "declare(strict_types=1)\n全適用とネイティブ型・PHPStan",
        "全6 PHPファイル",
        "暗黙型強制バグの静的遮断と\n型安全カバレッジ 90%+ 達成",
        "php/typing",
    ],
]
tbl.draw_flexible(
    xy=(3, 125),
    column_widths=[11, 35, 30, 36, 28],
    row_heights=[7.2] + [10.4] * 11,
    data=rows,
)

save()
```
