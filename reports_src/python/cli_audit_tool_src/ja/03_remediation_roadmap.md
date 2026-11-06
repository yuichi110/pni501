# 3. 推奨する変更対応

監査で特定された12件の指摘事項を解消し、総合スコアを Grade B (`77`) から Grade A/S 水準（`88+`）へ引き上げるため、緊急度と投資対効果に基づき **P0（緊急基盤整備：2施策） -> P1（品質・統治強化：4施策） -> P2（完成度向上：3施策）** の計9施策を定義する。

```drawlib file=remediation_priority_roadmap.png caption="優先度フェーズ別 改善ロードマップ (P0 -> P1 -> P2)"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import Roadmap
from drawlib.styles import Styles

setup(width=146, height=58, dpi=150)

rm = Roadmap(
    style=Styles.Neutral,
    text_style=Styles.DarkBold.patch(text_size=10.2),
    description_style=Styles.Dark.patch(text_size=9.5),
    spine_style=Styles.PrimaryBold,
    badge_style=Styles.Danger,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.5),
    direction="horizontal",
    spacing=3.5,
)
rm.add(
    "P0 緊急基盤 (2件)",
    "uv lock 完全ハッシュ化\nCliRunnerテスト追加(90%超)",
    badge_text="P0",
    style=Styles.DangerNeutral,
    badge_style=Styles.Danger,
    icon=phosphor.lock_key,
    icon_style=Styles.Danger,
)
rm.add(
    "P1 品質・統治 (4件)",
    "@app.callback / ストリーム読込\nSECURITY・Dependabot・CI導入",
    badge_text="P1",
    style=Styles.WarningNeutral,
    badge_style=Styles.Warning,
    icon=phosphor.wrench,
    icon_style=Styles.Warning,
)
rm.add(
    "P2 完成度向上 (3件)",
    "README拡充・MIT全文記載\npip更新・TypedDict・ty導入",
    badge_text="P2",
    style=Styles.PrimaryNeutral,
    badge_style=Styles.Primary,
    icon=phosphor.rocket_launch,
    icon_style=Styles.Primary,
)
rm.draw(xy=(4, 5), width=138, height=48)

save()
```

## フェーズ別実行計画とトレーサビリティ

- **Phase 1 (`P0` — 即時対応)**: 現状12行のスタブに留まる `uv.lock` を `uv lock` で完全解決して静的 SCA の盲点を解消するとともに、`tests/test_cli.py`（`typer.testing.CliRunner`）および `tests/test_formatter.py` を新設し、現在 `0.0%` の `cli.py` カバレッジを一挙に引き上げる。
- **Phase 2 (`P1` — 短期優先対応)**: `src/logpulse/cli.py` に `@app.callback()` を設けて `README.md` 記載の `logpulse scan <file>` 構文と `--version` / `-h` を両立させ、`read_text().splitlines()` を逐次ストリーム読込＋`OSError`/`UnicodeDecodeError` 捕捉（Exit 2）へ置換する。併せて `SECURITY.md`・`.github/dependabot.yml`・最小権限 GitHub Actions CI を整備する。
- **Phase 3 (`P2` — 継続的品質向上)**: `README.md` と `LICENSE` の標準化、コンテナ配布時の `pip>=26.2.0` 更新・Debian パッチ適用、ならびに `formatter.py` の `TypedDict` 化・Docstring 追加・`ty` 型チェッカー導入を行う。

```drawlib file=remediation_action_table.png caption="推奨改善アクション計画マトリクス (P0 -> P1 -> P2 全9施策)"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=106, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=9.5),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.5),
    border_style=Styles.NeutralThin,
)
rows = [
    ["優先度", "施策", "対象ファイル", "期待効果", "関連ルール"],
    [
        "P0",
        "完全な uv.lock 再生成と\nSHA256 ハッシュ固定",
        "uv.lock\npyproject.toml",
        "再現ビルド確立と推移依存\nCVE検知の有効化",
        "common/supply_chain\npython/dependencies",
    ],
    [
        "P0",
        "CliRunner 統合テストと\nFormatter テスト追加",
        "src/logpulse/cli.py\nsrc/logpulse/formatter.py",
        "実測行網羅率を 67% から\n90%超へ引き上げ",
        "python/testing\ncommon/cli_guidelines",
    ],
    [
        "P1",
        "@app.callback() 追加と\n--version / -h 対応",
        "src/logpulse/cli.py\nREADME.md",
        "logpulse scan 構文維持と\nclig.dev 規約準拠",
        "common/cli_guidelines\ncommon/documentation",
    ],
    [
        "P1",
        "ログ逐次ストリーム読込と\nCLI境界入力検証",
        "src/logpulse/cli.py",
        "巨大ログOOM防止・読込失敗\nExit 2保証・不正値拒否",
        "common/security\ncommon/maintainability",
    ],
    [
        "P1",
        "供給網ガバナンス整備\n(SECURITY/Dependabot/CI)",
        ".\npyproject.toml",
        "OpenSSF 準拠の最小権限CIと\n脆弱性自動更新の確立",
        "common/supply_chain",
    ],
    [
        "P1",
        "実測行(67%)・分岐(33.3%)\n未踏パスの完全解消",
        "src/logpulse/cli.py\nsrc/logpulse/parser.py",
        "RV-03 健全基準(行80% /\n分岐70%)の確実な達成",
        "common/runtime_verification\npython/testing",
    ],
    [
        "P2",
        "Standard Readme 拡充と\nMIT ライセンス全文記載",
        "README.md\nLICENSE",
        "導入・テスト手順・全フラグと\nライセンス条項の明確化",
        "common/documentation\ncommon/supply_chain",
    ],
    [
        "P2",
        "コンテナ pip>=26.2.0 更新と\nベースOSパッチ適用",
        "pyproject.toml\nuv.lock",
        "pip 同梱 6件のCVE解消と\nDebian OS層リスク低減",
        "common/security_vulnerability\nCVE-2026-13346 他",
    ],
    [
        "P2",
        "Any 排除・Docstring追加・\nty 型検査器導入",
        "src/logpulse/formatter.py\npyproject.toml",
        "Docstring 100%達成・Any排除\n静的型検査の自動化",
        "python/typing\npython/code_quality",
    ],
]
tbl.draw_flexible(
    xy=(3, 103),
    column_widths=[11, 34, 30, 35, 30],
    row_heights=[7.5] + [10.2] * 9,
    data=rows,
)

save()
```
