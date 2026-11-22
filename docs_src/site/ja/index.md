# pni501 (Project Nemesis Index) — 公式ドキュメント

**Project Nemesis Index (`pni501` `v0.2.0`)** は、**57 個のネイティブ `tree-sitter` CST 文法**（`ast-grep-py` から完全移行）を通じて **55 言語** に対応する、AI ネイティブなソフトウェア健全性監査・ペネトレーションテスト・モノレポ統合ロールアップ・マイグレーション計画フレームワークです。決定論的な静的解析・隔離コンテナ実行ツールと、SQLite ベースの **Workflow v2 条件付き DAG エンジン**（`needs:` / `when:`、Phase 0 偵察プランニング、`confirm_plan` 承認ゲート）、さらに自己完結型の **Drawlib ビジュアルレポート基盤**（`_facts/` 自動同期を備えた `pni_report_src -> pni_report`）を統合することで、LLM 特有の数値・パスハルシネーションを排除し、エビデンス Δ（Delta）と誤検知トリアージ（`finding_adjustments`）を備えた再現性の高い 7 軸品質スコア、トポロジカル移行計画、および出版品質の A4 ベクター PDF / HTML レポートを出力します。

```drawlib align=center code=fold file=pni_overview_pillars.png caption="pni501 (v0.2.0) の4つのアーキテクチャ基盤ピラーと55言語ポリグロット対応"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import KpiCards, Panel
from drawlib.styles import Styles

setup(width=156, height=90, dpi=150)

outer = Panel(
    "Project Nemesis Index (pni501 v0.2.0) — Four Foundational Pillars",
    header_variant="filled",
    style=Styles.PrimaryNeutral.patch(shape_r=2.0),
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=12.5),
)
outer.draw(xy=(3.0, 24.0), width=150.0, height=63.0)

cards = KpiCards(
    style=Styles.Neutral.patch(shape_r=1.8),
    metric_style=Styles.PrimaryBold.patch(text_size=13.5),
    text_style=Styles.DarkBold.patch(text_size=10.8),
    description_style=Styles.Dark.patch(text_size=10.0),
    accent_position="left_pill",
    accent_style=Styles.PrimaryFlat,
    icon_style=Styles.PrimaryBold,
    spacing=3.5,
)
cards.add(
    "P1",
    "Cascading Rules (_rules)",
    "356 built-in rules + .pni/ overrides\n55 languages (Tier A / B / C)",
    icon=phosphor.book_open_text,
)
cards.add(
    "P2",
    "Zero-Guess Analyzers (_actions)",
    "182 actions: 57 Tree-sitter CSTs,\nDocker, Trivy, pentest & DAG",
    accent_style=Styles.SecondaryFlat,
    metric_style=Styles.SecondaryBold.patch(text_size=13.5),
    icon_style=Styles.SecondaryBold,
    icon=phosphor.cpu,
)
cards.add(
    "P3",
    "Workflow v2 Engine (_workflows)",
    "112 DAG templates, plan/confirm,\nbased_on & monorepo rollup",
    icon=phosphor.database,
)
cards.add(
    "P4",
    "Blueprint Reporter (_reporter)",
    "7-axis Score+Delta, FP triage &\npni_report_src/_facts -> PDF",
    accent_style=Styles.SuccessFlat,
    metric_style=Styles.SuccessBold.patch(text_size=13.5),
    icon_style=Styles.SuccessBold,
    icon=phosphor.chart_polar,
)
cards.draw(xy=(6.5, 27.0), width=143.0, height=49.5, columns=2)

kpis = KpiCards(
    style=Styles.Neutral.patch(shape_r=1.6),
    metric_style=Styles.PrimaryBold.patch(text_size=13.0),
    text_style=Styles.DarkBold.patch(text_size=10.0),
    accent_style=Styles.PrimaryFlat,
    accent_position="top_bar",
    metric_layout="top_stack",
    spacing=3.0,
)
kpis.add("55 Languages", "Tier A(20) · B(20) · C(15)")
kpis.add("356 Rules", "182 Actions · 112 Workflows")
kpis.add("Workflow v2", "DAG, Plan Gate & Rollup")
kpis.add("7 Quality Axes", "Score, Delta, FP & A4 PDF")
kpis.draw(xy=(3.0, 3.0), width=150.0, height=18.0, columns=4)
save()
```

## 1. エグゼクティブ概要：決定論的解析 × AI 推論のハイブリッドエンジン

