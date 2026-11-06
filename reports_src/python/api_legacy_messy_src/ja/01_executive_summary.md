# 1. エグゼクティブサマリー

`legacy-order-hub`（`examples/python/api_legacy_messy`）の総合健全性スコアは **20 / 100 (Grade D)** であり、評価対象15ルール中 **適合 `0件`（`FAIL` 14件・`WARN` 1件）** という危機的状態にあります。最大の課題は、未固定の `requirements.txt` により導入される Pydantic v2 環境下で `order_app/schemas.py` の未注釈属性 `legacy_flag = True  # type: ignore` が **`PydanticUserError` を引き起こし、起動スモーク検証（`run_check`）のみならず実コンテナ HTTP 動的ペネトレーション検証（`web_pentest`: `status="error"`, `server_booted=false`, `3.52s`）でも ASGI アプリが完全起動不能** になっている点です。これにより `.pni/pentests/examples/python/api_legacy_messy/` に整備された DAST プローブ群（`POST /orders` の `CWE-306` 無認証検証・`CWE-20` 未型付け `items` 500 検証等）のライブ実行も遮断（`0/0` 実行）されています。さらに唯一存在するアサーション無しの単体テスト（実測行カバレッジ `6.6%`・分岐 `0.0%`）がこの致命的起動障害を完全に看過しており、`order_app/services/processor.py` には **CWE-502（`yaml.load`）** と **CWE-78（`subprocess.run(..., shell=True)`）**、ハードコード秘密鍵、可変デフォルト引数バグが集中し、`FROM python:latest`（root 実行）により **計 3,561 件の CVE** を抱えています。

```drawlib file=01_health_radar.png caption="図1-1: 7軸エンジニアリング健全性レーダーチャート（左）と強み・最優先リスク対比（右）"
from drawlib.canvas import save, setup
from drawlib.charts.radar import RadarChart
from drawlib.smartarts import CardList, Panel
from drawlib.styles import Styles

setup(width=146, height=68, dpi=150)

radar = RadarChart(
    categories=[
        "アーキテクチャ",
        "コード品質",
        "型安全性",
        "テスト健全性",
        "依存関係",
        "セキュリティ",
        "ドキュメント",
    ],
    axis_line_style=Styles.Gray4Thin,
    grid_style=Styles.Gray3DashedThin,
    axis_text_style=Styles.DarkBold.patch(text_size=9.2),
    scale_text_style=Styles.Muted.patch(text_size=8.8),
    background_style=Styles.Neutral,
    title="7軸健全性バランス (総合 20/100・Grade D)",
    title_style=Styles.DarkBold.patch(text_size=10.5),
    min_value=0,
    max_value=100,
    levels=5,
    radius=18.0,
)
radar.add_series(
    "legacy-order-hub 実測値",
    [22, 24, 26, 12, 18, 12, 28],
    style=Styles.DangerBold,
    fill_alpha=0.28,
    line_width=2.2,
)
radar.add_series(
    "Grade B 基準線 (70)",
    [70, 70, 70, 70, 70, 70, 70],
    style=Styles.PrimaryDashed,
    fill_alpha=0.04,
    line_width=1.4,
    line_style="dashed",
    point_shape="none",
)
radar.draw((2, 2), width=68, height=64)

Panel(
    "主要な強みと最優先是正リスク (Top Findings)",
    style=Styles.Neutral,
    header_style=Styles.Dark,
    text_style=Styles.WhiteBold.patch(text_size=10.5),
).draw((73, 2), width=71, height=64)

cards = CardList(
    style=Styles.WhiteBordered,
    text_style=Styles.DarkBold.patch(text_size=9.5),
    description_style=Styles.Dark.patch(text_size=9.0),
    badge_style=Styles.DangerNeutral,
    badge_text_style=Styles.DangerBold.patch(text_size=9.0),
)
cards.add("起動 & DAST ブートクラッシュ", "schemas.py:L9 未注釈属性で server_booted=false", badge_text="CRIT")
cards.add("CWE-502 & CWE-78 危険シンク内在", "processor.py の yaml.load と shell=True 実行", badge_text="CRIT")
cards.add("root python:latest & 特権CI実行", "OS 3,554 CVE・Python 7 CVE・pull_request_target", badge_text="CRIT")
cards.add(
    "強み: constants.py & DASTプローブ網",
    "Final型注釈100% + 修正後検証用 .pni/pentests 完備",
    badge_style=Styles.SuccessNeutral,
    badge_text_style=Styles.SuccessBold.patch(text_size=9.0),
    badge_text="GOOD",
)
cards.draw((75, 4), width=67, height=51)

save()
```

