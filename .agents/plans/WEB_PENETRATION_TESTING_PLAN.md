# Web ペネトレーションテスト（DAST: Python + httpx）導入計画

## 1. 背景と目的

[SECURITY_VULNERABILITY_SCANNING_PLAN.md](SECURITY_VULNERABILITY_SCANNING_PLAN.md)（Phase A）により、AST による危険シンク抽出（`AstFacts.dangerous_sinks`）・API エンドポイント棚卸し（`AstFacts.api_endpoints`）・ソケットレス Trivy コンテナスキャン（`SecurityFacts`）までの静的／サプライチェーン監査基盤が確立された。

本計画（Phase B）では、Web アプリケーション／API（Python / Java / PHP 等、対象言語不問）を隔離コンテナ上で起動し、**ホスト側の `pni501` Python 環境（`pytest` + `httpx`）から非破壊の動的 HTTP ペネトレーションプローブを実行する仕組み（`web_pentest`）** を導入する。

---

## 2. コア設計方針（二層アセット管理と透明性）

既存の [`src/pni/_dockerfiles/`](../../src/pni/_dockerfiles) → [`.pni/dockerfiles/<target>/`](../../.pni/dockerfiles) と完全に同じ設計思想を採用する。

1. **`.pni/pentests/_templates/` は作らず、パッケージ内蔵 `src/pni/_pentests/` から `.pni/pentests/<target>/` へ明示展開（Materialize）する**
   - 組み込み雛形は `src/pni/_pentests/` に保持し、監査対象ごとに対応する `.pni/pentests/<target_rel_path>/`（ルート単一プロジェクトの場合は `.pni/pentests/`）へ**自己完結した Python テストコード**として書き出す。
   - ディレクトリを開けば、ベースライン検証（セキュリティヘッダ・CORS・露出ファイル等）もターゲット固有エンドポイント検証もすべて明示的な `httpx` コードとして確認・編集できる。
   - 既存ファイルが存在する場合は上書きせず保護し（`force_regenerate_pentests=True` / `--force` 指定時のみ再生成）、人間や AI が追加・調整したプローブを資産として維持する。

2. **対象言語に依存しない統一実行基盤（`Python + pytest + httpx`）**
   - 監査対象アプリ（Spring Boot / Laravel / Raw PHP / FastAPI / Flask）は [`.pni/dockerfiles/<target>/Dockerfile`](../../.pni/dockerfiles) でビルドされた隔離コンテナ内で起動する。
   - ホスト側のポート公開は **`127.0.0.1:<ephemeral_port>:<container_port>`（ホスト側ループバック限定、`0.0.0.0` バインド禁止）** とし、`pni501` 自身の Python 環境（`sys.executable -m pytest` + `httpx`）から HTTP プローブを実行する。
   - `conftest.py` 側でも `base_url` のホスト名がループバック（`127.0.0.1` / `localhost` / `::1`）であることを検証し、外部本番サーバへの誤送信をフェイルクローズで防止する。

3. **キャッシュ汚染の防止**
   - `pytest` 実行時の JUnit XML レポート・キャッシュ・コンテナ起動ログはすべて `.pni/cache/<workflow_id>/pentest/` に出力し、`PYTHONDONTWRITEBYTECODE=1` と `-o cache_dir=...` によって `.pni/pentests/<target>/` 配下に不要な一時ファイルを残さない。

---

## 3. ディレクトリ構成とモジュール設計

### 3.1 パッケージ内蔵テンプレート & 展開マネージャ（`src/pni/_pentests/`）

```text
src/pni/_pentests/
├── __init__.py
├── manager.py                  # ensure_target_pentests() による明示展開・保護制御
├── surface_codegen.py          # AstFacts.api_endpoints / dangerous_sinks からの test_target_surface.py 生成
├── conftest.py.tmpl            # ループバック強制ガード・http_client (httpx.Client)・pentest_meta フィクスチャ
└── test_baseline_http.py.tmpl  # セキュリティヘッダ・CORS・機微パス露出・TRACE 無効化プローブ
```

### 3.2 ワークスペース側の明示展開先（`.pni/pentests/<target>/`）

```text
.pni/pentests/
└── examples/php/legacy_shop_messy/
    ├── conftest.py              # base_url / httpx.Client / record_property メタデータ付与フィクスチャ
    ├── test_baseline_http.py    # 共通 HTTP セキュリティベースライン検証 (明示展開・個別編集可)
    └── test_target_surface.py   # AST 抽出エンドポイント・クエリ引数に基づく XSS/SQLiエラー露出/LFI/未認証検証
```

### 3.3 動的検証アクションエンジン（`src/pni/_actions/pentest/`）

```text
src/pni/_actions/pentest/
├── __init__.py
├── models.py        # PentestOptions, PentestFindingItem, PentestProbeSummary, PentestFacts
├── server_plan.py   # Python(ASGI/WSGI) / Java(Spring) / PHP(Built-in) コンテナ起動コマンド & 127.0.0.1 ポート管理
├── junit_parser.py  # pytest JUnit XML + property タグからの決定的 PentestFindingItem 変換・ソート
└── runner.py        # Stage P0(展開) -> P1(ビルド) -> P2(隔離起動・Readiness待機) -> P3(pytest実行) -> P4(破棄・保存)
```

---

## 4. 検証プローブ体系（非破壊・決定的）

