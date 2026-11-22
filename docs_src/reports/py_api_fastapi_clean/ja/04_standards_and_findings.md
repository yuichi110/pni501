# 4. 監査パイプライン（DAG）・評価基準・検出事項

本章では、ワークフロー実行 `wf-f819234f`（`py_api_fastapi_clean`）の完全な再現性と証跡の透明性を提示します。実行されたアクションレベルの監査パイプライン DAG、検査対象範囲と決定論アナライザ群、7 軸の決定論ベースライン対 AI 調整（`±10pt` 上限）、監査ステップ別スコア、`WARN -> PASS` ルール準拠マトリクス、集約済み検出事項、AI 誤検知トリアージ記録、および機械可読アーティファクト一覧を網羅します。

```drawlib align=center code=fold file=executed_audit_dag.png caption="実行済み PNI Workflow v2 監査パイプライン DAG（9 論理ステージ：ASK・HYBRID・AI バッジ表示）"
from drawlib.canvas import save, setup
from drawlib.graph import LayerGraph
from drawlib.lines import lines
from drawlib.shapes import rectangle
from drawlib.styles import Styles
from drawlib.text import text

setup(width=156, height=84, dpi=150)

text(
    (78.0, 79.5),
    "Executed Audit Pipeline DAG — py_api_fastapi_clean (wf-f819234f | 0 Skipped)",
    style=Styles.DarkBold.patch(text_size=11.5),
)

g = LayerGraph(
    direction="LR",
    rank_sep=5.5,
    node_sep=2.8,
    default_node_width=23.0,
    default_node_height=9.2,
    edge_routing="orthogonal",
)

g.node("plan", width=22.0, height=9.5, layer=0)
g.node("repo", width=23.5, height=9.5, layer=1)
g.node("supply", width=25.5, height=8.8, layer=2)
g.node("ast", width=25.5, height=8.8, layer=2)
g.node("runtime", width=25.5, height=8.8, layer=2)
g.node("trivy", width=25.5, height=8.8, layer=2)
g.node("dast", width=25.5, height=8.8, layer=2)
g.node("synth", width=24.0, height=9.5, layer=3)
g.node("score", width=24.5, height=11.0, layer=4)

g.edge("plan", "repo")
g.edge("repo", "supply")
g.edge("repo", "ast")
g.edge("repo", "runtime")
g.edge("repo", "trivy")
g.edge("repo", "dast")
g.edge("ast", "synth")
g.edge("supply", "score")
g.edge("synth", "score")
g.edge("runtime", "score")
g.edge("trivy", "score")
g.edge("dast", "score")

layout = g.get_layout(width=156.0, height=84.0, margin=4.0)

# Compute exact bounding box of solved nodes and center cleanly inside x=[4, 152], y=[13, 73]
min_x = min(n.x - n.width / 2.0 for n in layout.nodes.values())
max_x = max(n.x + n.width / 2.0 for n in layout.nodes.values())
min_y = min(n.y - n.height / 2.0 for n in layout.nodes.values())
max_y = max(n.y + n.height / 2.0 for n in layout.nodes.values())
dx = 78.0 - (min_x + max_x) / 2.0
dy = 43.0 - (min_y + max_y) / 2.0

for edge in layout.edges:
    pts = [(px + dx, py + dy) for px, py in edge.points]
    lines(pts, arrow_head="->", style=Styles.Muted)

specs = [
    ("plan", "[ASK] Confirm Plan", "Auto-approved DAG", Styles.Neutral, Styles.DarkBold, Styles.Muted),
    ("repo", "[HYBRID] Repo & Deps", "14 src / 3 tests, 5 deps", Styles.PrimaryNeutral, Styles.DarkBold, Styles.Muted),
    ("supply", "[AI] Supply Chain", "SHA-pin CI, non-root", Styles.SecondaryNeutral, Styles.DarkBold, Styles.Muted),
    ("ast", "[HYBRID] Python AST", "14 files, 435 LOC, 0 sinks", Styles.PrimaryNeutral, Styles.DarkBold, Styles.Muted),
    ("runtime", "[HYBRID] Docker Run", "4/4 tests, 85.2% cov", Styles.PrimaryNeutral, Styles.DarkBold, Styles.Muted),
    ("trivy", "[HYBRID] Trivy SCA", "Trivy 0 CRIT/HIGH app", Styles.PrimaryNeutral, Styles.DarkBold, Styles.Muted),
    ("dast", "[HYBRID] Live DAST", "DAST 15/19 probes", Styles.PrimaryNeutral, Styles.DarkBold, Styles.Muted),
    ("synth", "[AI] Arch / PRR / Test", "5 layers, 12F, cov audit", Styles.SecondaryNeutral, Styles.DarkBold, Styles.Muted),
    ("score", "[AI] Score & Report", "94/100 (S) | 16 rules", Styles.PrimaryFlat, Styles.WhiteBold, Styles.White),
]

for nid, title_lbl, sub_lbl, box_style, t_style, s_style in specs:
    n = layout[nid]
    cx, cy = n.x + dx, n.y + dy
    rectangle((cx, cy), width=n.width, height=n.height, style=box_style.patch(shape_r=1.5))
    text((cx, cy + 1.6), title_lbl, style=t_style.patch(text_size=9.2))
    text((cx, cy - 2.0), sub_lbl, style=s_style.patch(text_size=8.6))

# Legend bar cleanly separated below DAG
legend_items = [
    (22.0, "[ASK] Human Plan Gate", Styles.Neutral, Styles.Dark),
    (59.0, "[HYBRID] Deterministic + AI", Styles.PrimaryNeutral, Styles.Dark),
    (97.0, "[AI] Qualitative Audit", Styles.SecondaryNeutral, Styles.Dark),
    (134.0, "Final Score (94/100 S)", Styles.PrimaryFlat, Styles.WhiteBold),
]
for lx, ltxt, lbox, lts in legend_items:
    rectangle((lx, 4.8), width=33.0, height=5.4, style=lbox.patch(shape_r=1.2))
    text((lx, 4.8), ltxt, style=lts.patch(text_size=9.2))

save()
```

