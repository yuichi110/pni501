# 6. セキュリティ・脆弱性・サプライチェーン分析

本章では、Trivy (`0.69.3`) によるコンテナイメージ・ファイルシステム検査（`security_scan`）、PHP AST によるハードコード秘密情報・13件の CWE 危険シンク・無認証 HTTP エンドポイント境界解析、および隔離ループバックコンテナ上で `.pni/pentests/examples/php/legacy_shop_messy/` 全19プローブを実行した動的 Web ペネトレーションテスト（`web_pentest` / SEC-06）の評価結果を統合して詳述する。

```drawlib file=security_cve_and_misconfig.png caption="ライブDAST (10 FAIL)・AST CWE危険シンク・秘密情報・IaC不備およびOS層CVE (12,051件) 内訳"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.icons import phosphor
from drawlib.smartarts import KpiCards
from drawlib.styles import Styles

setup(width=146, height=70, dpi=150)

chart = BarChart(
    axis_line_style=Styles.Neutral,
    grid_style=Styles.NeutralThin,
    axis_text_style=Styles.DarkBold.patch(text_size=8.8),
    value_text_style=Styles.DarkBold.patch(text_size=8.5),
    background_style=Styles.Neutral.patch(shape_r=2.0),
    categories=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
    orientation="vertical",
    bar_mode="group",
    bar_width_ratio=0.72,
    bar_r=0.8,
    width=80,
    height=50,
    title="アプリ層DAST・SAST・秘密情報・IaC 深刻度別検出数",
    title_style=Styles.DarkBold.patch(text_size=9.2),
)
chart.add_series("ライブDAST (10)", [2, 4, 2, 2], style=Styles.Danger)
chart.add_series("AST CWEシンク (13)", [0, 12, 1, 0], style=Styles.Warning)
chart.add_series("Secret & 無認証API", [2, 4, 0, 0], style=Styles.Primary)
chart.add_series("Dockerfile IaC", [0, 1, 0, 1], style=Styles.Secondary if hasattr(Styles, "Secondary") else Styles.Dark)
chart.draw(xy=(4, 13))
chart.draw_legend(
    xy=(5.0, 4.5),
    text_style=Styles.DarkBold.patch(text_size=7.9),
    orientation="horizontal",
    item_gap=4.5,
)

kpis = KpiCards(
    style=Styles.Neutral,
    metric_style=Styles.DangerBold.patch(text_size=12.0),
    text_style=Styles.DarkBold.patch(text_size=9.5),
    description_style=Styles.Dark.patch(text_size=8.6),
    metric_width_ratio=0.36,
    spacing=2.8,
)
kpis.add(
    "12,051 件",
    "php:7.4-apache OS CVE",
    "CRIT 62 / HIGH 1,940 / MED 7,496",
    icon=phosphor.bug,
    accent_style=Styles.Danger,
    icon_style=Styles.Danger,
)
kpis.add(
    "10 / 19 FAIL",
    "ライブ DAST (web_pentest)",
    "CRIT 2 (RCE・0e突破) / HIGH 4",
    icon=phosphor.x_circle,
    accent_style=Styles.Danger,
    metric_style=Styles.DangerBold.patch(text_size=11.6),
    icon_style=Styles.Danger,
)
kpis.add(
    "RCE & 0e突破",
    "実HTTPでカナリア・管理者奪取",
    "PNI_RCE_CANARY_8842 / 240610708",
    icon=phosphor.lock_key,
    accent_style=Styles.Danger,
    metric_style=Styles.DangerBold.patch(text_size=11.0),
    icon_style=Styles.Danger,
)
kpis.draw(xy=(87, 7), width=56, height=56, columns=1)

save()
```

## セキュリティゲート（SEC-01〜SEC-05）およびサプライチェーンの詳細評価