1. **ベースライン HTTP プローブ（`test_baseline_http.py`）**
   - `CWE-693`（Protection Mechanism Failure）: `X-Content-Type-Options: nosniff` およびクリックジャッキング対策（`X-Frame-Options` または CSP `frame-ancestors`）の欠如検出、`TRACE` メソッド有効化の検出。
   - `CWE-200`（Information Exposure）: `X-Powered-By` 等の詳細ランタイムバージョン露出、および `/.env`・`/.git/config`・`/phpinfo.php`・`/actuator/env` の公開露出検出。
   - `CWE-942`（Permissive Cross-domain Policy）: 任意 `Origin: https://evil.pni-probe.invalid` に対するオリジン反射または認証付きワイルドカード CORS の検出。

2. **AST 連動サーフェスプローブ（`test_target_surface.py`）**
   - `CWE-79`（Reflected XSS）: 抽出されたエンドポイントおよびクエリパラメータ（`q`, `promo_html` 等）へ無害カナリア文字列 `<pni-xss-canary-7f3a>` を送信し、`text/html` レスポンス内に未エスケープのまま反射されないことを検証。
   - `CWE-89` / `CWE-209`（SQLi Error / Stacktrace Exposure）: シングルクォート等の境界入力を送出し、生 SQL エラー（`SQLSTATE`, `mysqli_`, `sqlite3.`, `You have an error in your SQL syntax`）や未捕捉スタックトレースが HTTP レスポンスに漏洩しないことを検証。
   - `CWE-22` / `CWE-98`（Path Traversal / LFI）: ファイル／ページ系パラメータに対するトラバーサル入力で `/etc/passwd` や PHP `Failed opening` エラーが露出しないことを検証。
   - `CWE-306`（Missing Authentication for Critical Function）: 未認証状態での管理系・状態変更系エンドポイント（`admin`, `backup` 等）へのリクエストが `2xx` で素通りしないことを検証。

---

## 5. ワークフロー・CLI・レポート統合

1. **Primitive & Composite Action**
   - `PrimitiveType.WEB_PENTEST = "web_pentest"` を追加し、`WorkflowFactsBundle.pentest_facts` / `ScoreResult.pentest_facts` に統合する。
   - 複合アクション [`src/pni/_actions/common/web_penetration_audit.yaml`](../../src/pni/_actions/common/web_penetration_audit.yaml) およびセキュリティ規約 `SEC-06`（[`common/security_vulnerability.md`](../../src/pni/_rules/common/security_vulnerability.md)）を追加する。
2. **CLI サブコマンド（`pni pentests`）**
   - `pni pentests init [--target-root ...] [--force]` : `.pni/pentests/<target>/` へテストコードを明示展開。
   - `pni pentests run [--target-root ...] [--base-url ...]` : 単体でコンテナ起動＋ペネトレーションテストを実行し結果を表示（手直し後の即時再検証用）。
3. **Report Blueprint 第6章連携**
   - [`src/pni/_reporter/blueprint.py`](../../src/pni/_reporter/blueprint.py) の `06_security_and_supply_chain.md` に動的ペネトレーションテスト結果（プローブ総数・失敗数・実証された CWE エンドポイント証拠）を自動出力する。

---

## Verification Plan

### Engineering & Functional Verification
- `./pcli code-check all` による Ruff lint/format および Ty 静的型検査の完全パスを確認する。
- `./pcli test all --parallel` による単体・統合テストを実行する：
  - ローカル `127.0.0.1` ループバック上のテスト用 HTTP サーバ（脆弱アプリ模擬・堅牢アプリ模擬）に対し、`.pni/pentests/<target>/` の明示展開、`pytest` + `httpx` プローブ実行、JUnit XML 解析、`PentestFacts` 生成を検証する。
  - 非ループバック URL（例: `https://example.com`）指定時に `conftest.py` がフェイルクローズで拒否することを検証する。
  - 既存カスタマイズ済みテストファイルが `force_regenerate=False` で保護されることを検証する。
  - Docker 環境を用いて実際のサンプル（`examples/php/legacy_shop_messy` および `examples/python/api_fastapi_clean`）に対するコンテナ隔離ペネトレーションテストの E2E 動作を確認する。

### Security Guidelines Validation
- **Loopback Binding Only**: コンテナのホスト側ポート公開は `127.0.0.1:<host_port>:<container_port>` に厳格固定し、`0.0.0.0` への公開を禁止する。また単体テスト用モックサーバも `127.0.0.1` のみにバインドする。
- **Command Execution Hardening**: Docker / Podman および `pytest` サブプロセス呼び出しはすべて `shell=False` の引数リスト（`run_safe_command`）で実行し、コマンドインジェクション経路を排除する。
- **Path Traversal Boundary Enforcement**: `target_root` および展開先パスは `normalize_target_subpath()` と `Path.is_relative_to(workspace_root.resolve())` で境界検証を行う。
- **Non-Destructive & Secret-Safe Logging**: プローブはすべて非破壊カナリア文字列のみを用い、レスポンス証拠抜粋は長さを制限・制御文字を除去して記録する。

### Automated Security Check
- **Security Scanner**: Run a scan on all newly created files to identify common vulnerabilities (e.g., XSS, SQL injection, command injection, path traversal). If findings are detected, apply fixes and document the results.
- **Security Audit**: Audit the new code for design-level security issues (input validation, subprocess safety, loopback-only network boundaries, path traversal guards) and verify clean security posture.
