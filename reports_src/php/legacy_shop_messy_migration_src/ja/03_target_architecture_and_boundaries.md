# 3. To-Be ターゲットアーキテクチャ設計（Strangler Fig & Modular Laravel 11）

前段の **Nginx Strangler Router** が移行済み URL パスを PHP 8.3-FPM（Laravel 11）へ、未移行パスのみをレガシーコンテナへ振り分けることで、ビッグバン凍結なしに段階移行する。Laravel 11 内部は `Http（Controller / FormRequest） -> Actions（UseCase） -> Domain Contracts（Port） <- Infrastructure（Eloquent / Redis / Http / Process）` の単方向アーキテクチャで構成する。

```drawlib file=php_strangler_to_be_architecture.png caption="Strangler Fig ルーティングと Modular Laravel 11 ターゲットアーキテクチャ図"
from drawlib.canvas import save, setup
from drawlib.diagrams.class_diagram import ClassDiagram, ClassNode
from drawlib.styles import Styles

setup(width=146, height=92, dpi=150)

diag = ClassDiagram(
    node_style=Styles.Neutral,
    header_style=Styles.PrimaryFlat,
    edge_style=Styles.PrimaryBold,
    edge_text_style=Styles.Dark.patch(text_size=8.4),
    style=Styles.Neutral.patch(shape_r=2.0),
    width=140,
    height=84,
    title="To-Be Strangler Fig Proxy & Modular Laravel 11 (Http -> Actions -> Domain <- Infra)",
    title_style=Styles.DarkBold.patch(text_size=9.6),
)

nx = ClassNode(
    "Nginx Strangler Proxy",
    stereotype="Route-by-Route Cutover",
    width=40,
    header_height=8.0,
    row_height=3.5,
    header_style=Styles.PrimaryNeutral,
)
nx.add_method("route", "/product, /, /login, /admin", "Laravel 11")

http_l = ClassNode(
    "Controllers & FormRequests",
    stereotype="App\\Http + Escaped Blade",
    width=42,
    header_height=8.0,
    row_height=3.5,
    header_style=Styles.PrimaryNeutral,
)
http_l.add_method("Product / Store / Auth", "DTO", "Response")

act_l = ClassNode(
    "UseCase Actions",
    stereotype="App\\Actions (strict_types=1)",
    width=42,
    header_height=8.0,
    row_height=3.5,
    header_style=Styles.PrimaryNeutral,
)
act_l.add_method("AuthWithRehash", "Credentials", "User")

dom_l = ClassNode(
    "Domain Entities & Contracts",
    stereotype="App\\Domain (Pure Readonly)",
    width=46,
    header_height=8.0,
    row_height=3.5,
    header_style=Styles.SuccessNeutral,
)
dom_l.add_method("ProductRepo / CartStore / PartnerPort", "VO", "Result")

leg_l = ClassNode(
    "Legacy PHP Fallback",
    stereotype="Retired in Phase 4 (PR-09)",
    width=38,
    header_height=8.0,
    row_height=3.5,
    header_style=Styles.DangerNeutral,
)
leg_l.add_attribute("Unmigrated routes only", "0 routes at P4")

inf_db = ClassNode(
    "Eloquent / PDO MySQL 8",
    stereotype="App\\Infrastructure\\Persistence",
    width=42,
    header_height=8.0,
    row_height=3.5,
    header_style=Styles.WarningNeutral,
)
inf_db.add_attribute("100% Prepared Bindings", "Zero SQLi")

inf_rd = ClassNode(
    "Redis 7 Session & CartStore",
    stereotype="App\\Infrastructure\\Redis",
    width=42,
    header_height=8.0,
    row_height=3.5,
    header_style=Styles.WarningNeutral,
)
inf_rd.add_attribute("HttpOnly Session + TTL 7d", "Zero unserialize")

inf_io = ClassNode(
    "HttpClient & Process Backup",
    stereotype="App\\Infrastructure\\Http & Jobs",
    width=42,
    header_height=8.0,
    row_height=3.5,
    header_style=Styles.WarningNeutral,
)
inf_io.add_attribute("TLS Verify + Timeout 5s", "Symfony Process[]")

diag.add(nx, xy=(23, 68))
diag.add(http_l, xy=(71, 68))
diag.add(act_l, xy=(117, 68))
diag.add(leg_l, xy=(23, 41))
diag.add(dom_l, xy=(94, 41))
diag.add(inf_db, xy=(24, 13))
diag.add(inf_rd, xy=(72, 13))
diag.add(inf_io, xy=(118, 13))

diag.connect(nx, http_l, directed=True)
diag.connect(nx, leg_l, directed=True, style=Styles.DangerBold)
diag.connect(http_l, act_l, directed=True)
diag.connect(act_l, dom_l, directed=True)
diag.connect(inf_db, dom_l, directed=True)
diag.connect(inf_rd, dom_l, directed=True)
diag.connect(inf_io, dom_l, directed=True)
diag.draw(xy=(3, 4))

save()
```

## 既存スクリプト・境界タッチポイントから Laravel 11 コンポーネントへのマッピング

```drawlib file=php_component_mapping_table.png caption="レガシー PHP 全6ファイルから Modular Laravel 11 への完全移行マッピング"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=104, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=8.5),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.0),
    border_style=Styles.NeutralThin,
)
rows = [
    ["As-Is ファイル", "Strangler 順序", "To-Be Laravel コンポーネント", "根絶される CWE 脆弱性・状態分離"],
    [
        "includes/db.php\n(@mysqli_connect)",
        "Phase 1 基盤\n(Infra)",
        "config/database.php &\nEloquent*Repository",
        "DB_PASSWORD / Stripe 秘密鍵を .env 化し\nglobal $LAST_DB_ERR と @ 演算子を撤去。",
    ],
    [
        "includes/helpers.php\n(curl_init / debug)",
        "Phase 1 基盤\n(Infra)",
        "HttpPartnerCatalogClient\n-> PartnerCatalogPort",
        "SSL 検証無効化 (CWE-295) と URL トークン露出\nを廃止し TLS 強制 + 5秒 Timeout 化。",
    ],
    [
        "product.php\n(?cat= / ?promo_html=)",
        "Phase 2\nRoute #1",
        "ProductController +\nProductFilterRequest",
        "SQLi (CWE-89) を PDO バインドで解消し、\nXSS (CWE-79) を Blade 自動エスケープ化。",
    ],
    [
        "index.php\n(shop_cart / ?q= / ?page=)",
        "Phase 2\nRoute #2",
        "StorefrontController +\nRedisCartStore (TTL 7d)",
        "Cookie unserialize (CWE-502) を Redis 化し\n?page= 動的 include LFI (CWE-98) を封鎖。",
    ],
    [
        "login.php\n(extract / md5 / ==)",
        "Phase 3\nRoute #3",
        "AuthenticateUserWithRehash\nAction + Redis Session",
        "extract (CWE-621) とマジックハッシュ ==\n(CWE-697) を撤去し透過 bcrypt 再ハッシュ。",
    ],
    [
        "admin_backup.php\n(shell_exec)",
        "Phase 3\nRoute #4",
        "Admin\\BackupController +\nBackupDatabaseJob",
        "shell_exec (CWE-78) を廃止し Admin Gate +\nCSRF + Symfony Process 配列引数へ置換。",
    ],
]
tbl.draw_flexible(
    xy=(3, 101),
    column_widths=[32, 22, 38, 48],
    row_heights=[8.0, 14.5, 14.5, 14.5, 15.0, 15.0, 14.5],
    data=rows,
)

save()
```