- **サプライチェーン欠落と EOL `php:7.4-apache` コンテナの `12,051` OS 層 CVE (`SEC-01` / `SEC-02`)**: `composer.json` / `composer.lock` が存在しないためアプリ依存パッケージ CVE は `0` 件だが、`Dockerfile:1` の `FROM php:7.4-apache`（2022年11月 EOL・Debian 11.5 凍結状態）に対する Trivy イメージスキャンにより、**計 `12,051` 件（`CRITICAL: 62`, `HIGH: 1,940`, `MEDIUM: 7,496`, `LOW: 2,296`）** の OS パッケージ脆弱性が検出された。代表例として `apache2@2.4.54-1~deb11u1` の HTTP リクエストスプリッティング/mod_rewrite 脆弱性（`CVE-2023-25690`, `CVE-2024-38474`, `CVE-2024-38476`、いずれも CVSS 9.8）や `curl`/`libcurl4@7.74.0` の SOCKS5 ヒープオーバーフロー（`CVE-2023-38545`、CVSS 9.8）が含まれる。さらに Trivy IaC で `DS-0002`（`HIGH`：`root` 実行）と `DS-0026`（`LOW`：`HEALTHCHECK` 不在）が検出された。
- **ハードコードされた DB パスワード・Stripe Live 秘密鍵 (`SEC-03` / CWE-798)**: `includes/db.php:6` に本番 MySQL パスワード定数（`DB_PASSWORD = '[REDACTED]'`）、同 `7` 行目に Stripe Live API シークレットキー（`$stripe_api_secret = 'sk_live_[REDACTED]'`、Trivy Secret Scanner が `CRITICAL` `stripe-secret-token` として検出）が平文で埋め込まれており、コンテナ内の `/var/www/html/includes/db.php` にそのままコピーされている。
- **CWE 危険コードシンク 13件と無認証管理エンドポイント (`SEC-04` / `SEC-05`)**:
  - **CWE-78 OS コマンドインジェクション (`admin_backup.php:6`)**: セッション確認（`$_SESSION['is_admin']`）も CSRF 対策もない公開フォームから `$_POST['backup_dir']` を `shell_exec("tar -czf /tmp/shop_backup.tar.gz " . $target)` へ直接連結しており、未認証のまま任意 OS コマンドを実行できる。
  - **CWE-98 LFI (`index.php:25`) & CWE-502 `unserialize` (`index.php:4`)**: `include $_GET['page'] . '.php';` による任意 PHP ファイル実行・パストラバーサル、および改ざん可能な `$_COOKIE['shop_cart']` の `unserialize()`（`allowed_classes` 制限なし）による PHP Object Injection が存在する。
  - **CWE-89 SQLi（3箇所）& CWE-79 反射型 XSS（3箇所）**: `index.php:8` (`$_GET['q']`)、`product.php:6-7` (`$_GET['cat']`)、`login.php:12` (`$_POST['username']`) がすべて文字列連結 SQL を `mysqli_query()` で実行し、`index.php:21`、`product.php:14` (`$_GET['promo_html']`)、`login.php:19` が未エスケープのまま HTML 出力している。
  - **CWE-621 / CWE-327 / CWE-697 マジックハッシュ認証バイパス (`login.php:6-17`)**: `extract($_POST)` による変数汚染、ソルトなし `md5()`、および初期値 `$expected_hash = '0e462097431906509019562988736854'` と緩い比較 `$pw_hash == $expected_hash` の組み合わせにより、`'240610708'` 等のマジックハッシュ入力で `0 == 0` が成立し管理者セッションを奪取できる。
  - **CWE-295 TLS 証明書検証無効化 (`includes/helpers.php:9`)**: `CURLOPT_SSL_VERIFYPEER => false` により HTTPS 証明書検証を無効化した上で、クエリパラメータ `?token=` にトークンを平文付与している。

## 動的Webペネトレーションテスト (`web_pentest` / `.pni/pentests/`, SEC-06)