単発プロンプトによる LLM コードレビューには、非決定論的なカウント誤差、実在しないファイルパスの捏造、チェック項目の抜け漏れ、根拠不明な誤検知スキップ、そしてコンテナ実行時の挙動・依存パッケージの既知 CVE・稼働 HTTP エンドポイントの脆弱性を一切検証できないという構造的限界があります。一方で、従来の静的リンターだけでは、ドメイン境界の凝集度や3視点のシステムアーキテクチャ、段階的モダナイゼーションのトレードオフを評価することはできません。

`pni501` (`v0.2.0`) は、3 つのティアに体系化された **55 言語**—**Tier A フル監査 (20)**・**Tier B 宣言的静的監査 (20)**・**Tier C コンパニオン IaC/スキーマ/ビルド/設定 (15)**—にわたり、**356 個の組み込みルールファイル**、**182 個のアクションテンプレート**、**112 個のワークフローテンプレート** を単一パイプラインに統合することで両者の強みを融合します：

- **ネイティブ Tree-sitter CST エンジンとオンデマンド ABI3 文法キャッシュ**：`ast-grep-py` を廃止し、**57 個の文法**を統一的に扱う単一パス `tree-sitter` CST エンジンを採用しました。**52 個の公式 PyPI `tree-sitter-*` wheel** に加え、MIT ライセンスの **5 文法**（`COBOL`、`R`、`Vue`、`Protocol Buffers`、`Dockerfile`）を GitHub Releases から SHA-256 検証付きで遅延キャッシュ（`pni grammars status` / `prefetch` / `clear`）することで、`pni501` 本体を軽量な pure-Python (`py3-none-any`) パッケージのまま維持します。
- **プログラムによるマルチモーダルな客観ファクト並列抽出**：DAG 並列コレクタが `project_inspect`、55 言語対応 `ast_analyze`、隔離 Docker コンテナでの `run_check`（オフライン単体テスト・カバレッジ計測・HTTP 起動確認）、ソケット非公開 Trivy による `security_scan`（CVE・IaC 設定不備・秘密情報漏洩）、ループバックコンテナに対する `pytest` + `httpx` の動的 `web_pentest`、トポロジカル依存グラフ解析 `migration_analyze`、および Git 進捗解析 `progress_analyze` を自動実行し、正確なテレメトリを `.pni/cache/<workflow_id>/facts.json` と `.pni/cache/workflow_state.db` に永続化します。
- **Workflow v2 DAG・Executed Audit DAG・エビデンス Δ・自己完結型ビジュアルレポート**：`pni workflows plan <id>` で Phase 0 偵察と検証済み Mermaid DAG を事前確認し、`confirm_plan` で合意形成（または `--auto-approve --pull` で自動承認）した上で、`finding_adjustments` による透明な誤検知（FP）トリアージを経て、Executed Audit DAG と 7 軸エビデンス Δ を備えた `pni_report/<target>_score.json`（`schema_version="2.0"`）、`*_summary.json`、`*_findings.sarif`（SARIF 2.1.0）を出力します。さらに `based_on` によるマイグレーション連鎖や `category: rollup` によるマルチ言語モノレポ統合評価を行い、`_facts/` を自動同期したフラット構成の **Drawlib ビジュアルレポート**（`pni_report_src/` -> `pni_report/<target>.pdf` および HTML）をコンパイルします。

