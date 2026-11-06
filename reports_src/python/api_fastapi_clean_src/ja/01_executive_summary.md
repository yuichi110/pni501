# 1. エグゼクティブサマリー

`order-dispatch` (`v1.2.0`) の総合健全性スコアは **89 / 100 (Grade A)** です。FastAPI Lifespan DI と Repository Protocol による厳格な4層クリーンアーキテクチャ、型アノテーション・Docstring・Import衛生すべて `100.0%`、CWE 危険コードシンク `0件`、Python アプリケーション実行時ライブラリの CVE `0件` を達成しており、さらに隔離コンテナに対する動的 Web ペネトレーションテスト（`web_pentest`：全19プローブ中15件合格・CRITICAL/HIGH `0件`）でも Pydantic `extra="forbid"` によるマスアサインメント拒否（HTTP `422`）および XSS・SQLi・パストラバーサル耐性が実測確認されました。最優先改善（P0〜P1）は、`python:3.12.6-slim-bookworm` ベースイメージ刷新、ライブプローブでも実証された `POST /v1/orders`（HTTP `201`、`CWE-306`）への OAuth2/JWT 認証・認可導入、`uv.lock` の完全ロック化、および ASGI HTTP 統合テスト拡充による分岐カバレッジ（現状 `62.5%`）の引き上げです。

```drawlib file=01_health_radar.png caption="図1-1: 7軸エンジニアリング健全性レーダーチャートと主要品質KPI"
from drawlib.canvas import setup
from drawlib.charts.radar import RadarChart
from drawlib.smartarts import KpiCards
from drawlib.styles import Styles

setup(width=146, height=66, dpi=150)

radar = RadarChart(
    categories=[
        "アーキテクチャ\n(94)",
        "コード品質\n(96)",
        "型安全性\n(98)",
        "テスト品質\n(81)",
        "依存関係\n(88)",
        "セキュリティ\n(78)",
        "ドキュメント\n(90)",
    ],
    axis_line_style=Styles.Gray4Thin,
    grid_style=Styles.Gray3DashedThin,
    axis_text_style=Styles.DarkBold.patch(text_size=9.5),
    scale_text_style=Styles.Muted.patch(text_size=9.5),
    background_style=Styles.Neutral,
    title="7軸健全性バランス (総合 89/100)",
    title_style=Styles.DarkBold.patch(text_size=11.0),
    min_value=0,
    max_value=100,
    levels=5,
    radius=18.5,
)
radar.add_series(
    "order-dispatch 実測値",
    [94, 96, 98, 81, 88, 78, 90],
    style=Styles.PrimaryBold,
    fill_alpha=0.25,
    line_width=2.2,
)
radar.add_series(
    "Grade A 基準線 (80)",
    [80, 80, 80, 80, 80, 80, 80],
    style=Styles.SecondaryDashed,
    fill_alpha=0.05,
    line_width=1.4,
    line_style="dashed",
    point_shape="none",
)
radar.draw((2, 2), width=72, height=62)

kpis = KpiCards(
    style=Styles.PrimaryNeutral,
    metric_style=Styles.PrimaryBold.patch(text_size=15.5),
    text_style=Styles.DarkBold.patch(text_size=9.5),
    description_style=Styles.Dark.patch(text_size=9.5),
    accent_style=Styles.Primary,
)
kpis.add("100%", "静的コード衛生3指標", "型・Doc・Import完全")
kpis.add("85.2%", "実測行カバレッジ", "分岐62.5%・4/4成功")
kpis.add("15 / 19", "動的Web侵入プローブ", "CRIT/HIGH 0・422防御")
kpis.add("P0: 1件", "最優先コンテナ刷新", "OS層・pip6件の解消")
kpis.draw((77, 2), width=67, height=62, columns=2)
```

## 主要な強みと優先リスクの対比

静的構造・サプライチェーン統制・12-Factor 運用準備度はいずれも高水準（監査ステップスコア `91〜93`）である一方、コンテナ OS ベースイメージの経年脆弱性・ライブ DAST で実証された `/v1/orders` 未認証注文生成（`CWE-306`）や HTTP ヘッダ強化・HTTP ルート層の実測分岐カバレッジに改善余地が集中しています。

