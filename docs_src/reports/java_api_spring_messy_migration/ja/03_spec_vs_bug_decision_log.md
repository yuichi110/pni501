# 3. ステークホルダー意思決定ログ（仕様かバグか：Spec vs. Bug）

**ハイラムの法則（Hyrum's Law）** および本ワークフローの `bug_handling_policy: ask_human` に従い、`BillingManager.java` に潜む曖昧なレガシー挙動は、Phase 0〜2 の基盤・Clean Architecture・DB/Redis 移行中に暗黙的に変更してはなりません。影響度の高い 4 項目（`DEC-JAVA-01`..`DEC-JAVA-04`）を Phase 0 ゴールデンマスターテストで固定し、Phase 3（`PR-07`）着手前にプロダクトオーナー（PO）の明示的承認を取得します。

```drawlib align=center code=fold file=decision_log_matrix.png caption="ステークホルダー意思決定マトリクス（DEC-JAVA-01..DEC-JAVA-04）：現状挙動・影響・推奨案"
from drawlib.canvas import save, setup
from drawlib.preset_colors import CssColors
from drawlib.smartarts import Table
from drawlib.styles import Colors, Styles
from drawlib.text import text

setup(width=156, height=78, dpi=150)

text(
    (78.0, 73.5),
    "Stakeholder Decision Matrix (Spec vs. Bug — ask_human Governance Gate)",
    style=Styles.DarkBold.patch(text_size=12.0),
)

table = Table(
    cell_style=Styles.Neutral,
    text_style=Styles.Dark.patch(text_size=9.5),
    header_cell_style=Styles.PrimaryFlat,
    header_text_style=Styles.WhiteBold.patch(text_size=10.0),
    border_style=Styles.MutedThin,
)
table.set_style_cell_evenodd(
    even_color=Colors.Light,
    even_text_style=Styles.Dark.patch(text_size=9.5),
    odd_color=Colors.White,
    odd_text_style=Styles.Dark.patch(text_size=9.5),
)
table.set_style_cell_header(
    background_color=Colors.Dark,
    text_style=Styles.WhiteBold.patch(text_size=10.0),
)
table.set_style_cell(
    background_color=Styles.WarningNeutral.shape_fill_color,
    text_style=Styles.WarningBold.patch(text_size=9.5),
    rows=[1, 2, 3, 4],
    columns=[0],
)
table.set_style_border(
    top=Styles.DarkBold.patch(line_width=1.4),
    top2=Styles.DarkBold.patch(line_width=1.0),
    bottom=Styles.DarkBold.patch(line_width=1.4),
    between_rows=Styles.MutedThin.patch(line_color=CssColors.LightGray, line_width=0.6),
    between_columns=Styles.MutedThin.patch(line_color=CssColors.LightGray, line_width=0.5),
)

data = [
    ["Decision ID", "Source Location", "Observed Legacy Behavior", "Impact if Changed Silently", "Recommended Resolution (P3)"],
    [
        "DEC-JAVA-01",
        "BillingManager\n.java:52,55,57",
        "Uses == for status==\"PAID\",\ncurrency==\"USD\"/\"JPY\"; skips\ntax/PAID on HTTP strings.",
        "Deserialized inputs begin\nincurring 8%/10% tax and\nchanging billedCents.",
        "Fix to Currency/InvoiceStatus\nenums (.equals()) after caller\naudit + release note.",
    ],
    [
        "DEC-JAVA-02",
        "BillingManager\n.java:65-71",
        "When amountCents <= 0 and\nforceRetry=true, sends fixed\n100L charge up to maxRetries.",
        "Alters retry fee revenue or\nledger reconciliation for\nzero-amount payloads.",
        "Confirm if 100L is auth hold;\nkeep configurable property\nor enforce @Positive.",
    ],
    [
        "DEC-JAVA-03",
        "BillingManager\n.java:80-82",
        "Conditionally emits diagnostic\nkey 'controllerPing' from\nmutable lastChannel() field.",
        "Dropping key may break\ndownstream monitor scripts\nunder strict compatibility.",
        "Pass request.getMethod() as\nstateless param if needed;\ndeprecate & remove later.",
    ],
    [
        "DEC-JAVA-04",
        "BillingManager\n.java:83-84",
        "Empty catch (Exception e) {}\nswallows audit & cache errors\nand returns HTTP 200.",
        "Propagating failures shifts\nHTTP 200 responses to\nHTTP 500/503 on DB fault.",
        "SLF4J + correlation ID; fail-\nfast on PostgreSQL audit,\ngraceful warn on Redis miss.",
    ],
]

table.draw_flexible(
    xy=(4.0, 69.5),
    column_widths=[19.0, 22.0, 38.0, 33.0, 36.0],
    row_heights=[8.0, 14.0, 14.0, 14.0, 14.0],
    data=data,
    align="top_left",
)
save()
```

