# 架構圖規格範例

三個可直接執行的匿名範例，涵蓋最常用的三種版式。構念刻意採用跨學科通用的變數，
拿來當模板改寫即可，不必從零寫 JSON。

| 檔案 | 版式 | 模型 |
|---|---|---|
| `example-mediation-dual-controls.json` | `mediation_dual_controls` | 數位轉型 → 組織敏捷性／知識整合／流程數位化 → 經營績效；**兩個依變數各一組控制變數框**（台灣商管論文最常見的版式） |
| `example-moderation.json` | `moderation` | 工作自主性 → 工作投入，主管支持為調節；調節箭頭指向主路徑中點 |
| `example-serial-mediation.json` | `serial_mediation` | 組織學習導向 → 知識分享 → 創新能力 → 新產品績效 |

用法：

```bash
python ../framework_figure.py example-mediation-dual-controls.json -o framework.svg
python ../framework_figure.py example-mediation-dual-controls.json -o framework.pptx
```

改版時直接編輯 JSON 的 `items` 陣列即可，不必重畫。
假說編號若與論文內文調整過，記得同步改 `hypotheses`（數字零容忍）。

完整欄位定義與其餘版式（`mediation`、`moderated_mediation`）見
`../../references/framework-figure-spec.md`。

