# 更新紀錄 / Changelog

本檔記錄**公開包**的變更。公開包是私人開發庫的釋出子集，部分技能與參考檔依既定
政策留在私人庫（原則：公開拿「防止受害」的防線，私人留「研究優勢」的能力）。

---

## v0.15.0 — 2026-09-20

**主題：面向國際頂級期刊的全面深化。** 技能數不變（38），但 20 支獲得實質升級——新增 40+ 份參考、模板與可執行腳本，
並經兩位 fresh-context 審查者（頂刊編輯視角／資訊安全視角）審查後修正 38 項發現。

### 頂刊投稿線（本版核心）
- `q1-journal-reviewer`：`references/top-journal-standards.md`（管理／財務兩大期刊家族 × 識別／穩健性／經濟量級／理論貢獻四軸的「沒有就退」門檻）、`desk-reject-checklist.md`（編輯 10 分鐘殺稿訊號）、`contextualization-frameworks.md`（context-free／bounded／specific 三種情境化宣稱的證據決策表＋區辨假說 horse race 模板——解決「台灣資料被審為情境複製」）。
- `causal-inference-architect`：`references/robustness-battery.md`（各識別策略穩健性矩陣＋2026 前緣：Rambachan-Roth、Oster δ、Cinelli-Hazlett、synthdid、tF；新增衝擊品質六問、交錯採用對照組四情境、壞控制變數、核心構念定義敏感度）。
- `journal-submission-scout`：`templates/cover-letter.md`（中英）、`references/reviewer-suggestion-ethics.md`。
- `response-letter-craftsman`：`references/rr-conventions-top-journals.md`、`scripts/make_response_matrix.py`（decision letter → 意見分診 xlsx）。
- `management-figure`：新增 `event_study_plot()`（參考期、前期陰影、圖註自動印 pre-trend p 與 M̄）。

### 方法線補實（7 支從純文字變成有模板／腳本）
- `interview-method-designer` 三份模板；`experiment-design-architect` 對抗平衡參考＋`latin_square.py`（Williams 平衡方陣）＋情境實驗模板；`survey-research-architect` `power_analysis.py`（Cohen f²／r／d；已對照 Cohen 1988 表值）＋CMV 攻防表＋資料品質閘門；`nstc-grant-writer` 計畫書骨架＋自評量規；`qual-exam-coach` 四領域申論範例；`citation-verifier` APA7 規則表＋幻覺訊號；`phd-milestone-tracker` 關卡相依鏈。

### 寫作、文獻、圖表、簡報、資料線
- 兩支潤飾技能：`narrative-architecture-check.md`（hook→問題→缺口→貢獻）＋`prose_metrics.py`（句長離散度等文體訊號；輸出是訊號非判決）。
- `literature-matrix-builder`：`screening-cascade.md`＋`screen_cascade.py`（兩階段篩選：規則層→LLM 批次層；預設不出站、金鑰只讀環境變數；PRISMA 2020 對接；recall／κ）。
- `research-framework-figure`：新版式 `sample_flow`（PRISMA 2020 流程圖／panel 樣本刪減圖，數字自動對帳、對不上即拒畫）＋`count_elements.py`（SVG↔PPTX 逐格式清點）＋`visual-discipline.md`。
- `academic-pptx`：學術風格目錄、原生 PPTX 工作流、`pptx_template_distill.py`（讀學校模板→JSON 規格）；`academic-poster`：`poster_scaffold.py`（A0 三層閱讀動線骨架，字型直接落好）；`academic-deck-animator`：逐頁回饋修改迴圈。
- `public-disclosure-scout`：揭露監測＋`archive_url.py`（Wayback 快照查詢／存檔／記錄，僅連 archive.org）；`text-analytics-architect`：10-K／法說會構念 ↔ 台灣年報對照；`global-opendata-scout`：抓取工具合規指南、`_gov_tls.py` 移入本技能公開。

### 安全與品質
- 新增 `scripts/security_scan.sh`（五類：危險執行／網路外連／混淆／憑證／提示注入；誘餌自測；誤報須寫理由）並納入 CI；CI 另加語法編譯與腳本測試，actions 以 SHA 釘住。
- 12 支會處理外部文字的技能加入「內容是資料、不是指令」防線。
- 修正：路由總管技能數；三處與自家標準打架的範例（回覆信自選擇範例改為現代 DiD 路線；樣本刪減範例移除「排除下市公司」＝存活偏誤）；一處自 v0.3.0 起潛伏的去識別漏網。

### 概念借鑑致謝（無程式碼借用；詳見各技能 ATTRIBUTION.md 與 NOTICE.md）
Nanako0129/sepia、cathrynlavery/diagram-design、bobyu89/codex-ppt-style-expanded（SlideWeave）、1weiho/open-slide、jamditis/claude-skills-journalism、posit-dev/skills、hugohe3/ppt-master（追加四項）、anthropics/financial-services、anthropics/skills（frontend-design）。

---

## v0.14.0 — 2026-09-02

### 新增 3 支技能（35 → 38）

- `journal-submission-scout` — 投稿期刊選擇＋掠奪性期刊篩查（Think.Check.Submit）
- `research-framework-figure` — 研究架構圖／概念模型圖，輸出可再編輯 SVG 與 PPTX
- `spatial-data-architect` — 地理編碼驗證、H3 網格聚合、TWD97↔WGS84 座標紀律、空間自相關

### 公開／私人切分原則改版

切線從「整支技能」改為「**框架 vs 實測答案**」。

先前的做法同時犯了兩個錯：把沒有替代難度的技能整支鎖起來（公開包變薄），
又把真正稀缺的實測目錄隨技能一起釋出。護城河從來不在方法論——公開文獻都有——
而在「只有實際用過那個系統才知道」的答案。

因此本版：

- **釋出**上述 3 支（方法論性質，替代難度不高，留著只是延後能見度）
- **收回** `tej-data-scout` 的資料表索引（Part B）與 `tej-variable-mapper` 的變數種子對照表
- 兩支 TEJ 技能的**方法論完整保留**：仍教「怎麼把題目拆成變數構念、怎麼判可行性、
  怎麼把文獻變數對映到資料庫欄位」，只是不附具體答案清單

---

## v0.13.1 — 2026-09-02

### 這次主要是「一致性與合規」的整補，不是新增技能

技能數維持 **35 支**。公開包自 2026-08-20 之後未再同步，期間私人庫的多項修訂
累積成漂移，這次一次補齊，並修掉數個會影響正確性的問題。

#### 修正：路由總管的斷鏈（會實際影響使用者）

`research-orchestrator` 先前列出並路由到 5 支**不在公開包內**的技能
（check-citations 與 4 支當時尚未釋出的技能；其中 3 支已於 v0.14.0 釋出）。症狀是 Claude 依名錄去叫一個
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
