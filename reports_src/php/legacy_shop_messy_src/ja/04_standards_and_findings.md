# 4. 評価指標とルール適合マトリクス

本章では、`php_legacy_shop_messy` ワークフローで実行した8つの評価ステップのスコア比較（弱点順）、全17エンジニアリングルールの適合判定マトリクス（`FAIL: 15` / `NOT_APPLICABLE: 2` / `PASS: 0`）、および重要度順に正規化された全33件の指摘事項（`CRITICAL: 10` / `HIGH: 12` / `MEDIUM: 9` / `LOW: 2`）を一覧化する。

```drawlib file=audit_dimensions_barchart.png caption="実行監査ステップ別スコア比較 (弱点順: 全8ディメンション)"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.styles import Styles

setup(width=146, height=64, dpi=150)

chart = BarChart(
    axis_line_style=Styles.Neutral,
    grid_style=Styles.NeutralThin,
    axis_text_style=Styles.DarkBold.patch(text_size=8.1),
    value_text_style=Styles.DarkBold.patch(text_size=9.0),
    background_style=Styles.Neutral.patch(shape_r=2.0),
    categories=[
        "PHP試験\n(0 / D)",
        "動的侵入\n(0 / D)",
        "脆弱性監査\n(5 / D)",
        "PHP AST\n(8 / D)",
        "供給網衛生\n(10 / D)",
        "本番準備\n(12 / D)",
        "構造監査\n(14 / D)",
        "動的実行\n(28 / D)",
    ],
    orientation="vertical",
    bar_width_ratio=0.56,
    bar_r=1.0,
    width=134,
    height=54,
    title="監査ステップ別 健全性スコア比較 (全8ステップ Grade D: 0 - 28点)",
    title_style=Styles.DarkBold.patch(text_size=10.3),
)
chart.add_series("監査ステップスコア", [0, 0, 5, 8, 10, 12, 14, 28], style=Styles.Danger)
chart.draw(xy=(6, 5))

save()
```

## ルール適合マトリクス（全17ルール：`FAIL: 15` / `N/A: 2` / `PASS: 0`）

全評価ルールは最悪ステータス優先で集約されており、フレームワーク固有の2ルール（`php/frameworks/laravel`, `php/frameworks/wordpress`：`raw_php` のため `NOT_APPLICABLE`）を除く **適用可能な全15ルールが `FAIL`** となり、`PASS` 達成ルールは `0` 件であった。

```drawlib file=rule_compliance_matrix.png caption="エンジニアリングルール適合マトリクス (FAIL -> NOT_APPLICABLE 全17ルール)"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=134, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=8.6),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.0),
    border_style=Styles.NeutralThin,
)
rows = [
    ["判定", "ルールID", "代表ステップ", "決定的エビデンス要約"],
    ["FAIL", "common/architecture", "act-05 (AST)", "0クラス・HTML+SQL混在・db.php<->helpers.php相互include循環"],
    ["FAIL", "common/documentation", "act-02 (構造)", "README.md が実質2行のみで前提・設定・テスト手順がすべて不在"],
    ["FAIL", "common/git_workflow", "act-02 (構造)", ".gitignore と .dockerignore が存在せず機密・一時ファイル混入リスク"],
    ["FAIL", "common/maintainability", "act-05 (AST)", "スーパーグローバル直参照17件・@握り潰し・die()・cURL Timeout欠如"],
    ["FAIL", "common/production_readiness", "act-09/12", "cURL/DB Timeout未設定・@無言失敗・専用/healthzとHEALTHCHECK不在"],
    ["FAIL", "common/runtime_verification", "act-12 (動的)", "Docker/php -l/起動応答通過もテスト0件で実測網羅率未計測(measured=false)"],
    ["FAIL", "common/security", "act-02 (構造)", "DB/Stripe秘密鍵平文直書き・rootコンテナ・SQLi/CMDi/LFI/unserialize"],
    ["FAIL", "common/security_vulnerability", "act-05/14/16", "DAST無認証RCE・0e突破実証 + OS CVE 12,051件 + 13 CWEシンク"],
    ["FAIL", "common/supply_chain", "act-02/14", "ロックファイル/LICENSE/SECURITY/CI/Dependabot全欠落・root Dockerfile"],
    ["FAIL", "common/twelve_factor", "act-09 (SRE)", "127.0.0.1直書き・分散getenv・ファイルSession・/tmp競合・var_dump出力"],
    ["FAIL", "php/code_quality", "act-05 (AST)", "import衛生0%・PHPDoc 0%・スパゲッティ構文・@mysqli_connect・die()"],
    ["FAIL", "php/dependencies", "act-02 (構造)", "composer.json/lock欠如(raw_php)・EOL php:7.4-apache・手動include循環"],
    ["FAIL", "php/modern_stack", "act-02/05", "PHP 7.4 EOL・extract($_POST)・md5 == '0e...'突破・TimeoutなしcURL"],
    ["FAIL", "php/testing", "act-10 (試験)", "ソース6件に対しテスト0件・phpunit.xml不在・オフライン検証分離なし"],
    ["FAIL", "php/typing", "act-05 (AST)", "全6ファイルで declare(strict_types=1) 欠落・引数/戻り値型宣言 0%"],
    ["N/A", "php/frameworks/laravel", "act-05 (AST)", "detected_frameworks=[] (Laravel/Illuminate 未使用の素PHPのため対象外)"],
    ["N/A", "php/frameworks/wordpress", "act-05 (AST)", "detected_frameworks=[] (WordPress プラグイン/テーマではないため対象外)"],
]
tbl.draw_flexible(
    xy=(3, 131),
    column_widths=[12, 36, 22, 70],
    row_heights=[7.0] + [7.1] * 17,
    data=rows,
)

save()
```

