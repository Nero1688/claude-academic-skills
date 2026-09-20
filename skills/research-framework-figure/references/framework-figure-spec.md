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

### `sample_flow`（樣本流程圖：PRISMA 2020／樣本刪減圖）

與前面幾種「假說關係圖」不同，`sample_flow` 畫的是**樣本怎麼從全樣本一路篩到
最終樣本**的流程，不含 X/M/Y 假說路徑，因此**不需要** `x`／`y` 欄位。用
`mode` 欄位選子版式，`prisma` 與 `attrition` 互斥，**不填或填錯值會直接報錯**
（不會靜默走某個預設版式）：

```json
{"template": "sample_flow", "mode": "prisma", "...": "..."}
{"template": "sample_flow", "mode": "attrition", "...": "..."}
```

使用時機：
- `prisma`：系統性文獻回顧／統合分析要交代 PRISMA 2020 四階段（識別／篩選／
  資格評估／納入）篩選過程時。
- `attrition`：panel／橫斷面實證研究要交代「全樣本 → 逐步排除 → 最終樣本」
  的樣本刪減過程時（台灣上市櫃 panel 研究最常見）。

#### `prisma` 子規格

```json
{
  "template": "sample_flow",
  "mode": "prisma",
  "identification": {
    "sources": [
      {"label": "資料庫 A", "n": 210},
      {"label": "資料庫 B", "n": 95},
      {"label": "手動追蹤引用（citation chasing）", "n": 12}
    ],
    "duplicates_removed": 47,
    "automation_excluded": 38,
    "automation_excluded_label": "自動化工具判定不合格（年份／語言／關鍵字規則）"
  },
  "screening": {
    "excluded": 152,
    "excluded_label": "篩選排除（標題與摘要不符）"
  },
  "retrieval": {
    "not_retrieved": 6,
    "not_retrieved_label": "全文無法取得"
  },
  "eligibility": {
    "excluded_reasons": [
      {"reason": "研究設計非量化實證", "n": 20},
      {"reason": "缺乏可比較之結果變數", "n": 15}
    ],
    "label": "資格排除（依理由）"
  },
  "included": {"label": "納入之研究"}
}
```

| 欄位 | 必填 | 說明 |
|---|---|---|
| `identification.sources` | **是** | 陣列，至少 1 筆；每筆 `{"label", "n"}`，對應多來源資料庫或手動追蹤引用，各自的 n 分開列出、圖上也分開顯示 |
| `identification.duplicates_removed` | 否（預設 0） | 重複記錄移除數 |
| `identification.automation_excluded` | 否（預設 0；填了才畫） | PRISMA 2020（Page et al., 2021, *BMJ*）識別框的「records marked as ineligible by automation tools」：**人未看過、由確定性規則或分類器直接排除**的記錄數。對接 `literature-matrix-builder` 的 `screen_cascade.py prisma` 輸出（stage1 規則層 `rule != duplicate_doi` 的排除數）；方法節須列出規則內容 |
| `identification.automation_excluded_label` | 否 | 該項標籤文字（預設「自動化工具判定不合格」） |
| `screening.excluded` | 否（預設 0） | 標題摘要篩選排除數（含 LLM 輔助篩選的排除；LLM 篩選對人工金標準的 recall 要寫進方法節，見 `screen_cascade.py kappa` 的輸出） |
| `screening.excluded_label` | 否 | 排除框標題文字 |
| `retrieval.not_retrieved` | 否（預設 0） | 全文無法取得數 |
| `retrieval.not_retrieved_label` | 否 | 該框標題文字 |
| `eligibility.excluded_reasons` | 否（預設空） | 陣列，每筆 `{"reason", "n"}`，依理由分列，圖上逐條列出 |
| `eligibility.label` | 否 | 資格排除框標題文字 |
| `included.label` | 否（預設「納入之研究」） | 最終納入框標題文字 |

**對帳規則（單一事實來源設計）**：每個階段框顯示的 n 一律由程式從上述原始
輸入**自動算出**，使用者不必也不能另外填一次算式結果：

```
已識別總數 = Σ sources[].n
篩選之記錄 = 已識別總數 − duplicates_removed − automation_excluded
尋求檢索之報告 = 篩選之記錄 − screening.excluded
評估資格之報告 = 尋求檢索之報告 − retrieval.not_retrieved
納入之研究 = 評估資格之報告 − Σ eligibility.excluded_reasons[].n
```