## 検査対象範囲と実行済み決定論ツール

| スコープ項目 | 記録された事実データ（`audit_scope`） |
| :--- | :--- |
| **対象ルート・パス** | `examples/python/api_fastapi_clean` ・ source=`['src']`, tests=`['tests']`, docs=`['README.md']`, exclude=`['none']` |
| **言語・フレームワーク** | 主要言語=`python`、副次言語=`['none']`、検出フレームワーク=`fastapi`, `pydantic`, `pytest`, `httpx` |
| **Git 来歴** | `main@d1e02277 (dirty)` |
| **実行済み決定論ツール** | `project_inspect (python)`、`tree-sitter AST (python)`、`container runtime harness (docker: python/uv.dockerfile)`、`Trivy (docker: fs+image)`、`web_pentest (httpx, 19 probes)` |
| **ステージ実行実績** | 全 12 ワークフローステージ（`ASK` 1・`HYBRID` 5・`AI` 6 — 11 完了 + `create_report` 実行中、スキップ `0` 件） |

## 7 軸の決定論ベースライン対 AI 調整（`±10pt` アンカリング）

各評価軸のスコアは決定論アナライザのベースラインを基準とし、明確な根拠に基づく AI 定性調整を最大 `±10pt` に制限して算出しています。

| 健全性評価軸 | 決定論ベースライン | AI 調整（`Δ`） | 最終スコア | 根拠・評価理由 |
| :--- | :---: | :---: | :---: | :--- |
| **Architecture（設計）** | `100` | `-4` | **96** | 循環依存ゼロ・純粋ドメイン中核の厳格な 4 層クリーン構成（`api -> services -> domain + infra`）。`-4pt` は 12-Factor VI における既定 `InMemoryOrderRepository` のプロセス内状態保持を反映。 |
| **Code Quality（品質）** | `100` | `-2` | **98** | インポート衛生 100%、複雑度ホットスポット・バグ懸念イディオムともに 0 件、構造化ログと最新 FastAPI ライフスパン／Pydantic v2 準拠。`-2pt` は軽微な `StarletteDeprecationWarning` を反映。 |
| **Typing（型安全性）** | `100` | `0` | **100** | 型カバレッジ 100%、`py.typed` マーカー完備、`from __future__ import annotations` 徹底、`Any` 使用・無条件 type ignore ともに 0 件。 |
| **Testing（テスト）** | `100` | `-10` | **90** | オフライン Docker pytest `4/4` 合格、行カバレッジ `85.2%`（コア領域 100%）。`-10pt` は `routes.py`（`56.0%`）・`webhook_client.py`（`55.6%`）の未カバー分岐に伴う分岐カバレッジ `62.5%` を反映。 |
| **Dependencies（依存）** | `100` | `-5` | **95** | PEP 621 `pyproject.toml` + `uv.lock`、未固定依存 0 件、宣言アプリ CVE 0 件、Dependabot・SHA 固定 CI 完備。`-5pt` は `pip@24.2` を内包する旧 `python:3.12.6-slim-bookworm` ベースイメージを反映。 |
| **Security（セキュリティ）** | `85` | `-1` | **84** | 宣言アプリ CVE・シークレット・危険シンクすべて 0 件、非 root Dockerfile、DAST `15/19` 合格。ライブ DAST の `CWE-306`（未認証 `POST /v1/orders`）、`CWE-200`（`/openapi.json`）、`CWE-693` ヘッダー欠如、および Debian 12.7 OS CVE を減点（ビルド専用 `pip` CVE 5 件は `low` へ再分類）。 |
| **Documentation（文書）** | `100` | `-2` | **98** | Diataxis 構成の `README.md`（Quickstart・How-To・API リファレンス・アーキテクチャ解説）と全公開シンボル 100% の Google スタイル docstring。 |