隔離ループバック環境（`127.0.0.1`）に対して `.pni/pentests/examples/php/legacy_shop_messy/`（`test_baseline_http.py`, `test_target_surface.py`, `test_app_probes.py`）の計 `19` プローブを実行した結果、**`status = "failed"`（`9` PASS / `10` FAIL、`CRITICAL: 2`・`HIGH: 4`・`MEDIUM: 2`・`LOW: 2`、実行時間 `4.31s`）** となり、SAST で検出された高リスク経路がライブ HTTP リクエスト単発で実際に成立することが決定的に証明された。特に無認証 `POST /admin_backup.php` におけるシェル注入カナリア `PNI_RCE_CANARY_8842` の実行出力（`CWE-78` CRITICAL）および `POST /login.php` における `'240610708'` マジックハッシュ送信での `'Logged in as admin'` 奪取（`CWE-697` CRITICAL）は、外部公開と同時に即座に侵害されることを示している。

```drawlib file=security_web_pentest_probes.png caption="動的Webペネトレーションテスト (.pni/pentests/ 全19プローブ: 9 PASS / 10 FAIL) ライブ実証結果"
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
    ["判定 / 深刻度", "プローブテスト / CWE", "対象エンドポイント", "ライブHTTP応答エビデンス", "修正・ゲート化方針"],
    ["FAIL\n[CRITICAL]", "test_app_probes.py\nCWE-78 (OS CMDi)", "POST /admin_backup.php\n(admin_backup.php:6)", "未認証POST backup_dir で注入した\necho カナリア PNI_RCE_CANARY_8842 出力", "shell_exec撤廃・Admin認可+CSRF・\nSymfony Process配列引数Job化"],
    ["FAIL\n[CRITICAL]", "test_app_probes.py\nCWE-697 (Auth突破)", "POST /login.php\n(login.php:17)", "password='240610708' 送信で 0==0 成立\nHTTP 200 'Logged in as admin' 応答", "0e定数と==比較廃止・Fail-Closed・\npassword_verify(bcrypt/Argon2)化"],
    ["FAIL\n[HIGH]", "test_target_surface.py\nCWE-306 (無認証操作)", "POST /admin_backup.php\n(admin_backup.php:4)", "セッションCookieなしの POST が\n401/403 拒否されず HTTP 200 応答", "管理系ルートへ認証ミドルウェア\nおよびCSRFトークン検証を強制"],
    ["FAIL\n[HIGH]", "test_target_surface.py\nCWE-22 (LFI露出)", "GET /index.php\n(index.php:25)", "page=../../../../etc/passwd 指定で\nHTTP 200 \"Failed opening '\" 露出", "動的include撤廃・固定ルートマップ\nおよび display_errors=Off 徹底"],
    ["FAIL\n[HIGH x2]", "test_target_surface &\napp_probes (CWE-79)", "GET /index.php & /product\n(index:21, product:14)", "<pni-xss-canary-7f3a> および promo_html\n=<pni-promo-xss-9a2b> が生HTML反射", "Blade/Twig自動エスケープ導入と\npromo_html生HTMLクエリ仕様の廃止"],
    ["FAIL\n[MED x2]", "test_baseline_http.py\nCWE-1021 / CWE-693", "GET / & TRACE /\n(Dockerfile / Web層)", "HTML応答にX-Frame-Options/CSP欠落\nおよび TRACE / -> HTTP 200 応答", "X-Frame-Options: DENY / CSP付与\n・本番SAPIでTRACEメソッド405遮断"],
    ["FAIL\n[LOW x2]", "test_baseline_http.py\nCWE-200 / CWE-693", "GET /\n(Dockerfile / Web層)", "X-Powered-By: PHP/8.3.36 露出\nX-Content-Type-Options=<absent>", "expose_php=Off 設定と全応答への\nX-Content-Type-Options: nosniff付与"],
    ["PASS (9件)\n[基準確認]", "baseline & surface\n(.env / .git / 404等)", "GET /.env, /.git/HEAD,\ncomposer.json 他", "機密ドットファイル非露出・異常長入力\nでの500クラッシュなし (9/19 PASS)", "移行後も全19プローブ 100% PASS を\nCI リリースゲートとして継続監視"],
]
tbl.draw_flexible(
    xy=(3, 103),
    column_widths=[19, 27, 27, 38, 29],
    row_heights=[7.0] + [11.5] * 8,
    data=rows,
)

save()
```