## 動的検証・セキュリティ・DAST 主要ヘッドライン指標

コンテナ隔離検証（`run_check`）、Trivy スキャン（`security_scan`）、および隔離ループバック HTTP ペネトレーション検証（`web_pentest`）によって、「実運用コンテナの即時インポートクラッシュによる HTTP 完全停止（`server_booted=false`）」と「フルサイズ OS イメージ由来の膨大な脆弱性露出」が動的に裏付けられました。

```drawlib file=01_runtime_security_headline.png caption="図1-2: コンテナ動的検証・Trivyスキャン・動的DAST (web_pentest) 主要ヘッドラインKPI"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import KpiCards, Panel
from drawlib.styles import Styles

setup(width=146, height=58, dpi=150)

panel = Panel(
    "動的実行検証 (run_check) × セキュリティスキャン (security_scan) × 動的DAST (web_pentest)",
    style=Styles.Neutral,
    header_style=Styles.Primary,
    text_style=Styles.WhiteBold.patch(text_size=10.5),
    icon=phosphor.shield_warning,
    icon_style=Styles.WhiteBold,
)
panel.draw((2, 2), width=142, height=54)

kpis = KpiCards(
    style=Styles.WhiteBordered,
    metric_style=Styles.DangerBold.patch(text_size=16.5),
    text_style=Styles.DarkBold.patch(text_size=10.0),
    description_style=Styles.Dark.patch(text_size=9.0),
    accent_style=Styles.Danger,
)
kpis.add("BOOT ERROR", "起動スモーク & DAST", "server_booted=false (PydanticUserError)")
kpis.add("6.6%", "実測行カバレッジ (7/106)", "分岐0.0%・主要6モジュールが完全未実行")
kpis.add("7 件 (HIGH 4)", "Python 依存パッケージ CVE", "setuptools / urllib3(×2) / msgpack")
kpis.add("3,554 件", "Debian 13.7 OS層 CVE", "CRIT 24・HIGH 436 + IaC設定不備 3件")
kpis.draw((5, 5), width=136, height=37, columns=4)

save()
```

## 7軸評価サマリー

| 評価軸 | スコア | 評価根拠の要点 |
| :--- | :---: | :--- |
| **ドキュメント (`documentation`)** | **28** | `README.md` は2行のスタブのみ。Docstring 網羅率 `40.9%`（欠落12件、`TODO` 1件、`pricing.py` 引数不一致1件）。 |
| **型安全性 (`typing`)** | **26** | 型注釈率 `44.4%`、`process_order_batch` 全9箇所未注釈、`schemas.py:L9` の `# type: ignore` が起動クラッシュを誘発。 |
| **コード品質 (`code_quality`)** | **24** | 認知的複雑度 `44`（8引数）、可変デフォルト `tags=[]`、裸の `except:`、`async def` 内の同期 `sleep`/`requests.post`。 |
| **アーキテクチャ (`architecture`)** | **22** | 3モジュール循環依存（`handlers -> processor -> pricing -> handlers`）、非公開 `infra._internal` 侵食、FastAPI/Flask 混在。 |
| **依存関係 (`dependencies`)** | **18** | `requirements.txt` 全8件ピン無し・ロック不在、本番に `flake8`/`black` 混入、`uvicorn` と `boto3` の宣言漏れ。 |
| **テスト健全性 (`testing`)** | **12** | 12ソースに対し `assert` 無しの2行テスト1件のみ。実測行カバレッジ `6.6%`・分岐 `0.0%` で起動不能障害を検知不能。 |
| **セキュリティ (`security`)** | **12** | Python HIGH CVE 4件、OS CRITICAL 24件、root 実行、CWE-502/78 シンク、秘密鍵直書き、`pull_request_target`、`web_pentest` 起動不能（DAST `CWE-306`/`CWE-20` 未通過）。 |