```drawlib align=center code=fold file=pni_end_to_end_pipeline.png caption="Workflow v2 エンドツーエンド実行パイプライン：Phase 0 計画と55言語ファクト抽出から7軸スコア+Δ・フラット Drawlib A4 PDF 生成まで"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import CardList, ChevronProcess
from drawlib.styles import Styles

setup(width=156, height=70, dpi=150)

pipeline = ChevronProcess(
    style=Styles.PrimaryNeutral,
    text_style=Styles.DarkBold.patch(text_size=10.2),
    description_style=Styles.Dark.patch(text_size=9.8),
    corner_angle=65.0,
    spacing=1.5,
    flat_left_end=True,
)
pipeline.add(
    "1. Plan & Gate\n(Phase 0-1)",
    description="workflows plan\n& confirm_plan",
)
pipeline.add(
    "2. Parallel Facts\n(55 Langs)",
    description="57 CSTs + Docker\n+ Trivy + Pentest",
    style=Styles.Neutral,
)
pipeline.add(
    "3. Grounded AI\n& FP Triage",
    description="3-Aspect Arch +\nFP Adjustments",
    style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=10.2),
    description_style=Styles.White.patch(text_size=9.8),
)
pipeline.add(
    "4. 7-Axis Score\n& Rollup/Plan",
    description="Score + Delta,\nSARIF & based_on",
    style=Styles.SecondaryNeutral,
)
pipeline.add(
    "5. Flat Drawlib\nA4 PDF",
    description="pni_report_src ->\npni_report/*.pdf",
    style=Styles.SuccessFlat,
    text_style=Styles.WhiteBold.patch(text_size=10.2),
    description_style=Styles.White.patch(text_size=9.8),
)
pipeline.draw(xy=(3.0, 43.0), width=150.0, height=23.0)

artifacts = CardList(
    style=Styles.Neutral.patch(shape_r=1.6),
    text_style=Styles.DarkBold.patch(text_size=10.4),
    description_style=Styles.Dark.patch(text_size=9.8),
    badge_shape="circle",
    badge_style=Styles.PrimaryFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=10.0),
    icon_style=Styles.WhiteBold,
    direction="horizontal",
    show_arrows=True,
    arrow_style=Styles.DarkBold,
    spacing=3.0,
)
artifacts.add(
    "plan & facts.json",
    ".pni/cache/<wf>/ + _facts/\nCST, Docker, Trivy & pentest",
    icon=phosphor.file_magnifying_glass,
)
artifacts.add(
    "workflow_state.db",
    "Workflow v2 DAG (needs/when)\n& path-verified arch JSON",
    icon=phosphor.database,
)
artifacts.add(
    "Score, SARIF & Plan",
    "pni_report/*_score.json,\n*.sarif & *_migration_plan",
    icon=phosphor.medal,
)
artifacts.add(
    "Flat PDF & HTML",
    "pni_report_src -> pni_report\nVector A4 PDF & HTML",
    badge_style=Styles.SuccessFlat,
    icon=phosphor.file_pdf,
)
artifacts.draw(xy=(3.0, 4.0), width=150.0, height=34.0)
save()
```

## 2. 主要機能サマリー

| 機能領域 | 組み込みアセット (`v0.2.0`) | 主な成果物・品質保証 |
| :--- | :--- | :--- |
| **対応プログラミング言語** | **55 言語**（**57 ネイティブ `tree-sitter` CST**）：**Tier A (20)** フル監査・**Tier B (20)** 宣言的静的監査・**Tier C (15)** IaC/スキーマ/設定 | pure-Python (`py3-none-any`) 維持；52 PyPI `abi3` wheel + 5 遅延キャッシュ MIT 文法（`pni grammars`） |
| **カスケード設計規約ルール** | **356 個の組み込みルールファイル**（`common/` + 55 言語スコープ）+ `.pni/rules/` 上書き | OWASP ASVS, OpenSSF Scorecard, 12-Factor, SRE PRR, CLI・ライブラリ規約を適用 |
| **コンポジットアクション** | **182 個のアクションテンプレート**（**16 個の正規 `PrimitiveType`** に展開） | 並列自動実行アナライザと Pydantic スキーマ検証付き AI 推論を統合 |
| **Workflow v2 DAG エンジン** | **112 個のワークフローテンプレート**（`audit`, `rollup`, `migration`, `progress`）+ `needs:` / `when:` | `pni workflows plan`、`confirm_plan`、`pni validate-mermaid`、単一コマンド `--pull` / `--next` / `-o` |
| **7軸品質スコアと誤検知トリアージ** | `architecture`, `code_quality`, `typing`, `testing`, `dependencies`, `security`, `documentation` | Executed Audit DAG、ベースライン対調整後 **エビデンス Δ**、根拠付き **`finding_adjustments`**、SARIF 2.1.0 |
| **フラット Drawlib レポート** | 自己完結型 `pni_report_src/`（`_facts/` 自動同期）-> `pni_report/`（ポータル時は `docs_src/reports/<slug>`） | `pni report build` による 7 章 監査・移行 PDF、6 章 ロールアップ PDF、5 章 進捗 PDF および HTML |

### ティア別 対応 55 言語一覧

