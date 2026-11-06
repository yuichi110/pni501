# 現状の診断エンジン・レポート品質改善プラン (Diagnostic Accuracy & Report Refinement Plan)

## 1. 背景と目的

`examples/java/api_spring_messy` の自動診断レポート（`reports/java/api_spring_messy.pdf`）に対する外部レビュー（Gemini Argon4）および実データ（`reports/java/api_spring_messy_score.json`、`reports_src/java/api_spring_messy_src/`）との照合により、PNI の強み（ハルシネーションゼロの `file:line` 特定、シークレット自動伏せ字、AST×コンテナ×Trivy の因果相関）が確認された一方、以下の **5 つの具体的な改善領域** が特定された。

本プランでは、Python・Java・PHP 全言語の既存診断ワークフロー（As-Is 健全性診断）の精度・説得力・PDF 視認性を一段引き上げるための改修仕様を定義する。

---

## 2. 特定された課題と原因の整理（裏取り結果）

| # | 課題カテゴリ | 現象・指摘内容 | コードベース上の真因 |
| :-: | :--- | :--- | :--- |
| **1** | **SCA 動的バージョン解釈のギャップ** | `pom.xml` の `LATEST` に対し、「Maven ビルドでは最新 `4.2.0-RC1` で失敗」と述べつつ、Trivy では過去の `CVE-2022-22965` (Spring4Shell) が検出されており一見矛盾して見える。 | Trivy の静的マニフェスト解析は非 SemVer 文字列（`LATEST`, `RELEASE`, `*`, `dev-main`）をバージョン `0` 相当として扱い、過去の脆弱性範囲にマッチさせる仕様であるため。 |
| **2** | **ビルド阻害要因の原文提示と網羅性** | ① `spring-boot-4.2.0-RC1.jar (version 61.0)` が AI の推測に見えやすい。<br>② `LATEST` 以外にも `Java 11 HttpClient` や `spring-tx` 欠落等の独立したコンパイル阻害要因がある。 | ① `runtime_facts` には `javac` の正確なエラー原文が残っているが、レポート本文で要約のみ記載していた。<br>② AST 側で「宣言言語バージョン（Java 1.8 / PHP 7.4 等）を超える標準 API・構文の使用」を直接検出していなかった。 |
| **3** | **同一箇所 (`file:line`) 指摘の重複表示** | 第 4 章の指摘一覧表で `Dockerfile:1` が `common/supply_chain`, `common/runtime_verification`, `common/security_vulnerability` 等で計 4 行に分かれて並ぶ。 | `src/pni/_workflows/aggregator.py` の `deduplicate_and_sort_findings()` が `(rule_id, file_path, line, symbol)` キーで正規化しており、レポート表示用の「箇所単位グルーピング」を持たないため。 |
| **4** | **並行競合とレガシー API 残存の表現精度** | ローカル生成・未呼び出しの `SimpleDateFormat` が、`BillingController.channel` や `static HashMap` と同列に「並行リクエスト下で競合状態を引き起こす」と記述された。 | AST の `modernization_hints`（レガシー API 残存）と `global_state_usages` / シングルトン可変フィールド（実競合リスク）の区別がルール解釈時に曖昧になりやすいため。 |
| **5** | **Drawlib 図表・PDF 組版の視認性** | ① `ClassDiagram` + `HeatmapOverlay` の等高線数値とノード文字の重なり。<br>② 複数系列 `BarChart` の凡例（Legend）欠落。<br>③ `Table` 内の `common/documentation` が列幅折り返しで `commondocumentation/` に見える現象。 | `src/pni/_reporter/drawlib_guide.py` に複数系列凡例必須化・オーバーレイ等高線抑制・ルール ID 列幅の制約が明文化されておらず、コンパイル時の静的チェックもないため。 |

---

## 3. ワークストリーム別 実装設計

### Workstream 1: 未固定・シンボリック依存バージョンに対する SCA 注記機構 (`security_scan`)