## 監査ステップ別スコア（低い順）

```drawlib align=center code=fold file=audit_step_scores.png caption="実行済み監査ステップ別スコア（低い順：82/100 〜 96/100）"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.styles import Styles

setup(width=146, height=62, dpi=150)

chart = BarChart(
    axis_line_style=Styles.DarkThin,
    width=96.0,
    height=44.0,
    categories=[
        "security_vulnerability_audit (A)",
        "web_penetration_audit (A)",
        "python_test_audit (A)",
        "container_runtime_audit (S)",
        "service_readiness_audit (S)",
        "supply_chain_audit (S)",
        "python_ast_audit (S)",
        "repo_structure_audit (S)",
    ],
    orientation="horizontal",
    bar_width_ratio=0.62,
    bar_r=0.8,
    axis_text_style=Styles.Dark.patch(text_size=9.6),
    grid_style=Styles.MutedDashedThin,
    value_text_style=Styles.DarkBold.patch(text_size=9.8),
    value_format="{:.0f}",
    title="Audit Step Scores (Weakest -> Strongest | Grade S >= 90)",
    title_style=Styles.DarkBold.patch(text_size=11.5),
)
chart.configure_x_axis(
    min_value=0.0,
    max_value=105.0,
    ticks=[0, 20, 40, 60, 80, 90, 100],
    show_grid=True,
    label="Audit Score (0-100)",
)
chart.add_series(
    "Step Score",
    [82, 86, 88, 90, 91, 92, 95, 96],
    style=Styles.PrimaryNeutral,
)
chart.draw((40.0, 9.0))

save()
```

## ルール準拠マトリクス（`WARN -> PASS`・全 16 ルール）

