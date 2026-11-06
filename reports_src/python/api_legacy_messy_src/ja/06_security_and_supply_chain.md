# 6. 詳細分析：セキュリティ・脆弱性・動的DAST・API境界

Trivy（`0.69.3`）によるファイルシステムおよび解決済コンテナイメージ検査（`security_scan`）、Python AST SAST 解析、および隔離ループバック HTTP 動的ペネトレーション検証（`web_pentest`）の結果、本リポジトリは **サプライチェーン・コンテナ基盤・アプリケーションコード・CI/CD・HTTP 境界・動的可用性の全6層に重大な脆弱性** を抱えています。具体的には、Python パッケージ層で **計7件（HIGH 4件 / MEDIUM 2件 / LOW 1件）**、フルサイズの `FROM python:latest`（Debian 13.7）OS パッケージ層で **計3,554件（CRITICAL 24件 / HIGH 436件 / MEDIUM 1,308件 / LOW 1,654件）** の CVE が検出されたほか、Dockerfile 設定不備3件（`DS-0002` root 実行等）、AST 危険シンク2件（`CWE-502`・`CWE-78`）、ハードコード秘密鍵、コミット済ダミー認証情報、無認証 API、さらに **`web_pentest` 実行時のコンテナ起動クラッシュ（`status="error"`, `server_booted=false`）** が確認されました。

```drawlib file=06_vulnerability_breakdown.png caption="図6-1: Python依存 vs Debian 13.7 OS層の重大度別CVE件数（左）とコンテナ・DAST・サプライチェーンリスクKPI（右）"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.smartarts import KpiCards
from drawlib.styles import Styles

setup(width=146, height=68, dpi=150)

chart = BarChart(
    axis_line_style=Styles.Gray5Thin,
    grid_style=Styles.Gray3DashedThin,
    axis_text_style=Styles.Dark.patch(text_size=9.2),
    value_text_style=Styles.DarkBold.patch(text_size=8.8),
    background_style=Styles.Neutral,
    title="Trivy 重大度別 CVE 検出内訳 (総計 3,561件)",
    title_style=Styles.DarkBold.patch(text_size=10.2),
    categories=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
    orientation="vertical",
    bar_mode="group",
    bar_width_ratio=0.72,
    bar_r=0.5,
    value_format="{:.0f}",
)
chart.value_axis.min_value = 0
chart.value_axis.max_value = 1850
chart.add_series("Python依存 (計7)", [0, 4, 2, 1], style=Styles.Warning)
chart.add_series("Debian 13.7 OS (計3,554)", [24, 436, 1308, 1654], style=Styles.Danger)
chart.draw((2, 2), width=80, height=64)

kpis = KpiCards(
    style=Styles.WhiteBordered,
    metric_style=Styles.DangerBold.patch(text_size=15.5),
    text_style=Styles.DarkBold.patch(text_size=9.8),
    description_style=Styles.Dark.patch(text_size=8.8),
    accent_style=Styles.Danger,
)
kpis.add("4 HIGH", "Python アプリ層 CVE", "setuptools / urllib3(×2) / msgpack")
kpis.add("24 CRIT", "OS層 致命的 CVE", "libmariadb* (CVSS 10.0) / libxml2")
kpis.add("BOOT ERR", "動的DAST (web_pentest)", "server_booted=false (3.52s・0件実行)")
kpis.add("2 シンク + 2 鍵", "SAST & 秘密情報リスク", "CWE-502/78 + 直書き鍵・JSON鍵")
kpis.draw((85, 2), width=59, height=64, columns=2)

save()
```

## AST 危険コードシンク（CWE）・動的 DAST・無認証 API・優先パッチ CVE 一覧

コード内部では `order_app/services/processor.py` が安全なローダ指定のない `yaml.load(override_yaml)`（**CWE-502**：任意 Python オブジェクト生成・RCE）と `subprocess.run(f"echo batch {batch_id} done", shell=True)`（**CWE-78**：OS コマンドインジェクション）を含み、HTTP 境界では `POST /orders` が認証ヒント無し（`has_auth_hint=false`）で公開されています。

