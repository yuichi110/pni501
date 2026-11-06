# 3. 推奨する改善ロードマップ

`acme/order-fulfillment-api` は現時点で緊急遮断を要する `P0`（`CRITICAL` / `HIGH`）課題を **0件** に抑え込んでおり、すでに Grade S（`94 / 100`）の健全性を達成している。さらなる大規模本番トラフィックへの対応、ライブ DAST 全18プローブ満点化、および OpenSSF Scorecard 満点水準への到達に向け、検出された改善項目（`MEDIUM: 1` 件・`LOW: 6` 件・`INFO: 5` 件）を **Phase 1（`P1` 本番ランタイム・OS 層強化：2施策） -> Phase 2（`P2` HTTP 応答ハードニング・CI/供給網統治：4施策） -> Phase 3（`P2` テスト・型・ドキュメント磨き込み：4施策）** の計10施策として体系化する。

```drawlib file=remediation_priority_roadmap.png caption="図3-1: 本番運用完成度向上に向けた継続的改善ロードマップ (P0=0件 / P1=2施策 / P2=8施策)"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import Roadmap
from drawlib.styles import Styles

setup(width=146, height=58, dpi=150)

rm = Roadmap(
    style=Styles.Neutral,
    text_style=Styles.DarkBold.patch(text_size=10.0),
    description_style=Styles.Dark.patch(text_size=9.2),
    spine_style=Styles.PrimaryBold,
    badge_style=Styles.Primary,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.3),
    direction="horizontal",
    spacing=3.2,
)
rm.add(
    "Phase 1: 本番基盤強化 (P1×2)",
    "Debian 12更新・多段ビルド化\nPHP-FPM/FrankenPHP + PSR-3ログ",
    badge_text="P1 優先",
    style=Styles.WarningNeutral,
    badge_style=Styles.Warning,
    icon=phosphor.shield_check,
    icon_style=Styles.Warning,
)
rm.add(
    "Phase 2: HTTP・供給網統治 (P2×4)",
    "nosniff/TRACE抑止・URI解決修正\nDependabot・PHPStan CI・LICENSE",
    badge_text="P2 統治",
    style=Styles.PrimaryNeutral,
    badge_style=Styles.Primary,
    icon=phosphor.git_branch,
    icon_style=Styles.Primary,
)
rm.add(
    "Phase 3: 検証・型洗練 (P2×4)",
    "public/ Clover計測・境界テスト追加\nBacked Enum化・DDL分離・README拡充",
    badge_text="P2 洗練",
    style=Styles.SuccessNeutral,
    badge_style=Styles.Success,
    icon=phosphor.rocket_launch,
    icon_style=Styles.Success,
)
rm.draw(xy=(4, 5), width=138, height=48)

save()
```

## フェーズ別継続改善計画と期待効果

- **Phase 1 (`P1` — コンテナ OS 層刷新と本番マルチワーカー化)**: `Dockerfile` のベースイメージを最新パッチ適用済みの `php:8.3-fpm-bookworm`（または `FrankenPHP`、`@sha256` ダイジェスト固定）へ更新し、マルチステージビルドにより `libsqlite3-dev` 等のビルドヘッダを最終イメージから除去することで Debian 12 OS 層 CVE を一掃する。同時に単一プロセス開発サーバ `php -S` からマルチワーカー SAPI へ切り替え、`OrderFulfillmentService` に `Psr\Log\LoggerInterface` 構造化監査ログを追加する。
- **Phase 2 (`P2` — HTTP セキュリティヘッダ強化・サプライチェーン自動化)**: 動的Webペネトレーション検証（`.pni/pentests/`）で検出された `X-Content-Type-Options: nosniff` 付与・`X-Powered-By` 除去・`TRACE` メソッド遮断・`public/index.php` の `$_SERVER['REQUEST_URI']` 参照による `cli-server` 404 応答統一を実施し、併せて `.github/dependabot.yml` 追加・CI での `phpstan`/`pint` 実行・`LICENSE` 全文記載を行う。
- **Phase 3 (`P2` — カバレッジ範囲拡張・Backed Enum・マイグレーション分離)**: `phpunit.xml` の `<source>` へ `public/` を追加して `buildHealthResponse` の 200/404 応答および数量上限（`quantity=1001`）を PHPUnit で直接検証し、`OrderRecord::$status` の PHP 8.3 Backed `enum` 化、`OrderRepository` コンストラクタからの DDL 分離、および `README.md` への Docker / `curl` クイックスタート追記を実施する。

