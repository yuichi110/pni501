# 2. アーキテクチャとソースコード構成

`legacy_shop_messy` はクラスや名前空間を一切持たない **手続き型素PHPページスクリプト構造（本番6ファイル・計107 LOC + `Dockerfile` + `README.md`）** である。本章では、(1) ディレクトリ構造と HTML+SQL 混在スパゲッティ・相互 `include_once` 循環、(2) 無認証エンドポイントからの CWE 攻撃データフロー、(3) EOL `php:7.4-apache` root コンテナ実行トポロジの3観点からシステム構造を可視化する。

```drawlib file=arch_tree_and_inventory.png caption="ソースディレクトリ構造ツリーとファイル構成・責務一覧 (全6 PHPファイル・107 LOC)"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import Panel, Table, TreeNode
from drawlib.styles import Styles

setup(width=146, height=82, dpi=150)

left_panel = Panel(
    "リポジトリ構成ツリー",
    "",
    style=Styles.Neutral,
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=10.2),
    icon=phosphor.git_branch,
    icon_style=Styles.White,
    header_height=9.5,
)
left_panel.draw(xy=(2, 3), width=46, height=76)

t_style = Styles.Dark.patch(text_size=8.8)
b_style = Styles.PrimaryBold.patch(text_size=9.0)
d_style = Styles.DangerBold.patch(text_size=8.8)
w_style = Styles.WarningBold.patch(text_size=8.8)

root = TreeNode(
    "legacy_shop_messy/",
    text_style=b_style,
    line_style=Styles.Neutral,
    line_horizontal_margin=0.9,
    line_horizontal_length=1.8,
    line_vertical_margin=3.6,
)
root.add("index.php (29 LOC) [1.00]", text_style=d_style)
root.add("login.php (20 LOC) [1.00]", text_style=d_style)
root.add("product.php (15 LOC) [0.28]", text_style=w_style)
root.add("admin_backup.php (12 LOC) [1.00]", text_style=d_style)
inc_node = root.add("includes/ (相互循環)", text_style=b_style)
inc_node.add("db.php (16 LOC) [1.00]", text_style=d_style)
inc_node.add("helpers.php (15 LOC) [0.86]", text_style=d_style)
root.add("Dockerfile (PHP 7.4 EOL) [1.00]", text_style=d_style)
root.add("README.md (2 lines) [0.21]", text_style=t_style)
root.draw(xy=(4.0, 66.0))

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=8.6),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.0),
    border_style=Styles.NeutralThin,
)
rows = [
    ["ファイルパス", "LOC", "関数・公開責務と主要アーキテクチャ/保安上の問題点"],
    ["index.php", "29", "関数なし | 商品検索・カート復元・動的ページ読込 (HTML+SQL混在)\n[Risk 1.00] Cookie unserialize・SQLi・DAST実証済XSS/LFI"],
    ["login.php", "20", "関数なし | POST管理者認証・session_start()\n[Risk 1.00] extract($_POST)・SQLi・DAST実証 '240610708' 突破"],
    ["product.php", "15", "関数なし | カテゴリ商品取得・プロモーション表示 (HTML+SQL混在)\n[Risk 0.28] $_GET['cat'] SQLi・mysqli_error露出・DAST実証XSS"],
    ["admin_backup.php", "12", "関数なし | アップロードディレクトリのtar圧縮管理画面\n[Risk 1.00] 認可なし・shell_exec(tar) DAST実証済無認証RCE"],
    ["includes/db.php", "16", "get_db_conn() | MySQL接続初期化・認証定数定義\n[Risk 1.00] helpers.php相互循環・DB/Stripe鍵直書き・@抑制"],
    ["includes/helpers.php", "15", "fetch_partner_catalog($endpoint) | 外部カタログcURL取得\n[Risk 0.86] db.php相互循環・SSL検証無効・Timeout欠如・var_dump"],
    ["Dockerfile /\nREADME.md", "6 /\n4", "FROM php:7.4-apache (root実行・OS CVE 12,051件・TRACE/Header欠落)\nREADMEは実質2行のみ (/var/www/html コピー手順1文)"],
]
tbl.draw_flexible(
    xy=(50, 79),
    column_widths=[27, 9, 57],
    row_heights=[7.0, 10.0, 9.8, 9.8, 9.8, 9.8, 9.8, 10.0],
    data=rows,
)

save()
```

## 観点1：HTML+SQL 混在スパゲッティ構造と相互 `include_once` 循環・リスク密度

全4エントリスクリプト（`index.php`, `product.php`, `login.php`, `admin_backup.php`）は手動で `include_once 'includes/db.php';` を呼び出し、単一ファイル内でスーパーグローバル参照・生 SQL クエリ（または `shell_exec`）・インライン HTML 描画を実行している。さらに **`includes/db.php:2` が `includes/helpers.php` を読み込み、`includes/helpers.php:2` が逆に `includes/db.php` を読み込む双方向 `include_once` 循環** が形成されており、関心の分離と単方向レイヤ原則が完全に崩れている。

