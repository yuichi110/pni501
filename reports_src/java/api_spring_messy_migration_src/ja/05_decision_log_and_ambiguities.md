# 5. 「仕様かバグか」ステークホルダー意思決定ログ（Decision Log）

レガシー移行において最も危険なのは、開発者や AI が「明らかなバグに見えるコード」をインフラ刷新と同時に黙って修正し、その挙動に依存していた外部クライアントを破壊することである（**Hyrum の法則**）。`bug_handling_policy: ask_human` に従い、AST 解析で抽出された下記4件の境界挙動は **Phase 0〜2 では現行挙動を Golden Master テストで厳格維持**し、プロダクトオーナー承認後に **Phase 3（`PR-08` / `PR-09`）で意図的に切り替える**。

```drawlib file=decision_log_gate_flow.png caption="Hyrum の法則を防ぐ「仕様 vs バグ」分離・承認ゲートフロー"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import Roadmap
from drawlib.styles import Styles

setup(width=146, height=56, dpi=150)

rm = Roadmap(
    style=Styles.Neutral,
    text_style=Styles.DarkBold.patch(text_size=9.4),
    description_style=Styles.Dark.patch(text_size=8.6),
    spine_style=Styles.PrimaryBold,
    badge_style=Styles.Primary,
    badge_text_style=Styles.WhiteBold.patch(text_size=8.8),
    direction="horizontal",
    spacing=3.0,
)
rm.add(
    "Step 1: 現行挙動の固定",
    "Phase 0 特性テストで\nバグ疑い挙動も一旦固定",
    badge_text="Phase 0-2",
    style=Styles.PrimaryNeutral,
    badge_style=Styles.Primary,
    icon=phosphor.camera,
    icon_style=Styles.Primary,
)
rm.add(
    "Step 2: PO 合意ゲート",
    "DEC-01〜04 の影響額・\n互換性を事業側と合意",
    badge_text="Sign-off",
    style=Styles.WarningNeutral,
    badge_style=Styles.Warning,
    icon=phosphor.users,
    icon_style=Styles.Warning,
)
rm.add(
    "Step 3: 独立 PR で修正",
    "Phase 3 (PR-09) で\n仕様変更とテストを同時更新",
    badge_text="Phase 3",
    style=Styles.SuccessNeutral,
    badge_style=Styles.Success,
    icon=phosphor.check_circle,
    icon_style=Styles.Success,
)
rm.draw(xy=(4, 5), width=138, height=46)

save()
```

## ステークホルダー承認対象リスト（DEC-01 〜 DEC-04）

```drawlib file=stakeholder_decision_log_table.png caption="Phase 3 着手前に合意必須のステークホルダー意思決定ログ (DEC-01 - DEC-04)"
from drawlib.canvas import save, setup
from drawlib.smartarts import Table
from drawlib.styles import Styles

setup(width=146, height=114, dpi=150)

tbl = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=8.5),
    header_cell_style=Styles.Primary,
    header_text_style=Styles.WhiteBold.patch(text_size=9.0),
    border_style=Styles.NeutralThin,
)
rows = [
    ["ID / 箇所", "現行コードの観測挙動 (As-Is)", "無断変更時の影響リスク", "推奨方針 (Recommended) と選択肢"],
    [
        "DEC-01\nBillingManager\n:L52-L57",
        "status == \"PAID\" / currency ==\n\"USD\",\"JPY\" を参照等価 (==) 比較\nしており税加算が実質不発。",
        ".equals() 化すると USD 8% / JPY\n10% 課税が急に有効化され、顧客\n請求額 (billedCents) が変動する。",
        "[推奨 Option A] Phase 0-2 は維持し、PO 承認・\n事前告知のうえ Phase 3 (PR-09) で Enum 税計算化\n[Option B] フラグ配下で段階有効化",
    ],
    [
        "DEC-02\nBillingManager\n:L67",
        "amountCents <= 0 のリトライ経路で\n固定リテラル 100L ($1 相当) を\nGatewayClient へ課金送信。",
        "即時 400 エラー化すると、$1 与信\nプローブとして利用中の下流決済\n連携が失敗する恐れがある。",
        "[推奨 Option A] アクセスログ監査後、不要なら\n@Positive 検証で HTTP 400 拒否へ統一\n[Option B] /charge/verify-card へ分離",
    ],
    [
        "DEC-03\nBillingManager\n:L81-L83",
        "レスポンスに controllerPing 診断\nキーを含め、例外時は空 catch で\n握り潰して正常応答を返す。",
        "循環依存切断時にキーを削除すると\n厳格な JSON スキーマ検証を行う\nクライアントがパース失敗する。",
        "[推奨 Option A] strict 互換に従いリクエスト\nX-Channel 由来で controllerPing を互換出力維持\n[Option B] 利用ゼロ確認後に即時削除",
    ],
    [
        "DEC-04\nBillingController\n:L24-L27",
        "GET 含む全 HTTP メソッドを受け付け\ncustomerId=\"anon\", amount=500\nへ暗黙フォールバックする。",
        "POST 限定化・必須入力化により、\nGET 死活監視や省略呼び出しを行う\n旧スクリプトが 405/400 となる。",
        "[推奨 Option A] POST /charge 限定化 (死活監視は\n/actuator/health) + 必須入力 ProblemDetail 400\n[Option B] DTO 既定値で一時フォールバック維持",
    ],
]
tbl.draw_flexible(
    xy=(3, 111),
    column_widths=[24, 38, 36, 42],
    row_heights=[8.0, 24.5, 24.5, 24.5, 24.5],
    data=rows,
)

save()
```