任一步算出負數（代表排除數超過上一階段可排除的樣本），程式會印出清楚的
錯誤訊息並以非零 exit code 結束，**不會畫出對不上的圖**。採單一事實來源
而非「使用者填兩份數字再互相核對」，是為了避免兩份數字剛好填成同一個錯值、
反而「對帳通過」的假象。

版面：左側直式標籤標出 Identification／Screening／Included 三階段涵蓋
範圍；主欄由上而下依序為已識別記錄→移除重複→篩選之記錄→尋求檢索之報告→
評估資格之報告→納入之研究，皆以向下實線箭頭連接；篩選排除、無法取得全文、
資格排除三個框在右側，各自以向右實線箭頭從其來源框接出。

#### `attrition` 子規格

```json
{
  "template": "sample_flow",
  "mode": "attrition",
  "unit": "firm-years",
  "steps": [
    {"label": "台灣上市櫃公司全樣本（20XX–20XX）", "remaining": 15000},
    {"label": "排除金融保險業", "excluded": 1200,
     "reason": "金融保險業之財報結構與一般產業不可比", "remaining": 13800},
    {"label": "排除上市未滿 12 個月之公司年", "excluded": 800,
     "reason": "上市首年財務與市場資料不足一完整年度；下市公司年保留於樣本內以避免存活偏誤", "remaining": 13000},
    {"label": "排除關鍵變數缺漏之公司年觀察值", "excluded": 2500,
     "reason": "主要研究變數缺漏無法計算", "remaining": 10500},
    {"label": "最終樣本", "excluded": 500,
     "reason": "排除合併控制變數與落後一期變數後仍缺漏之觀察值（連續變數於前後 1% 縮尾，不刪樣本）", "remaining": 10000}
  ]
}
```

**兩條篩選步驟紅線（財務家族審稿人第一輪就會抓）**：
1. **排除下市公司＝存活偏誤（survivorship bias）。** 治理／ESG／財務困境研究的「下市」
   正是結果之一，把它當篩選步驟等於把結果變數截尾。除非研究問題**明文限定存續公司**
   （並在資料節說明理由），否則不得作為篩選步驟；下市公司年一律保留，並在資料節報告
   「其中下市公司 N 家保留」。TEJ 匯出時要合併「各年度下市檔」，否則主表根本不含下市
   公司——見 `tej-data-scout/references/tej-catalog.md` Part D「存活偏誤與回填」。
2. **縮尾（winsorize）不產生缺失，不得寫成排除步驟。** 「winsorize 後仍缺失」是把
   trimming（刪除極端值）與 winsorizing（極端值改為分位數值）混為一談，審稿人會問你
   到底做了哪一種。極端值處理的說明放資料節文字，不進樣本刪減圖。

| 欄位 | 必填 | 說明 |
|---|---|---|
| `unit` | 否（預設「筆」） | N 後面的單位文字，如 `firm-years`、`firms` |
| `steps` | **是**，至少 2 筆 | 依序列出每一個篩選步驟 |
| `steps[].label` | **是** | 該步驟名稱，會畫在框標題列 |
| `steps[].remaining` | **是** | 該步驟篩選後剩餘 N；**第一筆**是起始全樣本數，不需要 `excluded`/`reason` |
| `steps[].excluded` | 第一筆以外必填（預設 0） | 從「上一步 remaining」扣除的排除數 |
| `steps[].reason` | 否 | 排除理由，畫在右側排除框 |

**自動對帳（一定要做，不可省略）**：對每一步 i（i ≥ 1，即第二筆起）檢查

```
上一步 remaining − 這一步 excluded == 這一步 remaining
```

只要有一步不成立，程式印出「第幾步、期望值、實際值」並以非零 exit code
結束，**不准畫出對不上的圖**。這呼應本技能家族一貫的「數字零容忍」紀律。

版面：主欄由上而下依序為各步驟框（皆顯示「步驟名稱＋N＝剩餘數 單位」），
以向下實線箭頭連接；每一步（第一步除外）右側各有一個排除說明框（「排除
n=…：理由」），以向右實線箭頭從其對應的主欄框接出；**最後一框的標題會
自動加註「（最終樣本）」**以特別標示。

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
