# 背景とコアコンセプト

`Python`、`Java`、`Go`、`TypeScript`、`Rust`、`C#`、`COBOL` から宣言的スクリプト（`Bash`、`Solidity`、`Zig`）やコンパニオン IaC/スキーマ資産（`Dockerfile`、`Terraform/HCL`、`Protobuf`、`SQL`）に至る **55 言語** の既存ソフトウェアをモダナイズし継続的に品質維持することは、エンジニアリング組織にとって最も投資対効果が高く、かつリスクの大きい課題です。`pni501` (`v0.2.0`) は、場当たり的な単発 AI プロンプトを、356 個のカスケード設計規約・57 個のネイティブ `tree-sitter` CST 文法・隔離コンテナ解析・SQLite **Workflow v2 DAG** 状態管理・フラットで自己完結型の Drawlib ビジュアルレポートを統合した決定論的ハーネスへと置き換えます。

```drawlib align=center code=fold file=pni_why_comparison.png caption="AI モダナイゼーションのギャップ：単発 AI プロンプト監査 vs. PNI501 (v0.2.0) 55言語の決定論ファクト × AI 推論"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.lines import line
from drawlib.smartarts import CardList, Panel
from drawlib.styles import Styles
from drawlib.text import text

setup(width=156, height=74, dpi=150)

left_panel = Panel(
    "Ad-Hoc AI Prompting (Without PNI)",
    header_variant="filled",
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.DangerFlat,
    text_style=Styles.WhiteBold.patch(text_size=12.0),
)
left_panel.draw(xy=(3.0, 3.0), width=68.0, height=68.0)

left_cards = CardList(
    style=Styles.Neutral.patch(shape_r=1.5),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Dark.patch(text_size=10.0),
    badge_shape="circle",
    badge_style=Styles.DangerFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=10.0),
    icon_style=Styles.WhiteBold,
    direction="vertical",
    spacing=2.2,
)
left_cards.add(
    "Senior-Engineer Bottleneck",
    "Inconsistent standards across 55 langs",
    icon=phosphor.warning,
)
left_cards.add(
    "Metric & Path Hallucinations",
    "Guesses LOC, cycles & nonexistent files",
    icon=phosphor.question,
)
left_cards.add(
    "Runtime & Security Blind Spots",
    "Misses Docker tests, Trivy CVEs & pentests",
    icon=phosphor.shuffle,
)
left_cards.add(
    "Workflow Drift & Silent FPs",
    "Subjective scores & raw Markdown dumps",
    icon=phosphor.file_text,
)
left_cards.draw(xy=(5.5, 5.5), width=63.0, height=54.0)

line((72.5, 37.0), (83.5, 37.0), arrow_head="->", style=Styles.PrimaryBold.patch(line_width=2.5))
text((78.0, 41.5), "PNI501", style=Styles.PrimaryBold.patch(text_size=11.0))

right_panel = Panel(
    "PNI501 v0.2.0 Deterministic Facts x AI",
    header_variant="filled",
    style=Styles.PrimaryNeutral.patch(shape_r=2.0),
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=12.0),
)
right_panel.draw(xy=(85.0, 3.0), width=68.0, height=68.0)

right_cards = CardList(
    style=Styles.Neutral.patch(shape_r=1.5),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Dark.patch(text_size=10.0),
    badge_shape="circle",
    badge_style=Styles.PrimaryFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=10.0),
    icon_style=Styles.WhiteBold,
    direction="vertical",
    spacing=2.2,
)
right_cards.add(
    "356 Rules & 182 Actions",
    "55 langs (Tier A/B/C) & 112 workflows",
    icon=phosphor.book_bookmark,
)
right_cards.add(
    "57 Tree-sitter CSTs + Runtime",
    "Exact inventory, Docker, Trivy & pentest",
    icon=phosphor.cpu,
)
right_cards.add(
    "Workflow v2 DAG & Delta",
    "confirm_plan, FP triage & rollup chain",
    icon=phosphor.git_commit,
)
right_cards.add(
    "Flat Self-Contained PDF",
    "pni_report_src/_facts -> pni_report PDF",
    badge_style=Styles.SuccessFlat,
    icon=phosphor.chart_bar,
)
right_cards.draw(xy=(87.5, 5.5), width=63.0, height=54.0)
save()
```

## 1. なぜ単発の AI プロンプト監査は実務リポジトリで破綻するのか

