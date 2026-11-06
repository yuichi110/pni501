# 3. 推奨する変更対応

検出された28件の指摘（`CRITICAL` 8件・`HIGH` 14件・`MEDIUM` 5件・`LOW` 1件）および14件の `FAIL` ルールを安全かつ段階的に解消するため、施策を **P0（即時緊急対応：7件）→ P1（構造・再現性・テスト基盤確立：5件）→ P2（保守性リファクタリング・ドキュメント整備：2件）** の計14アクションへ整理しました。まずは **Phase 1 (P0)** で秘密情報・特権CI・CWE危険シンク・コンテナ基盤CVE・起動時クラッシュを解消し、ステージ済 `.pni/pentests/` DAST ゲートおよび回帰テスト網を通過させた上で **Phase 2 (P1)** の循環依存解消へ進む手順を推奨します。

```drawlib file=03_remediation_roadmap.png caption="図3-1: 優先度順の3段階是正ロードマップ (P0 緊急止血・DAST起動復旧 -> P1 境界・ロック・網羅率確立 -> P2 複雑度低減・文書化)"
from drawlib.canvas import save, setup
from drawlib.smartarts import Panel, Roadmap
from drawlib.styles import Styles

setup(width=146, height=62, dpi=150)

Panel(
    "段階的改善ロードマップ (全14アクション: P0=7件 / P1=5件 / P2=2件)",
    style=Styles.Neutral,
    header_style=Styles.Primary,
    text_style=Styles.WhiteBold.patch(text_size=11.0),
).draw((2, 2), width=142, height=58)

rm = Roadmap(
    style=Styles.WhiteBordered,
    text_style=Styles.DarkBold.patch(text_size=10.2),
    description_style=Styles.Dark.patch(text_size=9.2),
    spine_style=Styles.PrimaryBold,
    badge_style=Styles.Danger,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.2),
    direction="horizontal",
)
rm.add(
    "Phase 1: P0 緊急止血 & DAST復旧 (7件)",
    "秘密鍵除去、特権CI廃止、safe_load化・shell廃止、slim非root化、起動復旧・DASTゲート通過",
    badge_text="P0 即時",
)
rm.add(
    "Phase 2: P1 クリーン境界 & 再現性確立 (5件)",
    "循環依存解消、pyproject.toml+uv.lock移行、Lifespan+/healthz+Timeout実装、行網羅率85%超達成",
    badge_style=Styles.Warning,
    badge_text="P1 優先",
)
rm.add(
    "Phase 3: P2 保守性向上 & CLI/文書刷新 (2件)",
    "processor.py認知的複雑度(44->15未満)分割・Docstring整備、legacy_sync.shのPython CLI化",
    badge_style=Styles.Primary,
    badge_text="P2 強化",
)
rm.draw((5, 5), width=136, height=42)

save()
```

## 最優先（P0〜P1）変更対応マトリクス

以下の図表は、即時着手が求められる P0 アクション群と中核アーキテクチャ改善 P1 代表施策の対象ファイル・期待効果・関連ルール対応を示しています。

```drawlib file=03_priority_action_matrix.png caption="図3-2: 最優先改善施策（優先度・施策・対象ファイル・期待効果・関連ルール）"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=74, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=8.8),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.2),
    border_style=Styles.Gray4Thin,
)
tbl.draw_flexible(
    (2, 72),
    column_widths=[10.0, 33.0, 31.0, 38.0, 30.0],
    row_heights=[9.0, 9.5, 9.5, 9.5, 9.5, 9.5, 9.5],
    data=[
        ["優先度", "施策", "対象ファイル", "期待効果", "関連ルール"],
        ["P0", "秘密鍵外部化 & ダミー鍵削除", "processor.py, config/*.json", "ソース・イメージからの秘密情報完全除去", "common/security"],
        ["P0", "特権CI廃止 & Action SHA固定", "deploy.yml, Dockerfile", "PR権限昇格防止・非rootコンテナ実行", "common/supply_chain"],
        ["P0", "CWE-502/78解消 & API認証追加", "processor.py, handlers.py", "RCE/OSコマンド注入根絶・境界防御確立", "security_vulnerability"],
        ["P0", "HTTP起動復旧 & DASTゲート通過", "schemas.py, handlers.py, reqs", "server_booted復旧・CWE-306/20プローブ合格", "CWE-306, CWE-20"],
        ["P0", "python:3.12-slim多段化 & CVE解消", "Dockerfile, requirements.txt", "Python HIGH 4件・OS CRIT 24件の解消", "CVE-2025-47273 他"],
        ["P1", "循環依存解消 & uv.lock・テスト網羅", "pricing.py, tests/test_orders.py", "単方向DAG回復・行カバレッジ85%以上", "architecture, testing"],
    ],
)

save()
```