```drawlib align=center code=fold file=rule_compliance_summary.png caption="PNI ルール準拠マトリクス（4 WARN・12 PASS・0 FAIL — 事前ソート済み）"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Colors, Styles
from drawlib.text import text

setup(width=146, height=96, dpi=150)

text(
    (73.0, 92.5),
    "PNI Rule Compliance Matrix — 12/16 PASS, 4 WARN, 0 FAIL",
    style=Styles.DarkBold.patch(text_size=11.5),
)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=9.5),
    header_cell_style=Styles.PrimaryFlat,
    header_text_style=Styles.WhiteBold.patch(text_size=9.8),
    border_style=Styles.MutedThin,
    has_header=True,
)
tbl.set_style_cell_evenodd(
    Colors.White,
    Styles.Dark.patch(text_size=9.5),
    Colors.Neutral,
    Styles.Dark.patch(text_size=9.5),
)
tbl.set_style_cell_header(Colors.Primary, Styles.WhiteBold.patch(text_size=9.8))
tbl.set_style_cell(
    Styles.WarningNeutral.shape_fill_color,
    Styles.DarkBold.patch(text_size=9.5),
    rows=[1, 2, 3, 4],
    columns=[0],
)
tbl.set_style_cell(
    Styles.SuccessNeutral.shape_fill_color,
    Styles.DarkBold.patch(text_size=9.5),
    rows=list(range(5, 17)),
    columns=[0],
)

rows = [
    ["Status", "Rule ID", "Source Action", "Primary Evidence Summary"],
    ["WARN", "common/security", "service_readiness", "0 secrets/sinks; /v1/orders lacks caller auth"],
    ["WARN", "common/security_vulnerability", "python_ast_audit", "0 app CRIT/HIGH; CWE-306/200/693 DAST; 612 OS"],
    ["WARN", "common/supply_chain", "security_vuln_audit", "SHA-pinned CI & uv.lock; aged Debian 12.7 base"],
    ["WARN", "common/twelve_factor", "service_readiness", "III/IV/IX/XI PASS; VI WARN (InMemoryRepo)"],
    ["PASS", "common/architecture", "python_ast_audit", "Strict 4-layer acyclic DAG; 0 cycles/violations"],
    ["PASS", "common/documentation", "repo_structure", "Diataxis README (23 lines) & 100% docstrings"],
    ["PASS", "common/git_workflow", "repo_structure", ".gitignore + CI ruff check & pytest on main"],
    ["PASS", "common/maintainability", "python_ast_audit", "0 complex funcs, 0 global state, 0 bug idioms"],
    ["PASS", "common/production_readiness", "container_runtime", "5.0s httpx timeout, /healthz 200, WEBHOOK_DEFERRED"],
    ["PASS", "common/runtime_verification", "deterministic", "Docker build PASS, 4/4 tests, 85.2% cov, smoke OK"],
    ["PASS", "python/code_quality", "python_ast_audit", "100% Google docstrings, 0 print logs, clean style"],
    ["PASS", "python/dependencies", "repo_structure", "PEP 621 uv_build, 5 bounded deps, uv.lock"],
    ["PASS", "python/frameworks/fastapi", "python_ast_audit", "Async lifespan, response_model, Depends() DI"],
    ["PASS", "python/modern_stack", "python_ast_audit", "100% import hygiene, Pydantic v2, Py 3.11+"],
    ["PASS", "python/testing", "python_test_audit", "4/4 offline tests, 100% core cov (62.5% branch)"],
    ["PASS", "python/typing", "python_ast_audit", "100% typing, py.typed, 0 Any, 0 type ignores"],
]

tbl.draw_flexible(
    (2.0, 89.5),
    column_widths=[14.0, 42.0, 28.0, 58.0],
    row_heights=[6.0] + [4.95] * 16,
    data=rows,
    align="top_left",
)

save()
```