```drawlib file=remediation_action_table.png caption="図3-2: 推奨改善アクション計画トレーサビリティマトリクス (P1 -> P2 全10施策)"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=118, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=8.8),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.2),
    border_style=Styles.NeutralThin,
)
rows = [
    ["優先度", "改善施策タイトル", "対象ファイル", "期待される改善効果", "関連ルール / CWE"],
    [
        "P1",
        "マルチワーカー本番SAPI採用と\nPSR-3構造化監査ログ導入",
        "Dockerfile\n.../OrderFulfillmentService.php",
        "高並行HTTP処理性能の確保と注文・\nWebhook署名拒否の監査証跡化",
        "common/production_readiness\ncommon/twelve_factor",
    ],
    [
        "P1",
        "PHP 8.3ベースイメージ刷新と\nマルチステージDockerfile化",
        "Dockerfile",
        "Debian 12 OS層CVE解消と\nlibsqlite3-devビルド資産の除外",
        "common/security_vulnerability\nCVE-2026-42010 / 31789",
    ],
    [
        "P2",
        "OrderRepositoryコンストラクタ\nからのDDLマイグレーション分離",
        ".../OrderRepository.php\n.../OrderFulfillmentService.php",
        "接続毎のCREATE TABLE負荷排除と\nRepositoryインターフェース抽象化",
        "common/architecture",
    ],
    [
        "P2",
        "Dependabot有効化およびCIでの\nPHPStan・Pint静的解析実行",
        ".github/workflows/ci.yml\ncomposer.lock",
        "依存更新PR自動化とPR毎の厳格型・\nPSR-12コードスタイル自動強制",
        "common/supply_chain\nphp/dependencies",
    ],
    [
        "P2",
        "LICENSEファイルへのSPDX標準\nApache-2.0ライセンス全文記載",
        "LICENSE",
        "SBOM・OpenSSFスキャナによる\nApache-2.0条項の100%自動認識",
        "common/supply_chain",
    ],
    [
        "P2",
        "READMEへのDocker起動手順・\nAPIリクエスト/応答例の追記",
        "README.md",
        "Diataxis Tutorial/How-To拡充に\nよる即時オンボーディング支援",
        "common/documentation",
    ],
    [
        "P2",
        "HTTPヘッダ・TRACE/X-Powered-By抑止\nおよびcli-server URI 404応答修正",
        "public/index.php\nDockerfile",
        "DAST全4件(TRACE/nosniff/バナー/\n未知URI 200)を解消し18/18合格化",
        "common/security_vulnerability\nCWE-693 / 200 / 755",
    ],
    [
        "P2",
        "ヘルスプローブ404および上限値\n(qty>1000)のDataProviderテスト",
        "tests/OrderFulfillmentServiceTest.php\nphpunit.xml",
        "上限ガード・LIMITクランプ・404応答\nの決定論的単体テスト網羅",
        "php/testing",
    ],
    [
        "P2",
        "public/index.php の PHPUnit\nClover カバレッジ対象組み込み",
        "phpunit.xml, public/index.php\ntests/OrderFulfillmentServiceTest.php",
        "フロントコントローラを含む全PHP\nコードのPCOV 100%計測達成",
        "common/runtime_verification\nphp/testing",
    ],
    [
        "P2",
        "OrderStatus Backed Enum導入と\nController配列シェイプPHPDoc化",
        ".../Models/OrderRecord.php\n.../OrderController.php",
        "不正ステータス文字列のコンパイル時\n排除とPHPStan最大レベル適合",
        "php/typing\nphp/modern_stack",
    ],
]
tbl.draw_flexible(
    xy=(3, 115),
    column_widths=[11, 35, 34, 34, 26],
    row_heights=[7.4] + [10.3] * 10,
    data=rows,
)

save()
```
