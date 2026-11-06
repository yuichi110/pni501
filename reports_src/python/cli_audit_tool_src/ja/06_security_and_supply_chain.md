# 6. 詳細分析：セキュリティ・脆弱性・API境界

本章では、Trivy (`0.69.3`) によるファイルシステムおよび解決済みコンテナイメージに対する SCA（ソフトウェア構成解析）・IaC 設定検査・秘密情報スキャン結果と、AST による危険な CWE コードシンク・API 攻撃面の検査結果を統合して評価する。

```drawlib file=security_cve_and_governance.png caption="アプリケーション依存 vs コンテナOS層 CVE内訳とサプライチェーン統治状況"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.icons import phosphor
from drawlib.smartarts import KpiCards
from drawlib.styles import Styles

setup(width=146, height=66, dpi=150)

chart = BarChart(
    axis_line_style=Styles.Neutral,
    grid_style=Styles.NeutralThin,
    axis_text_style=Styles.DarkBold.patch(text_size=9.5),
    value_text_style=Styles.DarkBold.patch(text_size=9.5),
    background_style=Styles.Neutral.patch(shape_r=2.0),
    categories=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
    orientation="vertical",
    bar_mode="group",
    bar_width_ratio=0.68,
    bar_r=0.8,
    width=76,
    height=54,
    title="深刻度別 CVE 件数比較 (App 6件 vs OS層 398件)",
    title_style=Styles.DarkBold.patch(text_size=10.0),
)
chart.add_series("Python層 (pip 6件)", [0, 0, 5, 1], style=Styles.Primary)
chart.add_series("Debian 12.13 OS層", [9, 91, 155, 136], style=Styles.Danger)
chart.draw(xy=(4, 6))

kpis = KpiCards(
    style=Styles.Neutral,
    metric_style=Styles.SuccessBold.patch(text_size=13.0),
    text_style=Styles.DarkBold.patch(text_size=10.0),
    description_style=Styles.Dark.patch(text_size=9.5),
    metric_width_ratio=0.33,
    spacing=2.8,
)
kpis.add(
    "0 件",
    "rich / typer 依存CVE",
    "実依存CVEゼロ (pipのみ6件)",
    icon=phosphor.shield_check,
    accent_style=Styles.Success,
    icon_style=Styles.Success,
)
kpis.add(
    "0 / 0 / 0",
    "Secret / IaC / CWE",
    "秘密漏洩0・設定0・危険関数0",
    icon=phosphor.check_circle,
    accent_style=Styles.Primary,
    metric_style=Styles.PrimaryBold.patch(text_size=12.5),
    icon_style=Styles.Primary,
)
kpis.add(
    "未整備",
    "供給網統治・ロック",
    "uv.lockスタブ・SECURITY不在",
    icon=phosphor.warning,
    accent_style=Styles.Danger,
    metric_style=Styles.DangerBold.patch(text_size=12.5),
    icon_style=Styles.Danger,
)
kpis.draw(xy=(83, 6), width=60, height=54, columns=1)

save()
```

## アプリケーション依存関係 vs コンテナ OS 層の脆弱性分離評価（SEC-01〜SEC-05）

