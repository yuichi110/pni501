# 4. 検査指標・ルール適合マトリクスと指摘一覧

本章では、`py_cli_audit_tool` ワークフローで実行した6つの監査ディメンションのスコア比較、評価対象となった全15エンジニアリングルールの適合判定（`FAIL -> WARN -> PASS`）、および重要度順に正規化された全12件の指摘事項（`HIGH -> MEDIUM -> LOW`）を一覧化する。

```drawlib file=audit_dimensions_barchart.png caption="実行監査ステップ別スコア比較 (弱点順: Weakest -> Strongest)"
from drawlib.canvas import save, setup
from drawlib.charts.bar import BarChart
from drawlib.styles import Styles

setup(width=146, height=62, dpi=150)

chart = BarChart(
    axis_line_style=Styles.Neutral,
    grid_style=Styles.NeutralThin,
    axis_text_style=Styles.DarkBold.patch(text_size=9.5),
    value_text_style=Styles.DarkBold.patch(text_size=9.5),
    background_style=Styles.Neutral.patch(shape_r=2.0),
    categories=[
        "テスト監査\n(62 / C)",
        "リポジトリ構造\n(68 / C)",
        "コンテナ実行\n(74 / B)",
        "CLI規約監査\n(76 / B)",
        "脆弱性・供給網\n(78 / B)",
        "Python AST\n(86 / A)",
    ],
    orientation="vertical",
    bar_width_ratio=0.56,
    bar_r=1.0,
    width=134,
    height=52,
    title="監査ステップ別 健全性スコア比較 (0 - 100点)",
    title_style=Styles.DarkBold.patch(text_size=11.0),
)
chart.add_series("監査ステップスコア", [62, 68, 74, 76, 78, 86], style=Styles.Primary)
chart.draw(xy=(6, 5))

save()
```

## ルール適合マトリクス（全15ルール：`FAIL: 2` / `WARN: 9` / `PASS: 4`）

全評価ルールは最悪ステータス優先で集約されており、`common/supply_chain`（`uv.lock` スタブおよび `SECURITY.md` / Dependabot / CI 不在）と `python/testing`（CLI・Formatter テスト欠落による網羅率基準未達）の2件が `FAIL` 判定となった。一方で、`common/architecture`・`common/maintainability`・`python/modern_stack`・`common/git_workflow` の4件は違反ゼロで `PASS` を達成している。

```drawlib file=rule_compliance_matrix.png caption="エンジニアリングルール適合マトリクス (FAIL -> WARN -> PASS 全15ルール)"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=118, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=9.5),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.5),
    border_style=Styles.NeutralThin,
)
rows = [
    ["判定", "ルールID", "評価ステップ", "決定的エビデンス要約"],
    ["FAIL", "common/supply_chain", "repo_structure_audit", "SECURITY.md・Dependabot・CI不在、uv.lock 推移ハッシュ欠落"],
    ["FAIL", "python/testing", "python_test_audit", "テスト2件のみ。cli.py / build_rich_table 未テスト(80%未満)"],
    ["WARN", "common/cli_guidelines", "cli_guidelines_audit", "--version/-h/stdin不在、@app.callback()不在で scan 縮退"],
    ["WARN", "common/documentation", "repo_structure_audit", "README に導入・テスト手順・--min-level/--fail-above 未記載"],
    ["WARN", "common/production_readiness", "container_runtime_audit", "cli.py:34 の read_text() 一括読込で OSError 時トレース露出"],
    ["WARN", "common/runtime_verification", "container_runtime_audit", "ビルド/テスト/Smoke合格も実測行 67.0%・分岐 33.3%"],
    ["WARN", "common/security", "python_ast_audit", "秘密情報0件。--min-level 境界検証不足と read_text() 例外未捕捉"],
    ["WARN", "common/security_vulnerability", "security_vulnerability_audit", "rich/typer CVE 0件・CWE 0件。同梱 pip@25.0.1 に MEDIUM 5件"],
    ["WARN", "python/code_quality", "python_ast_audit", "Docstring率 88.9%: formatter.py 公開関数2件で Docstring 欠落"],
    ["WARN", "python/dependencies", "repo_structure_audit", "PEP 621 準拠だが uv.lock が未解決スタブ、dev群に型検査器不在"],
    ["WARN", "python/typing", "python_ast_audit", "型付与率 100.0% だが report_to_dict が dict[str, Any]"],
    ["PASS", "common/architecture", "python_ast_audit", "循環依存 0件・境界違反 0件。cli -> 処理/表示層 -> models"],
    ["PASS", "common/git_workflow", "repo_structure_audit", ".gitignore 整備済み(__pycache__, .venv 等)、不要物混入なし"],
    ["PASS", "common/maintainability", "python_ast_audit", "全6ファイル 207 LOC(最大52 LOC)、複雑関数・大域状態 0件"],
    ["PASS", "python/modern_stack", "python_ast_audit", "import衛生 100.0%、pathlib・frozen dataclass・PEP 585 徹底"],
]
tbl.draw_flexible(
    xy=(3, 115),
    column_widths=[12, 34, 30, 64],
    row_heights=[7.2] + [7.0] * 15,
    data=rows,
)

save()
```