| 判定 | ルール ID | 評価元アクション | 検証済み証跡 |
| :---: | :--- | :--- | :--- |
| **WARN** | `common/security` | `service_readiness_audit` | コミット済み・ハードコード秘密情報 0 件、危険シンク 0 件、Pydantic v2 `ConfigDict(extra='forbid')` 厳格検証、非 root `uid 10001`、最小権限 CI。ただし `/v1/orders` エンドポイントに呼び出し元認証が未実装（`routes.py:73` の `TODO`）。 |
| **WARN** | `common/security_vulnerability` | `python_ast_audit` | `SEC-01`: 宣言アプリ依存の CRIT/HIGH 0 件、`pip@24.2` CVE 6 件 + Debian 12.7 OS CVE 612 件。`SEC-02`: `DS-0026`（`HEALTHCHECK` なし）。`SEC-03/04`: シークレット・危険シンク 0 件。`SEC-05/06`: ライブ DAST で `CWE-306`（未認証 `POST /v1/orders -> 201`）、`CWE-200`（`/openapi.json`）、`CWE-693`（`X-Content-Type-Options` 欠如）を実測確認。 |
| **WARN** | `common/supply_chain` | `security_vulnerability_audit` | `uv.lock`、未固定依存 0 件、`LICENSE`、`SECURITY.md`、Dependabot、`contents: read` かつ SHA 固定の CI、非 root `appuser` と `.dockerignore` 完備。一方 `Dockerfile` が旧 `python:3.12.6-slim-bookworm`（Debian 12.7 / `pip@24.2`）を固定し `HEALTHCHECK` を欠く。 |
| **WARN** | `common/twelve_factor` | `service_readiness_audit` | Factor III（`pydantic-settings`）、IV（`OrderRepository` Protocol）、IX（lifespan）、XI（`logging.getLogger`）は PASS。Factor VI は `main.py:33` の既定 `InMemoryOrderRepository` により WARN。 |
| **PASS** | `common/architecture` | `python_ast_audit` | 厳格な非循環レイヤー DAG（`api -> services -> domain + infra`）。`domain/` 内にフレームワーク／ネットワーク依存ゼロ、循環依存 0 件、境界違反 0 件。 |
| **PASS** | `common/documentation` | `repo_structure_audit` | `README.md`（23 行・6 見出し）が Diataxis 構成に沿った Quickstart・運用 How-To・HTTP API リファレンス・レイヤー解説を網羅。 |
| **PASS** | `common/git_workflow` | `repo_structure_audit` | `.gitignore` コミット済み。`.github/workflows/ci.yml` が `main` への push / PR で `ruff check` と `pytest` を自動ゲート実行。 |
| **PASS** | `common/maintainability` | `python_ast_audit` | 全 14 ファイル（435 LOC）で複雑関数 0 件、過多引数 0 件、グローバル可変状態 0 件、バグ誘発イディオム 0 件。 |
| **PASS** | `common/production_readiness` | `container_runtime_audit` | タイムアウト欠落 I/O 0 件（`timeout_sec=5.0`）、`/healthz -> 200`、`logging.getLogger` による構造化ログ、`httpx.HTTPError` 時の `WEBHOOK_DEFERRED` グレースフル縮退。 |
| **PASS** | `common/runtime_verification` | `deterministic_baseline` | `RV-01` Dockerfile・ハーネスビルド成功、`RV-02` オフラインテスト `4/4` 合格（`--network=none`）、`RV-03` 行 `85.2%`（`178/209` 文）・分岐 `62.5%`、`RV-04` ASGI スモーク `/healthz -> 200`。 |
| **PASS** | `python/code_quality` | `python_ast_audit` | Google スタイル docstring カバレッジ 100.0%、シグネチャ不一致 0 件、非構造化 `print` 0 件、一貫した命名規約。 |
| **PASS** | `python/dependencies` | `repo_structure_audit` | PEP 621 `pyproject.toml`（`uv_build`、`requires-python >=3.11`）、上限／下限明示の実行時依存 5 件、`[dependency-groups].dev` 分離、`uv.lock` コミット済み。 |
| **PASS** | `python/frameworks/fastapi` | `python_ast_audit` | `main.py` のモダン `asynccontextmanager` lifespan、全ルートへの `response_model` 明示、`routes.py` の `Depends()` DI、タイムアウト付き非同期 `httpx.AsyncClient`。 |
| **PASS** | `python/modern_stack` | `python_ast_audit` | インポート衛生 100.0%、PEP 621 + `uv.lock`、Pydantic v2 `ConfigDict` / `@field_validator`、Python 3.11+ `StrEnum` と `X \| None` ユニオン型、未使用／未宣言依存 0 件。 |
| **PASS** | `python/testing` | `python_test_audit` | `pytest` + `pytest-cov` 構成済み。決定論オフラインテスト `4/4`、アサーションなしテスト 0 件、静的モジュールカバレッジ 100%、コア領域行カバレッジ 100%（分岐 `62.5%`）。 |
| **PASS** | `python/typing` | `python_ast_audit` | 型安全性カバレッジ 100.0%、`py.typed` 完備、弱い `Any` 使用 0 件、無条件 type ignore 0 件、`from __future__ import annotations` 全ファイル統一。 |