- **対象ファイル**:
  - `src/pni/_actions/security_scan/models.py`
  - `src/pni/_actions/security_scan/parsers.py`
  - `src/pni/_rules/common/security_vulnerability.md`（および `.pni/rules/common/security_vulnerability.md`）
  - `src/pni/_reporter/blueprint.py`
- **変更内容**:
  1. `VulnerabilityItem` モデルに以下のフィールドを追加する:
     - `is_unpinned_specifier: bool = False`
     - `version_resolution_note: str = ""`
  2. `parsers.py` で `installed_version` がシンボリック指定またはワイルドカード（`LATEST`, `RELEASE`, `*`, `dev-*`, `*-SNAPSHOT`, `main`, `master`, `HEAD`, 不完全範囲）に該当する場合、`is_unpinned_specifier=True` を自動付与し、`version_resolution_note="Unpinned symbolic version in manifest; static SCA evaluates full historical CVE range until locked"` を設定する。
  3. `blueprint.py` の第 6 章データ整形および `security_vulnerability.md` ルールにて、`is_unpinned_specifier=True` の CVE は「確定バージョンの脆弱性」ではなく **「バージョン未固定（`LATEST` 等）に起因する不定リスク・Trivy 範囲マッチ警告」** として明示的に解説させる。

### Workstream 2: コンパイルエラー原文の証跡引用とターゲット言語バージョン互換 AST チェック

- **対象ファイル**:
  - `src/pni/_actions/ast_analyze/models.py`
  - `src/pni/_actions/ast_analyze/java/quality.py`（または `frameworks.py`）
  - `src/pni/_actions/ast_analyze/php/typing.py` / `frameworks.py`
  - `src/pni/_actions/ast_analyze/python/typing.py`
  - `src/pni/_reporter/blueprint.py`
- **変更内容**:
  1. **言語バージョン互換性（Language Level Mismatch）の AST 検出**:
     - `run_ast_analyze()` にオプション引数 `declared_lang_version: str | None`（`ProjectFacts.language_version_constraint` から自動連携）を渡す。
     - **Java**: `1.8` / `8` 指定時に Java 11+ API（`java.net.http.HttpClient`, `String.isBlank`, `List.of` 等）や Java 14+/16+/17+ 構文（`record`, `sealed`）を使用している箇所を確定的にリストアップする。
     - **PHP**: `7.x` 指定時に PHP 8.0+ / 8.1+ / 8.2+ 構文（`match`, `readonly`, `enum`, 名前付き引数）を使用している箇所を検出する。
     - **Python**: `requires-python`（例: `>=3.9`）に対し `3.10+` `match/case` や `3.11+` `tomllib` / `ExceptionGroup` を使用している箇所を検出する。
  2. **ビルド・テスト失敗時のエラーログ原文（Verbatim Excerpt）出力**:
     - `blueprint.py` の第 5 章（コード品質・動的検証）用データに、`RuntimeFacts.harness_build` / `project_dockerfile_build` / `test_execution` の失敗時コアエラー行（最大 3〜5 行の原文抜粋）をそのまま埋め込み、AI の言い換えによる疑義を防ぐ。

### Workstream 3: 指摘事項の「箇所単位グルーピング (`LocationFindingGroup`)」導入 (`aggregator.py`)

- **対象ファイル**:
  - `src/pni/_actions/base_model.py`
  - `src/pni/_workflows/aggregator.py`
  - `src/pni/_reporter/blueprint.py`
