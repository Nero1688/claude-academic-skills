# 來源標示 (Attribution)

本技能的多維度審稿/一致性稽核框架,改作自下列開源專案:

Based on awesome_proofreading_auto by qqfly1to19
https://github.com/qqfly1to19/awesome_proofreading_auto
授權:CC BY-NC-SA 4.0(姓名標示-非商業性-相同方式分享)

改作說明:
- 未複製原專案之中文醫學術語庫(衛健委 42,217 條)、臨床邏輯/醫學術語/醫學圖
  校驗等醫學專屬子技能,亦未採用 GB/T 7714 參考文獻格式。
- 僅汲取其「資料一致性 / 表格 / 前後一致」之審稿框架理念,重新撰寫為自包含工具
  scripts/audit_docx.py 與 references/audit_checklist.md,並改為瞄準管理/財務量化
  論文 + APA 7 + TEJ。
- 依 CC BY-NC-SA 4.0 之「相同方式分享」條款,本衍生技能亦以 CC BY-NC-SA 4.0 釋出,
  供個人學術(非商業)使用。

## 補充概念來源(2026-09-20 新增)

- **jamditis/claude-skills-journalism**
  (https://github.com/jamditis/claude-skills-journalism,MIT,
  2026-09-20 實抓 LICENSE:`/blob/master/LICENSE`)
  第六維度(引用與表註一致)新增的「網頁來源存檔紅旗」規則,概念上借鏡自該專案
  的引用網頁存檔留底思路——論文引用的網頁來源應可事後驗證,而非僅憑一次性連結。
  本技能僅汲取此**概念**寫成稽核規則,**未複製其任何程式碼**;實際存檔操作由
  `public-disclosure-scout` 的 `scripts/archive_url.py` 執行,本技能只負責稽核
  「有沒有附存檔證據」,不重複實作存檔功能。

## 補充概念來源(2026-10-08 新增)

- **anthropics/knowledge-work-plugins**
  (https://github.com/anthropics/knowledge-work-plugins,Apache-2.0,2026-10-08 實抓根目錄 LICENSE)
  `scripts/audit_docx.py` 新增的「掃描範圍」報告與「機械層覆蓋不足」警示,借鏡該專案
  `small-business/shared/absent-is-not-zero.md` 的原則:空結果與沒檢查到長得一模一樣,
  零發現必須先交代掃到多少才有意義。本技能僅汲取此**原則**,以自己的程式與文字實作,
  **未複製其任何文字或程式碼**;`audit_docx.py` 整體仍依上方 CC BY-NC-SA 4.0 條款釋出。