## 意思決定ガバナンス・ワークフロー（Phase 0 -> Phase 3）

すべての曖昧候補は 4 段階のガバナンス工程を経て処理されるため、基盤刷新の透明性を保ちながら意図的かつ監査可能な形で仕様確定・バグ修正を行えます。

```drawlib align=center code=fold file=decision_governance_workflow.png caption="Phase 0 特性固定から Phase 3 承認・実装までの 4 段階 Spec vs. Bug ガバナンスフロー"
from drawlib.canvas import save, setup
from drawlib.icons import phosphor
from drawlib.smartarts import CardList, Panel
from drawlib.styles import Styles

setup(width=150, height=58, dpi=150)

frame = Panel(
    "ask_human Decision Governance Flow (Hyrum's Law Safeguard)",
    "Zero silent behavioral drift during Phases 0-2",
    style=Styles.Neutral.patch(shape_r=2.0),
    header_style=Styles.PrimaryNeutral,
    text_style=Styles.DarkBold.patch(text_size=11.0),
    description_style=Styles.Muted.patch(text_size=9.5),
    header_variant="filled",
    header_height=8.5,
)
frame.draw((4.0, 4.0), width=142.0, height=50.0)
inner_xy, inner_w, inner_h = frame.get_content_box((4.0, 4.0), width=142.0, height=50.0, padding=(3.5, 3.0))

steps = CardList(
    style=Styles.Neutral.patch(shape_r=2.0),
    text_style=Styles.DarkBold.patch(text_size=10.5),
    description_style=Styles.Muted.patch(text_size=9.5),
    badge_shape="circle",
    badge_style=Styles.PrimaryNeutral,
    badge_text_style=Styles.PrimaryBold.patch(text_size=9.5),
    icon_style=Styles.PrimaryBold,
    direction="horizontal",
    show_arrows=True,
    arrow_style=Styles.DarkBold,
    spacing=4.0,
)
steps.add(
    "1. Characterize",
    "Phase 0 (PR-02)\nLock current quirks\nin MockMvc tests",
    icon=phosphor.flask,
)
steps.add(
    "2. Quarantine",
    "Phases 1-2 (PR-03..06)\nRefactor ports/DB/Redis\nwith zero semantic drift",
    icon=phosphor.shield_check,
)
steps.add(
    "3. PO Sign-Off",
    "Pre-Phase 3 Gate\nResolve DEC-JAVA-01..04\nOption A vs. Option B",
    icon=phosphor.users_three,
    style=Styles.WarningNeutral.patch(shape_r=2.0),
    badge_style=Styles.WarningFlat,
    icon_style=Styles.WhiteBold,
)
steps.add(
    "4. Execute PR-07",
    "Phase 3 Cutover\nApply approved fixes +\nupdate test contracts",
    icon=phosphor.check_circle,
    badge_style=Styles.PrimaryFlat,
    icon_style=Styles.WhiteBold,
)
steps.draw(xy=inner_xy, width=inner_w, height=inner_h)

save()
```

## 意思決定レコード詳細と選択肢

### `DEC-JAVA-01` — `status` および `currency` の参照等価比較（`==`）
- **対象箇所**: `src/main/java/com/example/billing/service/BillingManager.java:52,55,57`（決定論的候補 `DEC-03`, `DEC-04`, `DEC-05` を統合）
- **現状挙動**: `status == "PAID"`, `currency == "USD"`, `currency == "JPY"` に Java の参照比較 `==` を使用しています。現状 `BillingController.chargeCustomer()` はインターン済みリテラル `"USD"` / `"PENDING"` を渡しているため HTTP `/charge` では偶然 8% 課税が効きますが、HTTP 経由でデシリアライズされた非インターン文字列では `PAID` 重複スキップや 8%/10% 課税が暗黙的に無視されます。
- **ステークホルダー選択肢**:
  - **Option A（推奨）**: Phase 3（`PR-07`）で型付き `Currency` / `InvoiceStatus` 列挙型（`.equals()` 値比較）へ修正し、明示的なリリースノートと特性テスト更新を添えて展開する。
  - **Option B**: カナリアロールアウト期間中、フィーチャーフラグ配下で従来の参照比較挙動を維持する。