- **Tier A — フル監査（20 言語）**: `Python`, `Java`, `PHP`, `Go`, `TypeScript`, `JavaScript`, `C#`, `Rust`, `Ruby`, `Kotlin`, `Swift`, `C`, `C++`, `Scala`, `Dart`, `Elixir`, `Vue`, `Perl`, `COBOL`, `R`。
- **Tier B — 宣言的静的監査（20 言語）**: `Bash/Shell`, `PowerShell`, `Groovy`, `Objective-C`, `Lua`, `Haskell`, `F#`, `OCaml`, `Zig`, `Julia`, `Fortran`, `MATLAB`, `Svelte`, `Solidity`, `CUDA`, `Verilog/SystemVerilog`, `VHDL`, `Ada`, `Odin`, `Common Lisp`。
- **Tier C — コンパニオン IaC・スキーマ・ビルド・設定（15 言語）**: `Dockerfile`, `HCL/Terraform`, `Bicep`, `Nix`, `Makefile`, `Starlark/Bazel`, `Protocol Buffers`, `SQL`, `HTML`, `CSS`, `SCSS`, `YAML`, `JSON`, `TOML`, `XML`。

## 3. クイックインストールと初回 Workflow v2 監査

`pip` または `uv` で `pni501` をインストールし、`.pni/` を初期化して Phase 0 偵察プラン・Mermaid DAG を確認した上で、単一コマンドの Workflow v2 ループを開始します：

```bash
# PyPI から pni501 をインストール（pure-Python wheel；52 PyPI 文法同梱 + 5 MIT 文法を遅延取得）
pip install pni501
# または uv を使用:
uv add pni501

# .pni/ 設定・ルール・アクション・ワークフローを初期化
pni init
pni grammars status
pni workflows list

# Phase 0 偵察と検証済み Mermaid DAG を確認し、開始と同時に act-01 を取得
pni workflows plan full_audit
pni workflows start full_audit --auto-approve --pull
```

## 4. ドキュメントロードマップ

セクション別に `pni501` の全ドキュメントを参照できます：

### 4.1 はじめに (Getting Started)
- [背景とコアコンセプト](01_getting_started/concepts.md) — なぜ単発の AI プロンプト監査が実務リポジトリで破綻するのか、そして PNI の4つの柱がいかに 55 言語でハルシネーションゼロの診断を保証するかを解説します。
- [クイックスタートガイド](01_getting_started/quickstart.md) — インストール、`pni grammars`、`.pni/` 初期化、`pni workflows plan` / `confirm_plan`、単一コマンド `--pull` / `--next` 実行、およびフラットな `pni_report_src -> pni_report` ビルド手順を説明します。
- [3つの主要ユースケース](01_getting_started/use_cases.md) — スプリント開発での継続的品質測定、ブラックボックス・レガシー資産＆モノレポ `rollup` 検査、`based_on` 連鎖によるマイグレーション計画を解説します。
- [リリースノート](01_getting_started/release_notes.md) — バージョン履歴 (`v0.1.0`〜`v0.2.0`)、55 言語 Tree-sitter CST 拡張、Workflow v2 DAG エンジン、フラットレポート構成の変更点をまとめています。

### 4.2 アーキテクチャ・ワークフロー・スコアリング・リファレンス
- [ドメイン構造と3層カスケード](02_architecture/domain_architecture.md) および [ステートフル Pull-Push エンジン](02_architecture/stateful_engine.md) — 内部パッケージ設計、3 層カスケード、SQLite Workflow v2 DAG 状態遷移の仕組み。
- [ワークフローと Pre-Flight ゲート](03_workflows_and_actions/workflows_guide.md)、[182 アクションと 16 プリミティブ](03_workflows_and_actions/actions_pipeline.md)、[決定論的解析器とペネトレーションテスト](03_workflows_and_actions/analyzers_and_pentest.md) — 条件付き DAG（`needs:` / `when:`）、モノレポ `rollup`、決定論的アナライザの詳細。
- [7軸品質スコアリングモデル](04_scoring_and_reports/scoring_model.md)、[Drawlib ビジュアルレポーター](04_scoring_and_reports/drawlib_reporter.md)、および [サンプルレポートギャラリー](04_scoring_and_reports/sample_reports.md) — Executed Audit DAG、エビデンス Δ、`finding_adjustments`、フラット `pni_report_src/_facts` ブループリント、および日英バイリンガル HTML/PDF 実測サンプル集。
- [対応55言語マトリクス](05_languages_and_reference/supported_languages.md) および [ルール拡張と CLI リファレンス](05_languages_and_reference/rules_and_cli.md) — 3 ティア 55 言語 CST 仕様、オンデマンド `pni grammars` キャッシュ、全 CLI コマンドリファレンス。
