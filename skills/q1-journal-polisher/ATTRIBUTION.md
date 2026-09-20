# ATTRIBUTION — q1-journal-polisher

本技能為作者原創(根 LICENSE)。以下為**概念層**借鑑,均未借用程式碼或原文。

## Nanako0129/sepia — 三層潤飾協議與人類分布校準(概念)

- 來源:https://github.com/Nanako0129/sepia
- 授權:MIT(2026-09-20 實抓 https://github.com/Nanako0129/sepia/blob/main/LICENSE 核實,
  首行為「MIT License」)
- 借鑑概念:
  1. **三層協議(敘事架構→論述流→表面風格)**——本技能 SKILL.md 階段零已標明的
     「三層由巨到微:敘事架構(階段零)→論證力度(進階層)→詞彙層(階段二至四)」,
     對應到 sepia README 的 Pass 1(narrative architecture)→Pass 2(discourse flow)→
     Pass 3(surface style)三段式。實作落在 `references/narrative-architecture-check.md`
     (敘事架構層);論述流/結構層的對應檢查文件為維護者本機版本專用,公開包不含此檔。
  2. **「校準到人類分布,而非反轉 AI 分布」**——對應維護者本機版本的論述流檢查文件(不在公開包內)
     caveat 2「本文件的目的不是規避 AI 偵測⋯就算完全不考慮 AI,也都是該修的寫作缺陷」,
     與 sepia README "calibrate to the human distribution, don't invert the AI one"
     為同一治理原則的轉譯。
  3. **中文/英文以句長離散度(而非平均句長)作訊號**——對應 `scripts/prose_metrics.py` 的
     `dist_stats()`,以變異係數 `cv = stdev/mean` 衡量句長分散度,`--lang zh`/`--lang en`
     兩種語言皆適用;與 sepia README style-pass 所述「看句長的 spread,不是英文中文都成立
     的那個句法量測」為同一訊號選擇邏輯。
- 引用查核:sepia README 引用的 StoryScope(arXiv:2604.03136)經 2026-09-20 實抓
  arxiv.org/abs/2604.03136 核實存在,標題與內容(人類/AI 小說敘事特徵比較)相符,
  與本技能維護者本機版本的論述流檢查文件既有引用一致。README 另提到的
  `SLOPSHAPE-2026`(其自述之 2026 年 StoryScope 於企業部落格文章上的複製研究,
  arXiv:2609.15369)為該 README 自身研究紀錄的自報用語,**本次未獨立核實其論文內容**,
  僅供讀者知悉來源性質。
- 未借用:sepia 的任何文字、規則檔、程式碼或私有語料;本技能既有的「目的是投稿可讀性、
  非規避 AI 偵測」立場為原創主張,非沿用自 sepia。
- 本技能加入的原創部分(舉例各一句):`references/narrative-architecture-check.md`
  「台灣稿件在頂刊的敘事落差→對策」一節的三個台灣商管稿投頂刊常見敘事落差
  (貢獻被讀成情境複製、先講台灣再講理論、缺口句是「沒人做過」而非「理論解釋不了」)
  為本技能作者針對台灣家族企業/公司治理稿件投稿經驗的原創歸納,sepia 未涉及此議題。