## 集約済み検出事項一覧（生検出 12 件 -> 9 箇所に集約）

**検出元内訳**: 決定論アナライザ `6` 件 + AI 定性監査 `6` 件 = 合計 `12` 件（`MEDIUM` 3 件・`LOW` 9 件）を、重複箇所を統合した `9` 行で以下に記載します。

| # | 深刻度 | 対象箇所 | 関連ルール ID | 集約済み証跡 | 推奨修正方針 |
| :-: | :---: | :--- | :--- | :--- | :--- |
| 1 | **MEDIUM** | `Dockerfile` | `common/security_vulnerability` | `python:3.12.6-slim-bookworm`（Debian 12.7）の Trivy イメージ検査で Debian OS CVE 9 CRITICAL / 158 HIGH（`libgnutls30` `CVE-2026-42010`、`openssl`/`libssl3` `CVE-2026-31789` 等）、`pip@24.2` CVE 6 件、および `DS-0026`（`HEALTHCHECK` 欠如）を検出。 | 最新パッチ適用済み `python:3.12.x-slim-bookworm` へ更新し、マルチステージ `uv` コピーで実行ステージから `pip` を除去・`/healthz` 用 `HEALTHCHECK` を追加。 |
| 2 | **MEDIUM** | `src/order_dispatch/api/routes.py` | `common/security_vulnerability`, `common/runtime_verification` | `POST /v1/orders`・`GET /v1/orders/{order_id}` に OAuth2/JWT/API キー `Depends()` ガードが未設定（73 行目 `TODO(security)`）。ライブ DAST が未認証 POST で HTTP 201 と生成 `order_id` を受信。さらに `routes.py` 行 `56.0%`・分岐 `0.0%` により全体分岐カバレッジが `62.5%`。 | FastAPI `Security`/`Depends()` による認証・テナント認可を導入し、`TestClient`（200/404）および `MockTransport` 分岐テストを追加。 |
| 3 | **LOW** | `src/order_dispatch/main.py` | `common/twelve_factor`, `common/security_vulnerability` | ライフスパン起動時の既定実装がプロセス内 `InMemoryOrderRepository`（複数レプリカ間で状態共有不可）。またライブプローブで認証不要の `GET /openapi.json -> 200`（4,753 bytes）と `/healthz` の `X-Content-Type-Options: nosniff` 欠如を確認。 | `env == "prod"` 向けに外部永続 `OrderRepository`（PostgreSQL/Redis）を選択可能にし、本番での `openapi_url` 無効化とセキュリティヘッダーミドルウェアを登録。 |
| 4 | **LOW** | `-` | `CVE-2025-8869` | `pip@24.2`（`python-pkg`）— AI 再分類済み（wheel シンボリックリンク展開脆弱性は ASGI 実行時非到達）。 | `pip >= 25.3` へ更新、またはマルチステージ実行イメージから `pip` を除外。 |
| 5 | **LOW** | `-` | `CVE-2026-13346` | `pip@24.2`（`python-pkg`）— AI 再分類済み（パッケージインデックス経由のインストールはビルド時限定）。 | `pip >= 26.2.0` へ更新、またはマルチステージベースイメージを刷新。 |
| 6 | **LOW** | `-` | `CVE-2026-1703` | `pip@24.2`（`python-pkg`）— 細工された wheel アーカイブ展開時のパストラバーサル情報漏えい。 | `pip >= 26.0` へ更新、または実行ステージから `pip` を除外。 |
| 7 | **LOW** | `-` | `CVE-2026-3219` | `pip@24.2`（`python-pkg`）— AI 再分類済み（Dockerfile 9 行目のビルド時インストールに限定）。 | `pip >= 26.1` へ更新、またはマルチステージビルドを採用。 |
| 8 | **LOW** | `-` | `CVE-2026-6357` | `pip@24.2`（`python-pkg`）— AI 再分類済み（アプリ実行時に `pip` を動的呼び出ししないため非到達）。 | `pip >= 26.1` へ更新、または実行ステージから `pip` を除去。 |
| 9 | **LOW** | `-` | `CVE-2026-8643` | `pip@24.2`（`python-pkg`）— AI 再分類済み（ベースイメージ同梱のビルド専用ツールであり実行時未使用）。 | マルチステージ化または `pip >= 26.1.2`（推奨 `>= 26.2.0`）へ更新。 |

