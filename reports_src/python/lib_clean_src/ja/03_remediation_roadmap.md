# 3. 推奨する変更対応

本診断では緊急対応を要するブロッカー（`P0`）は **0 件**であった。ライブラリの数値境界安全性とサプライチェーン再現性をさらに高める **`P1` アクション 2 件**、および CI・ドキュメント・境界テストを完璧に仕上げる **`P2` アクション 3 件**の段階的適用を推奨する。

```drawlib file=03_remediation_timeline.png caption="図3-1: フェーズ別改善ロードマップ (P0: 0件 → P1: 高優先2件 → P2: 品質研磨3件)"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import Panel, Roadmap
from drawlib.styles import Styles

setup(width=146, height=60, dpi=150)

panel = Panel(
    "段階的改善ロードマップ (Phased Remediation Timeline: P0 → P1 → P2)",
    style=Styles.Neutral.patch(shape_r=1.8),
    header_style=Styles.PrimaryFlat,
    text_style=Styles.WhiteBold.patch(text_size=11.5),
    icon=phosphor.road_horizon,
    icon_style=Styles.WhiteBold,
    header_variant="filled",
    header_height=8.5,
)
panel.draw((3.0, 4.0), width=140.0, height=52.0)
p_xy, p_w, p_h = panel.get_content_box((3.0, 4.0), width=140.0, height=52.0, padding=(3.5, 3.0))

rm = Roadmap(
    style=Styles.White.patch(shape_r=1.4),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Muted.patch(text_size=9.5),
    spine_style=Styles.DarkBold,
    badge_style=Styles.PrimaryNeutral,
    badge_text_style=Styles.PrimaryBold.patch(text_size=10.0),
    icon_style=Styles.PrimaryBold,
    direction="horizontal",
    alternating=True,
)
rm.add(
    "緊急是正なし (0件)",
    "CRITICAL/HIGH 指摘ゼロ\n現行のまま安全に利用可能",
    badge_text="P0",
    icon=phosphor.check_circle,
    badge_style=Styles.SuccessFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=10.0),
)
rm.add(
    "NaN / Inf 境界ガード",
    "allow_inf_nan=False と\nisfinite 検証追加",
    badge_text="P1-1",
    icon=phosphor.shield_warning,
    badge_style=Styles.WarningFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.8),
)
rm.add(
    "uv.lock & 検証基盤更新",
    "推移的 wheel ハッシュ固定\n& pip>=26.2.0 更新",
    badge_text="P1-2",
    icon=phosphor.lock_key,
    badge_style=Styles.PrimaryFlat,
    badge_text_style=Styles.WhiteBold.patch(text_size=9.8),
)
rm.add(
    "CI・README・境界テスト",
    "ty/--locked 追加・API追記\n& parametrize 拡充 (3件)",
    badge_text="P2",
    icon=phosphor.sparkle,
    badge_style=Styles.SecondaryNeutral,
    badge_text_style=Styles.DarkBold.patch(text_size=10.0),
)
rm.draw(p_xy, width=p_w, height=p_h)

save()
```

## 3.1 アクションプラン・トレーサビリティマトリクス

以下の図3-2および詳細リストは、検出された指摘事項と関連規約・CVE ID に対する全5件の推奨アクションを優先度順（`P1 → P2`）に整理したものである。

