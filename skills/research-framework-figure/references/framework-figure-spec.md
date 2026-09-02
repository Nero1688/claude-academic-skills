# 研究架構圖 JSON 規格

`scripts/framework_figure.py` 的輸入格式。所有欄位皆為 UTF-8 繁體中文可直接填寫。

## 最小可用規格

```json
{
  "template": "mediation",
  "x": {"label": "自變數(X)", "items": ["數位轉型程度"]},
  "y": {"label": "應變數(Y)", "items": ["經營績效 (ROA)"]}
}
```

## 完整欄位表

| 欄位 | 型別 | 必填 | 說明 |
|---|---|---|---|
| `template` | string | 否（預設 `mediation`） | 版式，見下節 |
| `title` | string | 否 | 圖標題，畫在最上方；期刊圖通常不放（標題寫在圖說 caption），預設不填 |
| `x` | object | **是** | 自變數框 |
| `y` | object | **是** | 應變數框 |
| `m` | object | 否 | 中介／作用機制變數框 |
| `mediators` | array | 否 | 序列中介用，依序列出多個中介框 |
| `moderator` | object | 否 | 調節變數框（箭頭會指向路徑中點） |
| `hypotheses` | object | 否 | 假說標籤，如 `{"h1":"H1","h2":"H2","h3":"H3"}` |
| `controls` | array | 否 | 控制變數框，可 1–2 組 |
| `style` | object | 否 | 版面微調，見末節 |

### 框物件（`x` / `y` / `m` / `moderator` / `controls[]`）

```json
{
  "label": "作用機制變數(M)",
  "items": ["組織敏捷性", "知識整合能力"],
  "target": "m"
}
```

- `label`：框的**標題列**文字（粗體、置中、下方有分隔線）。
- `items`：框內條列。**單項自動置中、多項自動加編號並靠左**——這是刻意的排版規則，
  符合台灣商管論文架構圖慣例（X／Y 框單一構念置中；M／控制變數框條列編號）。
- `target`：**僅 `controls[]` 需要**。值為 `"m"` 或 `"y"`，指定這組控制變數的虛線
  箭頭要接到哪個依變數框。

## 版式（template）

### `mediation_dual_controls`（台灣商管論文最常見）
中介模型＋**每個依變數各一組控制變數**。版面：M 在上方置中，X 在左、Y 在右，
兩個控制變數框在下方左右分置，各以虛線彎箭頭接入其對應的依變數。

適用時機：你的論文有兩條迴歸式（一條以 M 為依變數、一條以 Y 為依變數），
兩條式子的控制變數不完全相同。

```json
{
  "template": "mediation_dual_controls",
  "x": {"label": "自變數(X)", "items": ["〔自變數〕"]},
  "m": {"label": "作用機制變數(M)", "items": ["〔中介1〕", "〔中介2〕"]},
  "y": {"label": "應變數(Y)", "items": ["〔應變數〕"]},
  "hypotheses": {"h1": "H1", "h2": "H2", "h3": "H3"},
  "controls": [
    {"label": "當應變數為〔M〕時的控制變數(C)", "target": "m", "items": ["公司年齡", "公司規模"]},
    {"label": "當應變數為〔Y〕時的控制變數(C)", "target": "y", "items": ["公司年齡", "ROA"]}
  ]
}
```

路徑對應：H1 = X→M（左下往右上）、H2 = X→Y（水平主路徑）、H3 = M→Y（右上往右下）。

### `mediation`
簡單中介。X 左、M 上中、Y 右，三條實線路徑。控制變數可用單一 `controls` 或省略。

### `moderation`
調節模型。W 框置於下方，箭頭指向 X→Y 路徑的**中點**（不是指向 Y）——
這是心理計量與管理學的標準畫法，理由見 `diagram-conventions.md`。

```json
{
  "template": "moderation",
  "x": {"label": "自變數(X)", "items": ["〔X〕"]},
  "y": {"label": "應變數(Y)", "items": ["〔Y〕"]},
  "moderator": {"label": "調節變數(W)", "items": ["〔W〕"]},
  "hypotheses": {"h2": "H1"}
}
```

### `moderated_mediation`
被調節的中介。以 `mediation` 為底，加上 `moderator`。
**注意**：圖上必須看得出 W 調節的是「第一階段 X→M」還是「第二階段 M→Y」，
在 `moderator.label` 明確寫出（如「調節變數(W)：調節第一階段」）。

### `serial_mediation`
序列中介 X→M1→M2→Y。用 `mediators` 陣列依序給多個中介框，版面自動水平排列。

```json
{
  "template": "serial_mediation",
  "x": {"label": "自變數(X)", "items": ["〔X〕"]},
  "mediators": [
    {"label": "中介變數(M1)", "items": ["〔M1〕"]},
    {"label": "中介變數(M2)", "items": ["〔M2〕"]}
  ],
  "y": {"label": "應變數(Y)", "items": ["〔Y〕"]},
  "hypotheses": {"h1": "H1", "h2": "H2", "h3": "H3"}
}
```

## style 微調

只在版面不理想時才動。預設值已對齊學術圖表比例。

| 鍵 | 預設 | 說明 |
|---|---|---|
| `font_family` | `Times New Roman, DFKai-SB, BiauKai, serif` | **西文字型必須排在中文前面**，否則英數不會套 Times New Roman |
| `font_size_header` | 19 | 框標題列字級 |
| `font_size_item` | 17 | 框內條列字級 |
| `font_size_hypo` | 20 | H1/H2/H3 標籤字級 |
| `line_height` | 27 | 條列行高；條目多時可降到 24 壓縮版面 |
| `stroke_width` | 1.8 | 框線與箭頭粗細 |
| `margin` | 40 | 畫布留白 |

```json
{"style": {"font_size_item": 15, "line_height": 23}}
```
↑ 控制變數多達 11–12 項時的常用壓縮設定。

## 常見踩雷

1. **控制變數超過 12 項**：框會長到破壞版面比例。建議改列在圖下方註解，
   圖內只寫「控制變數（詳見表 3-1）」。
2. **`target` 忘了填**：控制變數的虛線箭頭會預設接到 `y`，若你要接 M 就會畫錯。
3. **中文字型 fallback**：SVG 只是「宣告」字型名稱，實際顯示取決於檢視端有沒有裝
   標楷體。產出後務必在有字型的機器上確認一次。
4. **`hypotheses` 編號與論文不一致**：圖上的 H1/H2/H3 要跟論文內文的假說編號對得起來，
   產圖前先核對一次（這屬於 CLAUDE.md 的數字零容忍範圍）。