エンタープライズのバックエンド、クラウドマイクロサービス、GPU/HPC カーネル、組み込み・HDL モジュール、メインフレーム資産、フロントエンド Web アプリケーション、そしてポリグロットなモノレポに至るまで、開発組織は数十のプログラミング言語と IaC・スキーマ・ビルド定義を横断して運用しています。こうしたコードベースを安全に保守・リファクタリング・移行するには、構造的健全性・ランタイム動作・セキュリティ態勢に関する客観的かつ再現可能なベースラインが不可欠です。

Code AI Agent（`Claude Code`、`Gemini CLI`、`Cursor`、`GitHub Copilot` など）はコード読解と変換を劇的に加速させましたが、チャット画面で単発プロンプトとして「このリポジトリを監査して品質を採点して」と依頼する従来のアプローチには、実務運用を阻む **4つの構造的限界** があります：

1. **シニアエンジニアの属人化とプロンプトのボトルネック**：共通アーキテクチャ原則（OWASP ASVS、OpenSSF サプライチェーン衛生、Twelve-Factor App、Google SRE PRR、CLI 設計標準）と、**55 言語** にわたる言語・フレームワーク固有のベストプラクティス（`FastAPI`、`Spring Boot`、`Laravel`、`Go`、`Rust`、`C#`、`COBOL`、`Terraform`、`Dockerfile` 等）を漏れなくプロンプトで指示するには、毎回スタッフエンジニア級の高度な専門知識が必要になります。
2. **定量メトリクスと構造パスのハルシネーション**：チャット上でリポジトリを直接読ませると、LLM はコード行数（LOC）や型注釈・ジェネリクスの付与率を推測で創作したり、強連結成分（SCC）の循環依存を見落としたり、ワークスペースに実在しないファイルパスや行番号を根拠に指摘を生成してしまいます。
3. **ランタイム動作・脆弱性・ペネトレーションテストの死角**：静的テキストの読解だけでは、クリーンなコンテナ内でユニットテストが実際に通るか、行/分岐カバレッジが何%か、`Trivy` が既知の重大 CVE・IaC 設定ミス・ハードコードされた秘密情報を検出するか、あるいは稼働中の HTTP エンドポイントが認証バイパスや SQLi / XSS / SSRF 攻撃プローブに耐えられるかを一切検証できません。
4. **主観スコアのブレ・不透明な誤検知スキップ・長文テキストの認知負荷**：長いチャットセッションでは実行ごとに評価基準が揺らぎ、誤検知アラートを監査証跡なしで黙殺したり、実行計画の事前合意なしに重い処理へ突入し、実際の依存グラフを無視した危険な「ビッグバン書き換え」や数千行の生 Markdown を出力してレビュアーを疲弊させます。

## 2. PNI501 のアプローチ：決定論的 AI 監査と移行を支える4つの柱

**Project Nemesis Index (`pni501` `v0.2.0`)** は、制御の主導権を逆転させることでこれらの課題を解決します。LLM に監査手順を即興で考えさせるのではなく、**決定論的な `pni` CLI と SQLite Workflow v2 DAG エンジン** がプロセス全体を主導し、AI エージェントには「検証済みファクトに基づく推論」「根拠付きの誤検知トリアージ」「ビジュアルレポート執筆」のみを委譲します。