## 重要度順 指摘事項一覧（全12件：`CRITICAL: 0` / `HIGH: 2` / `MEDIUM: 6` / `LOW: 4`）

各指摘事項は実在するリポジトリパス・行番号・決定的ファクトに紐付けられている。特に `src/logpulse/cli.py`（4件）と `src/logpulse/formatter.py`（3件）、および供給網設定ファイル群（`uv.lock` / `pyproject.toml` / `LICENSE` / `README.md`）に修正対象が集約されているため、少ない変更範囲で全件を解消可能である。

```drawlib file=findings_evidence_table.png caption="重要度順 検出指摘一覧 (HIGH -> MEDIUM -> LOW 全12件)"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=130, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=9.5),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.5),
    border_style=Styles.NeutralThin,
)
rows = [
    ["重要度", "ルールID", "該当箇所", "検出事象・根拠", "推奨修正策"],
    ["HIGH", "common/supply_chain", "uv.lock:4", "rootのみ記載のスタブで\n推移版・SHA256欠落", "uv lock で完全生成し\nuv sync --locked 化"],
    ["HIGH", "python/testing", "src/logpulse/\ncli.py:18", "CliRunner テスト 0件で\n終了コード未検証", "tests/test_cli.py を追加し\nExit 0/1/2 を検証"],
    ["MEDIUM", "common/cli_guidelines", "src/logpulse/\ncli.py:15", "@app.callback()不在で\nscan 縮退・--version欠落", "@app.callback() で\n--version / -h を実装"],
    ["MEDIUM", "common/security", "src/logpulse/\ncli.py:34", "read_text()一括読込・\nOSError未捕捉・level未検証", "open()逐次読込＋Exit 2捕捉\n＋Enum/Choice 引数化"],
    ["MEDIUM", "common/\nsecurity_vulnerability", "pyproject.toml:12", "同梱 pip@25.0.1 にCVE 6件\nDebian OS層に 398件", "pip>=26.2.0 更新または除外\n＋ベースOSパッチ適用"],
    ["MEDIUM", "common/supply_chain", ".", "SECURITY.md・Dependabot・\nCI定義が全て不在", "脆弱性開示方針・自動更新・\n最小権限CIを追加"],
    ["MEDIUM", "common/\nruntime_verification", "src/logpulse/\ncli.py:18", "実測行 67.0%・分岐 33.3%\n(cli 0% / fmt 55.6%)", "cli.py 全26文と formatter\n43-50行をテスト追加"],
    ["MEDIUM", "python/testing", "src/logpulse/\nformatter.py:34", "build_rich_table と\n非dict行のテスト欠落", "test_formatter.py と\n境界値テストを追加"],
    ["LOW", "common/supply_chain", "LICENSE:1", "MIT 見出し2行のみで\n許諾・免責全文が欠落", "SPDX 標準の MIT\nライセンス全文を記載"],
    ["LOW", "common/documentation", "README.md:11", "導入・テスト手順・一部\nCLIフラグが未記載", "Standard Readme 構成と\n全フラグ表を追記"],
    ["LOW", "python/code_quality", "src/logpulse/\nformatter.py:13", "report_to_dict 等の\n公開 Docstring 欠落", "Google形式の Args/Returns\nDocstring を追加"],
    ["LOW", "python/typing", "src/logpulse/\nformatter.py:13", "dict[str, Any] 返却・\npy.typed と型検査器不在", "TypedDict 定義・py.typed・\nty 型検査器を導入"],
]
tbl.draw_flexible(
    xy=(3, 127),
    column_widths=[14, 30, 24, 36, 36],
    row_heights=[7.5] + [9.6] * 12,
    data=rows,
)

save()
```
