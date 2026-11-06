# 6. 詳細分析：セキュリティ・脆弱性・API境界

Trivy（v0.69.3）によるロックファイル・解決済みコンテナイメージスキャンおよび AST SAST 解析の結果、`metrics-kit` 本体と直接依存パッケージ（`pydantic`）の脆弱性は **0 件**、IaC 設定不備 **0 件**、秘密情報漏洩 **0 件**、CWE 危険コードシンク **0 件**、外部 HTTP 攻撃面 **0 件**であることを確認した。

```drawlib file=06_supply_chain_cve_breakdown.png caption="図6-1: レイヤ別脆弱性検出内訳 (uv.lock 直接依存 vs コンテナ同梱 pip vs Debian OS層)"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.smartarts import Table
from drawlib.styles import Colors, Styles

setup(width=146, height=66, dpi=150)

chart = BarChart(
    axis_line_style=Styles.Primary,
    categories=["uv.lock\n(直接依存)", "基盤同梱\npip@25.0.1", "Debian 12.13\n(OSレイヤ)"],
    width=66.0,
    height=49.0,
    orientation="vertical",
    bar_mode="stack",
    bar_width_ratio=0.55,
    bar_r=0.8,
    title="スキャン対象レイヤ別 CVE 件数比較",
    title_style=Styles.DarkBold.patch(text_size=11.5),
    axis_text_style=Styles.Dark.patch(text_size=9.5),
    grid_style=Styles.MutedDashed,
    background_style=Styles.Neutral.patch(shape_r=1.6),
)
chart.add_series("CRIT", [0, 0, 9], style=Styles.DangerFlat)
chart.add_series("HIGH", [0, 0, 91], style=Styles.WarningFlat)
chart.add_series("MED", [0, 5, 155], style=Styles.PrimaryFlat)
chart.add_series("LOW/他", [0, 1, 143], style=Styles.SecondaryNeutral)
chart.draw(xy=(3.0, 12.0))
chart.draw_legend(xy=(6.0, 4.5), text_style=Styles.Dark.patch(text_size=9.5), orientation="horizontal", item_gap=5.5)

tbl = Table(
    cell_style=Styles.White,
    text_style=Styles.Dark.patch(text_size=9.5),
    header_cell_style=Styles.PrimaryFlat,
    header_text_style=Styles.WhiteBold.patch(text_size=9.8),
    border_style=Styles.MutedThin,
)
tbl.set_style_cell_evenodd(
    even_color=Colors.Neutral,
    even_text_style=Styles.Dark.patch(text_size=9.5),
    odd_color=Colors.White,
    odd_text_style=Styles.Dark.patch(text_size=9.5),
)
tbl.set_style_cell(
    background_color=Colors.SuccessNeutral,
    text_style=Styles.SuccessBold.patch(text_size=9.5),
    rows=[1, 4],
    columns=[1],
)

sec_rows = [
    ["検査対象レイヤ", "検出件数", "修正版・配布物への影響"],
    ["uv.lock\n(直接依存)", "0 件", "脆弱性ゼロ\n(配布ホイールは安全)"],
    ["pip@25.0.1\n(基盤同梱)", "6 件\n(MED 5)", "pip>=26.2.0 で解消\n(配布物には不含)"],
    ["debian 12.13\n(検証OS層)", "398 件", "CRIT 9 / HIGH 91\n(検証コンテナ限定)"],
    ["Dockerfile &\n全ソース", "0 件", "IaC設定不備 0件\n秘密漏洩 0件"],
]
tbl.draw_flexible(
    xy=(72.0, 61.0),
    column_widths=[22.0, 16.0, 33.0],
    row_heights=[9.0, 11.2, 11.2, 11.2, 11.2],
    data=sec_rows,
)

save()
```

## 6.1 アプリケーション依存 vs コンテナベースイメージ CVE 詳細と修正バージョン

ライブラリ配布物（`metrics-kit` および `pydantic>=2.7.0`）自体には既知の脆弱性は一切存在しない。解決済みコンテナイメージ上の `python-pkg` 検出 6 件はすべて Python 3.12 ベースイメージ標準添付の `pip@25.0.1` に起因し、OS パッケージ検出 398 件（`debian 12.13`）とともにライブラリ利用者環境へは伝播しないが、CI・検証コンテナの衛生維持のため更新が望ましい。