## 重要度順 指摘事項一覧（全33件：`CRITICAL: 10` / `HIGH: 12` / `MEDIUM: 9` / `LOW: 2`）

各監査ステップ（SAST・Trivy・ライブ DAST `web_pentest`）から抽出・正規化された全33件の指摘事項を `CRITICAL -> HIGH -> MEDIUM -> LOW` の厳密な順序で3分割して以下に示す（機密リテラル値はすべて `[REDACTED]` 処理済み）。

```drawlib file=findings_crit_table.png caption="重要度順 検出指摘一覧 (1/3: CRITICAL 全10件 — DASTライブ実証2件を含む)"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=90, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=8.3),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=8.8),
    border_style=Styles.NeutralThin,
)
rows = [
    ["重要度", "ルールID", "該当箇所", "検出事象・CWE/CVE/DAST根拠", "推奨修正策"],
    ["CRIT", "security_vulnerability", "Dockerfile:1", "php:7.4-apache OS CVE 12,051件 (CRIT 62)", "php:8.3-apache-bookwormへ刷新"],
    ["CRIT", "common/security", "includes/db.php:6", "DB_PASSWORDとStripe鍵の平文直書き(CWE-798)", "既存鍵を即時失効し環境変数注入化"],
    ["CRIT", "security_vulnerability", "admin_backup.php:6", "SAST: 無認証 shell_exec('tar ...'.$target) (CWE-78)", "認可+CSRF強制・シェル呼出を廃止"],
    ["CRIT", "security_vulnerability", "admin_backup.php:6", "DAST実証: POSTで PNI_RCE_CANARY_8842 実行(CWE-78)", "即時アクセス遮断・ZipArchive置換"],
    ["CRIT", "security_vulnerability", "includes/db.php:7", "Trivy Secret検出: stripe-secret-token [REDACTED]", "Stripe鍵ローテーション・Secret管理"],
    ["CRIT", "security_vulnerability", "index.php:4", "$_COOKIE['shop_cart'] の危険な unserialize(CWE-502)", "Server Sessionまたは署名付JSON化"],
    ["CRIT", "security_vulnerability", "index.php:8", "index/product/login 3箇所の生SQL連結(CWE-89)", "PDOプリペアドステートメントへ統一"],
    ["CRIT", "security_vulnerability", "index.php:25", "include $_GET['page'].'.php' によるLFI(CWE-98)", "動的include廃止・固定ルーティング化"],
    ["CRIT", "security_vulnerability", "login.php:17", "DAST実証: '240610708' で管理者ログイン突破(CWE-697)", "0eフォールバック撤去・Fail-Closed化"],
    ["CRIT", "php/modern_stack", "login.php:17", "SAST: extract + md5 + == '0e...' 型強制(CWE-697)", "extract削除・password_verify()移行"],
]
tbl.draw_flexible(
    xy=(3, 87),
    column_widths=[11, 31, 26, 40, 32],
    row_heights=[7.0] + [7.7] * 10,
    data=rows,
)

save()
```