```drawlib file=security_boundary_details_table.png caption="SEC-01〜SEC-05 セキュリティゲート・主要CVE・CWE危険シンク詳細一覧"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=118, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=8.4),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=8.8),
    border_style=Styles.NeutralThin,
)
rows = [
    ["ゲート / 深刻度", "CWE / CVE / ID", "対象箇所", "脆弱性メカニズム・攻撃影響", "必須緩和・修正策"],
    ["SEC-04 / 05 / 06\n[CRITICAL]", "CWE-78 / CWE-306\nCommand Inj.", "admin_backup\n.php:4-6", "無認証POST backup_dir を shell_exec\nへ直結しDASTでもRCEカナリア実証", "認可+CSRF必須化・シェル呼出廃止\n(ZipArchive / 固定ジョブ化)"],
    ["SEC-04 / 06\n[CRITICAL]", "CWE-98 / CWE-502\nLFI & Unserialize", "index.php:4,\nindex.php:25", "Cookie unserialize() と動的 include\n$_GET['page'].'.php' (DAST LFI実証)", "json_decode + HMAC署名へ変更・\nmatchホワイトリストルーティング"],
    ["SEC-04\n[CRITICAL]", "CWE-89 (x3)\nSQL Injection", "index:8 / login:12\nproduct.php:6-7", "3画面で未エスケープ入力をSELECT文\nへ直接連結し全件抽出・認証突破", "PDO (EMULATE_PREPARES=false)\nプリペアドステートメント全面適用"],
    ["SEC-04 / 06\n[CRITICAL]", "CWE-697 / 327 /\n621 Auth Bypass", "login.php:6-17", "extract + md5 + 緩い == '0e4620...'\n('240610708' でDAST管理者奪取実証)", "extract削除・password_hash(Argon2)\n+ password_verify・Fail-Closed化"],
    ["SEC-03\n[CRITICAL]", "CWE-798 / Trivy\nstripe-secret-token", "includes/db.php\n:6-7", "DB_PASSWORDとStripe本番秘密鍵\n([REDACTED])をソースに平文埋込", "両クレデンシャル即時ローテーション\n・Secret Manager / 環境変数注入"],
    ["SEC-01\n[CRITICAL]", "CVE-2023-25690\nCVE-2023-38545他", "Dockerfile:1\n(php:7.4-apache)", "EOL Debian 11.5層に OS CVE 12,051件\n(CRIT 62 / HIGH 1,940, CVSS 9.8)", "php:8.3-apache-bookworm へ刷新し\nダイジェスト固定・定期再ビルド"],
    ["SEC-04 / 06\n[HIGH]", "CWE-79 (x3)\nReflected XSS", "index:21 / login:19\nproduct.php:14", "q・promo_html・username を生echo\n(DASTでカナリアHTMLタグ反射実証)", "Twig/Blade自動エスケープまたは\nhtmlspecialchars(ENT_QUOTES)徹底"],
    ["SEC-04\n[HIGH]", "CWE-295\nInsecure TLS", "includes/helpers\n.php:7-9", "CURLOPT_SSL_VERIFYPEER=false かつ\nURLクエリにトークン付与(MITM漏洩)", "VERIFYPEER=true・VERIFYHOST=2・\nAuthorizationヘッダ・Timeout設定"],
    ["SEC-02 / 06\n[HIGH / MED]", "Trivy DS-0002 /\nCWE-1021 / 693", "Dockerfile:1-5", "root稼働・HEALTHCHECK不在に加え\nCSP/XFO/nosniff欠落・TRACE有効", "USER www-data・HEALTHCHECK定義\n・セキュリティヘッダ一括付与"],
]
tbl.draw_flexible(
    xy=(3, 115),
    column_widths=[19, 24, 23, 39, 35],
    row_heights=[7.0] + [11.5] * 9,
    data=rows,
)

save()
```
