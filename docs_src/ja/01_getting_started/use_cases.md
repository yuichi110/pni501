# 3つの主要ユースケース

`pni501` (`v0.1.3`) は、**Python**、**Java**、**PHP**、**Go**、**TypeScript**、**JavaScript** の6言語にわたり、ソフトウェア開発ライフサイクル全体をカバーする3つの主要シナリオを提供します：(1) スプリント開発中の **継続的な品質・進捗モニタリング**、(2) 引き継ぎ案件やドキュメント不在システムの **ブラックボックス・レガシー資産＆セキュリティ監査**、そして (3) 完了済み監査を継承（`based_on`）する **段階的マイグレーション実行計画の作成** です。

```drawlib align=center code=fold file=pni_use_cases_overview.png caption="スプリント進行に伴う品質スコア推移と pni501 の3つの主要エンジニアリングシナリオ"
from drawlib.canvas import save, setup
from drawlib.charts.line import LineChart
from drawlib.icons import phosphor
from drawlib.smartarts import CardList, Panel
from drawlib.styles import Colors, Styles

setup(width=158, height=74, dpi=150)

chart = LineChart(
    categories=["Sprint 1", "Sprint 2", "Sprint 3", "Sprint 4", "Sprint 5"],
    title="Quality Score Trajectory Across Sprints",
    title_style=Styles.DarkBold.patch(text_size=12.0),
    axis_line_style=Styles.Muted,
    axis_text_style=Styles.DarkBold.patch(text_size=10.0),
    grid_style=Styles.MutedThin,
    value_text_style=Styles.DarkBold.patch(text_size=10.0),
    background_style=Styles.Neutral.patch(shape_fill_color=Colors.White, shape_r=2.0),
)
chart.configure_y_axis(min_value=0, max_value=100, tick_step=20)
chart.add_series(
    "With PNI501 Audit",
    [72, 80, 86, 91, 94],
    style=Styles.PrimaryBold,
    line_width=2.8,
    point_size=1.0,
)
chart.add_series(
    "Without Audit (Debt)",
    [72, 62, 49, 36, 24],
    style=Styles.DangerDashedBold,
    line_width=2.4,
    line_style="dashed",
    point_shape="square",
    point_size=0.95,
)
chart.draw(xy=(3.0, 14.0), width=74.0, height=56.0)
chart.draw_legend(
    xy=(6.0, 5.0),
    text_style=Styles.DarkBold.patch(text_size=10.0),
    orientation="horizontal",
    item_gap=4.5,
)

right_panel = Panel(
    "Three Core Engineering Scenarios",
    header_variant="filled",
    style=Styles.PrimaryNeutral.patch(shape_r=2.0),
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=12.0),
)
right_panel.draw(xy=(81.0, 4.0), width=74.0, height=66.0)

scenarios = CardList(
    style=Styles.Neutral.patch(shape_r=1.5),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Dark.patch(text_size=10.0),
    badge_shape="circle",
    badge_style=Styles.PrimaryFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=10.0),
    icon_style=Styles.WhiteBold,
    direction="vertical",
    spacing=2.5,
)
scenarios.add(
    "1. Continuous Sprint Quality",
    "quick_check, .pni/rules/ & progress\ntrajectory tracking across sprints",
    icon=phosphor.trend_up,
)
scenarios.add(
    "2. Black-Box Legacy Audit",
    "3-aspect arch recovery, Docker tests,\nTrivy CVEs & live Web pentesting",
    badge_style=Styles.SecondaryFlat,
    icon=phosphor.shield_check,
)
scenarios.add(
    "3. Phased Migration Plan",
    "based_on audit chain, SCC wave DAG,\nHyrum DEC-XX & PR WBS PDF",
    badge_style=Styles.SuccessFlat,
    icon=phosphor.git_branch,
)
scenarios.draw(xy=(83.5, 6.5), width=69.0, height=52.0)
save()
```

