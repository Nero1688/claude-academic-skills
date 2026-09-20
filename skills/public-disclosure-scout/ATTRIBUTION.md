# 來源標示 (Attribution)

本技能的核心方法(免費源目錄、事件研究就緒度、抓取合規紅線)為原創撰寫，
未複製任何外部專案的程式碼。`scripts/archive_url.py` 亦為原創，僅使用 Python
標準庫（urllib/json/csv/hashlib），未依賴或複製任何第三方套件的程式碼。

## 概念來源

- **jamditis/claude-skills-journalism**
  （https://github.com/jamditis/claude-skills-journalism，MIT，
  2026-09-20 實抓 LICENSE：`/blob/master/LICENSE`）
  `references/disclosure-monitoring.md` 的「頁面變更即存檔」（page-monitoring）
  與「引用網頁應留存檔證據」概念，借鏡自該專案的頁面監測與引用存檔思路。
  本技能僅汲取此**方法概念**重新撰寫成文件指引與 `scripts/archive_url.py`，
  **未複製其任何程式碼**，也**未採用其付費牆（paywall）相關子技能**——
  付費牆繞過涉及規避站方存取控制，超出本技能「合規抓取＋引用永久性」的
  設計範圍與紅線（見 `references/dynamic-scraping-escalation.md` 的 🚫 清單）。

## 使用的外部服務

- **Internet Archive Wayback Machine**（archive.org / web.archive.org）：
  `scripts/archive_url.py` 呼叫其公開 CDX 查詢與 Save Page Now 端點，
  端點行為與實測狀態記錄於 `references/disclosure-monitoring.md` 第四節，
  使用時機與限流因應方式見該檔與腳本檔頭註解。本技能不對 Wayback Machine
  的服務條款或可用性負責，僅盡合理的重試與禮貌間隔之責。

本技能供學術研究使用。