## 全14件の改善アクション一覧（完全トレーサビリティ表）

| # | 優先度 | 施策タイトルと具体実装内容 | 対象ファイル | 期待効果 | 関連ルール / CVE |
| :---: | :---: | :--- | :--- | :--- | :--- |
| 1 | **P0** | **ハードコード秘密鍵の外部化とコミット済鍵ファイルの削除**: `WEBHOOK_SIGNING_SECRET` を環境変数設定へ移行し、`config/service_account_dummy.json` を履歴・ビルド文脈から除外する。 | `order_app/services/processor.py`, `config/service_account_dummy.json` | ソース・コンテナ層からの秘密情報漏洩リスクを根絶。 | `common/security` |
| 2 | **P0** | **GitHub Actions 最小権限化とコンテナビルド衛生の確立**: `pull_request_target` を `pull_request` に変更し、`permissions: contents: read` と 40文字コミットSHA固定、`.dockerignore` を導入する。 | `.github/workflows/deploy.yml`, `Dockerfile`, `config/service_account_dummy.json` | 未信頼 PR による任意コード実行・権限昇格を遮断。 | `common/supply_chain`, `common/security` |
| 3 | **P0** | **CWE-502/CWE-78 危険シンク除去・可変状態修正・API認証強制**: `yaml.safe_load()` への置換、`subprocess.run(..., shell=True)` 廃止、`tags=[]` と `ORDER_STATE_CACHE` 排除、`POST /orders` 認証追加を行う。 | `order_app/services/processor.py`, `order_app/api/handlers.py`, `order_app/schemas.py` | RCE/コマンド注入シンクとリクエスト間タグ汚染バグを解消。 | `common/security_vulnerability`, `common/security`, `common/maintainability` |
| 4 | **P0** | **コンテナ HTTP 起動復旧と `.pni/pentests/` DAST ゲート通過**: `legacy_flag: bool = True` と型付き `OrderItem` DTO 導入、`uvicorn` 固定、`POST /orders` 認可・セキュリティヘッダ付与後、`web_pentest` 全プローブを通過させる。 | `order_app/schemas.py`, `order_app/api/handlers.py`, `requirements.txt` | `server_booted=true` を回復し、`CWE-306`（`401`/`403`）・`CWE-20`（`422`）・HTTP ヘッダ防御を動的に保証。 | `common/security_vulnerability`, `CWE-306`, `CWE-20`, `CWE-693` |
| 5 | **P0** | **脆弱 Python パッケージ更新と `python:latest` root 基盤の刷新**: `python:3.12-slim` マルチステージ＋非root `USER`＋`HEALTHCHECK` へ移行し、`urllib3>=2.8.0` 固定および不要 `flake8`/`black`/`setuptools` 除外を行う。 | `Dockerfile`, `requirements.txt`, `setup.py` | Python HIGH CVE 4件と Debian `-dev` 由来の 3,554 OS CVE の大半を一掃。 | `common/security_vulnerability`, `common/supply_chain`, `CVE-2025-47273`, `CVE-2026-97687`, `CVE-2026-97689`, `GHSA-6v7p-g79w-8964`, `DS-0002`, `DS-0001`, `DS-0026` |
| 6 | **P0** | **アサーション付きミラー単体・統合テストスイート構築**: `pytest`/`pytest-cov`/`httpx` を dev 依存へ追加し、API・バッチ処理・価格計算の正常／異常系テストを整備する。 | `tests/test_orders.py`, `order_app/api/handlers.py`, `order_app/services/processor.py`, `order_app/domain/pricing.py` | 安全なリファクタリングのための回帰検知網（85%以上）を確立。 | `python/testing` |
| 7 | **P0** | **起動時 `PydanticUserError` 修正と `uvicorn` 依存の明示**: `schemas.py` の `legacy_flag: bool = True` 型注釈付与と Pydantic v2 移行、`uvicorn` 宣言、FastAPI `GET /healthz` 実装を行う。 | `order_app/schemas.py`, `order_app/api/handlers.py`, `requirements.txt`, `Dockerfile` | ASGI アプリの正常インポート・起動スモーク（RV-04）を復旧。 | `common/runtime_verification`, `common/production_readiness` |
| 8 | **P1** | **循環依存の解消・クリーンレイヤ境界と型注釈 100% 化**: `ACTIVE_PROMO_CODES` を `constants.py` へ移設し、`pricing.py` の `handlers`/`_internal` 参照と Flask 同居・未宣言 `boto3` を撤去、全関数に型を付与する。 | `order_app/domain/pricing.py`, `order_app/api/handlers.py`, `order_app/infra/_internal.py`, `order_app/infra/gateway.py`, `order_app/constants.py` | 単方向 DAG アーキテクチャ回復と静的型検査ゼロエラーを達成。 | `common/architecture`, `python/typing`, `python/modern_stack` |
| 9 | **P1** | **FastAPI Lifespan・`/healthz`・型付き設定・非同期 Timeout 実装**: `pydantic-settings` による設定一元化、`@asynccontextmanager lifespan`、`httpx.AsyncClient(timeout=5.0)`、構造化 `logging` を導入する。 | `order_app/api/handlers.py`, `order_app/infra/gateway.py`, `order_app/services/processor.py`, `order_app/infra/_internal.py` | イベントループブロッキング防止とマルチレプリカ無状態運用を実現。 | `common/twelve_factor`, `common/production_readiness` |
| 10 | **P1** | **OpenSSF ガバナンス文書と Dependabot 自動更新の整備**: `.gitignore`・`LICENSE`・`SECURITY.md`・`.github/dependabot.yml` を追加し、PR 自動テストゲートを構成する。 | `.github/workflows/deploy.yml`, `requirements.txt` | サプライチェーン統制と脆弱性検知の継続的自動化を実現。 | `common/supply_chain`, `common/git_workflow` |
| 11 | **P1** | **PEP 621 `pyproject.toml` + `uv.lock` への完全移行**: レガシー `setup.py` と未ピン `requirements.txt` を廃止し、実行時依存と `[dependency-groups].dev` を厳格分離する。 | `requirements.txt`, `setup.py` | 100% 決定論的な依存解決と不要パッケージ混入防止を実現。 | `python/dependencies`, `common/supply_chain` |
| 12 | **P1** | **カバレッジ 0.0% モジュール群の解消（6.6% → 85%以上）**: 未実行だった主要6モジュール（計99文）に対するオフライン単体・HTTP テストを追加し、`--cov-fail-under=80` を強制する。 | `tests/test_orders.py`, `order_app/services/processor.py`, `order_app/domain/pricing.py`, `order_app/infra/gateway.py` | 全ビジネス分岐・エラー経路の実行保証を確立。 | `common/runtime_verification` |
| 13 | **P2** | **バッチ処理関数の複雑度分割と正確な Docstring 整備**: `process_order_batch`（認知的複雑度 `44`）を責務別ヘルパーへ分割し、全公開シンボルの Google 形式 Docstring を同期する。 | `order_app/services/processor.py`, `order_app/domain/pricing.py`, `order_app/api/handlers.py` | 認知的複雑度を 65%以上削減し、保守性と API 仕様明確性を向上。 | `python/code_quality`, `common/maintainability` |
| 14 | **P2** | **レガシー Bash 同期スクリプトの Python CLI 化と README 拡充**: `scripts/legacy_sync.sh`（106 LOC）を型付き Python CLI へ置換し、Standard Readme 準拠の運用・開発手順書を整備する。 | `README.md`, `scripts/legacy_sync.sh` | シェル解析バグを排除し、開発者オンボーディング時間を短縮。 | `common/documentation`, `common/git_workflow` |