### `DEC-JAVA-02` — 非正金額（`amountCents <= 0`）に対する固定 `100L` セントのリトライ課金
- **対象箇所**: `src/main/java/com/example/billing/service/BillingManager.java:65-71`（決定論的候補 `DEC-08` を統合）
- **現状挙動**: `rec.getAmountCents() <= 0` かつ `forceRetry == true` の場合、最大 `maxRetries`（`2` 回）まで `gatewayClient.sendCharge(customerId, 100L)` を実行し、成功時に `100L` セントを `total` に加算します。
- **ステークホルダー選択肢**:
  - **Option A（推奨）**: 課金プロダクトオーナーが「最小オーソリ与信枠の仕様」か「レガシーバグ」かを確定するまで `BillingProperties` で設定可能（既定値 `100L`）として維持し、バグ確定後に `@Positive` バリデーションへ切り替える。
  - **Option B**: Phase 3 で `amountCents <= 0` を即座に HTTP `400 Bad Request` で拒否する。

### `DEC-JAVA-03` — 循環シングルトン状態由来の診断キー `controllerPing`
- **対象箇所**: `src/main/java/com/example/billing/service/BillingManager.java:80-82` および `BillingController.java:20,41-43`（決定論的候補 `DEC-09` を統合）
- **現状挙動**: `circularController != null && extraContext != null` の条件で、シングルトン Controller の非同期可変フィールドを読み取る `circularController.lastChannel()` をレスポンス Map の `"controllerPing"` キーとして返却します。
- **ステークホルダー選択肢**:
  - **Option A（推奨）**: Phase 1 で循環参照とデータ競合を即座に解消しつつ厳格互換を守るため、`traceHint` 指定時は `servletRequest.getMethod()` をステートレスなリクエスト引数として `BillingCommand` に渡し、非推奨ヘッダを付与して段階廃止する。
  - **Option B**: 呼び出し元のログ調査で参照クライアントがゼロと確認できた後、Phase 3 で `controllerPing` を完全削除する。

### `DEC-JAVA-04` — 監査・キャッシュ障害を握り潰す空の `catch (Exception e) {}`
- **対象箇所**: `src/main/java/com/example/billing/service/BillingManager.java:83-84`（決定論的候補 `DEC-02` および標準出力ログ候補 `DEC-01`, `DEC-06`, `DEC-07` を統合）
- **現状挙動**: `saveAuditTrail(...)`、`INVOICE_CACHE.put(...)`、`controllerPing` 設定を空の `catch (Exception e) {}` で囲み、監査保存やキャッシュ書き込みが失敗しても HTTP `200 OK` を返却します。
- **ステークホルダー選択肢**:
  - **Option A（推奨）**: すべての例外を相関 ID 付きで SLF4J 記録した上で、PostgreSQL 監査書き込み障害は **フェイルファスト**（HTTP `500`/`503` へ伝播）、Redis キャッシュ障害は **グレースフルデグレード**（警告ログ + メトリクス計上）とする。
  - **Option B**: Phase 2 シャドー検証中は SLF4J ログ記録のみ有効化し、ベストエフォートの HTTP `200` を一時維持する。

## 厳格な `POST /charge` 外部契約の保全一覧

| 契約要素 | ベースライン (`ANY /charge`) | Phase 0〜2 の挙動 | Phase 3 目標状態 (`POST /charge`) | 関連決定 |
| :--- | :--- | :--- | :--- | :--- |
| **HTTP メソッド** | 全メソッド許可 `@RequestMapping("/charge")` | ゴールデンマスターで `POST` を固定しつつ維持 | `@PostMapping("/charge")` に限定（非 POST は `405`） | 厳格 API 互換 |
| **入力 `customerId`** | raw `Map` キー（既定値 `"anon"`） | そのまま維持 | `ChargeRequest.customerId`（`@Size`、省略時 `"anon"` フォールバック） | 厳格 API 互換 |
| **入力 `amountCents`** | raw `Map` を `Long.parseLong`（既定値 `500`） | そのまま維持 | `ChargeRequest.amountCents`（`Long`、既定値 `500L`、承認結果に応じ検証） | `DEC-JAVA-02` |
| **出力 `customerId`** | raw `Map` の `String` | ゴールデンマスターで固定 | `ChargeResponse.customerId` | 厳格 API 互換 |
| **出力 `billedCents`** | `long`（インターン済み `"USD"` に対し `Math.round(cents * 1.08)`） | ゴールデンマスターで固定 | `ChargeResponse.billedCents`（`TaxPolicy` 列挙型による評価） | `DEC-JAVA-01` |
| **出力 `controllerPing`** | 可変シングルトン由来の条件付き `String` | Wave 3 でステートレスな `requestMethod` 伝搬へ置換 | 条件付き `@JsonInclude(NON_NULL)` または非推奨・削除 | `DEC-JAVA-03` |
| **監査/キャッシュ障害時ステータス** | 空の `catch` により無言 HTTP `200` | シム/アダプタ結線中は現行挙動を維持 | PostgreSQL 障害は `5xx` フェイルファスト、Redis 障害は警告フォールバック | `DEC-JAVA-04` |