## AI 誤検知トリアージ記録および設計免除（Waiver）

**設定済み設計免除（`pni.toml [[opt_out]]`）**: `0` 件。  
**AI 検出調整（`finding_adjustments`）**: `pip@24.2` に対する決定論スキャン検出 `5` 件を `medium` から `low` へ再分類しました。`pip` は `python:3.12.6-slim-bookworm` に同梱されたビルド時パッケージ管理ツールであり、`order-dispatch` の Uvicorn ASGI リクエスト処理からインポート・実行される経路が存在しないためです。

| 検出 ID | CVE ID | 処置 | トリアージ根拠 |
| :--- | :--- | :---: | :--- |
| `det-13c60704` | `CVE-2026-8643` | `reclassify -> low` | `pip@24.2` はベースイメージ同梱のビルド専用ツールであり `order-dispatch` 実行時には未使用。マルチステージビルドまたは `pip>=26.2` で解消可能。 |
| `det-f749f183` | `CVE-2026-13346` | `reclassify -> low` | パッケージインデックス経由インストール時の脆弱性であり、実行時 HTTP リクエストからは到達不能。ベースイメージ刷新で軽減。 |
| `det-88839930` | `CVE-2026-6357` | `reclassify -> low` | wheel 展開時の脆弱性であり、`order-dispatch` が実行時に `pip` を動的起動しないため非到達。マルチステージ実行イメージで対処。 |
| `det-dac9a878` | `CVE-2025-8869` | `reclassify -> low` | シンボリックリンク展開検証漏れは wheel インストール時のみに該当し、Uvicorn ASGI 処理では発生しない。 |
| `det-dbf87858` | `CVE-2026-3219` | `reclassify -> low` | アーカイブ処理の不具合は `Dockerfile` 9 行目のビルド時インストールに限定され、実行時には露出しない。 |

## 機械可読証跡アーティファクト一覧

本レポートの根拠となる構造化テレメトリ・検出事項・アーキテクチャ記録は、以下の機械可読ファイルとして保存されています。

| アーティファクトパス | スキーマ / 形式 | 用途 |
| :--- | :--- | :--- |
| `docs/reports/py_api_fastapi_clean/py_api_fastapi_clean_score.json` | `ScoreResult` v2.0（JSON） | 7 軸スコア・根拠・ランタイム／Trivy／DAST 実測値・全検出事項の完全データ |
| `docs/reports/py_api_fastapi_clean/py_api_fastapi_clean_summary.json` | `ScoreSummary`（JSON） | CI ゲートおよびポータル連携向けの軽量サマリー |
| `docs/reports/py_api_fastapi_clean/py_api_fastapi_clean_findings.sarif` | `SARIF 2.1.0` | GitHub Code Scanning および IDE インポート用検出結果 |
| `docs_src/reports/py_api_fastapi_clean/_facts/plan.json` | PNI 計画（JSON） | 事前偵察計画および検証済み Mermaid 実行 DAG |
| `docs_src/reports/py_api_fastapi_clean/_facts/facts.json` | 決定論ファクト束（JSON） | AST・コンテナランタイム・Trivy SCA・DAST の生テレメトリ |
| `docs_src/reports/py_api_fastapi_clean/_facts/architecture.json` | `ArchitectureRecord`（JSON） | 実コード根拠付き 5 レイヤー構造マップおよび実行フロー定義 |