```drawlib align=center code=fold file=pni_four_step_architecture.png caption="PNI501 (v0.2.0) の4ステップ・アーキテクチャ：55言語 CST 解析器・Workflow v2 DAG 推論・連鎖移行計画・フラットレポートの統合"
from drawlib.canvas import save, setup
from drawlib.diagrams.architecture import (
    ArchitectureDiagram,
    Node,
    NodeGroup,
    PhosphorIcon,
)
from drawlib.styles import Colors, Styles
from drawlib.text import text

setup(width=158, height=66, dpi=150)

text(
    (4.5, 61.0),
    "How PNI501 v0.2.0 Unites 55-Lang Analyzers, Workflow v2 DAG, Plans & Flat Reports",
    style=Styles.DarkBold.patch(text_size=12.0, halign="left"),
)

white_card = Styles.Neutral.patch(shape_fill_color=Colors.White, shape_r=1.6)

diagram = ArchitectureDiagram(
    node_style=Styles.PrimaryBold,
    node_text_style=Styles.DarkBold.patch(text_size=10.0),
    node_card_style=white_card,
    edge_style=Styles.PrimaryBold,
    edge_text_style=Styles.Dark.patch(text_size=10.0),
)

prep_group = diagram.add(
    NodeGroup(
        title="1. Rules & Objective Facts",
        padding=2.6,
        style=Styles.Neutral.patch(shape_r=2.0),
        text_style=Styles.PrimaryBold.patch(text_size=10.2, halign="left"),
    ),
    xy=(4.5, 4.0),
)
n_rules = prep_group.add(
    Node(
        "356 Rules & 182 Actions\n(55 Langs, 112 WFs)",
        width=31.0,
        height=17.5,
        icon=PhosphorIcon.BOOK_OPEN_TEXT,
        icon_size=5.2,
        card_style=Styles.PrimaryNeutral.patch(shape_r=1.5),
    ),
    xy=(18.0, 35.5),
)
n_ast = prep_group.add(
    Node(
        "57 Tree-sitter CSTs,\nDocker, Trivy & Pentest",
        width=31.0,
        height=17.5,
        icon=PhosphorIcon.CPU,
        icon_size=5.2,
        style=Styles.SecondaryBold,
        card_style=Styles.SecondaryNeutral.patch(shape_r=1.5),
    ),
    xy=(18.0, 14.0),
)

n_agent = diagram.add(
    Node(
        "2. Workflow v2 DAG\n& Grounded AI Audit\n(Plan + FP Triage)",
        width=27.0,
        height=27.0,
        icon=PhosphorIcon.ROBOT,
        icon_size=5.8,
        style=Styles.WhiteBold,
        text_style=Styles.WhiteBold.patch(text_size=10.0),
        card_style=Styles.PrimaryFlat.patch(shape_r=2.0),
    ),
    xy=(65.5, 31.0),
)

n_score_plan = diagram.add(
    Node(
        "3. Score + Delta,\nRollup & Migration\n(based_on Chain)",
        width=27.0,
        height=27.0,
        icon=PhosphorIcon.GIT_BRANCH,
        icon_size=5.8,
        style=Styles.SecondaryBold,
        card_style=Styles.SecondaryNeutral.patch(shape_r=2.0),
    ),
    xy=(102.5, 31.0),
)

n_report = diagram.add(
    Node(
        "4. Flat Drawlib\nReport & Decision\n(pni_report PDF)",
        width=27.0,
        height=27.0,
        icon=PhosphorIcon.CHART_POLAR,
        icon_size=5.8,
        style=Styles.SuccessBold,
        card_style=Styles.SuccessNeutral.patch(shape_r=2.0),
    ),
    xy=(139.5, 31.0),
)

diagram.connect(prep_group, n_agent, arrow="->", routing="direct")
diagram.connect(n_agent, n_score_plan, arrow="->", routing="direct")
diagram.connect(n_score_plan, n_report, arrow="->", routing="direct")

diagram.draw(xy=(0.0, 0.0))
save()
```

### 2.1 第1の柱：55言語カスケード規約ルールとアクションテンプレート (`_rules` & `_actions`)
単発プロンプトに頼る代わりに、`pni501` は `common/` および **55 言語スコープ**—**Tier A フル監査 (20)**・**Tier B 宣言的静的監査 (20)**・**Tier C コンパニオン IaC/スキーマ/ビルド/設定 (15)**—にわたる **356 個の組み込みルールファイル**、**182 個のアクションテンプレート**、および **112 個のワークフローテンプレート** を内蔵しています。すべてのルール・アクション・ワークフローは `.pni/` ディレクトリによる非破壊の3層カスケード上書き（`local > <lang> > common`）に対応しており、組織やチーム固有の設計標準を Git でバージョン管理できます。詳細は [ドメイン構造と3層カスケード](../02_architecture/domain_architecture.md) および [対応55言語マトリクス](../05_languages_and_reference/supported_languages.md) を参照してください。