- **アプリケーション依存関係 (`SEC-01` — `app_vuln_counts`)**: 解決済みコンテナイメージ上の Python パッケージ検査において、`CRITICAL` および `HIGH` の脆弱性は **`0` 件**であった。`logpulse` が直接・推移的に利用する `rich`・`typer`・`click`・`pygments` 等には脆弱性は一切存在せず、検出された計6件（`MEDIUM` 5件、`LOW` 1件）はすべてベースイメージ内のシステム `pip@25.0.1` に起因する（`pip>=26.2.0` への更新または本番イメージからの `pip` 除外で全件解消可能）。
- **スタブ `uv.lock` による静的ファイルシステムスキャンの盲点**: リポジトリ内の `uv.lock` に対する Trivy FS スキャンでは、ルートパッケージ `logpulse@0.2.1` 1件のみしか認識されなかった。`uv lock` による完全な推移依存バージョンとハッシュの記録が、再現性確保のみならず CI での高速ロックファイル SCA を機能させる上でも不可欠である。
- **OS ベースイメージ層と SAST / Secret / API 境界 (`SEC-02`〜`SEC-05`)**: Debian 12.13 ベースレイヤーでは `libgnutls30` (`CVE-2026-42010`) や `openssl`/`libssl3` (`CVE-2026-31789`) を含む計 `398` 件（`CRITICAL` 9件、`HIGH` 91件）が検出されており、コンテナ配布時にはセキュリティ更新適用または Distroless イメージ採用が推奨される。一方、ソースコード自体にはハードコード秘密情報（`0` 件）、IaC 設定不備（`0` 件）、危険な CWE コードシンク（`eval`/`exec`/`shell=True`/`pickle` 等 `0` 件）、外部公開 HTTP API エンドポイント（`0` 件）はいずれも存在せず、コードレベルの攻撃面は極めて小さく保たれている。

```drawlib file=security_cve_sinks_table.png caption="主要検出CVE・修正バージョン対応表およびSAST / Secret / API境界検査サマリー"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=102, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=9.5),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.5),
    border_style=Styles.NeutralThin,
)
rows = [
    ["区分 / 深刻度", "CVE / 検査ID", "パッケージ・対象", "導入版 -> 修正版", "脆弱性・検査結果の概要"],
    ["App [MEDIUM]", "CVE-2026-13346", "pip (python-pkg)", "25.0.1 -> 26.2.0", "悪意あるインデックス経由の\n任意ファイル配置"],
    ["App [MEDIUM]", "CVE-2026-8643", "pip (python-pkg)", "25.0.1 -> 26.1.2", "不正 entry point 名による\nパストラバーサル上書き"],
    ["App [MEDIUM]", "CVE-2026-3219\nCVE-2026-6357", "pip (python-pkg)", "25.0.1 -> 26.1", "細工された wheel 展開時の\n不適切配置・任意コード実行"],
    ["App [MED/LOW]", "CVE-2025-8869\nCVE-2026-1703", "pip (python-pkg)", "25.0.1 -> 25.3 /\n26.0", "シンボリックリンク検証不備・\nwheel 展開時情報漏洩"],
    ["OS [CRITICAL]", "CVE-2026-42010", "libgnutls30\n(debian 12.13)", "3.7.9-2+deb12u5\n-> deb12u7", "GnuTLS ユーザ名 NUL 文字による\n認証バイパス (CVSS 9.8)"],
    ["OS [CRITICAL]", "CVE-2026-31789", "openssl / libssl3\n(debian 12.13)", "3.0.18-1~deb12u2\n-> 3.0.19", "大型 X.509 証明書処理における\nヒープバッファ溢れ"],
    ["OS [CRITICAL]", "CVE-2026-8376\nCVE-2026-42496", "perl-base\n(debian 12.13)", "5.36.0-7+deb12u3\n-> deb12u4", "正規表現コンパイル溢れ・\nArchive::Tar パストラバーサル"],
    ["IaC / Secret", "SEC-02 / SEC-03", "全リポジトリ対象", "検出 0 件 (PASS)", "Dockerfile設定不備 0件・\n秘密情報漏洩 0件 (Trivy+AST)"],
    ["SAST / API", "SEC-04 / SEC-05", "src/logpulse/*.py", "危険シンク 0 件\nHTTP API 0 件", "CWE-78/89/94/502 危険呼出 0件・\nHTTPルート 0件 (CLI専用)"],
]
tbl.draw_flexible(
    xy=(3, 99),
    column_widths=[20, 24, 25, 25, 46],
    row_heights=[7.5] + [9.6] * 9,
    data=rows,
)

save()
```