```drawlib file=arch_layer_hotspot_diagram.png caption="観点1: スパゲッティ依存グラフ（db.php ↔ helpers.php 相互循環）とリスク密度 (HeatmapOverlay)"
from drawlib.canvas import save, setup
from drawlib.charts.heatmap import HeatmapOverlay
from drawlib.diagrams.class_diagram import ClassDiagram, ClassNode
from drawlib.styles import Styles

setup(width=146, height=74, dpi=150)

diag = ClassDiagram(
    node_style=Styles.Neutral,
    header_style=Styles.PrimaryFlat,
    edge_style=Styles.PrimaryBold,
    edge_text_style=Styles.Dark.patch(text_size=8.6),
    style=Styles.Neutral.patch(shape_r=2.0),
    width=124,
    height=66,
    title="観点1: 手続き型 include_once 依存構造 × モジュールリスク密度",
    title_style=Styles.DarkBold.patch(text_size=10.0),
)

n_idx = ClassNode("index.php", stereotype="HTML+SQL Script (29 LOC)", width=36, header_height=7.6, row_height=3.4, header_style=Styles.Danger)
n_idx.add_attribute("$_COOKIE / $_GET", "unserialize / SQLi")
n_idx.add_method("include $_GET['page']", "LFI", "HTML")

n_prd = ClassNode("product.php", stereotype="HTML+SQL Script (15 LOC)", width=36, header_height=7.6, row_height=3.4, header_style=Styles.Warning)
n_prd.add_attribute("$_GET['cat']", "raw SQL concat")
n_prd.add_method("die(mysqli_error)", "err leak", "HTML")

n_lgn = ClassNode("login.php", stereotype="Auth Script (20 LOC)", width=36, header_height=7.6, row_height=3.4, header_style=Styles.Danger)
n_lgn.add_attribute("extract($_POST)", "var pollution")
n_lgn.add_method("md5 == '0e4620...'", "juggling", "bool")

n_adm = ClassNode("admin_backup.php", stereotype="No-Auth Admin (12 LOC)", width=36, header_height=7.6, row_height=3.4, header_style=Styles.Danger)
n_adm.add_attribute("$_POST['backup_dir']", "no session check")
n_adm.add_method("shell_exec('tar ...')", "CMDi", "string")

n_db = ClassNode("includes/db.php", stereotype="Global DB & Secrets (16 LOC)", width=42, header_height=7.6, row_height=3.4, header_style=Styles.Danger)
n_db.add_attribute("DB_PASSWORD / $stripe", "hardcoded secrets")
n_db.add_method("get_db_conn", "", "@mysqli|null")

n_hlp = ClassNode("includes/helpers.php", stereotype="cURL Helper (15 LOC)", width=42, header_height=7.6, row_height=3.4, header_style=Styles.Danger)
n_hlp.add_attribute("SSL_VERIFYPEER=false", "no timeout")
n_hlp.add_method("fetch_partner_catalog", "$endpoint", "mixed")

diag.add(n_idx, xy=(22, 53))
diag.add(n_prd, xy=(63, 53))
diag.add(n_lgn, xy=(104, 53))
diag.add(n_adm, xy=(22, 30))
diag.add(n_db, xy=(64, 15))
diag.add(n_hlp, xy=(105, 15))

diag.connect(n_idx, n_db, directed=True)
diag.connect(n_prd, n_db, directed=True)
diag.connect(n_lgn, n_db, directed=True)
diag.connect(n_adm, n_db, directed=True)
diag.connect(n_db, n_hlp, directed=True)
diag.connect(n_hlp, n_db, directed=True)
diag.draw(xy=(3, 4))

ov = HeatmapOverlay(
    min_style=Styles.Success,
    max_style=Styles.Danger,
    width=124,
    height=66,
    min_value=0.0,
    max_value=1.0,
    default_radius=13.5,
    max_alpha=0.30,
    show_contour_lines=False,
)
ov.add_spot(xy=(22, 53), value=1.00, radius=14.5)
ov.add_spot(xy=(63, 53), value=0.28, radius=12.0)
ov.add_spot(xy=(104, 53), value=1.00, radius=14.5)
ov.add_spot(xy=(22, 30), value=1.00, radius=14.5)
ov.add_spot(xy=(64, 15), value=1.00, radius=15.0)
ov.add_spot(xy=(105, 15), value=0.86, radius=14.0)
ov.draw(xy=(3, 4))
ov.draw_colorbar(
    xy=(131, 13),
    text_style=Styles.Dark.patch(text_size=9.0),
    length=44.0,
    thickness=2.6,
    orientation="vertical",
    label="Risk",
)

save()
```

## 観点2・観点3：無認証エンドポイント攻撃データフローと EOL `php:7.4-apache` コンテナ実行トポロジ

公開ドキュメントルート `/var/www/html/` 直下にすべての `.php` ファイルが配置されており（`Dockerfile:4 COPY . /var/www/html/`）、外部からの未検証 HTTP リクエストが認可ガードや型検証を経由せず危険なシンクへ直結している。加えて Apache ワーカーが `root` 権限で動作し、固定ファイル `/tmp/shop_backup.tar.gz` への排他なし書き込みやタイムアウト未設定の外部通信を行うため、セキュリティ侵害とサービス停止の双方に対して無防備な実行トポロジとなっている。

