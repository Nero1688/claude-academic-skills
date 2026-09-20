# 來源標示 (Attribution)

本技能的出版級繪圖樣式底子(色盲友善調色盤、despine、300dpi 與向量輸出紀律、
多面板規範)改作自下列開源專案:

Based on nature-skills (nature-figure) by Yuan Yizhe (Yuan1z0825)
https://github.com/Yuan1z0825/nature-skills
授權:MIT License, Copyright (c) 2026 Yuan Yizhe

改作說明:
- 未直接複製原 repo 的自然科學圖庫(火山圖、熱圖、顯微影像等)與其 ../_shared 依賴。
- 僅汲取其「出版級 matplotlib 樣式與輸出紀律」之設計理念,重新撰寫為自包含模組
  scripts/mgmt_figures.py,並重新瞄準管理／財務實證常用圖種(轉折點、係數森林圖、
  交互作用、分組比較、趨勢)。
- 依 MIT 條款保留上述版權聲明。本技能供學術研究使用。

## 借用的設計模式（非程式碼，2026-09-20 新增）

### diagram-design — 視覺紀律概念

本技能與 `research-framework-figure` 共用的視覺紀律文件
`research-framework-figure/references/visual-discipline.md`，其密度上限、
單一強調色、對齊網格等判準借用自 `diagram-design` 技能。授權：MIT License。
**借用了什麼**：視覺紀律的概念（見上述共用文件說明）。**未借用什麼**：
**未借用程式碼**；本技能的 `scripts/mgmt_figures.py` 與 `diagram-design`
無關、獨立實作。

### frontend-design — 先定調再產出的流程概念

同一份共用文件「畫圖前先回答三個問題」一節，借用自 `frontend-design` 技能
「先定調再產出」的流程精神。授權：Apache License 2.0。**借用了什麼**：
產出前先確立目的與情境的流程概念。**未借用什麼**：**未借用程式碼**。