| 区分 / 重大度 | CVE ID | パッケージ（現行バージョン） | 修正バージョン (`fixed_version`) | 概要 |
| :--- | :--- | :--- | :--- | :--- |
| **Python基盤 `MEDIUM`** | `CVE-2026-13346` 他計5件 | `pip@25.0.1`（コンテナ標準添付） | `26.2.0` | `pip` アーカイブ展開・URL処理等（`CVE-2026-8643`, `6357`, `3219`, `2025-8869` 含む） |
| **Python基盤 `LOW`** | `CVE-2026-1703` | `pip@25.0.1`（コンテナ標準添付） | `26.2.0` | `pip` 軽微なパス検証課題 |
| **OS層 `CRITICAL`** | `CVE-2026-42010` / `33845` | `libgnutls30@3.7.9-2+deb12u5` | `3.7.9-2+deb12u7` | GnuTLS NUL文字認証バイパス / DTLS DoS |
| **OS層 `CRITICAL`** | `CVE-2026-31789`（2件） | `libssl3`, `openssl@3.0.18-1~deb12u2` | `3.0.19-1~deb12u2` | 32-bit X.509 証明書処理ヒープバッファオーバーフロー（HIGH `CVE-2026-45447` は `3.0.20-1~deb12u2`） |
| **OS層 `CRITICAL`** | `CVE-2026-8376` / `13221` / `42496` | `perl-base@5.36.0-7+deb12u3` | `5.36.0-7+deb12u4` | Perl 正規表現ヒープ境界 / `perl-archive-tar` シンボリックリンク走査 |
| **OS層 `CRITICAL`** | `CVE-2023-45853` / `2025-7458` | `zlib1g@1:1.2.13`, `libsqlite3-0@3.40.1` | 未提供（upstream未修正） | `minizip` 整数オーバーフロー / SQLite 整数オーバーフロー |
| **OS層 `HIGH`** | `CVE-2026-86145` / `16742` | `libpcre2-8-0@10.42-1`, `libsystemd0` | `10.42-1+deb12u1` / 未提供 | PCRE2 境界外書き込み / `systemd-homed` 署名検証課題 |

## 6.2 AST 危険コードシンク（CWE SAST）と API 攻撃面マップ

```drawlib file=06_sast_and_attack_surface.png caption="図6-2: AST 危険コードシンク検査 (CWE SAST) と API 境界・サプライチェーン統制マップ"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import CardList, Panel
from drawlib.styles import Styles

setup(width=146, height=64, dpi=150)

sast_panel = Panel(
    "AST 危険コードシンク & 秘密情報スキャン (0件)",
    style=Styles.Neutral.patch(shape_r=1.8),
    header_style=Styles.SuccessFlat,
    text_style=Styles.WhiteBold.patch(text_size=11.0),
    icon=phosphor.shield_check,
    icon_style=Styles.WhiteBold,
    header_variant="filled",
    header_height=8.5,
)
sast_panel.draw((3.0, 4.0), width=68.5, height=56.0)
s_xy, s_w, s_h = sast_panel.get_content_box((3.0, 4.0), width=68.5, height=56.0, padding=(3.0, 2.8))

sast_cards = CardList(
    style=Styles.White.patch(shape_r=1.2),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Muted.patch(text_size=9.5),
    badge_shape="rounded_rect",
    badge_style=Styles.SuccessNeutral,
    badge_text_style=Styles.SuccessBold.patch(text_size=9.6),
    direction="vertical",
    spacing=2.4,
)
sast_cards.add("CWE-78 / 89 / 94 インジェクション検査", "subprocess / eval / exec / 生SQL シンク: 0件", badge_text="PASS")
sast_cards.add("CWE-502 / 327 / 295 逆直列化・暗号検査", "pickle / yaml.load / 弱ハッシュ / TLS無効化: 0件", badge_text="PASS")
sast_cards.add("ハードコード秘密情報・鍵ファイル検査", "AST リテラル・Trivy Secret スキャン検出: 0件", badge_text="PASS")
sast_cards.draw(s_xy, width=s_w, height=s_h)

api_panel = Panel(
    "API 攻撃面 & サプライチェーン防御境界",
    style=Styles.Neutral.patch(shape_r=1.8),
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=11.0),
    icon=phosphor.lock_key,
    icon_style=Styles.WhiteBold,
    header_variant="filled",
    header_height=8.5,
)
api_panel.draw((74.5, 4.0), width=68.5, height=56.0)
a_xy, a_w, a_h = api_panel.get_content_box((74.5, 4.0), width=68.5, height=56.0, padding=(3.0, 2.8))

api_cards = CardList(
    style=Styles.White.patch(shape_r=1.2),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Muted.patch(text_size=9.5),
    badge_shape="rounded_rect",
    badge_style=Styles.PrimaryNeutral,
    badge_text_style=Styles.PrimaryBold.patch(text_size=9.6),
    direction="vertical",
    spacing=2.4,
)
api_cards.add("ネットワーク API 攻撃面ゼロ", "HTTP ルート 0件 (インプロセス純粋関数ライブラリ)", badge_text="API")
api_cards.add("不変スキーマ・出力サニタイズ境界", "frozen=True / extra='forbid' と名前サニタイズ", badge_text="TYPE")
api_cards.add("OpenSSF ガバナンス・CI 最小権限", "contents: read / SHA固定Actions / Dependabot", badge_text="CI")
api_cards.draw(a_xy, width=a_w, height=s_h)

save()
```