```drawlib file=06_sinks_endpoints_and_cves.png caption="図6-2: AST CWE危険シンク・動的DASTゲート・無認証API・優先修正CVEの統合セキュリティマトリクス"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=76, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=8.8),
    header_cell_style=Styles.Danger,
    header_text_style=Styles.WhiteBold.patch(text_size=9.2),
    border_style=Styles.Gray4Thin,
)
tbl.draw_flexible(
    (2, 74),
    column_widths=[16.0, 26.0, 44.0, 56.0],
    row_heights=[8.5, 8.2, 8.2, 8.2, 8.2, 8.2, 8.2, 8.2],
    data=[
        ["区分 / 重大度", "識別子 (CWE/CVE)", "検出箇所 / パッケージ", "攻撃リスクと具体的な緩和・修正バージョン"],
        ["DAST [CRIT]", "SEC-06 (Boot失敗)", "schemas.py:9 (54305/tcp)", "server_booted=false (3.52s) -> legacy_flag型注釈付与・起動復旧"],
        ["DAST [HIGH]", "CWE-306 / CWE-20", "POST /orders (test_app_probes)", "無認証200 & 未型付けitems 500 -> 認可強制・OrderItem厳格DTO化"],
        ["SAST [HIGH]", "CWE-502", "services/processor.py:30", "yaml.load(override_yaml) 任意コード実行 -> yaml.safe_load() へ置換"],
        ["SAST [HIGH]", "CWE-78", "services/processor.py:63", "subprocess.run(..., shell=True) 注入 -> shell廃止・構造化ログ化"],
        ["API [MED]", "SEC-05 (未接続)", "GET /legacy/health (L31)", "未マウントFlask定義 -> FastAPI GET /healthz へ移設・公開範囲明示"],
        ["PyPkg [HIGH]", "CVE-2025-47273", "setuptools@70.3.0 (CVSS 8.8)", "PackageIndex パストラバーサル -> 78.1.1 更新または本番イメージ除外"],
        ["OS/IaC [CRIT]", "CVE-2026-85746 他", "python:latest / DS-0002", "MariaDB/OpenEXR等 CRIT 24件 & root実行 -> python:3.12-slim 非root化"],
    ],
)

save()
```

## 動的 HTTP ペネトレーション検証 (`web_pentest`) とステージ済 DAST スイート

隔離ループバックコンテナ上でプロジェクト `Dockerfile` を起動して HTTP 攻撃耐性を実測する `web_pentest`（対象: `http://127.0.0.1:54305`、実行時間 `3.52s`）は、ASGI インポート直後に `order_app/schemas.py:9`（`legacy_flag = True  # type: ignore`）でクラッシュし、**`status="error"`・`server_booted=false`**（`boot_failure_reason`: `"For further information visit https://errors.pydantic.dev/2.14/u/model-field-missing-annotation"`）を記録しました。これによりサービスの動的可用性喪失が実証されるとともに、`.pni/pentests/examples/python/api_legacy_messy/` に生成・整備済みの4ファイル（計15テスト項目）は起動復旧後の必須 CI DAST ゲートとして待機状態（実行 `0/0`）となっています。