### 2.2 第2の柱：ネイティブ Tree-sitter CST・コンテナ・脆弱性・Pentest 解析器
数えられる指標、実行可能なテスト、構造的に証明可能な依存関係はすべてプログラムで計測され、`.pni/cache/<workflow_id>/facts.json` にキャッシュされます：
- **57 文法ネイティブ `tree-sitter` CST とマニフェスト検査 (`project_inspect`, `ast_analyze`)**：`ast-grep-py` を廃止し、**52 個の公式 PyPI `tree-sitter-*` `abi3` wheel** と、GitHub Releases から SHA-256 検証付きで遅延キャッシュされる **5 個の MIT 文法**（`COBOL`、`R`、`Vue`、`Protocol Buffers`、`Dockerfile`、`pni grammars status` / `prefetch` / `clear`）を統合した単一パス CST エンジンにより、`pni501` を pure-Python (`py3-none-any`) のまま維持しつつ、Tier A/B/C 全般の `module_inventory`、LOC、型/ジェネリクス付与率、循環的複雑度、API エンドポイント、危険なセキュリティシンク、循環インポートグラフを抽出します。
- **隔離コンテナ検証・脆弱性スキャン・動的 Web Pentest (`run_check`, `security_scan`, `web_pentest`)**：隔離コンテナ内でユニットテスト・カバレッジ収集・HTTP 起動確認を実行し、4 段階スコープ分類付きのソケット非公開 `Trivy` スキャン（`vuln,misconfig,secret`）と、ループバックコンテナに対する `pytest` + `httpx` ペネトレーションテストを実行します。
- **トポロジカル移行 Wave 解析と進捗テレメトリ (`migration_analyze`, `progress_analyze`)**：強連結成分（SCC）の循環依存、外部境界タッチポイント、ボトムアップの `refactoring_waves`、および Git マイルストーン・`git merge-tree` 競合シミュレーションを算出します。詳細は [決定論的解析器とペネトレーションテスト](../03_workflows_and_actions/analyzers_and_pentest.md) を参照してください。

### 2.3 第3の柱：Workflow v2 条件付き DAG エンジン・エビデンス Δ・FP トリアージ (`_workflows`)
`pni workflows` は、`needs:` 依存関係と決定論的 `when:` ガードを備えた SQLite **Workflow v2 DAG** ステートマシン（`.pni/cache/workflow_state.db`）上で、並列ファクト収集と AI 推論を誘導します：
- **Plan-First 人間合意ゲート (`pni workflows plan` & `confirm_plan`)**：重いステージを実行する前に、Phase 0 偵察が対象ディレクトリ・コンテナ基盤・モノレポコンポーネントを自動検出し、Python で構文検証済みの Mermaid Execution DAG（`pni validate-mermaid` でも検証可能）を提示します。ユーザー合意を `confirm_plan` で確定する（CI では `--auto-approve`）ことで手戻りを防ぎます。
- **3視点アーキテクチャ記録と根拠付き誤検知トリアージ (`record_architecture`, `ai_interpret`)**：採点前に `purpose_and_stack`、`layers_and_modules`、`flows_and_state` の3視点で構造を記録（`module_inventory` と実在パス照合し `.pni/cache/<workflow_id>/architecture.json` に保存）し、決定論的アラート（`det-*`）の誤検知は黙殺せず `finding_adjustments`（`waive` / `reclassify` + 明確な理由）として監査証跡に残します。
- **Executed Audit DAG・7軸エビデンス Δ・連鎖ワークフロー (`emit_score`, `based_on`, `rollup`)**：Executed Audit DAG と各軸のベースライン対調整後 **エビデンス Δ** を記録した `pni_report/<target>_score.json`（`schema_version="2.0"`）、`*_summary.json`、`*_findings.sarif`（SARIF 2.1.0）を出力します。さらに `based_on` によるマイグレーション計画連鎖と、`category: rollup` によるマルチ言語モノレポ統合評価に対応します。詳細は [ステートフル Pull-Push エンジン](../02_architecture/stateful_engine.md) を参照してください。

### 2.4 第4の柱：フラットで自己完結型のビジュアル Drawlib レポート (`_reporter`)
長文テキストによるレビュー疲れと冗長なディレクトリ階層を解消するため、`_reporter` は **フラットな自己完結型レイアウト** を採用しています。`--src-dir`（デフォルト `pni_report_src`、統合ポータルでは `docs_src/reports/<slug>`）直下に `drawlib.toml`・`styles.py`・`utils.py`・各章 Markdown（`00_cover.md`〜`06_*.md`）と、検証済み JSON ファクト群（`plan.json`, `facts.json`, `architecture.json`, `score.json`）を自動同期する **`_facts/`** を高凝集に配置します。エグゼクティブ向け `KpiCards`、7軸 `RadarChart`、エビデンス Δ 分析、2次元モジュール `HeatmapChart`、`P0`〜`P2` / Wave `Roadmap` を組み合わせ、`pni report build` によって `pni_report/` 配下に鮮明な A4 ベクター PDF（`pni_report/<target>.pdf`）および HTML をコンパイルします。詳細は [Drawlib ビジュアルレポーター](../04_scoring_and_reports/drawlib_reporter.md) を参照してください。