## 1. シナリオ 1：新規・継続開発ソフトウェアの定点品質測定と進捗ガバナンス

`pni501` のもともとの開発目的は、**継続開発中のソフトウェアにおいて技術的負債を溜め込まないための定点観測基盤** です。機能追加の速度が優先される通常のスプリント開発では、気づかないうちに循環依存・複雑度肥大・型やテストの欠落が進行し、後から大規模な手戻りが発生しがちです（上図左グラフの赤破線）。

対応する **6言語** の開発プロセスに `pni501` を組み込むことで、以下のメリットが得られます：

- **高速な定点ヘルスチェック (`quick_check`)**：`quick_check`（`repo_structure_audit` -> `<lang>_ast_audit` -> `emit_score`）をスプリントごとに実行し、フルレポート生成を待たずに構造劣化・型安全性の低下・複雑度スパイクを即座に検知します。
- **チーム設計規約の自動浸透 (`.pni/rules/`)**：`.pni/rules/` にプロジェクト固有のレイヤ境界やフレームワーク規約を定義しておくことで、すべての Code AI Agent が一貫した基準でコードをレビュー・採点します。
- **マイルストーン進捗と Git ガバナンス追跡 (`category: progress`)**：Git 追跡される `.pni/history/audit/<id>.jsonl` と `progress_assessment` / `write_progress_report` を組み合わせることで、マイルストーン達成状況、`git merge-tree` による非破壊ブランチ競合シミュレーション、および LOC・テスト・品質スコアの時系列推移を5章構成の PDF レポート（`reports/<target>_progress.pdf`）として出力できます。

```bash
# 高速なスプリントヘルスチェックの実行、またはプロジェクト進捗計画の初期化・検証
pni workflows start quick_check --supersede
pni progress init project_progress && pni progress validate project_progress
```

## 2. シナリオ 2：既存・レガシー資産（ブラックボックス）の多角品質・セキュリティ検査

他チームからの引き継ぎ案件、M&A・外部委託資産の受け入れ評価、あるいは本番強化を控えたレガシーモノリス（`Python`、`Java`、`PHP`、`Go`、`TypeScript`、`JavaScript`）では、設計書が失われているか実態と乖離しているケースが大半です。

`full_audit` は、4層のインスペクションを通じてハルシネーションゼロの多角診断を実行します：

1. **仕様書不要の3視点アーキテクチャ復元 (`architecture_analysis`)**：`purpose_and_stack`（目的・技術構成）、`layers_and_modules`（レイヤ・責務境界）、`flows_and_state`（データフロー・状態管理）の3視点で現行設計を記録し、全参照パスを `module_inventory` と突合して `.pni/cache/<wf>/architecture.json` に保存します。
2. **ポリグロット AST・保守性テレメトリ (`<lang>_ast_audit`)**：循環的複雑度、モジュールの Fan-in / Fan-out、強連結成分（SCC）の循環依存、API ルート一覧、危険なコードシンクを定量化します。
3. **隔離コンテナ動作検証とサプライチェーンセキュリティ (`container_runtime_audit`, `security_vulnerability_audit`)**：隔離 Docker コンテナ内でビルド・オフライン単体テスト・HTTP 起動が成功するかを検証しつつ、ソケット非公開の `Trivy` で依存パッケージ CVE・Dockerfile 設定ミス・秘密情報漏洩をスキャンします。
4. **ループバック動的 Web ペネトレーションテスト (`web_penetration_audit`)**：ループバックコンテナ内でアプリを起動し、`.pni/pentests/<target>/` に定義された `pytest` + `httpx` セキュリティプローブ（`SQLi`、`XSS`、`SSRF`、`IDOR`、認証バイパス）を実行します。

最終成果物として、ホットスポット密度ランキングを含む **7軸定量スコア（`0–100` 点 / `S`〜`D` グレード）** と、経営層・開発現場の双方が即座に意思決定に使える **7章構成の A4 診断 PDF レポート**（`reports/<target>.pdf`、`P0`〜`P2` 改善計画付き）を出力します。

