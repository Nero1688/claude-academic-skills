# 大規模文獻篩選串接（Screening Cascade）

系統性回顧（SR）標題／摘要篩選在數千筆規模下，人工全篩不可行、但頂刊審稿人
（AMJ、SMJ、JOM 等）要的是 PRISMA 2020 流程數字、雙人篩選＋Cohen's κ、
預先註冊的納入排除準則——這三件事缺一不可。本檔是
`literature-matrix-builder` 的 `scripts/screen_cascade.py` 的設計說明與使用紀律。

## 緣起與立場：借架構思想，不借服務

社群關注 TypeSafe AI 的 Jev（System One「判斷模型」）能以低成本、短時間對大量
文本做快速判斷（例如以分鐘級時間、以美分計價篩過上千則新聞）。這對「篩選」這種
高量、低單筆風險、可分層決策的任務確實是對的架構方向——便宜的判斷層先把明顯
不相關的過濾掉，昂貴、謹慎的決策層只看存活者。

但學術文獻篩選不是新聞篩選，兩個差異決定了我們的選擇：

1. **可重現性要求不同。** SR 的篩選過程要能被審稿人、後續研究者重跑與稽核；
   閉源、白名單制的第三方服務做不到「凍結版本、逐字重跑得到同樣結果」。
2. **資料出站的學術風險不同。** 論文摘要多數公開（CrossRef／OpenAlex 可查），
   但研究者的準則設計、篩選決策本身、以及混在同一個檔案裡的未發表資料
   （見下一節），一旦送到不受控的第三方伺服器，就不是「用了 AI 工具」這麼
   簡單，而是資料治理與倫理審查層級的問題。

**結論：本串接不接 Jev API，借用的只是「判斷層／決策層分工」這個架構思想。**
未使用其 API、未借用其程式碼，完整聲明見 `../ATTRIBUTION.md`。

## 三階段架構

```
records.csv ──▶ [階段一：規則] ──▶ stage1.csv ──▶ [階段二：LLM 判斷] ──▶ stage2 結果
                 零 LLM、零網路        (pass/exclude)   只看階段一存活者        │
                                                         預設 Anthropic Batches  ▼
                                                                         [階段三：人工複核]
                                                                    unsure ＋ 抽樣核對
```

### 階段一｜確定性規則（`stage1` 子指令）

不靠 LLM，靠可稽核的布林規則，對應 `screen_cascade.py` 的檢查順序：

1. **DOI 去重**——同一 DOI 第二次出現直接判 `duplicate_doi`，不管內容。
2. **年份區間**——`year_min`／`year_max` 任一超界就排除，缺年份視為超界
   （保守處理：驗證不到就不放行，呼應 CLAUDE.md 的數字零容忍精神）。
3. **語言粗估**——用非 ASCII 字母比例猜語言，不在 `allowed_languages` 內就排除。
   這是粗估不是語言學判斷，別拿它宣稱「已完成語言篩選的效度檢定」。
4. **`exclude_any` 排除詞**——命中任一詞（如 retracted／erratum）就排除。
5. **`include_any` 納入詞**——一個都沒命中就排除；清單留空代表不設此關卡。

每筆記錄輸出 `decision`（pass／exclude）與 `rule`（觸發的規則名），這兩欄
就是 PRISMA 流程圖「排除理由」的原始資料，不需要另外重新統計。

### 階段二｜LLM 批次判斷（`stage2-prepare` ＋ `stage2-submit`）

**只處理階段一的存活者**——這是成本控制的核心：便宜的規則層先把明顯不合格
的擋掉，貴的判斷層只花在真正模稜兩可的記錄上。

- `stage2-prepare` 純本機操作，讀 `stage1.csv` 與凍結的 `criteria.json`，
  組出 Anthropic Message Batches API 的 JSONL 請求檔，**完全不連網**。
  每筆請求的 `system` 帶入準則版本號與凍結日期，`user` 帶入 title＋abstract，
  要求回傳結構化 JSON：`{"decision": "include|exclude|unsure", "reason": "...",
  "quote": "..."}`。要求給 `quote`（可引用的原文短句）是為了讓人工複核時
  能立刻對照原文，不必整篇重看。
- `stage2-submit` 才會連網，且**只送往 `https://api.anthropic.com/`**。
  金鑰只讀環境變數 `ANTHROPIC_API_KEY`，程式絕不把金鑰寫進檔案或印到畫面；
  沒有金鑰就印說明並以結束碼 2 退出，`--dry-run` 可以只看請求摘要不送出。

### 階段三｜人工複核（不自動化，工具只幫你找出該複核什麼）

