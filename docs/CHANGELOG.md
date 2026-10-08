# 更新紀錄 / Changelog

本檔記錄**公開包**的變更。公開包是私人開發庫的釋出子集，部分技能與參考檔依既定
政策留在私人庫（原則：公開拿「防止受害」的防線，私人留「研究優勢」的能力）。

---

## v0.16.0 — 2026-10-09

**主題：既有技能的強化，合併三批（2026-10-04 金融方法、10-06、10-08 外部專案借設計）。** 技能數不變（38），未新增技能；
20 支強化，新增 11 份參考檔。所有外部專案都只借設計概念，未安裝、未執行、未複製其程式碼，致謝見 `NOTICE.md`。

### 圖表（借鑑 cathrynlavery/diagram-design，MIT）
- `research-framework-figure`：
  - `references/diagram-type-selector.md`：先定論證角色再選版式。含「表格測試」與「目錄測試」，補上研究流程圖、2×2 類型矩陣、多層次巢套、構念樹、DiD 政策時間軸的畫法。
  - `references/output-tiers.md`：期刊、口試、海報三種用途要重畫，不是縮放。附字級門檻、刪減順序與「省略帳」。
  - `visual-discipline.md` 補上連線衛生。
  - **修正**：假說標籤會蓋掉斜線一段，現改為沿法線外推。
- `management-figure`：
  - `references/chart-honesty.md`：逐圖種誠實紅線。實算 Okabe-Ito 的黃、淺藍、灰在白底對比不到 3:1，這三色不作細線或文字。
  - **修正**：森林圖不顯著者改為空心點加 `#767676`（原灰只有 2.83:1）；`interaction_plot` 與 `trend_plot` 內建線型與標記第二線索，黑白印刷也分得出來。
  - 新增 `car_plot()`：短窗事件研究的 CAAR 曲線（10-04）。
- `academic-poster`：海報上的圖依欄寬實寸重出。

### 連接器與退路（借鑑 anthropics/knowledge-work-plugins，Apache-2.0）
- `research-orchestrator`：`references/connector-map.md`。技能以工具類別書寫（文獻管理器、引用脈絡庫……），有接工具走加值路徑，沒接也能跑。原則包括「連上不等於有內容，也不等於有額度」。
- `citation-verifier`：「查不到不等於不存在」，可比對本機文獻庫。`literature-matrix-builder` 補上連接器退路。
- `thesis-consistency-audit`：`audit_docx.py` 改為回報掃到幾張表。原本英文表頭的表格會整張被略過。
- `phd-milestone-tracker`：`deadline_calc.py --ics` 匯出行事曆檔；給事件日可反推申請截止日。
- `nstc-grant-writer`：`references/assumption-risk-table.md`。「困難與因應」改為把最大風險排在第一年前段先驗證。

### 資料（借鑑 public-apis、Agent-Reach、rea，皆 MIT）
- `global-opendata-scout`：`references/free-api-vetting.md`，免費 API 學術准入檢核，涵蓋：
  - Auth、HTTPS、CORS 三欄在研究上的意義
  - 一手源與包裝層的區分
  - 八項檢核
  - 判定失效前的五步區辨
  - 「200 不等於成功」
  - 健康狀態詞彙與 A–D 用途分級
- `multi-source-data-integrator`、`public-disclosure-scout`：
  - 事先宣告取得順序
  - `_src` 記實際供數者
  - 備援來源與主源要做重疊期對帳
  - 回 200 但內容是空的或驗證頁，算取數失敗
- `spatial-data-architect`：接收座標欄前先查編碼（經度正負號、度分秒打包、格點吸附、地理編碼失敗率）。
- `phd-researcher`：`references/method-evidence-ledger.md`。方法逆向的判讀分「觀察／推論／未知」，否定陳述要帶搜尋邊界。

### 金融與事件研究方法（2026-10-04）
- `causal-inference-architect`：`references/event-study-estimation.md`，事件研究估計層。涵蓋窗口、市場模型、AR／CAR／BHAR、跨事件檢定，以及台灣 13:30 順延與漲跌停；完整估計引擎依時間差政策暫留私人庫。
- `r-spss-syntax-architect`：`references/finance-timeseries-lane.md`，金融時序第五軌。
- `text-analytics-architect`：`references/text-timestamp-alignment.md`，發布時間對交易日。
- `q1-journal-reviewer`：實證資產定價與預測論文子類。
- `tej-data-wrangler`：股價與報酬序列的六項紅旗。

### 其他
- `academic-deck-animator`：open-slide 致謝連結改為新組織 open-slide/open-slide（10-06）。

### 前次釋出後未記入的變更（commit d536e44）
- 結構層論證力度檢查 `argument-force-check.md`（中英兩支潤飾技能）與變數種子對照表的 A／B／D 區公開。

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