| プローブファイル (`.pni/pentests/.../`) | 対象エンドポイント | 検証 CWE / カテゴリ | 想定重大度 | プローブ検証内容と起動復旧後の合格条件 |
| :--- | :--- | :---: | :---: | :--- |
| **`test_app_probes.py`** | `POST /orders` | `CWE-306` (`missing_authentication`) | **HIGH** | 認証ヘッダ無しの注文バッチ投入が `2xx` で受理されないこと（`401`/`403` 必須）。 |
| **`test_app_probes.py`** | `POST /orders` | `CWE-20` (`improper_input_validation`) | **MEDIUM** | `items: List[Dict[str, Any]]` への欠損辞書投入で未処理 `500` を起こさず `422` で拒否すること。 |
| **`test_baseline_http.py`** | `/`〜`/api/health`, `/.env`, `/.git/config` 他 | `CWE-693`, `CWE-1021`, `CWE-200`, `CWE-942`, `CWE-538` | **CRIT〜LOW** | `X-Content-Type-Options: nosniff`、CORS 反射抑止、機密ファイル非公開、`TRACE` 無効化（計9項目）。 |
| **`test_target_surface.py`** | `GET /legacy/health` | `CWE-79`, `CWE-89`, `CWE-209`, `CWE-22` | **CRIT〜MED** | クエリ反射 XSS・SQL エラー／スタックトレース漏洩・`../` パストラバーサル耐性（計4項目）。 |

## 主要 CVE・IaC 設定不備・秘密情報・API 境界の詳細対照表

| 区分 | 重大度 | 識別子 | 対象（現在バージョン / 箇所） | 修正先 (`fixed_version` / 対策) | 詳細と推奨アクション |
| :--- | :---: | :--- | :--- | :--- | :--- |
| **Python 依存** | **HIGH** | `CVE-2025-47273` | `setuptools@70.3.0` (CVSS `8.8`) | `78.1.1`（または本番除外） | `PackageIndex` パストラバーサル。マルチステージ `uv` ビルドでランタイムから除外。 |
| **Python 依存** | **HIGH** | `CVE-2026-97687`, `CVE-2026-97689` | `urllib3@2.7.0` (CVSS `8.1`, `7.5`) | `2.8.0` | HTTPS プロキシ TLS 設定上書きおよびチャンク解析 DoS。未使用宣言を削除し `>=2.8.0` に固定。 |
| **Python 依存** | **HIGH** | `GHSA-6v7p-g79w-8964` | `msgpack@1.1.2` (CVSS `7.5`) | `1.2.1` | エラー捕捉後の `Unpacker` 再利用時の境界外読み取り。`flake8`/`black` を本番から分離し更新。 |
| **OS (Debian 13.7)** | **CRITICAL** | `CVE-2026-85746`, `CVE-2026-92262`, `CVE-2026-49261` | `libmariadb3`, `libmariadb-dev` (`1:11.8.6-0+deb13u1`, CVSS `10.0`/`9.8`) | `python:3.12-slim` / distroless 移行 | フルサイズ `python:latest` が同梱する不要な DB 開発ライブラリ群の脆弱性。最小ベースイメージ化で除去。 |
| **OS (Debian 13.7)** | **CRITICAL** | `CVE-2026-42217`, `CVE-2026-6653`, `CVE-2026-60002` | `libopenexr`, `libxml2`, `openssh-client` (CVSS `9.8`〜`9.4`) | 最小ベースイメージ移行 + `apt-get upgrade` | 画像・XML・SSH クライアント開発パッケージをランタイムから排除して攻撃面を極小化。 |
| **IaC (`Dockerfile`)** | **HIGH / MED / LOW** | `DS-0002`, `DS-0001`, `DS-0026` | `Dockerfile:1-6` | 非root `USER`・ダイジェスト固定・`HEALTHCHECK` | UID 10001 等の非特権実行ユーザ指定、`:latest` 廃止、`/healthz` ヘルスチェック命令を追加。 |
| **秘密情報 (`SEC-03`)** | **CRITICAL / MED** | `OWASP-ASVS / S105` | `processor.py:8` (`sk_live_***REDACTED***`), `config/service_account_dummy.json` | 環境変数注入 + Git/Docker 除外 | ハードコード署名トークンとコミット済 JSON ファイルを削除し、シークレットスキャンを CI 化。 |
| **CI/CD (`Supply`)** | **CRITICAL** | `OpenSSF Token-Permissions` | `.github/workflows/deploy.yml:4,11` | `pull_request` + `contents: read` + SHA固定 | 特権 `pull_request_target` と可変 `@main` 参照を廃止し、未信頼 PR コード実行を防止。 |