- LLM 判 `unsure` 的記錄，一律進人工複核，不可自動歸類為 include 或 exclude。
- 建議另外對 LLM 判 `include`／`exclude` 的記錄各抽 10–15% 做人工核對，
  核對結果與 LLM 決策一起餵給 `kappa` 子指令，監控 LLM 判斷是否隨時間漂移
  （準則沒變、但模型版本換了，一致性可能跟著變）。

## 隱私分級（硬規則，不可繞過）

| 資料類型 | 能否送進階段二（LLM） |
|---|---|
| 公開摘要（CrossRef／OpenAlex／出版社官網取得） | 可以 |
| 未發表稿件（含作者自己的工作論文全文或摘要） | **不可以** |
| 審稿中稿件（含自己身為審稿人看到的稿件） | **不可以** |
| 訪談逐字稿、受訪者可識別內容 | **不可以** |

理由很直接：公開摘要本來就已經是公開資訊，送進已信任供應商的批次 API
風險與查該篇論文的 Google Scholar 頁面相去不遠；但未發表稿件、審稿中稿件
牽涉到他人（含期刊、共同作者、受訪者）尚未同意公開的內容，送進任何第三方
伺服器都是資料治理層級的風險，不是「方便就好」可以抵銷的。

`screen_cascade.py` 用 `records.csv` 的選填欄位 `source_type` 做技術防呆：
標成 `unpublished`／`under_review`／`interview_transcript`／
`working_paper_confidential`（或中文「未發表」／「審稿中」／「訪談逐字稿」）
的記錄，即使階段一判 `pass`，`stage2-prepare` 也會直接擋下、不寫進 JSONL，
並在輸出中回報擋了幾筆。**但這只是防呆網，不是免責。** 建檔當下就該把這類
資料放進 `library.json` 而不是塞進要送階段二的 `records.csv`。

## judge 可插拔設計

`stage2-submit --judge <名稱>` 決定送去哪個判斷層：

- **`anthropic-batch`（預設，已實作）**——Anthropic Message Batches API。
  選它的原因：資料留在使用者已經在用、已讀過其資料政策的同一個供應商，
  不是額外多信任一個新的第三方；批次定價通常低於即時呼叫（本檔不寫死
  折扣比例，請查 Anthropic 官方定價頁當日數字）。
- **`jev`（未實作插槽，刻意留空）**——呼叫時直接印隱私警告並以結束碼 3
  退出，不執行任何動作。不接的原因：

  1. **閉源。** System One 的判斷邏輯、資料處理細節不公開，無法對審稿人
     交代「篩選過程如何被驗證」。
  2. **白名單制。** 非開放 API，一般研究者拿不到穩定、可重現的存取管道，
     不符合「別人也能重跑我的 SR」的可重現性要求。
  3. **資料出站至第三方伺服器。** 送出的內容（哪怕只是摘要）離開了使用者
     已審視過政策的供應商範圍，多了一層無法稽核的資料流。
  4. **官方站名混淆風險。** 社群常見的 `jevai.org` 並非官方站，官方站是
     `typesafe.ai`——文獻或方法節若要提到這個工具，網址要查證過再寫，
     不要憑記憶貼連結（此類細節正是幻覺文獻的溫床）。

  **若未來真的要接**，必須先過三個檢查，任一過不了就不接：

  - [ ] 讀過官方隱私政策，確認摘要資料的用途範圍與是否會被用於模型訓練；
  - [ ] 確認資料保留（retention）政策，能否要求不留存、留存多久；
  - [ ] 確認是否可以明確關閉「輸入資料用於訓練」——關不掉就不接，
        沒有例外（送審稿摘要進一個會拿去訓練的黑盒子，等同把同儕的
        未發表構想餵給第三方，這不是效率問題是倫理問題）。

  新增 judge 後端時，`references/screening-cascade.md`（本檔）與
  `ATTRIBUTION.md` 都要同步更新來源與限制說明，不能只改程式碼。

## 雙篩設計與 Cohen's κ

單人篩選（不管是一位研究生還是一個 LLM）都有系統性偏誤的風險，頂刊審稿人
對「只有一人篩選、沒有一致性指標」的 SR 稿件會直接質疑其可信度。

**雙篩設計三選一：**

1. **人工 × 人工**（傳統做法，成本最高、但仍是金標準）。
2. **LLM × 人工**（本串接的建議預設）——LLM 做主篩，另抽樣或全量由一位
   人工獨立篩選（不能看過 LLM 的決策再篩，否則失去獨立性），兩者決策
   餵進 `kappa` 子指令。
3. **LLM × LLM（不同 prompt／不同模型）**——最省成本但說服力最弱，
   頂刊審稿人可能質疑「兩個 AI 一致不代表篩選是對的」；若用這個設計，
   至少要對不一致的子集做人工終裁，且在方法節誠實揭露設計限制。