```drawlib file=03_action_traceability_matrix.png caption="図3-2: アクションプラン・トレーサビリティマトリクス (優先度順 P1 → P2)"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Colors, Styles

setup(width=146, height=66, dpi=150)

tbl = Table(
    cell_style=Styles.White,
    text_style=Styles.Dark.patch(text_size=9.5),
    header_cell_style=Styles.PrimaryFlat,
    header_text_style=Styles.WhiteBold.patch(text_size=10.0),
    border_style=Styles.MutedThin,
)
tbl.set_style_cell_evenodd(
    even_color=Colors.Neutral,
    even_text_style=Styles.Dark.patch(text_size=9.5),
    odd_color=Colors.White,
    odd_text_style=Styles.Dark.patch(text_size=9.5),
)
tbl.set_style_cell(
    background_color=Colors.WarningNeutral,
    text_style=Styles.DarkBold.patch(text_size=9.6),
    rows=[1, 2],
    columns=[0],
)
tbl.set_style_cell(
    background_color=Colors.PrimaryNeutral,
    text_style=Styles.PrimaryBold.patch(text_size=9.6),
    rows=[3, 4, 5],
    columns=[0],
)

matrix_data = [
    ["優先度", "推奨アクション項目", "対象ファイル", "期待される改善効果", "関連ルール / CVE"],
    [
        "P1",
        "NaN / Infinity 非有限値の\n境界バリデーション追加",
        "models.py, stats.py,\ntests/test_stats.py",
        "非有限値混入時のソート破綻防止\nと例外契約の一貫性保証",
        "common/security,\npython/code_quality",
    ],
    [
        "P1",
        "uv.lock 推移的ハッシュ完全化\nと検証ベース環境 pip 更新",
        "uv.lock,\npyproject.toml",
        "決定論的ハッシュ検証の確立と\nコンテナ pip CVE 5件解消",
        "security_vulnerability,\nCVE-2026-13346 他",
    ],
    [
        "P2",
        "CI への ty 型チェックと\n--locked 検証フラグ追加",
        ".github/workflows/\nci.yml, pyproject.toml",
        "PR段階でのロック乖離防止と\n静的型安全性の自動ゲート化",
        "common/supply_chain,\npython/dependencies",
    ],
    [
        "P2",
        "README への公開API追記と\n開発・テスト手順の整備",
        "README.md",
        "公開19シンボルとの完全一致と\n開発者オンボーディング向上",
        "common/documentation",
    ],
    [
        "P2",
        "境界条件エッジケースの\nparametrize テスト拡充",
        "test_stats.py, test_rules.py,\ntest_formatting.py",
        "行・分岐カバレッジの98%〜100%\n到達と境界回帰耐性の強化",
        "python/testing",
    ],
]
tbl.draw_flexible(
    xy=(3.0, 62.5),
    column_widths=[12.0, 35.0, 29.0, 36.0, 28.0],
    row_heights=[8.5, 10.0, 10.0, 10.0, 10.0, 10.0],
    data=matrix_data,
)

save()
```

## 3.2 各アクションの具体的実装ガイド

1. **`[P1]` NaN / Infinity 非有限浮動小数点数に対する境界バリデーション追加**（分類: `code_quality`）
   - **対象ファイル**: `src/metrics_kit/models.py`, `src/metrics_kit/stats.py`, `tests/test_stats.py`
   - **実施内容**: `models.py` の各モデル `ConfigDict` に `allow_inf_nan=False` を設定するとともに、`stats.py` の `_require_non_empty` で `math.isfinite()` を検証し、非有限値に対して `InvalidParameterError` を送出する単体テストを追加する。
   - **期待効果**: 異常テレメトリ値（`NaN` / `Inf`）混入時にも未処理の `ValueError` や不正確なパーセンタイル算出を防ぎ、公開APIの例外契約を一貫して保証できる。
2. **`[P1]` `uv.lock` の推移的依存・SHA256ハッシュ完全化と検証ベースイメージ pip/OS 更新**（分類: `security`）
   - **対象ファイル**: `uv.lock`, `pyproject.toml`
   - **実施内容**: `uv lock --upgrade` で `pydantic` 2.14+ および推移的依存（`pydantic-core`, `annotated-types`, `typing-extensions`）の wheel SHA-256 ハッシュを `uv.lock` に完全記録し、コンテナ検証環境ではシステム `pip>=26.2.0` 更新または不要な `pip` 除去と Debian セキュリティパッチ適用を行う（関連: `CVE-2026-13346`, `CVE-2026-8643`, `CVE-2026-6357`）。
   - **期待効果**: 決定論的ハッシュ検証によるサプライチェーン耐性が向上し、コンテナスキャン上の MEDIUM CVE（`pip` 5件）を解消できる。
3. **`[P2]` CI パイプラインへの `ty` 型チェックと `--locked` 検証の追加**（分類: `dependencies`）
   - **対象ファイル**: `.github/workflows/ci.yml`, `pyproject.toml`
   - **実施内容**: `.github/workflows/ci.yml` で `uv run --locked ruff check src tests`、`uv run --locked ty check`、`uv run --locked pytest --cov=metrics_kit` を実行するよう強化する。
4. **`[P2]` `README.md` への公開API追記と開発・テスト手順セクションの整備**（分類: `documentation`）
   - **対象ファイル**: `README.md`
   - **実施内容**: `## API Reference` に `sanitize_prometheus_name` を追記し、`uv run ruff check` / `uv run ty check` / `uv run pytest --cov` の開発者向け手順を明記する。
5. **`[P2]` 境界条件エッジケース（単一要素・ゼロ分散・全比較演算子）の `parametrize` テスト拡充**（分類: `testing`）
   - **対象ファイル**: `tests/test_stats.py`, `tests/test_rules.py`, `tests/test_formatting.py`
   - **実施内容**: `ComparisonOp.LT`、`z_threshold <= 0`、サンプル点数 `< 2`、標準偏差 `0`、単一要素 `compute_percentile`、および空白 `metric_name` の各分岐を `pytest.mark.parametrize` で網羅する。