```drawlib file=findings_high_table.png caption="重要度順 検出指摘一覧 (2/3: HIGH 全12件 — DASTライブ実証LFI/XSSを含む)"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=106, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=8.3),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=8.8),
    border_style=Styles.NeutralThin,
)
rows = [
    ["重要度", "ルールID", "該当箇所", "検出事象・CWE/DAST根拠", "推奨修正策"],
    ["HIGH", "production_readiness", "helpers.php:7", "cURLにCURLOPT_TIMEOUT未設定でハング危険", "CONNECTTIMEOUT=3/TIMEOUT=10設定"],
    ["HIGH", "common/supply_chain", "Dockerfile:1", "EOL PHP 7.4・USER未指定・.dockerignore不在", "ダイジェスト固定・非root・ignore追加"],
    ["HIGH", "security_vulnerability", "Dockerfile:1", "Trivy IaC DS-0002: root権限でApache稼働", "USER www-data による最小権限実行"],
    ["HIGH", "security_vulnerability", "admin_backup.php:1", "全4公開エンドポイントに認可・CSRF・型検証なし", "public/集約・認可ミドルウェア強制"],
    ["HIGH", "security_vulnerability", "helpers.php:9", "CURLOPT_SSL_VERIFYPEER=false & URLトークン", "TLS検証有効化・Bearerヘッダ送信"],
    ["HIGH", "security_vulnerability", "index.php:21", "SAST: index/product/login 3箇所の生echo(CWE-79)", "Twig/Bladeまたはhtmlspecialchars徹底"],
    ["HIGH", "security_vulnerability", "index.php:21", "DAST実証: <pni-xss-canary-7f3a> 生HTML反射", "検索語出力のUTF-8 HTMLエスケープ強制"],
    ["HIGH", "security_vulnerability", "index.php:25", "DAST実証: ../../../../etc/passwd でLFIエラー露出", "動的include撤廃・display_errors=Off"],
    ["HIGH", "security_vulnerability", "product.php:14", "DAST実証: promo_html=<pni-promo-xss-9a2b> 反射", "生HTMLクエリ廃止・テンプレートID化"],
    ["HIGH", "php/dependencies", "Dockerfile:1", "composer.json/lock未導入・PHP 7.4 EOL指定", "Composer PSR-4導入・PHP 8.3移行"],
    ["HIGH", "runtime_verification", "index.php:1", "php -l通過もテスト0件で実測網羅率未計測", "PHPUnit 11 + pcovで網羅率80%+計測"],
    ["HIGH", "php/testing", "login.php:1", "本番6ファイルに対し自動テスト・phpunit.xml不在", "pdo_sqliteオフライン単体テスト整備"],
]
tbl.draw_flexible(
    xy=(3, 103),
    column_widths=[11, 31, 26, 40, 32],
    row_heights=[7.0] + [7.7] * 12,
    data=rows,
)

save()
```

```drawlib file=findings_med_low_table.png caption="重要度順 検出指摘一覧 (3/3: MEDIUM 9件・LOW 2件)"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=98, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=8.3),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=8.8),
    border_style=Styles.NeutralThin,
)
rows = [
    ["重要度", "ルールID", "該当箇所", "検出事象・根拠", "推奨修正策"],
    ["MED", "common/architecture", "includes/db.php:2", "db.php <-> helpers.php 相互include循環・HTML+SQL混在", "PSR-4単方向レイヤ(Controller/Service/Repo)化"],
    ["MED", "common/twelve_factor", "includes/db.php:4", "DB_HOST='127.0.0.1'直書きと分散getenv()呼び出し", "型付きAppConfigクラスで環境変数を一元読込"],
    ["MED", "production_readiness", "Dockerfile:5", "専用 /healthz・/readyz ルートおよび HEALTHCHECK 不在", "/healthz・/readyz JSON実装とHEALTHCHECK定義"],
    ["MED", "common/twelve_factor", "helpers.php:12", "?debug=1でのvar_dump出力と固定/tmp/shop_backup競合", "var_dump撤廃・PSR-3 JSONログ・外部保存化"],
    ["MED", "php/code_quality", "includes/db.php:12", "@mysqli_connect握り潰し・global変数・die(mysqli_error)", "@・global・die廃止とPDO例外ハンドラ統一"],
    ["MED", "common/supply_chain", "README.md:1", "LICENSE・SECURITY.md・Dependabot・CIワークフロー欠如", "統治文書追加と最小権限GitHub Actions整備"],
    ["MED", "security_vulnerability", "Dockerfile:1", "DAST実証: X-Frame-Options/nosniff欠落・TRACE 200応答", "TraceEnable Off・expose_php=Off・CSP/nosniff付与"],
    ["MED", "common/supply_chain", "Dockerfile:4", "COPY . /var/www/html/ による全ファイル露出・root実行", ".dockerignore追加・public/のみ公開・非root化"],
    ["MED", "php/typing", "helpers.php:4", "全6ファイル strict_types=1 欠落・全2関数で型宣言なし", "strict_types=1全適用・ネイティブ型・PHPStan"],
    ["LOW", "common/documentation", "README.md:1", "見出し1つと1文のみで環境変数・起動・テスト手順が欠落", "Standard Readme構成で構築・検証手順を明記"],
    ["LOW", "common/git_workflow", "(repo root)", ".gitignore不在により機密ファイルや一時成果物の混入危険", "vendor/・.env等を除外する.gitignoreを追加"],
]
tbl.draw_flexible(
    xy=(3, 95),
    column_widths=[11, 29, 24, 41, 35],
    row_heights=[7.0] + [7.7] * 11,
    data=rows,
)

save()
```
