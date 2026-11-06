# 2. As-Is 依存グラフ解析・移行 Wave・暗黙の外部契約

`migration_analyze` による PHP `include_once` 依存グラフ解析の結果、共通インフラの **`includes/db.php` と `includes/helpers.php` が相互 `include_once` する循環依存（Wave 3 SCC）** を形成し、上位の4つのエントリスクリプト（`index.php`, `product.php`, `login.php`, `admin_backup.php`：Wave 4）がそれにぶら下がる構造が特定された。

```drawlib file=php_waves_and_cycle_diagram.png caption="As-Is 手続き型 include 依存グラフと db.php <-> helpers.php 循環切断ポイント"
from drawlib.canvas import save, setup
from drawlib.diagrams.class_diagram import ClassDiagram, ClassNode
from drawlib.styles import Styles

setup(width=146, height=84, dpi=150)

diag = ClassDiagram(
    node_style=Styles.Neutral,
    header_style=Styles.PrimaryFlat,
    edge_style=Styles.PrimaryBold,
    edge_text_style=Styles.DarkBold.patch(text_size=8.5),
    style=Styles.Neutral.patch(shape_r=2.0),
    width=140,
    height=76,
    title="As-Is include 依存構造 (Wave 3 循環インフラ & Wave 4 エントリスクリプト群)",
    title_style=Styles.DarkBold.patch(text_size=9.8),
)

e_prod = ClassNode(
    "product.php",
    stereotype="Wave 4: Route #1",
    width=32,
    header_height=8.0,
    row_height=3.5,
    header_style=Styles.PrimaryNeutral,
)
e_prod.add_attribute("$_GET[cat, promo]", "SQLi/XSS")

e_idx = ClassNode(
    "index.php",
    stereotype="Wave 4: Route #2",
    width=34,
    header_height=8.0,
    row_height=3.5,
    header_style=Styles.WarningNeutral,
)
e_idx.add_attribute("$_COOKIE['shop_cart']", "unserialize")
e_idx.add_attribute("$_GET['q','page']", "SQLi/LFI")

e_login = ClassNode(
    "login.php",
    stereotype="Wave 4: Route #3",
    width=34,
    header_height=8.0,
    row_height=3.5,
    header_style=Styles.DangerNeutral,
)
e_login.add_attribute("extract($_POST)", "md5 + ==")

e_adm = ClassNode(
    "admin_backup.php",
    stereotype="Wave 4: Route #4",
    width=34,
    header_height=8.0,
    row_height=3.5,
    header_style=Styles.DangerNeutral,
)
e_adm.add_attribute("$_POST['backup_dir']", "shell_exec")

c_db = ClassNode(
    "includes/db.php",
    stereotype="Wave 3: SCC Cycle",
    width=46,
    header_height=8.0,
    row_height=3.5,
    header_style=Styles.DangerNeutral,
)
c_db.add_attribute("DB_PASSWORD / stripe_secret", "hardcoded")
c_db.add_method("get_db_conn", "", "@mysqli_connect")

c_hlp = ClassNode(
    "includes/helpers.php",
    stereotype="Wave 3: SCC Cut Source",
    width=46,
    header_height=8.0,
    row_height=3.5,
    header_style=Styles.WarningNeutral,
)
c_hlp.add_attribute("PARTNER_FEED_TOKEN", "getenv")
c_hlp.add_method("fetch_partner_catalog", "url", "curl (SSL off)")

diag.add(e_prod, xy=(19, 60))
diag.add(e_idx, xy=(54, 59))
diag.add(e_login, xy=(90, 60))
diag.add(e_adm, xy=(125, 60))
diag.add(c_db, xy=(44, 16))
diag.add(c_hlp, xy=(102, 16))

diag.connect(e_prod, c_db, directed=True)
diag.connect(e_idx, c_db, directed=True)
diag.connect(e_idx, c_hlp, directed=True)
diag.connect(e_login, c_db, directed=True)
diag.connect(e_adm, c_db, directed=True)
diag.connect(c_db, c_hlp, directed=True, style=Styles.DangerBold)
diag.connect(c_hlp, c_db, directed=True, style=Styles.DangerBold)
diag.draw(xy=(3, 4))

save()
```

## 暗黙のスーパーグローバル入出力契約・秘密定数インベントリ（自動マスク済み）

AST 解析により `$_GET` / `$_POST` / `$_COOKIE` / `define` / `getenv` から全スクリプトの暗黙パラメータ契約を抽出した（機密キー値は `<REDACTED>` マスク済み）。

```drawlib file=php_implicit_contracts_table.png caption="AST 抽出された暗黙のリクエスト/Cookie 契約と環境設定定数 (機密値マスク済み)"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=104, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=8.6),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.0),
    border_style=Styles.NeutralThin,
)
rows = [
    ["エンドポイント / 定数", "キー名 (方向)", "既定値 / マスク", "抽出箇所", "Laravel 11 移行・無害化マッピング"],
    [
        "GET /product.php",
        "cat, promo_html\n(GET Input)",
        "\"featured\" /\n\"Special Sale\"",
        "product.php\n:L4, L14",
        "ProductFilterRequest (?cat= 維持) +\npromo_code 許可リスト Blade 描画",
    ],
    [
        "GET /index.php",
        "q, page (GET)\nshop_cart (Cookie)",
        "null (未検証)",
        "index.php\n:L4, L5, L24",
        "?q= PDO 検索維持・?page= 固定 301・\nCookie unserialize 廃止→RedisCartStore",
    ],
    [
        "POST /login.php",
        "username,\npassword (POST)",
        "<REDACTED>",
        "login.php\n:L7, L11",
        "LoginRequest 厳密型検証 + extract 廃止 +\nDual-Verify bcrypt 透過再ハッシュ",
    ],
    [
        "POST /admin_backup.php",
        "backup_dir\n(POST Input)",
        "null (CMDi 危険)",
        "admin_backup\n:L4",
        "ユーザーパス指定を廃止し固定 Storage\nディスクへの非同期 BackupDatabaseJob 化",
    ],
    [
        "includes/db.php\n(define 定数)",
        "DB_HOST, DB_USER,\nDB_PASSWORD",
        "127.0.0.1 /\n<REDACTED>",
        "includes/db.php\n:L4-L6",
        ".env (DB_HOST / DB_USERNAME / DB_PASSWORD)\n+ config/database.php へ外部化",
    ],
    [
        "includes/helpers.php\n(getenv / GET)",
        "PARTNER_FEED_TOKEN\n/ ?debug",
        "null / \"\"",
        "helpers.php\n:L6, L11",
        "services.partner.token 設定注入 (Header\n送信) + 本番 ?debug var_dump 完全削除",
    ],
]
tbl.draw_flexible(
    xy=(3, 101),
    column_widths=[30, 26, 22, 22, 40],
    row_heights=[8.0, 14.5, 15.0, 14.5, 14.5, 14.5, 14.5],
    data=rows,
)

save()
```