```drawlib file=arch_attack_dataflow_roadmap.png caption="観点2: 無認証 .php エンドポイントから危険シンクへの攻撃データフロー"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import Roadmap
from drawlib.styles import Styles

setup(width=146, height=58, dpi=150)

flow = Roadmap(
    style=Styles.Neutral,
    text_style=Styles.DarkBold.patch(text_size=9.3),
    description_style=Styles.Dark.patch(text_size=8.7),
    spine_style=Styles.Danger,
    badge_style=Styles.Danger,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.0),
    direction="horizontal",
    spacing=2.2,
)
flow.add(
    "1. 無認証 HTTP 到達",
    "全4スクリプト auth_hint=NONE\n$_GET/$_POST/$_COOKIE直参照",
    badge_text="Entry",
    style=Styles.WarningNeutral,
    badge_style=Styles.Warning,
    icon=phosphor.globe,
    icon_style=Styles.Warning,
)
flow.add(
    "2. 変数汚染・認証突破",
    "login.php: extract($_POST)\nmd5() == '0e4620...' 型強制一致",
    badge_text="Auth",
    style=Styles.DangerNeutral,
    badge_style=Styles.Danger,
    icon=phosphor.lock_key,
    icon_style=Styles.Danger,
)
flow.add(
    "3. SQLi & Object注入",
    "index/product/login 生SQL連結\nshop_cart Cookie unserialize()",
    badge_text="Data",
    style=Styles.DangerNeutral,
    badge_style=Styles.Danger,
    icon=phosphor.database if hasattr(phosphor, "database") else phosphor.warning,
    icon_style=Styles.Danger,
)
flow.add(
    "4. LFI & root RCE",
    "index.php: include $_GET[page]\nadmin_backup: shell_exec(tar)",
    badge_text="RCE",
    style=Styles.DangerNeutral,
    badge_style=Styles.Danger,
    icon=phosphor.terminal_window if hasattr(phosphor, "terminal_window") else phosphor.bug,
    icon_style=Styles.Danger,
)
flow.draw(xy=(3, 5), width=140, height=48)

save()
```

```drawlib file=arch_container_runtime_topology.png caption="観点3: EOL php:7.4-apache root コンテナ実行トポロジとバッキングサービス接続境界"
from drawlib.canvas import save, setup
from drawlib.diagrams.class_diagram import ClassDiagram, ClassNode
from drawlib.styles import Styles

setup(width=146, height=62, dpi=150)

topo = ClassDiagram(
    node_style=Styles.Neutral,
    header_style=Styles.PrimaryFlat,
    edge_style=Styles.Danger,
    edge_text_style=Styles.Dark.patch(text_size=8.6),
    style=Styles.Neutral.patch(shape_r=2.0),
    width=140,
    height=54,
    title="観点3: コンテナ実行境界 (FROM php:7.4-apache / Debian 11.5 / USER root)",
    title_style=Styles.DarkBold.patch(text_size=10.0),
)

n_cli = ClassNode("External HTTP Client", stereotype="Untrusted Network", width=34, header_height=7.4, row_height=3.4, header_style=Styles.Warning)
n_cli.add_attribute("Port 80 (HTTP)", "No WAF / No CSRF")

n_ctr = ClassNode("Container: php:7.4-apache", stereotype="USER root | OS CVE 12,051", width=44, header_height=7.4, row_height=3.4, header_style=Styles.Danger)
n_ctr.add_attribute("/var/www/html/*", "includes/db.php exposed")
n_ctr.add_attribute("/tmp/shop_backup.tar.gz", "shared race file")
n_ctr.add_method("apache2 + mod_php + tar", "DS-0002", "root UID 0")

n_sql = ClassNode("MySQL 127.0.0.1", stereotype="Backing DB: legacy_shop", width=36, header_height=7.4, row_height=3.4, header_style=Styles.PrimaryFlat)
n_sql.add_attribute("user: shop_root", "hardcoded password")
n_sql.add_method("@mysqli_connect", "no timeout", "products/admins")

n_api = ClassNode("Partner Catalog API", stereotype="External HTTPS Endpoint", width=36, header_height=7.4, row_height=3.4, header_style=Styles.Danger)
n_api.add_attribute("?token=PARTNER_FEED...", "token in URL query")
n_api.add_method("curl_exec", "SSL_VERIFYPEER=false", "no timeout")

topo.add(n_cli, xy=(22, 28))
topo.add(n_ctr, xy=(71, 28))
topo.add(n_sql, xy=(120, 40))
topo.add(n_api, xy=(120, 15))

topo.connect(n_cli, n_ctr, directed=True)
topo.connect(n_ctr, n_sql, directed=True)
topo.connect(n_ctr, n_api, directed=True)
topo.draw(xy=(3, 4))

save()
```