```drawlib file=01_strengths_and_risks.png caption="図1-2: 確認されたエンジニアリング上の強み（左）と優先対応リスク（右）"
from drawlib.canvas import setup
from drawlib.smartarts import CardList, Panel
from drawlib.styles import Styles

setup(width=146, height=68, dpi=150)

Panel(
    "主要な強み (Key Engineering Strengths)",
    style=Styles.Neutral,
    header_style=Styles.Success,
    text_style=Styles.WhiteBold.patch(text_size=10.5),
).draw((2, 2), width=69, height=64)

strengths = CardList(
    style=Styles.WhiteBordered,
    text_style=Styles.DarkBold.patch(text_size=9.5),
    description_style=Styles.Dark.patch(text_size=9.5),
    badge_style=Styles.SuccessNeutral,
    badge_text_style=Styles.SuccessBold.patch(text_size=9.5),
)
strengths.add("CI最小権限 & 40文字SHA固定", "contents:readとAction SHA固定を徹底", badge_text="Supply")
strengths.add("PEP 621分離 & 厳格な4層DAG", "循環依存0・Domain外部依存0・py.typed", badge_text="Arch")
strengths.add("DAST 422防御 & 注入耐性実証", "extra='forbid'とXSS/SQLi/LFI全遮断", badge_text="DAST")
strengths.add("非root(UID 10001) & 5秒Timeout", "障害時はWEBHOOK_DEFERREDへ安全縮退", badge_text="SRE")
strengths.draw((4, 4), width=65, height=51)

Panel(
    "優先対応リスク (Top Remediation Risks)",
    style=Styles.Neutral,
    header_style=Styles.Danger,
    text_style=Styles.WhiteBold.patch(text_size=10.5),
).draw((75, 2), width=69, height=64)

risks = CardList(
    style=Styles.WhiteBordered,
    text_style=Styles.DarkBold.patch(text_size=9.5),
    description_style=Styles.Dark.patch(text_size=9.5),
    badge_style=Styles.DangerNeutral,
    badge_text_style=Styles.DangerBold.patch(text_size=9.5),
)
risks.add("Debian 12.7 OS層 & pip脆弱性", "OS CRITICAL 9 / HIGH 116件・pip 6件", badge_text="HIGH")
risks.add("POST /v1/orders 未認証201応答", "DASTでCWE-306実証・OAuth2/JWT必須", badge_text="MED")
risks.add("uv.lock 未解決 & pipビルド", "推移的依存のハッシュ固定が未完了", badge_text="MED")
risks.add("HTTPルート/Webhook分岐不足", "routes(56%)・webhook(55.6%)が未通電", badge_text="MED")
risks.draw((77, 4), width=65, height=51)
```

## 7軸評価サマリー

| 評価軸 | スコア | 評価根拠の要点 |
| :--- | :---: | :--- |
| **型安全性 (`typing`)** | **98** | 全23関数・14クラスで型注釈率 `100.0%`、`Any` や無制限 `type: ignore` `0件`、PEP 561 `py.typed` 同梱。 |
| **コード品質 (`code_quality`)** | **96** | Google形式 Docstring `100.0%`、Import衛生 `100.0%`、複雑関数 `0件`、グローバル可変状態 `0件`。 |
| **アーキテクチャ (`architecture`)** | **94** | API → Services → Domain / Infra の単方向 DAG（循環依存 `0件`）。Lifespan HTTP 接続プール共有でさらに向上。 |
| **ドキュメント (`documentation`)** | **90** | `README.md` と `SECURITY.md` で起動・設定・API例を明記。開発者向け検証コマンド（`pytest`/`ruff`/`ty`）追記を推奨。 |
| **依存関係 (`dependencies`)** | **88** | 実行時依存5件と `dev` グループを明確分離。`uv.lock` の完全解決とマルチステージ Docker 化が残課題。 |
| **テスト品質 (`testing`)** | **81** | 単体テスト `4/4` がオフライン環境で確定成功（行 `85.2%`）。`TestClient` / `MockTransport` 追加で分岐 `62.5%` を改善可能。 |
| **セキュリティ (`security`)** | **78** | 実行時依存CVE `0件`・危険シンク `0件`・DAST重大脆弱性 `0件`（`15/19`合格）。OSパッチ適用と `/v1/orders` 認証（`CWE-306`）・ヘッダ強化が課題。 |
