# 更新紀錄 / Changelog

本檔記錄**公開包**的變更。公開包是私人開發庫的釋出子集，部分技能與參考檔依既定
政策留在私人庫（原則：公開拿「防止受害」的防線，私人留「研究優勢」的能力）。

---

## v0.13.1 — 2026-09-02

### 這次主要是「一致性與合規」的整補，不是新增技能

技能數維持 **35 支**。公開包自 2026-08-20 之後未再同步，期間私人庫的多項修訂
累積成漂移，這次一次補齊，並修掉數個會影響正確性的問題。

#### 修正：路由總管的斷鏈（會實際影響使用者）

`research-orchestrator` 先前列出並路由到 5 支**不在公開包內**的技能
（check-citations、journal-submission-scout、research-framework-figure、
spatial-data-architect、tw-opendata-scout）。症狀是 Claude 依名錄去叫一個
不存在的技能，然後無聲降級成一般回答——使用者不會收到任何錯誤，只會覺得
「怎麼跟說明寫的不一樣」。

本次已移除這些條目與對應路由行，並把宣告的可路由數改為公開包實際的 **34 個**
（總數 35 減去 orchestrator 自身）。

#### 修正：指向不存在檔案的引用

`global-opendata-scout` 的內文指向兩份未隨公開包釋出的來源目錄
（`catalog-event-risk-data.md`、`catalog-national-primary.md`）。同上，
Claude 會去讀一個不存在的參考檔而無聲降級。已改寫。

跨國資料中**台灣在 UN Comtrade／WITS 沒有獨立國碼、被併入 `490`「Other Asia, nes」**
這項陷阱警告仍保留在公開包——查 `158` 會得到 0 筆卻不報錯，極易誤判「沒有台灣資料」。
這類「不知道就會踩坑」的警告屬公共利益，一律公開。

#### 內容更新

同步了 2026-08-20 之後的多項修訂，涵蓋 `academic-journal-polisher`、
`q1-journal-polisher`、`phd-milestone-tracker`、`qualitative-thematic-coder`、
`r-spss-syntax-architect`、`public-disclosure-scout`、`tej-data-scout`、
`academic-slides`、`research-method-selector` 等技能的 SKILL.md 與參考檔。

新增 `tej-data-scout/references/tej-access-channels.md`：TEJ 資料的三條取得管道
（Pro 桌面端／tejapi／TQuant-Lab）對照，含「TEJ Pro 校園帳號不含 API 授權，
兩套系統不通用」這個常見誤解，以及金鑰與帳號的安全紀律。

---

## 2026-08-20 — v0.13.0

兩道學術誠信防線：撤稿查核（併入 `literature-matrix-builder`）與雙盲投稿的
身分資訊清除（`thesis-consistency-audit/scripts/anonymize_office.py`）。

---

> 更早的紀錄見 git 歷史。
