# 5. 「仕様かバグか」ステークホルダー意思決定ログ（Decision Log）

レガシー PHP の脆弱性修正では、**セキュリティ無害化と既存ユーザー体験・ブックマーク互換のトレードオフ**が必ず発生する（例：既存データベース内の MD5 パスワードハッシュを単純に無効化すると全会員がログイン不能になり、移行瞬間の旧ブラウザ Cookie を `unserialize` せずにどう扱うかでカート挙動が変わる）。下表の4論点をステークホルダー承認ゲートとして管理する。

```drawlib file=php_dual_verify_rehash_flow.png caption="会員ロックアウトゼロを実現する MD5 -> bcrypt 透過再ハッシュ (DEC-01) フロー"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import Roadmap
from drawlib.styles import Styles

setup(width=146, height=56, dpi=150)

rm = Roadmap(
    style=Styles.Neutral,
    text_style=Styles.DarkBold.patch(text_size=9.3),
    description_style=Styles.Dark.patch(text_size=8.4),
    spine_style=Styles.PrimaryBold,
    badge_style=Styles.Primary,
    badge_text_style=Styles.WhiteBold.patch(text_size=8.8),
    direction="horizontal",
    spacing=3.0,
)
rm.add(
    "1. アルゴリズム判定",
    "password_algo == bcrypt\nなら標準 Hash::check 実行",
    badge_text="Check",
    style=Styles.PrimaryNeutral,
    badge_style=Styles.Primary,
    icon=phosphor.magnifying_glass,
    icon_style=Styles.Primary,
)
rm.add(
    "2. 旧 MD5 定数時間照合",
    "legacy_md5 なら hash_equals\nで厳密照合 (== は完全廃止)",
    badge_text="Verify",
    style=Styles.WarningNeutral,
    badge_style=Styles.Warning,
    icon=phosphor.shield_check,
    icon_style=Styles.Warning,
)
rm.add(
    "3. 透過 bcrypt 昇格",
    "照合成功直後に Hash::make\nで bcrypt 保存 + Session 再生成",
    badge_text="Upgrade",
    style=Styles.SuccessNeutral,
    badge_style=Styles.Success,
    icon=phosphor.lock_key,
    icon_style=Styles.Success,
)
rm.draw(xy=(4, 5), width=138, height=46)

save()
```

## ステークホルダー承認対象リスト（DEC-01 〜 DEC-04）

```drawlib file=php_stakeholder_decision_log_table.png caption="ルートカットオーバー前に合意必須のステークホルダー意思決定ログ (DEC-01 - DEC-04)"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=116, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=8.5),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.0),
    border_style=Styles.NeutralThin,
)
rows = [
    ["ID / 箇所", "現行コードの観測挙動 (As-Is)", "無断変更時の影響リスク", "推奨方針 (Recommended) と選択肢"],
    [
        "DEC-01\nlogin.php\n:L7, L17",
        "md5() とマジックハッシュ '0e4620...'\nを == 比較 (DAST で '240610708'\nによる管理者突破を実証済み)。",
        "DB カラムが 32文字 MD5 のまま\nbcrypt 専用照合へ切り替えると、\n全既存会員がログイン不能になる。",
        "[推奨 Option A] Dual-Verify 透過移行: hash_equals\nで旧 MD5 照合成功時に bcrypt へ自動更新保存\n[Option B] 全会員パスワード強制リセット",
    ],
    [
        "DEC-02\nindex.php\n:L4",
        "$_COOKIE['shop_cart'] を直接\nunserialize() してカート配列を\n復元している (CWE-502 RCE)。",
        "Redis カートへ切り替えた瞬間、\n訪問中ブラウザに残る旧 serialize\n形式 Cookie の未決済商品が消える。",
        "[推奨 Option A] RCE 遮断を最優先し unserialize\nは完全禁止。旧 Cookie は失効・空カート初期化\n[Option B] allowed_classes=false で数値 ID 移行",
    ],
    [
        "DEC-03\nproduct.php\n:L14",
        "GET パラメータ ?promo_html= を\nエスケープせずそのまま echo 出力\n(DAST で Reflected XSS 実証済み)。",
        "メルマガ等で HTML タグ付き URL\nを配布中の場合、Blade エスケープ\nによりタグ文字列が露出する。",
        "[推奨 Option A] 任意 HTML 入力を廃止し、許可済み\n?promo_code= 識別子からサーバー側 Blade を選択\n[Option B] クエリ廃止・DB 管理バナーへ統一",
    ],
    [
        "DEC-04\nindex.php:L24\nhelpers.php:L11",
        "?page= に .php を連結して動的\ninclude (DAST で LFI 露出実証)、\n?debug=1 で var_dump 出力。",
        "?page=about 等の正規静的ページ\nURL をブックマークしている利用者\nが 404 エラーになる。",
        "[推奨 Option A] ?debug は完全削除。?page= は\n固定 Enum (about/terms/contact) のみ 301 転送\n[Option B] ?page= クエリを即時廃止",
    ],
]
tbl.draw_flexible(
    xy=(3, 113),
    column_widths=[24, 38, 36, 42],
    row_heights=[8.0, 25.0, 25.0, 25.0, 25.0],
    data=rows,
)

save()
```