- **変更内容**:
  1. スコア計算およびルール適合判定のための正規化リスト `ScoreResult.findings`（ルール別）は後方互換のまま維持する。
  2. 新たに `ConsolidatedFinding` モデルを追加し、`ScoreResult.consolidated_findings` として自動生成する:
     ```python
     class ConsolidatedFinding(BaseModel):
         severity: SeverityLevel
         file_path: str
         line: Optional[int] = None
         symbol: Optional[str] = None
         rule_ids: list[str] = Field(default_factory=list)
         categories: list[str] = Field(default_factory=list)
         primary_description: str
         combined_evidence: str
         merged_recommendation: str
     ```
  3. `aggregator.py` にて `(file_path, line or 0)` が同一で内容が重複・近接する指摘（例: `Dockerfile:1` に対する `common/supply_chain`, `common/runtime_verification`, `common/security_vulnerability`）を 1 エントリに束ね、`rule_ids` に複数ルール ID を格納する。
  4. `blueprint.py` の第 4 章「指摘一覧表」では `consolidated_findings` を優先表示し、関連ルールを複数併記することで重複感を排除する。

### Workstream 4: 並行状態競合とレガシー API 残存のルール明確化

- **対象ファイル**:
  - `src/pni/_rules/java/frameworks/spring_boot.md`
  - `src/pni/_rules/php/code_quality.md`
  - `src/pni/_rules/python/code_quality.md`
- **変更内容**:
  - シングルトン Bean / ワーカープロセス上でリクエストを跨いで共有される可変状態（`BillingController.channel`、`public static Map`、Python モジュールグローバル辞書等）のみを **「実行時スレッド・リクエスト競合（Race Condition / State Bleed）」** と定義する。
  - ローカル変数内の `SimpleDateFormat` / `Vector` や未到達ヘルパー等は **「レガシー・非推奨 API 残存（Modernization Debt）」** として明確に書き分けるようルールガイドを改訂する。

### Workstream 5: Drawlib チャート・図表・テーブル組版ガードレールの強化 (`_reporter`)

- **対象ファイル**:
  - `src/pni/_reporter/drawlib_guide.py`
  - `src/pni/_reporter/compiler.py`
- **変更内容**:
  1. **`drawlib_guide.py` の組版ルール強化**:
     - **複数系列 `BarChart` / `LineChart` の凡例必須化**: `add_series()` を 2 回以上呼ぶチャートでは必ず凡例（Legend）または系列ラベルを明示すること。
     - **`ClassDiagram` + `HeatmapOverlay` の重なり防止**: ノード数が 5 個以上の `ClassDiagram` では `height >= 80` を確保し、`HeatmapOverlay` を重ねる場合は `show_contour_lines=False`（半透明ヒートスポット＋右端 `draw_colorbar` のみ）を標準として等高線数値とクラス名・矢印の衝突を防止すること。
     - **`Table` ルール ID 列の折り返し崩れ防止**: `common/security_vulnerability` や `common/documentation` を格納する列は十分な列幅（`>= 38`）を確保するか、スラッシュ直後に改行（`"common/\ndocumentation"`）を入れて PDF テキスト結合崩れ（`commondocumentation/`）を防止すること。
  2. **`compiler.py` への軽量プリフライト検査（静的構文チェック）の追加**:
     - `pni report build` / `compile` 実行時に `*.md` 内の `drawlib` コードブロックを走査し、以下を検出した場合に警告（または `--strict` 時にエラー）を出す:
       - `chart.add_series(` が 2 回以上出現するのに凡例指定が存在しない `BarChart`。
       - `ClassDiagram` と `show_contour_lines=True` の同時使用。

---

## 4. 実装ステップと検証計画

1. **Step 1**: Workstream 1〜2（`security_scan` 未固定バージョン注記、AST 言語バージョン互換検査、エラー原文抜粋）の実装と単体テスト追加。
2. **Step 2**: Workstream 3〜4（`aggregator.py` の `ConsolidatedFinding` 集約と各言語ルールの表現精緻化）の実装と単体テスト追加。
3. **Step 3**: Workstream 5（`drawlib_guide.py` 更新と `compiler.py` プリフライト検査）の実装。
4. **Step 4**: `./pcli code-check all` および `./pcli test all --parallel` による品質ゲート通過確認後、`java_api_spring_messy` レポートを再生成して p.3 / p.6 / p.11 / p.12 / p.16 の改善箇所すべてが解消されていることを実 PDF で検証する。