## 3. シナリオ 3：前提条件ゲート付きの段階的マイグレーション計画 (`based_on`)

レガシー資産の品質検査が完了した次のステップとして、同一言語内でのクリーン/ヘキサゴナルアーキテクチャ再構築や、Strangler Fig パターンによるフレームワーク・言語刷新の具体的な実行計画が必要になります。

```drawlib align=center code=fold file=pni_migration_scenario_flow.png caption="監査結果を継承する4段階マイグレーションパイプライン (based_on) と2つのモダナイゼーション類型"
from drawlib.canvas import save, setup
from drawlib.diagrams.architecture import ArchitectureDiagram, Node, PhosphorIcon
from drawlib.smartarts import CardList
from drawlib.styles import Colors, Styles

setup(width=162, height=72, dpi=150)

diag = ArchitectureDiagram(
    node_style=Styles.DarkBold,
    node_text_style=Styles.DarkBold.patch(text_size=10.2, text_line_spacing=1.3),
    edge_style=Styles.PrimaryBold,
    edge_text_style=Styles.Dark.patch(text_size=10.0),
    width=162,
    height=72,
)

stages = [
    (
        21.5,
        "1. Audit Inheritance\n(based_on: <audit_id>)",
        "Reuses As-Is arch, 7-axis\nscore & security facts",
        PhosphorIcon.DATABASE,
        Styles.PrimaryBold,
        Styles.DarkBold.patch(text_size=10.2),
        Styles.PrimaryNeutral.patch(shape_r=2.0),
    ),
    (
        61.2,
        "2. Topological DAG\n(migration_analyze)",
        "Wave 1-4 leaf-to-root order\n& SCC cycle break points",
        PhosphorIcon.GIT_BRANCH,
        Styles.DarkBold,
        Styles.DarkBold.patch(text_size=10.2),
        Styles.Neutral.patch(shape_r=2.0),
    ),
    (
        100.8,
        "3. Decision Log\n(Hyrum's Law DEC-XX)",
        "Pins legacy bug vs. contract\ndecisions with human",
        PhosphorIcon.SCALES,
        Styles.SecondaryBold,
        Styles.DarkBold.patch(text_size=10.2),
        Styles.SecondaryNeutral.patch(shape_r=2.0),
    ),
    (
        140.5,
        "4. Plan JSON & PDF\n(Phase 0-4 / PR WBS)",
        "Safety-gated PR breakdown\n& 7-chapter A4 PDF plan",
        PhosphorIcon.FILE_PDF,
        Styles.WhiteBold,
        Styles.WhiteBold.patch(text_size=10.2),
        Styles.PrimaryFlat.patch(shape_r=2.0),
    ),
]

stage_nodes = []
for cx, title_txt, desc_txt, icon_enum, icon_st, txt_st, card_st in stages:
    s_node = diag.add(
        Node(
            text=title_txt,
            width=35.0,
            height=21.0,
            icon=icon_enum,
            icon_size=5.0,
            style=icon_st,
            text_style=txt_st,
            card_style=card_st,
        ),
        xy=(cx, 57.5),
    )
    diag.add(
        Node(
            text=desc_txt,
            width=35.0,
            height=11.5,
            text_style=Styles.Dark.patch(text_size=10.0),
            card_style=Styles.Neutral.patch(shape_fill_color=Colors.White, shape_r=1.6),
        ),
        xy=(cx, 39.0),
    )
    stage_nodes.append(s_node)

for idx in range(len(stage_nodes) - 1):
    diag.connect(stage_nodes[idx], stage_nodes[idx + 1], padding=0.5)

diag.draw(xy=(0, 0))

archetypes = CardList(
    style=Styles.Neutral.patch(shape_r=1.6),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Dark.patch(text_size=10.0),
    badge_shape="circle",
    badge_style=Styles.PrimaryFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=10.5),
    direction="horizontal",
    spacing=3.5,
)
archetypes.add(
    "Archetype A: Same-Language Modernization",
    description="e.g. Legacy Spring / FastAPI / Go ->\nClean Hexagonal Architecture (phased_pr)",
    badge_text="A",
    style=Styles.Neutral,
)
archetypes.add(
    "Archetype B: Cross-Stack Strangler Fig",
    description="e.g. Procedural PHP -> Laravel 11 or\nJavaScript -> Strict TypeScript (strangler_fig)",
    badge_text="B",
    style=Styles.PrimaryNeutral,
    badge_style=Styles.SecondaryFlat,
)
archetypes.draw(xy=(4.0, 3.5), width=154.0, height=25.0)
save()
```