**κ 判讀門檻（Landis & Koch, 1977，`kappa` 子指令內建）：**

| κ 範圍 | 判讀 |
|---|---|
| < 0 | poor（比隨機猜測還不一致） |
| 0.00–0.20 | slight |
| 0.20–0.40 | fair |
| 0.40–0.60 | moderate |
| 0.60–0.80 | substantial |
| 0.80–1.00 | almost perfect |

**κ 不是自動化篩選的主要效度指標——recall 才是。** κ 衡量兩位篩選者的一致性，
但對「漏掉該收的研究」不敏感：LLM 把 100 篇該收的漏了 10 篇、把 900 篇該排的
全排對，κ 仍然很高，而漏收正是 SR 的致命錯誤。自動化篩選工具的驗證指標是
**對人工金標準的 recall（sensitivity）**（O'Mara-Eves et al., 2015, *Systematic Reviews*），
JOM／IJMR 審稿人會問「LLM 篩掉的裡面有多少是該收的」。`kappa` 子指令因此在 κ 之外
一併印出（以 `file_a` 為人工真值，`--truth b` 可對調；正類預設 `include`）：

| 輸出 | 定義 | 怎麼用 |
|---|---|---|
| recall（嚴格） | 人工判 include 中，LLM 也判 include 的比例；`unsure` 視為 exclude | 最壞情況；若 unsure 沒有全數進人工複核，就是這個數字 |
| recall（寬鬆） | 同上，但 `unsure` 視為 include | 依本串接規範 unsure 一律人工複核，實際漏收率是這個 |
| precision | LLM 判 include 中，人工也判 include 的比例 | 低＝人工全文階段要多做工，不是效度問題 |
| 漏收 id 清單 | 嚴格模式下人工 include、LLM 未 include 的記錄 | 逐篇看：是準則模糊還是模型錯，回饋到準則版本 |

recall（寬鬆）未達 0.95 級別時，方法節要說明處置：擴大人工複核抽樣比例、
或對 LLM 判 exclude 的記錄改全量人工篩選。

**κ 低於 .60 時該做的事：先修準則，不是先修模型。** 常見原因是
`include_any`／`exclude_any` 定義得太模糊、或準則沒講清楚邊界案例
（例如「家族企業」要不要包含家族僅任監察人但不任董事的公司）。把不一致
的案例挑出來，逐一討論該收斂到哪一邊，寫進準則的 `notes` 欄，**升版號**
而不是靜默修改，再重新篩一次抽樣子集驗證 κ 是否回升。直接加大 LLM 樣本
或換更貴的模型不能解決準則本身模糊的問題。

## 成本試算（不寫死定價）

每千則摘要的估算公式（自行代入官方定價頁「當日」數字，模型與定價會變動）：

```
每則輸入 token 數 ≈ (system prompt token 數) + (title token 數) + (abstract token 數)
每則輸出 token 數 ≈ 100–200（含 JSON 結構與 quote，視摘要長度而定）

每千則預估成本
  = 1000 × [ (每則輸入 token / 1,000,000 × 輸入單價)
           + (每則輸出 token / 1,000,000 × 輸出單價) ]
```

- 批次 API（Message Batches）相對即時呼叫通常有價格折扣，折扣比例查官方
  定價頁當日資訊，本檔不寫死數字（比例本身會變動，寫死等於寫錯）。
- system prompt（含準則）在同一批請求中重複出現，若供應商支援 prompt
  caching，重複的準則文字部分理論上可受益於快取折扣；是否啟用、如何計費
  一樣查官方文件當日版本。
- 概算方法：先跑 `stage2-prepare` 產出 JSONL，用任一 token 計數工具
  （官方 token counting endpoint，或近似地用「英文約 4 字元 1 token、
  中文約 1–2 字 1 token」概估）抓實際 token 數，再代入上式，比憑印象
  估計準確。

## PRISMA 2020 對接

**先把一件事講清楚：stage1（規則）與 stage2（LLM）都是標題／摘要層級的篩選，
全部落在 PRISMA 2020（Page et al., 2021, *BMJ*）的 Identification／Screening 兩框；
「reports sought for retrieval／reports assessed for eligibility」是**全文**階段，
本串接不自動化。** 舊版把 stage2 對到 "reports assessed for eligibility" 是錯的——
JOM／IJMR 的 SR 審稿人會直接指出 LLM 只看了摘要、沒看全文。

`prisma` 子指令的對應（`--stage1-as automation` 為預設）：

