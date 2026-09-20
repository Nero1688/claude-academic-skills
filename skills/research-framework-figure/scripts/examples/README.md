# 架構圖規格範例

五個可直接執行的匿名範例，涵蓋最常用的三種假說關係版式，以及 `sample_flow`
的 `prisma`／`attrition` 兩個 mode。構念與數字刻意採用跨學科通用、匿名合成的
內容，拿來當模板改寫即可，不必從零寫 JSON。

| 檔案 | 版式 | 模型 |
|---|---|---|
| `example-mediation-dual-controls.json` | `mediation_dual_controls` | 數位轉型 → 組織敏捷性／知識整合／流程數位化 → 經營績效；**兩個依變數各一組控制變數框**（台灣商管論文最常見的版式） |
| `example-moderation.json` | `moderation` | 工作自主性 → 工作投入，主管支持為調節；調節箭頭指向主路徑中點 |
| `example-serial-mediation.json` | `serial_mediation` | 組織學習導向 → 知識分享 → 創新能力 → 新產品績效 |
| `example-sample-flow-prisma.json` | `sample_flow`（`mode: "prisma"`） | 系統性文獻回顧的 PRISMA 2020 流程圖：多來源識別（資料庫 A／B＋手動追蹤引用）→ 去重 → 篩選 → 檢索 → 資格評估（依理由排除）→ 納入；匿名合成數字，已自動對帳 |
| `example-sample-flow-attrition.json` | `sample_flow`（`mode: "attrition"`） | Panel 研究常見的樣本刪減圖：台灣上市櫃全樣本（年份以「20XX–20XX」泛稱）→ 逐步排除金融保險業／缺漏值／極端值 → 最終樣本；匿名合成數字，已手算驗證通過自動對帳 |

用法：

```bash
python ../framework_figure.py example-mediation-dual-controls.json -o framework.svg
python ../framework_figure.py example-mediation-dual-controls.json -o framework.pptx
python ../framework_figure.py example-sample-flow-prisma.json -o prisma.svg
python ../framework_figure.py example-sample-flow-attrition.json -o attrition.pptx --format pptx
```

改版時直接編輯 JSON 的 `items`／`sources`／`steps` 等陣列即可，不必重畫。
假說編號若與論文內文調整過，記得同步改 `hypotheses`（數字零容忍）；
`sample_flow` 的 `identification.sources`／`eligibility.excluded_reasons`
（`prisma`）或 `steps[].remaining`／`excluded`（`attrition`）改動後，程式會
自動重新對帳，數字對不上會直接報錯、不會畫出對不上的圖。

完整欄位定義、`sample_flow` 的對帳規則，以及其餘版式（`mediation`、
`moderated_mediation`）見 `../../references/framework-figure-spec.md`。
畫圖前建議先讀 `../../references/visual-discipline.md`（視覺紀律）。