コードベースを一から再調査するのではなく、`pni501` のマイグレーションワークフロー（`category: migration`）は `based_on: <audit_workflow_id>` を宣言します：

- **Fail-Closed な監査ファクト継承 (`based_on`)**：`pni workflows start <migration_id>` は、`.pni/cache/workflow_state.db` 内に `<audit_workflow_id>` の `COMPLETED` ランが存在することを検証し、`targets`、`ProjectFacts`、`AstFacts`、`RuntimeFacts`、`SecurityFacts`、`ArchitectureRecord`、`ScoreResult` をそのまま自動継承します。
- **トポロジカル依存グラフ・Wave 解析 (`migration_analyze`)**：強連結成分（SCC）、外部境界タッチポイント（DB / HTTP / ファイルシステム / 環境変数）、およびボトムアップの `refactoring_waves`（`Wave 1`..`Wave N`）を決定論的に算出し、依存のないリーフモジュールから安全に移行を開始できるよう順序付けます。
- **Hyrum の法則に基づく仕様 vs. バグ判定ログ (`DEC-XX`)**：既存のバグや暗黙の挙動に外部クライアントが依存しているリスクに対処するため、Pre-Flight ヒアリングを通じて暗黙契約を維持するか Phase 3 で修正するかを人間と合意し、`DEC-XX` 判定ログとしてピン留めします（`bug_handling_policy: ask_human`）。
- **PR 単位の作業分解書 (WBS) と7章構成 PDF**：`Phase 0`（Characterization テストハーネス整備）から `Phase 4`（旧コード撤去）までの安全検証ゲート・ロールバック基準を備えた `reports/<target>_migration_plan.json` および `reports/<target>_migration.pdf` を出力します。

## 4. 3つのシナリオの比較マトリクス

| 比較観点 | シナリオ 1：継続的品質・進捗測定 | シナリオ 2：レガシー・セキュリティ監査 | シナリオ 3：マイグレーション計画 |
| :--- | :--- | :--- | :--- |
| **ワークフローカテゴリ** | `audit` (`quick_check`) / `progress` | `audit` (`full_audit`) | `migration` (`based_on: <audit_id>`) |
| **主なコンポジットアクション** | `repo_structure_audit`, `<lang>_ast_audit`, `emit_score`, `progress_assessment` | `container_runtime_audit`, `security_vulnerability_audit`, `web_penetration_audit` を含む全15監査アクション | `migration_proposal`, `write_migration_report` |
| **構造化 JSON 成果物** | `reports/<target>_score.json` / `*_progress.json` | `reports/<target>_score.json` + `.pni/cache/<wf>/architecture.json` | `reports/<target>_migration_plan.json` |
| **ビジュアル PDF 成果物** | 任意（または5章構成 `*_progress.pdf`） | 7章構成 健全性診断 PDF (`reports/<target>.pdf`) | 7章構成 移行実行計画 PDF (`reports/<target>_migration.pdf`) |

続いて [ドメイン構造と3層カスケード](../02_architecture/domain_architecture.md) に進み、`pni501` の内部アーキテクチャを詳しく確認してください。