| PRISMA 2020 盒子 | 本串接的資料來源 |
|---|---|
| Identification：records identified | `stage1.csv` 總筆數 |
| Identification：duplicate records removed | `rule == duplicate_doi` 的筆數 |
| Identification：**records marked as ineligible by automation tools** | stage1 `decision == exclude` 且 `rule != duplicate_doi`（年份／語言／關鍵字等確定性規則，人未看過）；方法節須列出規則內容。若你偏好把這些算進篩選排除，用 `--stage1-as screening` |
| Screening：records screened | 進入 stage2 的筆數（= 去重後 − 自動化工具排除） |
| Screening：records excluded | stage2 `decision == exclude`（LLM 輔助、人工抽核）；`unsure` 待 Stage 3 人工複核後分流 |
| Retrieval：reports sought for retrieval | stage2 `include` ＋ unsure 複核後判 include 者 → **人工全文階段的輸入** |
| Retrieval：reports not retrieved | `--fulltext` 檔 `decision == not_retrieved` |
| Eligibility：reports assessed for eligibility | `--fulltext` 檔扣除 not_retrieved |
| Eligibility：reports excluded（依理由） | `--fulltext` 檔 `decision == exclude`，依 `reason` 欄分列 |
| Included：studies included | `--fulltext` 檔 `decision == include` |

全文階段的人工判定存成 `fulltext.csv`（欄位 `id, decision ∈ include/exclude/not_retrieved, reason`）
餵給 `prisma --fulltext`；沒提供時後三框印「待補」，**不可用 stage2 的數字冒充全文階段**。

對帳規則與 `phd-researcher` 完全一致：識別數＝去重後數＋重複數；
篩選之記錄＝篩選排除＋unsure＋進入全文階段；全文評讀數＝納入＋排除。
任一級對不上，`prisma` 子指令會印警告並回傳非 0 結束碼——**依規範這時要
停下來標紅，不准填一個看起來合理但湊不平的數字**。對帳通過後，把數字填進
`phd-researcher` 的 `references/prisma-flowdiagram-recipe.md` 所述的官方
PRISMA2020 工具（R 套件或 Shiny 網頁版），或 `research-framework-figure` 的
`sample_flow`（mode = prisma；自動化工具排除數填 `identification.automation_excluded`）
產出正式流程圖，不要手畫、也不要在這個階段之前就先畫圖湊數字。

## 頂刊落差：台灣 SR 稿件常見的三個扣分點

| 常見問題 | 對策 |
|---|---|
| 篩選只有一人做，沒有第二篩選者 | 至少做 LLM × 人工雙篩（見上節），並在方法節寫清楚分工 |
| 沒有一致性指標（κ 或其他），或只報 κ 不報 recall | `kappa` 子指令算出來的 κ **與對人工金標準的 recall／precision** 一起寫進方法節，附判讀等級與漏收處置 |
| 納入排除準則「事後追加」——寫作時發現某類文獻麻煩就臨時加一條排除規則 | 準則存成版本化的 JSON（`screening-criteria-template.json`），frozen_date 定案後改準則要升版號；有能力的話在 PROSPERO 或 OSF 預先註冊，審稿人看到版本紀錄比看到一段「我們排除了不相關文獻」的文字有說服力得多 |

**額外提醒：** LLM 判斷本身要揭露。方法節不要寫「我們判斷了 X」，要寫類似
「本研究於標題／摘要篩選階段先以確定性規則（年份、語言、關鍵字；規則內容見附錄）
排除 n = … 筆（PRISMA 2020 之 records marked as ineligible by automation tools），
再以 Claude（模型版本、準則版本、篩選日期）輔助判斷，並由一位研究者獨立篩選
隨機抽樣之 …% 記錄作為金標準；LLM 輔助篩選對人工金標準的 recall = …
（unsure 視為納入）、precision = …，雙篩一致性 Cohen's κ = …；全部 unsure 案例
均經人工複核。全文資格評讀由兩位研究者獨立進行」這種可被稽核複製的寫法——
**recall 是自動化篩選的主指標，κ 是輔助**，兩個都要報。
語言紀律與 `text-analytics-architect` 的 LLM 標註信效度紀律一致：LLM 是
「輔助判斷工具」，不是「做出學術判斷的主體」，論文裡的措辭要反映這件事。

## 與既有工具的銜接

- 篩選完成、綜整欄要填時，交棒本 skill 既有的 `add`／`build` 流程
  （見 `SKILL.md` 的工作流程 Step 1–4），把納入的文獻建進 `library.json`
  與 Excel 矩陣。
- 正式跑完整 SR／MA（偏誤風險評估、後設分析、預先註冊）交棒
  `anthropic-skills:phd-researcher` 的階段四模組。
- 引用真偽查核（這篇文獻真的存在嗎）交棒 `check-citations`；
  內文與清單對帳交棒 `citation-verifier`。
- 維護者本機版本若已有真實 SR 主題（家族企業／ESG／公司治理）的準則調校紀錄，
  記在維護者本機版本專用的準則調校文件（公開包不含此檔）。
