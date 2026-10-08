# 更新紀錄 / Changelog

這裡記錄每一版改了什麼，最新的在最上面。

---

## v0.16.0 — 2026-10-09

**這版沒有新增技能（一樣 38 支），而是把其中 20 支練得更扎實，另外多了 11 份參考資料。**
有些點子參考了其他開源專案的做法，名單都列在 `NOTICE.md`；我們只借想法，沒有搬他們的程式。

### 畫圖更不容易出錯
- `research-framework-figure`（研究架構圖）
  - 新增「先想清楚這張圖要說什麼，再決定怎麼畫」的選圖指南，連第一章常見的研究流程圖、2×2 分類表、時間軸都有範例。
  - 同一張圖要放期刊、口試簡報、海報時，教你怎麼重畫，而不是硬縮小。
  - 修好一個小毛病：H1、H2 這類標籤以前會把斜線遮掉一段，現在不會了。
- `management-figure`（統計圖）
  - 新增「每種圖的誠實規則」，例如哪些顏色印成黑白就分不出來。
  - 森林圖裡「不顯著」的點以前灰得太淡，現在改成空心點、顏色加深。
  - 交互作用圖和趨勢圖現在除了顏色，還會用不同線型和記號區分，黑白列印也看得懂。
  - 新增事件研究常用的平均累積異常報酬（CAAR）曲線。
- `academic-poster`（海報）：海報上的圖要照欄寬重新出圖，不要直接放大期刊圖。

### 有沒有接上外部工具都能用
- `research-orchestrator`（研究流程總管）：有接 Zotero 這類工具就多用一點，沒接也照樣能跑。也提醒「連得上」不代表「裡面有資料」或「還有額度」。
- `citation-verifier`：查不到一篇文獻，不等於這篇不存在，要分開說清楚。
- `thesis-consistency-audit`：現在會告訴你它檢查了幾張表，以前英文表頭的表格會被整張跳過。
- `phd-milestone-tracker`：可以把所有截止日匯出成行事曆檔（`--ics`），匯入手機就有提醒。
- `nstc-grant-writer`：「困難與因應」改成先列最大的風險，並安排在第一年前段先驗證。

### 找資料、用資料
- `global-opendata-scout`：新增一份清單，幫你判斷網路上的免費資料 API 能不能拿來寫論文——資料是誰產生的、授權允不允許、版本能不能追溯。也提醒：網站回應「成功」不代表真的拿到資料。
- `multi-source-data-integrator`、`public-disclosure-scout`：記下每筆資料實際是從哪個來源抓到的；抓到空白頁或驗證頁要算失敗，不能當成「沒有資料」。
- `spatial-data-architect`：拿到別人的座標資料，先檢查經緯度的正負號和格式對不對。
- `phd-researcher`：拆解別人論文的方法時，把「原文寫了的」「自己推論的」「查不到的」分開記；說「原文沒做某件事」之前，要先講清楚你查過哪些地方。

### 金融與事件研究
- `causal-inference-architect`：新增事件研究的估計步驟說明（事件窗口、市場模型、異常報酬、檢定方法，以及台灣盤後 13:30 與漲跌停的處理）。
- `r-spss-syntax-architect`：新增金融時間序列的語法指南。
- `text-analytics-architect`：新聞或公告的發布時間，要怎麼對到正確的交易日。
- `q1-journal-reviewer`：新增資產定價與預測類論文的審稿重點。
- `tej-data-wrangler`：整理股價與報酬資料時要注意的六個地雷。

### 其他
- `academic-journal-polisher`、`q1-journal-polisher`：新增「論證力道」檢查。
- `tej-variable-mapper`：補上常用變數的對照範例。
- `academic-deck-animator`：更新一個致謝連結。

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

- `journal-submission-scout` — 幫你挑投稿期刊，也幫你避開掠奪性期刊
- `research-framework-figure` — 畫研究架構圖，可以輸出成能再編輯的 SVG 和 PPTX
- `spatial-data-architect` — 地理資料分析：地址轉座標的檢查、六角網格、台灣座標系統的轉換

### 調整
- `tej-data-scout`、`tej-variable-mapper`：專注在方法——怎麼把研究題目拆成變數、怎麼判斷資料夠不夠用、怎麼把文獻裡的變數對到資料庫欄位。

---

## v0.13.1 — 2026-09-02

這版主要是修正，沒有新增技能（35 支）。

- **修好研究流程總管的「斷鏈」**：`research-orchestrator` 以前會叫用幾支不在本技能包裡的技能。Claude 叫不到時不會報錯，只會默默改成一般回答，讓人以為技能沒作用。現在名單和實際內容一致，可叫用的技能是 34 支。
- **修好指向不存在檔案的引用**：`global-opendata-scout` 以前會去讀兩份已經不在的參考檔，已改寫。台灣在聯合國貿易資料庫（UN Comtrade／WITS）被併入代碼 `490` 的提醒完整保留——查錯代碼會拿到 0 筆卻不報錯，很容易誤以為「沒有台灣資料」。
- **內容更新**：多支技能的說明與參考檔更新，包括兩支潤飾技能、`phd-milestone-tracker`、`qualitative-thematic-coder`、`r-spss-syntax-architect`、`public-disclosure-scout`、`tej-data-scout`、`academic-slides`、`research-method-selector`。
- 新增 `tej-data-scout/references/tej-access-channels.md`：TEJ 資料的三種取得方式比較，並提醒「學校的 TEJ Pro 帳號不能直接拿來用 API」。

---

## 2026-08-20 — v0.13.0

兩道學術誠信防線：撤稿查核（併入 `literature-matrix-builder`）與雙盲投稿的
身分資訊清除（`thesis-consistency-audit/scripts/anonymize_office.py`）。

---

> 更早的紀錄見 git 歷史。
